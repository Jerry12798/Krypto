import discord
import asyncio
import aiohttp
import time
import pymongo
import motor.motor_asyncio
from discord.ext import commands, tasks
from datetime import datetime



class iOS(commands.Cog, name="iOS"):
	def __init__(self,bot):
		self.bot = bot
		self.check_iOS.start()
	def cog_unload(self):
		self.check_iOS.cancel()
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)

	@commands.command() # Signed Versions Command
	async def signed(self, ctx, *, param:str=None):
		async with self.bot.session.get("https://api.ipsw.me/v2.1/firmwares.json/condensed") as url:
			data = await url.json()
			devices = data['devices']
			itunes = data['iTunes']
			signed = 0
			embeds = []
			build_ids = []
			builds = {}

			for z in devices:
				versions = []
				ids = []
				sizes = []
				dates = []
				urls = []
				name = devices[f'{z}']['name']
				firmwares = devices[f'{z}']['firmwares']
				regex = [f"{param}"]
				if param is None:
					regex = ["iPhone", "iPad", "iPod"]
				regex_2 = ["China", "Global", "WiFi"]
				
				counter = 0
				if any(x.lower() in name.lower() for x in regex):
					if not any(x.lower() in name.lower() for x in regex_2):
						for x in firmwares:
							if x['signed'] is True:
								versions += {x['version']}
								ids += {x['buildid']}
								org = x['size']
								size = org*10**-9
								show = f"{size:.2f} GB"
								if int(size) < 1:
									size = org*10**-6
									show = f"{size:.2f} MB"
								sizes += {show}
								try:
									grab = x['releasedate']
								except:
									grab = x['uploaddate']
								fmt = "%I:%M%p %B %d, %Y %Z"
								fix = datetime.strptime(grab, "%Y-%m-%dT%H:%M:%SZ")
								date = fix.strftime(fmt)
								dates += {date}
								urls += {x['url']}
						embed = discord.Embed(title=f"**{name}**", timestamp=datetime.utcnow(), color=0xac5ece)
						embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
						for x in versions:
							if not "iPad".lower() in name.lower():
								embed.add_field(name=f"__**iOS Version {versions[counter]}**__", value=f"**Build ID:** [{ids[counter]}]({urls[counter]})\n**Size:** {sizes[counter]}\n**Release Date:** {dates[counter]}", inline=False)
							if "iPad".lower() in name.lower():
								embed.add_field(name=f"__**iPadOS Version {versions[counter]}**__", value=f"**Build ID:** [{ids[counter]}]({urls[counter]})\n**Size:** {sizes[counter]}\n**Release Date:** {dates[counter]}", inline=False)
							counter += 1
						if not versions == []:
							signed += 1
							embeds += {embed}
							log = {}
							log ["Name"] = name
							log ["Version"] = versions
							log ["Build"] = ids
							log ["URL"] = urls
							log ["Size"] = sizes
							log ["Date"] = dates
							builds[f'{z}'] = log
							build_ids += {z}
			if signed == 0:
				embed = discord.Embed(title="__**iOS Updates Error**__", description=f"No Results with the Keyword `{param}`..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			message = await ctx.send(embed=embeds[0])
			collection = self.bot.db["AM_iOS"]
			log = {}
			log ["Guild_Name"] = ctx.guild.name
			log ["Guild"] = ctx.guild.id
			log ["Author"] = ctx.author.id
			log ["Channel"] = ctx.channel.id
			log ["Message"] = message.id
			log ["List"] = builds
			log ["IDs"] = build_ids
			log ["Counter"] = 1
			log ["Pages"] = signed
			await collection.insert_one(log)
			reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
			for x in reactions:
				await message.add_reaction(x)
			try:
				await ctx.message.delete()
			except:
				print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
			await asyncio.sleep(300)
			old_log = {"Message": message.id}
			await collection.delete_one(old_log)
			await message.delete()

	@commands.command() # Tweak Lookup Command
	async def tweak(self, ctx, *, param:str=None):
		async with self.bot.session.get(f"https://api.parcility.co/db/search?q={param}") as url:
			data = await url.json()
			results = {}
			tresults = 0
			if int(data['code']) != 200:
				embed = discord.Embed(title="__**Tweak Lookup Error**__", description=f"No Results with the Keyword `{param}`..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			for x in data['data']:
				tweak = x['normalizedName']
				icon = x['Icon']
				desc = x['Description']
				try:
					link = x['Depiction']
				except:
					link = "N/A"
				author = x['Author']
				maintainer = x['Maintainer']
				version = x['Version']
				build_id = x['Package']
				section = x['Section']
				req = x['Depends']
				b = x['builds'][len(x['builds'])-1]
				r = x['repo']
				repo = r['label']
				repo_link = r['url']
				repo_icon = r['icon']
				if not repo_link.endswith('/'):
					repo_link+"/"
				download = repo_link+b['Filename']
				org = int(b['Size'])
				size = org*10**-9
				show = f"{size:.2f} GB"
				if int(size) < 1:
					size = org*10**-6
					show = f"{size:.2f} MB"
				if int(size) < 1:
					size = org/1000
					show = f"{size:.2f} KB"
				log = {}
				log ['Tweak'] = tweak
				log ['Logo'] = icon
				log ['Description'] = desc
				log ['Link'] = link
				log ['Author'] = author
				log ['Maintainer'] = maintainer
				log ['Version'] = version
				log ['Build'] = build_id
				log ['Section'] = section
				log ['Requirements'] = req
				log ['Repo'] = repo
				log ['Repo_URL'] = repo_link
				log ['Repo_Logo'] = repo_icon
				log ['Download'] = download
				log ['Size'] = show
				results[f'{repo} | {tweak}'] = log
				if tresults < 1:
					embed = discord.Embed(title=f"", description=f"**{tweak}**\n{desc}", timestamp=datetime.utcnow(), color=0xac5ece)
					if not link == "N/A":
						embed = discord.Embed(title=f"", description=f"**[{tweak}](<{link}>)**\n{desc}", timestamp=datetime.utcnow(), color=0xac5ece)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
					embed.set_author(name=f"{repo}", icon_url=repo_icon)
					embed.set_thumbnail(url=icon)
					embed.add_field(name=f"__**Author**__", value=f"*{author}*", inline=False)
					embed.add_field(name=f"__**Maintainer**__", value=f"*{maintainer}*", inline=False)
					embed.add_field(name=f"__**Version**__", value=f"*{version}*", inline=False)
					embed.add_field(name=f"__**Size**__", value=f"*{show}*", inline=False)
					embed.add_field(name=f"__**Bundle ID**__", value=f"*{build_id}*", inline=False)
					embed.add_field(name=f"__**Section**__", value=f"*{section}*", inline=False)
					embed.add_field(name=f"__**Requirements**__", value=f"*{req}*", inline=False)
					embed.add_field(name=f"__**Download**__", value=f"*[Click Here to Download](<{download}>)*", inline=False)
				tresults += 1

			if tresults == 1:
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
			message = await ctx.send(embed=embed)
			if tresults > 1:
				collection = self.bot.db["AM_iOS_tweaks"]
				log = {}
				log ["Guild_Name"] = ctx.guild.name
				log ["Guild"] = ctx.guild.id
				log ["Author"] = ctx.author.id
				log ["Channel"] = ctx.channel.id
				log ["Message"] = message.id
				log ["List"] = results
				log ["Counter"] = 1
				log ["Pages"] = tresults
				await collection.insert_one(log)
				reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
				for x in reactions:
					await message.add_reaction(x)
				try:
					await ctx.message.delete()
				except:
					print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
				await asyncio.sleep(300)
				old_log = {"Message": message.id}
				await collection.delete_one(old_log)
			await message.delete()
		
	@commands.command() # Set iOS Updates Channel
	@commands.has_permissions(administrator=True)
	async def iupdates(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**iOS Updates Error**__", description=f"Mention Channel to Receive iOS Update Logs in.\n`{self.bot.prefix}ios <Mention Channel>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_iOS_channel"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will be sent to {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will now be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await channel.send(embed=embed_3)
			await ctx.message.delete()
			return
		async for x in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_channel = x["Channel"]
			old_channel = ctx.message.guild.get_channel(grab_old_channel)
		embed_2 = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will no longer be sent to {old_channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will no longer be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@iupdates.error
	async def iupdates_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



	@commands.Cog.listener() # Paginate Event
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		collection = self.bot.db["AM_iOS"] # Paginate iOS Versions
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				builds = x["List"]
				build_ids = x["IDs"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)
		
		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages
			firmwares = builds[f'{build_ids[counter-1]}']
			name = firmwares['Name']
			versions = firmwares['Version']
			builds = firmwares['Build']
			urls = firmwares['URL']
			sizes = firmwares['Size']
			dates = firmwares['Date']
			query = 0
			embed = discord.Embed(title=f"**{name}**", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			for x in versions:
				if not "iPad".lower() in name.lower():
					embed.add_field(name=f"__**iOS Version {versions[query]}**__", value=f"**Build ID:** [{builds[query]}]({urls[query]})\n**Size:** {sizes[query]}\n**Release Date:** {dates[query]}", inline=False)
				if "iPad".lower() in name.lower():
					embed.add_field(name=f"__**iPadOS Version {versions[query]}**__", value=f"**Build ID:** [{builds[query]}]({urls[query]})\n**Size:** {sizes[query]}\n**Release Date:** {dates[query]}", inline=False)
				query += 1
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})




		collection = self.bot.db["AM_iOS_tweaks"] # Paginate iOS Tweaks
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				results = x["List"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)
				grab = []
				for i in results:
					grab += [results[f"{i}"]]
		

		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages

			current = grab[counter-1]
			tweak = current['Tweak']
			icon = current['Logo']
			desc = current['Description']
			link = current['Link']
			author = current['Author']
			maintainer = current['Maintainer']
			version = current['Version']
			build_id = current['Build']
			section = current['Section']
			req = current['Requirements']
			repo = current['Repo']
			repo_link = current['Repo_URL']
			repo_icon = current['Repo_Logo']
			download = current['Download']
			size = current['Size']

			embed = discord.Embed(title=f"", description=f"**[{tweak}](<{link}>)**\n{desc}",timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{repo}", icon_url=repo_icon)
			embed.set_thumbnail(url=icon)
			embed.add_field(name=f"__**Author**__", value=f"*{author}*", inline=False)
			embed.add_field(name=f"__**Maintainer**__", value=f"*{maintainer}*", inline=False)
			embed.add_field(name=f"__**Version**__", value=f"*{version}*", inline=False)
			embed.add_field(name=f"__**Size**__", value=f"*{size}*", inline=False)
			embed.add_field(name=f"__**Bundle ID**__", value=f"*{build_id}*", inline=False)
			embed.add_field(name=f"__**Section**__", value=f"*{section}*", inline=False)
			embed.add_field(name=f"__**Requirements**__", value=f"*{req}*", inline=False)
			embed.add_field(name=f"__**Download**__", value=f"*[Click Here to Download](<{download}>)*", inline=False)
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})



	@tasks.loop(minutes=10)
	async def check_iOS(self):
		try:
			collection = self.bot.db["AM_iOS_updates"]
			collection_2 = self.bot.db["Config_iOS_channel"]
			async with self.bot.session.get("https://api.ipsw.me/v2.1/firmwares.json/condensed") as url:
				new = 0
				old = 0
				add = ""
				remove = ""
				data = await url.json()
				devices = data['devices']
				channels = []
				channel_ids = collection_2.find({})
				async for x in channel_ids:
					channels += {x["Channel"]}
		
				for z in devices:
					versions = []
					ids = []
					urls = []
					name = devices[f'{z}']['name']
					firmwares = devices[f'{z}']['firmwares']
					regex = ["iPhone", "iPad", "iPod"]
					regex_2 = ["China", "Global", "WiFi"]

					grab = collection.find({"Build": z}, {"_id": 0})
					old_versions = []
					async for x in grab:
						old_versions = x["Version"]
						old_ids = x["BuildIDs"]
					
					if any(x.lower() in name.lower() for x in regex):
						if not any(x.lower() in name.lower() for x in regex_2):

							for x in firmwares:
								if x['signed'] is True:
									versions += {x['version']}
									ids += {x['buildid']}
									urls += {x['url']}
							amount = 0
							for x in versions:
								if not x in old_versions:
									if "iPad".lower() in name.lower():
										check = add + f"***{name}*** *-* iPadOS {x}*({ids[amount]})*\n"
									if not "iPad".lower() in name.lower():
										check = add + f"***{name}*** *-* iOS {x}*({ids[amount]})*\n"
									#if "iPad".lower() in name.lower():
									#	check = add + f"***{name}*** *-* [iPadOS {x}({ids[amount]})](<{urls[amount]}>)\n"
									#if not "iPad".lower() in name.lower():
									#	check = add + f"***{name}*** *-* [iOS {x}({ids[amount]})](<{urls[amount]}>)\n"
									if len(check) > 1024:
										embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.utcnow(), color=0xac5ece)
										embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
										embed.add_field(name=f"**Apple just started signing New iOS Versions for these devices:**", value=f"{add}", inline=False)
										for y in channels:
											try:
												channel = self.bot.get_channel(y)
												await channel.send(embed=embed)
												await asyncio.sleep(2)
											except:
												pass
										add = ""
									if "iPad".lower() in name.lower():
										add += f"***{name}*** *-* iPadOS {x}*({ids[amount]})*\n"
									if not "iPad".lower() in name.lower():
										add += f"***{name}*** *-* iOS {x}*({ids[amount]})*\n"
									#if "iPad".lower() in name.lower():
									#	add += f"***{name}*** *-* [iPadOS {x}({ids[amount]})](<{urls[amount]}>)\n"
									#if not "iPad".lower() in name.lower():
									#	add += f"***{name}*** *-* [iOS {x}({ids[amount]})](<{urls[amount]}>)\n"
									new += 1
								amount += 1

							amount = 0
							if not old_versions == []:
								for x in old_versions:
									if not x in versions:
										if "iPad".lower() in name.lower():
											check = remove + f"***{name}*** *-* iPadOS {x}*({old_ids[amount]})*\n"
										if not "iPad".lower() in name.lower():
											check = remove + f"***{name}*** *-* iOS {x}*({old_ids[amount]})*\n"
										#if "iPad".lower() in name.lower():
										#	check = remove + f"***{name}*** *-* [iPadOS {x}({old_ids[amount]})](<{urls[amount]}>)\n"
										#if not "iPad".lower() in name.lower():
										#	check = remove + f"***{name}*** *-* [iOS {x}({old_ids[amount]})](<{urls[amount]}>)\n"
										if len(check) > 1024:
											embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.utcnow(), color=0xac5ece)
											embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
											embed.add_field(name=f"**Apple is No Longer signing iOS Versions for these devices:**", value=f"{remove}", inline=False)
											for y in channels:
												try:
													channel = self.bot.get_channel(y)
													await channel.send(embed=embed)
													await asyncio.sleep(2)
												except:
													pass
											remove = ""
										if "iPad".lower() in name.lower():
											remove += f"***{name}*** *-* iPadOS {x}*({old_ids[amount]})*\n"
										if not "iPad".lower() in name.lower():
											remove += f"***{name}*** *-* iOS {x}*({old_ids[amount]})*\n"
										#if "iPad".lower() in name.lower():
										#	remove += f"***{name}*** *-* [iPadOS {x}({old_ids[amount]})](<{urls[amount]}>)\n"
										#if not "iPad".lower() in name.lower():
										#	remove += f"***{name}*** *-* [iOS {x}({old_ids[amount]})](<{urls[amount]}>)\n"
										old += 1
									amount += 1

							if not versions == []:
								log = {}
								log["Build"] = z
								log ["Name"] = name
								log ["Version"] = versions
								log ["BuildIDs"] = ids
								old_log = {"Build": z}
								await collection.delete_one(old_log)
								await collection.insert_one(log)
								#try:
								#	await collection.update_one({"Build": z}, {"$set":{"Version": versions}})
								#except:
								#	await collection.insert_one(log)

				embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				embed.add_field(name=f"**Apple just started signing New iOS Versions for these devices:**", value=f"{add}", inline=False)
				for y in channels:
					try:
						channel = self.bot.get_channel(y)
						await channel.send(embed=embed)
						await asyncio.sleep(2)
					except:
						pass

				embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				embed.add_field(name=f"**Apple is No Longer signing iOS Versions for these devices:**", value=f"{remove}", inline=False)
				for y in channels:
					try:
						channel = self.bot.get_channel(y)
						await channel.send(embed=embed)
						await asyncio.sleep(2)
					except:
						pass
		except Exception as e:
			print(str(e))

	@check_iOS.before_loop
	async def before_check_iOS(self):
		await self.bot.wait_until_ready()

def setup(bot):
	bot.add_cog(iOS(bot))