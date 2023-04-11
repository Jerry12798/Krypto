import discord
import asyncio
import aiohttp
import time
import json
import pymongo
import motor.motor_asyncio
import random
import pytz
from pytz import timezone
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from Utils.Helpers import server_stats



class Tasks(commands.Cog, name="Tasks"):
	def __init__(self,bot):
		self.bot = bot
	async def cog_load(self):
		self.manage_sub_role.start()
		self.delete_ads.start()
		self.end_giveaways.start()
		self.end_alarms.start()
		self.end_mutes.start()
		self.change_bot_presence.start()
		self.check_iOS.start()
		self.check_pogo_events.start()
		self.AutoBump.start()
	async def cog_unload(self):
		self.manage_sub_role.cancel()
		self.delete_ads.cancel()
		self.end_giveaways.cancel()
		self.end_alarms.cancel()
		self.end_mutes.cancel()
		self.change_bot_presence.cancel()
		self.check_iOS.cancel()
		self.check_pogo_events.cancel()
		self.AutoBump.cancel()

	@tasks.loop()
	async def change_bot_presence(self):
		try:
			await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="DM's for Support Tickets"))
			await asyncio.sleep(15)
			await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming, name=f"to {len(self.bot.guilds)} Servers | {self.bot.prefix}help", url="https://twitch.tv/unknown"))
			await asyncio.sleep(15)
		except Exception as e:
			print(str(e))

	@change_bot_presence.before_loop
	async def before_change_bot_presence(self):
		await self.bot.wait_until_ready()

	@tasks.loop(hours=24)
	async def delete_ads(self):
		try:
			collection = self.bot.db["Mod_member_ads"]
			await collection.delete_many({})
			print("Advertisements has been Reset.")
		except Exception as e:
			print(str(e))

	@delete_ads.before_loop
	async def before_delete_ads(self):
		await self.bot.wait_until_ready()

	@tasks.loop()
	async def end_alarms(self):
		try:
			collection = self.bot.db["AM_alarms"]
			async for m in collection.find({}, {"_id": 0}):
				user = m["Member"]
				grab_guild = m["Guild"]
				grab_channel = m["Channel"]
				messagez = m["Message"]
				reminder = m["Reminder"]
				start = m["Begin"]
				end = m["End"]
				guild = self.bot.get_guild(grab_guild)
				channel = self.bot.get_channel(grab_channel)
				member = self.bot.get_user(user)
				old_log = {"Member": member.id, "Message": messagez}

				td = end - datetime.utcnow()
				if int(td.total_seconds()) < 0:
					embed = discord.Embed(title="__**Reminder**__", description=f"{reminder}", timestamp=start.astimezone(timezone("US/Eastern")), color=0xac5ece)
					embed.set_footer(text=f"{member}", icon_url=member.display_avatar.replace(format="png", static_format="png"))
					try:
						await member.send(embed=embed)
					except:
						pass
					try:
						await channel.send(embed=embed)
					except:
						pass
					await collection.delete_many(old_log)
					await asyncio.sleep(1)
		except Exception as e:
			print(str(e))

	@end_alarms.before_loop
	async def before_end_alarms(self):
		await self.bot.wait_until_ready()

	@tasks.loop()
	async def end_mutes(self):
		try:
			collection_2 = self.bot.db["logs"]
			collection = self.bot.db["AM_tmute"]
			mod_log = None
			async for m in collection.find({}, {"_id": 0}):
				user = m["Member"]
				sender = m["Author"]
				grab_guild = m["Guild"]
				async for z in collection_2.find({"Guild": grab_guild}, {"_id": 0, "Guild": 0}):
					Channelz = z["Channel"]
					mod_log = self.bot.get_channel(Channelz)
				grab_role = m["Role"]
				grab_channel  = m["Channel"]
				reason = m["Reason"]
				display = m["Display_Time"]
				start = m["Begin"]
				end = m["End"]
				start = start.astimezone(timezone("US/Eastern"))
				guild = self.bot.get_guild(grab_guild)
				role = guild.get_role(grab_role)
				channel = self.bot.get_channel(grab_channel)
				author = guild.get_member(sender)
				if author is None:
					author = self.bot.user
				member = guild.get_member(user)
				if member is None:
					await collection.delete_many({"Guild": grab_guild, "Member": user, "End": end})
					continue
				old_log = {"Guild": grab_guild, "Member": member.id, "End": end}

				td = end - datetime.utcnow()
				if int(td.total_seconds()) < 0:
					await member.remove_roles(role)
					embed = discord.Embed(title="__**Unmuted**__", timestamp=datetime.now(), color=0xff0000)
					embed.add_field(name=":satellite: Server:", value=f"**{guild}**", inline=False)
					embed.add_field(name=":alarm_clock: Started:", value=f"{display}", inline=False)
					embed.add_field(name=":newspaper: Reason:", value=f"Served Mute Duration.", inline=False)
					embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
					embed.set_footer(text=f"{author}", icon_url=author.display_avatar.replace(format="png", static_format="png"))
					try:
						await member.send(embed=embed)
					except:
						pass
					embed_2 = discord.Embed(title="__**Unmute**__", description=f"{member.mention} has been Unmuted.", timestamp=datetime.now(), color=0xff0000)
					embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
					embed_2.add_field(name=":alarm_clock: Started:", value=f"{display}", inline=False)
					embed_2.add_field(name=":newspaper: Reason:", value=f"**Served Mute Duration.**\n*{reason}*", inline=False)
					embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
					embed_2.set_footer(text=f"{author}", icon_url=author.display_avatar.replace(format="png", static_format="png"))
					await channel.send(embed=embed_2)
					if not mod_log is None:
						await mod_log.send(embed=embed_2)
					await collection.delete_many(old_log)
					await asyncio.sleep(1)
		except Exception as e:
			print(str(e))

	@end_mutes.before_loop
	async def before_end_mutes(self):
		await self.bot.wait_until_ready()

	@tasks.loop()
	async def end_giveaways(self):
		try:
			collection = self.bot.db["Fun_giveaways_entries"]
			collection_2 = self.bot.db["Fun_giveaways"]
			collection_3 = self.bot.db["Fun_ended_giveaways"]
			async for m in collection_2.find({}, {"_id": 0}):
				end = m["End"]
				start = m["Begin"]
				prize = m["Prize"]
				description = m["Description"]
				amount = m["Winners"]
				grab_channel = m["Channel"]
				messagez = m["Message"]
				channel = self.bot.get_channel(grab_channel)
				if channel is None:
					old_log = {"Guild": channel.guild.id, "Message": messagez}
					await collection.delete_many(old_log)
					await collection_2.delete_many(old_log)
				message = await channel.fetch_message(messagez)

				current = datetime.utcnow()
				td = end - current
				if int(td.total_seconds()) < 0:
					entries = []
					async for m in collection.find({}, {"_id": 0}):
						entries += {m["Member"]}
					if entries == []:
						old_log = {"Guild": channel.guild.id, "Message": messagez}
						await collection.delete_many(old_log)
						await collection_2.delete_many(old_log)
						embed = discord.Embed(title="__**Giveaway Ended**__", description=f"No Members Entered", timestamp=current, color=0xac5ece)
						embed.set_footer(text=f"{channel.guild.name}", icon_url=channel.guild.icon.replace(format="png", static_format="png"))
						await message.edit(embed=embed)
						await channel.send(f"No Members Entered!")
						return
					order = f"__***{prize}***__\n{description}\n__***Winners***__\n"
					counter = 1
					win_list = ""
					while counter <= amount:
						winners = random.choice(entries)
						member = channel.guild.get_member(winners)
						if counter + 1 >= amount:
							win_list += f"{member.mention}"
						if not counter + 1 >= amount:
							win_list += f"{member.mention}, "
						order += f"**{counter}:** {str(member.mention)}\n"
						counter +=1
					log = {}
					log ["Guild_Name"] = str(channel.guild)
					log ["Guild"] = channel.guild.id
					log ["Prize"] = prize
					log ["Description"] = description
					log ["Winners"] = amount
					log ["Channel"] = grab_channel
					log ["Members"] = entries
					log ["Message"] = messagez
					log ["End"] = end
					log ["Begin"] = start
					await collection_3.insert_one(log)
					old_log = {"Guild": channel.guild.id, "Message": messagez}
					await collection.delete_many(old_log)
					await collection_2.delete_many(old_log)
					embed = discord.Embed(title="__**Giveaway Ended**__", description=f"{order}", timestamp=current, color=0xac5ece)
					embed.set_footer(text=f"{channel.guild.name}", icon_url=channel.guild.icon.replace(format="png", static_format="png"))
					await message.edit(embed=embed)
					await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
				await asyncio.sleep(1)
		except Exception as e:
			print(str(e))

	@end_giveaways.before_loop
	async def before_end_giveaways(self):
		await self.bot.wait_until_ready()

	@tasks.loop(minutes=30)
	async def manage_sub_role(self):
		collection = self.bot.db["Config_server_subs"]
		collection_2 = self.bot.db["Config_sub_role"]
		collection_3 = self.bot.db["Config_server_endpoints"]
		try:
			for guild in self.bot.guilds:
				endpoint = None
				grab_endpoint = collection_3.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
				async for x in grab_endpoint:
					endpoint = x["Endpoint"]
				if not endpoint is None:
					for m in guild.members:
						endpoint_check = False
						async for u in collection.find({"guild": guild.id, "user": m.id}, {"_id": 0}):
							email = u['email']
							endpoint_check = True
						if endpoint_check is True:
							user_endpoint = endpoint.replace(f"%EMAIL", f"{email}")
							async with self.bot.session.get(f"{user_endpoint}") as url:
								data = await url.json()
								try:
									sub_type = data['data']['subscription_type']
								except:
									sub_type = None
								try:
									access = data['data']['subscription_active']
								except:
									access =  None
								if access is  None:
									try:
										access = data['data']['subscriber']
									except:
										access = False
							role_found = False
							async for r in collection_2.find({"Guild": guild.id, "Type": sub_type}, {"_id": 0}):
								sub_role = guild.get_role(r['Role'])
								role_found= True
							if role_found is True:
								if sub_role in m.roles:
									if access is False:
										print(f"Subscriber Role ({sub_type}) Removed from {m} in {guild}")
										await m.remove_roles(sub_role)
										await asyncio.sleep(3)
								if not sub_role in m.roles:
									if access is True:
										print(f"Subscriber Role ({sub_type}) Added to {m} in {guild}")
										await m.add_roles(sub_role)
										await asyncio.sleep(3)
			print("Successfully Added & Removed Subscriber Roles in All Servers")
		except Exception as e:
			print(str(e))

	@manage_sub_role.before_loop
	async def before_manage_sub_role(self):
		await self.bot.wait_until_ready()

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

							amount = 0 # Add New Versions into String
							for x in versions:
								if not x in old_versions:
									if "iPad".lower() in name.lower():
										check = add + f"***{name}*** *-* iPadOS {x}*({ids[amount]})*\n"
									if not "iPad".lower() in name.lower():
										check = add + f"***{name}*** *-* iOS {x}*({ids[amount]})*\n"
									if len(check) > 1024:
										embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.now(), color=0xac5ece)
										embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
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
									new += 1
								amount += 1

							amount = 0 # Add Old Versions into a String
							if not old_versions == []:
								for x in old_versions:
									if not x in versions:
										if "iPad".lower() in name.lower():
											check = remove + f"***{name}*** *-* iPadOS {x}*({old_ids[amount]})*\n"
										if not "iPad".lower() in name.lower():
											check = remove + f"***{name}*** *-* iOS {x}*({old_ids[amount]})*\n"
										if len(check) > 1024:
											embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.now(), color=0xac5ece)
											embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
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
										old += 1
									amount += 1

							if not versions == []: # Add Current Versions into Database
								log = {}
								log["Build"] = z
								log ["Name"] = name
								log ["Version"] = versions
								log ["BuildIDs"] = ids
								old_log = {"Build": z}
								await collection.delete_one(old_log)
								await collection.insert_one(log)

				if len(add) > 0: # Send Subscribed Channels New Updates
					embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.now(), color=0xac5ece)
					embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					embed.add_field(name=f"**Apple just started signing New iOS Versions for these devices:**", value=f"{add}", inline=False)
					for y in channels:
						try:
							channel = self.bot.get_channel(y)
							await channel.send(embed=embed)
							await asyncio.sleep(2)
						except:
							pass
					add = ""

				if len(remove) > 0: # Send Subscribed Channels Old Updates
					embed = discord.Embed(title="__**iOS Updates**__", timestamp=datetime.now(), color=0xac5ece)
					embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					embed.add_field(name=f"**Apple is No Longer signing iOS Versions for these devices:**", value=f"{remove}", inline=False)
					for y in channels:
						try:
							channel = self.bot.get_channel(y)
							await channel.send(embed=embed)
							await asyncio.sleep(2)
						except:
							pass
					remove = ""
		except Exception as e:
			print(str(e))

	@check_iOS.before_loop
	async def before_check_iOS(self):
		await self.bot.wait_until_ready()

	@tasks.loop(minutes=10)
	async def check_pogo_events(self):
		try:
			collection = self.bot.db["AM_pogo_updates"]
			collection_2 = self.bot.db["Config_pogo_channel"]

			channels = []
			async for x in collection_2.find({}):
				channels += {x["Channel"]}

			old_events = []
			old_events_desc = []
			async for x in collection.find({}):
				old_events += {x["Event"]}
				old_events_desc += {x["Details"]}

			current_events = []

			async with self.bot.session.get("https://raw.githubusercontent.com/ccev/pogoinfo/v2/active/events.json") as url:
				page = await url.read()
				data = json.loads(page)
				for x in data:
					name = x['name']
					typing = x['type']
					start = x['start']
					try:
						start = datetime.strptime(start, "%Y-%m-%d %H:%M")
						start = start.strftime("%B %d, %Y %H:%M")
					except:
						pass
					end = x['end']
					try:
						end = datetime.strptime(end, "%Y-%m-%d %H:%M")
						end = end.strftime("%B %d, %Y %H:%M")
					except:
						pass
					spawns = x['spawns']
					eggs = x['eggs']
					raids = x['raids']
					shinies = x['shinies']
					bonuses = x['bonuses']
					features = x['features']
					has_quests = x['has_quests']
					has_spawnpoints = x['has_spawnpoints']
					
					order = f"__**{name}**__\n`{start}` - `{end}`\n\n"

					if not spawns == []:
						mons = "**Pokemon Spawns**\n"
						for x in spawns:
							mon_id = x['id']
							mon_name = x['template']
							try:
								mon_form = x['form']
							except:
								pass
							mons += f"{mon_name} ({mon_id})\n"
						order += f"{mons}\n"

					if not eggs == []:
						egg_mons = "**Egg Spawns**\n"
						for x in eggs:
							mon_id = x['id']
							mon_name = x['template']
							try:
								mon_form = x['form']
							except:
								pass
							egg_mons += f"{mon_name} ({mon_id})\n"
						order += f"{egg_mons}\n"

					if not raids == []:
						event_raids = "**Raids**\n"
						for x in raids:
							mon_id = x['id']
							mon_name = x['template']
							try:
								mon_form = x['form']
							except:
								pass
							event_raids += f"{mon_name} ({mon_id})\n"
						order += f"{event_raids}\n"

					if not shinies == []:
						shiny_mons = "**Shinies**\n"
						for x in shinies:
							mon_id = x['id']
							mon_name = x['template']
							try:
								mon_form = x['form']
							except:
								pass
							shiny_mons += f"{mon_name} ({mon_id})\n"
						order += f"{shiny_mons}\n"

					if not bonuses == []:
						bonus = "**Bonuses**\n"
						counter = 1
						for x in bonuses:
							bonus_info = x['text']
							bonus += f"**{counter})** {bonus_info}"
							#try:
							#	bonus_type = x['template']
							#	bonus += f"\n{bonus_type}"
							#	try:
							#		bonus_amount = x['value']
							#		bonus += f" ({bonus_amount})"
							#	except:
							#		pass
							#except:
							#	pass
							bonus += f"\n"
							counter += 1
						order += f"{bonus}\n"

					if not features == []:
						event_features = "**Features**\n"
						for x in features:
							event_features += f"{x}\n"
						order += f"{event_features}\n"

					order += f"**Quests:** {has_quests}\n**Added Spawnpoints:** {has_spawnpoints}\n\n\n"
					current_events += {name}

					if not name in old_events:
						log = {}
						log["Event"] = name
						log["Details"] = order
						await collection.insert_one(log)
						
						embed = discord.Embed(title="__**PoGo Events**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
						embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
						for z in channels:
							try:
								channel = self.bot.get_channel(z)
								await channel.send(embed=embed)
								await asyncio.sleep(2)
							except:
								pass
			
			for z in old_events:
				if not z in current_events:
					old_log = {"Event": z}
					await collection.delete_one(old_log)
		except Exception as e:
			print(str(e))

	@check_pogo_events.before_loop
	async def before_check_pogo_events(self):
		await self.bot.wait_until_ready()

	@tasks.loop(hours=1)
	async def AutoBump(self):
		collection = self.bot.db["Bump_autobump"]
		async for x in collection.find({}, {"_id": 0}):
			try:
				guild = discord.utils.get(self.bot.guilds,id=int(x["Guild"]))
			except Exception as e:
				print(e)
				continue
			if guild is None:
				continue
			bot_count = 0
			for b in guild.members:
				if b.bot:
					bot_count += 1
			online, idle, offline, dnd = server_stats(guild)
			collection = self.bot.db["Bump_guild_channels"]
			collection_2 = self.bot.db["Bump_guild_banner"]
			collection_3 = self.bot.db["Bump_guild_description"]
			collection_4 = self.bot.db["Bump_guild_invite"]
			grab_channels = collection.find({}, {"_id": 0})
			bump_channels = []
			guilds = []
			async for x in grab_channels:
				bump_channels += {x["Channel"]}
				guilds += {x["Guild"]}
			server_banner = None
			server_description = None
			server_invite = None
			grab_banner = collection_2.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
			async for x in grab_banner:
				server_banner = x["Message"]
			grab_description = collection_3.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
			async for x in grab_description:
				server_description = x["Message"]
			grab_invite = collection_4.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
			async for x in grab_invite:
				server_invite = x["Message"]
			creation_date = guild.created_at
			az = creation_date.astimezone(timezone("US/Eastern"))
			correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
			create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
			if server_invite is None:
				print(f"Server {guild} has Not Setup an Invite to Bump.")
				return
			if server_description is None:
				print(f"Server {guild} has Not Setup a Description to Bump.")
				return
			embed = discord.Embed(description=f":crown: __**Owner:**__ {guild.owner}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.now(), color=0xac5ece)
			embed.set_author(name=f"{guild}", icon_url=str(guild.icon.replace(format="png", static_format="png")))
			embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
			embed.add_field(name=f":busts_in_silhouette: Members [{guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(guild.roles)}`\n__**Categories:**__ `{len(guild.categories)}`\n__**Channels:**__ `{len(guild.channels)}`\n__**Verification:**__ {guild.verification_level}\n__**Content Filter:**__ {guild.explicit_content_filter}", inline=False)
			if not len(guild.emojis) == 0:
				embed.add_field(name=f":100: Emotes [{len(guild.emojis)}]", value=" ".join(map(lambda o: str(o), guild.emojis[0:9])), inline=False)
			if not server_banner is None:
				embed.set_image(url=f"{server_banner}")		
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			for x in bump_channels:
				try:
					bump_feed = self.bot.get_channel(x)
					await bump_feed.send(embed=embed)		
				except:
					print(f"Server {x} has Altered their Bump Channel.")
			print(f"[Auto Bump] {guild.name} has been Bumped.")
			await asyncio.sleep(180)

	@AutoBump.before_loop
	async def before_AutoBump(self):
		await self.bot.wait_until_ready()

async def setup(bot):
	await bot.add_cog(Tasks(bot))