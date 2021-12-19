import discord
import asyncio
import aiohttp
import time
import json
import pymongo
import motor.motor_asyncio
import random
from discord.ext import commands, tasks
from datetime import datetime



class Tasks(commands.Cog, name="Tasks"):
	def __init__(self,bot):
		self.bot = bot
		self.delete_ads.start()
		self.end_giveaways.start()
		self.end_alarms.start()
		self.end_mutes.start()
		self.change_bot_presence.start()
	def cog_unload(self):
		self.delete_ads.cancel()
		self.end_giveaways.cancel()
		self.end_alarms.cancel()
		self.end_mutes.cancel()
		self.change_bot_presence.cancel()

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
					embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
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
					mod_log = self.get_channel(Channelz)
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
					embed = discord.Embed(title="__**Unmuted**__", timestamp=datetime.utcnow(), color=0xff0000)
					embed.add_field(name=":satellite: Server:", value=f"**{guild}**", inline=False)
					embed.add_field(name=":alarm_clock: Started:", value=f"{display}", inline=False)
					embed.add_field(name=":newspaper: Reason:", value=f"Served Mute Duration.", inline=False)
					embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
					embed.set_footer(text=f"{author}", icon_url=author.avatar_url_as(format=None, static_format="png"))
					try:
						await member.send(embed=embed)
					except:
						pass
					embed_2 = discord.Embed(title="__**Unmute**__", description=f"{member.mention} has been Unmuted.", timestamp=datetime.utcnow(), color=0xff0000)
					embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
					embed_2.add_field(name=":alarm_clock: Started:", value=f"{display}", inline=False)
					embed_2.add_field(name=":newspaper: Reason:", value=f"**Served Mute Duration.**\n*{reason}*", inline=False)
					embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
					embed_2.set_footer(text=f"{author}", icon_url=author.avatar_url_as(format=None, static_format="png"))
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
				channel = self.get_channel(grab_channel)
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
					embed.set_footer(text=f"{channel.guild.name}", icon_url=channel.guild.icon_url_as(format=None, static_format="png"))
					await message.edit(embed=embed)
					await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
				await asyncio.sleep(1)
		except Exception as e:
			print(str(e))

	@end_giveaways.before_loop
	async def before_end_giveaways(self):
		await self.bot.wait_until_ready()

def setup(bot):
	bot.add_cog(Tasks(bot))