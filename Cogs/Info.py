import discord
import asyncio
import time
import motor.motor_asyncio
import pymongo
from discord.ext import commands
from datetime import datetime



class Info(commands.Cog, name="Info"):
	def __init__(self,bot):
		self.bot = bot
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)

	@commands.command() # Set Log Command
	@commands.has_permissions(kick_members=True)
	async def ilog(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Logging Error**__", description=f"Mention Channel to Receive Information Channel Logs in.\n`{self.bot.prefix}ilog <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
		collection = self.bot.db["ad_logs"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Logging**__", description=f"Information Channel Logs will be sent to {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Logging**__", description=f"Information Channel Logs will now be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**Logging**__", description=f"Information Channel Logs will no longer be Received in {old_channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Logging**__", description=f"Information Channel Logs will no longer be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@ilog.error
	async def ilog_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Server Limit
	@commands.has_permissions(kick_members=True)
	async def reset(self, ctx):
		collection = self.bot.db["Mod_member_ads"]
		await collection.delete_many({"Guild": ctx.guild.id})
		embed = discord.Embed(title="__**Cleared Successfully**__", description=f"{ctx.guild}'s Advertisement Limit has been Cleared.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@reset.error
	async def reset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Member Limit
	@commands.has_permissions(kick_members=True)
	async def mreset(self, ctx, *, memberz: discord.Member):
		collection = self.bot.db["Mod_member_ads"]
		old_log = {"Guild": ctx.guild.id, "Member": memberz.id}
		await collection.delete_one(old_log)
		if memberz is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"Mention a Member to Clear their Ad Limit for this 24 hours.\n`{self.bot.prefix}mreset <Mention Member>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cleared Successfully**__", description=f"{memberz.mention}'s Advertisement Limit has been Cleared.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@mreset.error
	async def mreset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Member Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Remove Member Limit
	@commands.has_permissions(kick_members=True)
	async def mremove(self, ctx, amount: int=None, *, memberz: discord.Member):
		collection = self.bot.db["Mod_member_ads"]
		ads = None
		if amount is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"Specify Amount to Remove from Advertisement Limit.\n`{self.bot.prefix}mreset <Amount of Ads> <Mention Member>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if memberz is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"Mention a Member to Clear their Advertisement Limit for this 24 hours.\n`{self.bot.prefix}mreset <Amount of Ads> <Mention Member>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for x in collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0, "Guild": 0}):
			ads = x["Ads"]
		if ads is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"{memberz.mention} doesn't have any Advertisements.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Guild": ctx.guild.id, "Member": memberz.id}, {"$set":{"Ads": ads-amount}})
		embed = discord.Embed(title="__**Removed Successfully**__", description=f"{memberz.mention} had {amount} of Advertisements Removed from Daily Limit.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@mremove.error
	async def mremove_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Information Channel & Message
	@commands.has_permissions(administrator=True)
	async def info(self, ctx, channel: discord.TextChannel=None, *, content: str=None):
		if channel is None:
			embed = discord.Embed(title="__**Information**__", description=f"Mention Channel & Create Informative Message to Display.\n`{self.bot.prefix}info <Mention Channel> <Create Message>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**Information**__", description=f"Create Informative Message to Display.\n`{self.bot.prefix}info <Mention Channel> <Create Message>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Mod_info"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Channel"] = channel.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Information**__", description=f"Message has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Information**__", description=f"Channel Information has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Information**__", description=f"Channel Information will be shown in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_5 = discord.Embed(title="__**Information**__", description=f"Channel Information has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_5.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_6 = discord.Embed(title="__**Information**__", description=f"Channel Information will not be shown in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_6.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		channelz = []
		async for x in collection.find({}, {"_id": 0, "Guild": 0}):
			channelz += {x["Channel"]}
		if channel.id not in channelz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await channel.send(embed=embed_4)
			await ctx.send(embed=embed_3)
			await ctx.message.delete()
			return
		async for x in collection.find({"Guild": ctx.message.guild.id, "Channel": channel.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		#embed_2 = discord.Embed(title="__**Advertisement Information**__", description=f"Advertisement Information Message has been Deleted.", timestamp=datetime.utcnow(), color=0xff0000)
		#embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if channel.id in channelz:
			old_log = {"Guild": ctx.message.guild.id, "Channel": channel.id}
			await collection.delete_one(old_log)
			await channel.send(embed=embed_6)
			await ctx.send(embed=embed_5)
			await ctx.message.delete()
			return
	@info.error
	async def info_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Role Limit
	@commands.has_permissions(administrator=True)
	async def set(self, ctx, ads: int=None, *, role: discord.Role=None):
		if ads is None:
			embed = discord.Embed(title="__**Ad Limit Error**__", description=f"Specify Amount of Ads for a Role's Daily Limit.\n`{self.bot.prefix}set <Ad Limit> <Mention Role>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if role is None:
			embed = discord.Embed(title="__**Ad Limit Error**__", description=f"Mention a Role to set it's Daily Limit.\n`{self.bot.prefix}set <Ad Limit> <Mention Role>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_ad_roles"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = role.id
		log ["Limit"] = ads
		embed = discord.Embed(title="__**Ad Limit**__", description=f"Advertisement Role Limit has been set as {ads} for {role.mention}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		rolez = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			rolez += {x["Role"]}
		if role.id not in rolez:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Ad Limit**__", description=f"Advertisement Role has been Disabled for {role.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if role.id in rolez:
			old_log = {"Guild": ctx.message.guild.id, "Role": role.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@set.error
	async def set_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



	@commands.Cog.listener() # Posts Channel Information Messages
	async def on_message(self, message):
		await self.bot.wait_until_ready()
		if message.author.id == self.bot.user.id:
			return
		msg = ":white_check_mark: No Viruses, Malware, Spyware, or Malicious Links Allowed\n"
		msg += ":white_check_mark: Once you **LEAVE** this Server. All your Advertisements will be Auto-Deleted\n"
		msg += ":white_check_mark: You can post `4` Advertisements every **24** hours\n"
		msg += ":white_check_mark: Your Advertisement **MUST** contain a Description\n"
		collection = self.bot.db["ad"]
		collection_3 = self.bot.db["Mod_info"]
		collection_4 = self.bot.db["Mod_member_ads"]
		collection_5 = self.bot.db["Config_ad_roles"]
		channelz = []
		posted_ads = []
		limit_roles = []
		limit = []

		async for x in collection_5.find({"Guild": message.guild.id}, {"_id": 0}).sort("Limit", pymongo.ASCENDING):
			limit_roles += {x["Role"]}
			limit += {x["Limit"]}
		async for z in collection_4.find({"Guild": message.guild.id}, {"_id": 0}):
			posted_ads += {z["Member"]}
		async for m in collection_3.find({"Guild": message.guild.id}, {"_id": 0}):
			channelz += {m["Channel"]}
		async for m in collection_3.find({"Guild": message.guild.id, "Channel": message.channel.id}, {"_id": 0}):
			msg = m["Message"]
		async for m in collection.find({"Channel": message.channel.id}, {"_id": 0}):
				ad_message = m["Message"]

		if message.channel.id in channelz:
			if not message.author.bot:
				if len(message.content) < 150:
					embed = discord.Embed(title="__**Error**__", description=f"{message.author.mention} you must Include a Good Description.", timestamp=datetime.utcnow(), color=0xff0000)
					embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
					await message.channel.send(embed=embed)
					await message.delete()

				#if "discord.gg" in message.content.lower() and len(message.content) > 150:
				if len(message.content) > 150:
					if message.author.id in posted_ads:
						Ad_Limit = 4
						counter = 0
						for x in limit_roles:
							ad_role = message.guild.get_role(x)
							counter += 1
							if ad_role in message.author.roles:
								Ad_Limit = limit[counter-1]

						async for m in collection_4.find({"Guild": message.guild.id, "Member": message.author.id}, {"_id": 0}):
							ads = m["Ads"]
						ads += 1
						if ads > Ad_Limit:
							ads -= 1
							embed = discord.Embed(title="__**Error**__", description=f"{message.author.mention} you have Reached your Daily Limit of {Ad_Limit} Posts.", timestamp=datetime.utcnow(), color=0xff0000)
							embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
							await message.channel.send(embed=embed)
							await message.delete()
						await collection_4.update_one({"Guild": message.guild.id, "Member": message.author.id}, {"$set":{"Ads": ads}})
					if message.author.id not in posted_ads:
						current_member = message.author
						if current_member.bot is False:
							member_ads = {}
							member_ads ["Guild_Name"] = message.guild.name
							member_ads ["Guild"] = message.guild.id
							member_ads ["Member"] = message.author.id
							member_ads ["Ads"] = 1
							await collection_4.insert_one(member_ads)


				embed = discord.Embed(title="__**Channel Information**__", description=f"{msg}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				try:
					info = await message.channel.fetch_message(ad_message)
					await info.delete()
				except:
					info = None
				new = await message.channel.send(embed=embed)
				log = {}
				log ["Channel"] = message.channel.id
				log ["Message"] = new.id
				old_log = {"Channel": message.channel.id}
				await collection.delete_one(old_log)
				await collection.insert_one(log)

	@commands.Cog.listener() # Delete Upon Leave
	async def on_member_remove(self, member):
		await self.bot.wait_until_ready()
		if self.bot.user.id == member.id:
			return
		num_ads = 0
		collection = self.bot.db["Mod_info"]
		collection_2 = self.bot.db["ad_logs"]
		async for m in collection.find({"Guild": member.guild.id}, {"_id": 0}):
			channelz = m["Channel"]
			ad_channelz = member.guild.get_channel(channelz)
			deleted = await ad_channelz.purge(check=lambda m: m.author == member)
			num_ads += len(deleted)
		mod_log = None
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0}):
			Channelz = m["Channel"]
			mod_log = member.guild.get_channel(Channelz)
		embed = discord.Embed(title="__**Member Left**__", description=f"{member.mention}\n*{member}* had {num_ads} Ads Deleted.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		if not mod_log is None:
			await mod_log.send(embed=embed)

def setup(bot):
	bot.add_cog(Info(bot))