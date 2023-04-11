import discord
import time
import asyncio
import pymongo
import motor.motor_asyncio
import discord
from discord.ext import commands
from datetime import datetime
from Utils.GFX import make_welcome_card



class Events(commands.Cog, name="Events"):
	def __init__(self,bot):
		self.bot = bot

	@commands.Cog.listener() # AutoMod Events
	async def on_message(self, message):
		await self.bot.wait_until_ready()
		if message.author.bot:
			return
		mod_mail = self.bot.get_channel(self.bot.mod_mail)
		krypto_announcement = self.bot.get_channel(self.bot.news)
		if message.guild is None:
			if message.content == "":
				return
			embed_7 = discord.Embed(title=f"__**{self.bot.user.name} Support**__", timestamp=datetime.now(), color=0xac5ece)
			embed_7.add_field(name="Ticket:", value=f"{message.author.id}", inline=False)
			embed_7.add_field(name="Message:", value=f"{message.content}", inline=False)
			embed_7.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
			embed_7.set_footer(text=f"{message.author}", icon_url=message.author.display_avatar.replace(format="png", static_format="png"))
			await mod_mail.send(embed=embed_7)
			await mod_mail.send(f"{message.author.id}")
			embed = discord.Embed(title="__**Support Ticket**__", description=f"**Your Message was Received.**\n*Please Wait Patiently for a Support Agent to Reply to your Ticket.*", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			await message.author.send(embed=embed)
			return
		external_links = ["https", ".com", ".net", ".org", ".tv"]
		bad_words = ["fuck", "shit", "damn", "dick", "asshole", "pussy", "cunt", "faggot", "quier", "bullshit", "bitch" "rape", "ass", "skank", "slut", "hoe", "whore", "prick", "bastard", "nigger", "kracker"]

		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = message.guild.get_channel(Channelz)
		
		collection_2 = self.bot.db["AM_no_links"]
		grab_nl_channels = collection_2.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0})
		no_link_channels = []
		async for x in grab_nl_channels:
			no_link_channels += {x["Channel"]}

		collection_3 = self.bot.db["AM_no_invites"]
		grab_ni_channels = collection_3.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0})
		no_invite_channels = []
		async for x in grab_ni_channels:
			no_invite_channels += {x["Channel"]}

		collection_4 = self.bot.db["AM_no_bad_words"]
		grab_bw_channels = collection_4.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0})
		no_bad_words_channels = []
		async for x in grab_bw_channels:
			no_bad_words_channels += {x["Channel"]}

		collection_6 = self.bot.db["AM_spam_mentions"]
		grab_spam_mentions = collection_6.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0})
		spam_mentions = []
		async for x in grab_spam_mentions:
			spam_mentions += {x["Channel"]}

		collection_33 = self.bot.db["AM_spam"]
		grab_spam = collection_33.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0})
		spam = []
		async for x in grab_spam:
			spam += {x["Channel"]}

		collection_22 = self.bot.db["AM_spam_caps"]
		grab_spam_caps = collection_22.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0})
		spam_caps = []
		async for x in grab_spam_caps:
			spam_caps += {x["Channel"]}

		collection_46 = self.bot.db["Mod_info"]
		grab_stickies = collection_46.find({"Guild": message.guild.id}, {"_id": 0})
		sticky_channels = []
		async for m in grab_stickies:
			sticky_channels += {m["Channel"]}

		collection_5 = self.bot.db["Config_announcements"]
		grab_announcements = collection_5.find({}, {"_id": 0, "Guild": 0})
		get_krypto_announcements = []
		async for x in grab_announcements:
			get_krypto_announcements += {x["Channel"]}

		collection_44 = self.bot.db["AM_levels"]
		member_level = False
		try:
			async for z in collection_44.find({"Member": message.author.id}, {"_id": 0}):
				member_level = True
				lvl_start = z["Level"]
				exp = z["EXP"]
		except:
			pass
		
		collection_11 = self.bot.db["AM_guild_levels"]
		guild_member_level = False
		try:
			async for z in collection_11.find({"Guild": message.guild.id, "Member": message.author.id}, {"_id": 0}):
				guild_member_level = True
				guild_lvl_start = z["Level"]
				guild_exp = z["EXP"]
		except:
			pass

		collection_13 = self.bot.db["Config_level_prompt"]
		levels =  []
		async for m in collection_13.find({"Guild": message.guild.id}, {"_id": 0}):
			levels += {m["Guild"]}

		collection_42 = self.bot.db["Config_global_level_prompt"]
		glevels =  []
		async for m in collection_42.find({}, {"_id": 0}):
			glevels += {m["Member"]}

		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Please do not advertise here {message.author.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please do not post links here {message.author.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't use that kind of language here {message.author.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
		embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed_9 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't spam mention here {message.author.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_9.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
		embed_9.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed_21 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't use excessive caps here {message.author.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_21.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
		embed_21.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed_32 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't spam here {message.author.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_32.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
		embed_32.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))

		if guild_member_level is True: # Add EXP to Guild Rank
			guild_exp += 5
			guild_lvl_end = int(guild_exp ** (1/4))
			await collection_11.update_one({"Member": message.author.id, "Guild": message.guild.id}, {"$set":{"EXP": guild_exp, "Level": guild_lvl_end, "Member_Name": f"{message.author}"}})
			if guild_lvl_end > guild_lvl_start:
				if message.guild.id in levels:
					embed = discord.Embed(title="__**Level Up**__", description=f"You have Advanced to Level {guild_lvl_end}!", timestamp=datetime.now(), color=0xac5ece)
					embed.set_footer(text=f"{message.author}", icon_url=message.author.display_avatar.replace(format="png", static_format="png"))
					await message.channel.send(embed=embed)

		if member_level is True: # Add EXP to Global Rank
			exp += 5
			lvl_end = int(exp ** (1/4))
			await collection_44.update_one({"Member": message.author.id}, {"$set":{"EXP": exp, "Level": lvl_end, "Member_Name": f"{message.author}"}})
			if lvl_end > lvl_start:
				if message.author.id in glevels:
					embed = discord.Embed(title="__**Level Up**__", description=f"You have Advanced to Level {lvl_end}!", timestamp=datetime.now(), color=0xac5ece)
					embed.set_footer(text=f"{message.author}", icon_url=message.author.display_avatar.replace(format="png", static_format="png"))
					try:
						await message.author.send(embed=embed)
					except:
						pass
		
		exp = 0
		lvl = 1
		member_stats = {}
		member_stats ["Member"] = message.author.id
		member_stats ["Member_Name"] = f"{message.author}"
		member_stats ["EXP"] = exp
		member_stats ["Level"] = lvl
		if member_level is False: # Add Member to Global System
			current_member = message.author
			if current_member.bot is False:
				await collection_44.insert_one(member_stats)

		if guild_member_level is False: # Add Member to Guild  System
			current_member = message.author
			if current_member.bot is False:
				member_stats ["Guild_Name"] = message.guild.name
				member_stats ["Guild"] = message.guild.id
				await collection_11.insert_one(member_stats)

		if message.channel is krypto_announcement: # Cross Server Announcements
			if message.content == "":
				return
			for x in get_krypto_announcements:
				try:
					announcements = self.bot.get_channel(x)
					await announcements.send(f"{message.content}")
				except:
					print(f"{x} has been Altered or Deleted.")

		if message.channel.id in no_invite_channels: # Invite Links Moderation
			if "discord.gg" in message.content.lower():
				if message.author.id != self.bot.user.id:
					embed_4 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.now(), color=0xff0000)
					embed_4.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_4.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_4.add_field(name="__**:newspaper: Reason:**__", value=f"Posted a Link", inline=False)
					embed_4.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_4.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_4.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
					embed_4.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					await message.channel.send(embed=embed)
					if not mod_log is None:
						await mod_log.send(embed=embed_4)
					await message.delete()

		if message.channel.id in no_link_channels: # External Links Moderation
			if message.author.id != self.bot.user.id:
				for x in external_links:
					if x in message.content.lower():
						embed_5 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.now(), color=0xff0000)
						embed_5.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
						embed_5.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
						embed_5.add_field(name="__**:newspaper: Reason:**__", value=f"Posted an Invite", inline=False)
						embed_5.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
						embed_5.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
						embed_5.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
						embed_5.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
						await message.channel.send(embed=embed_2)
						if not mod_log is None:
							await mod_log.send(embed=embed_5)
						await message.delete()

		if message.channel.id in no_bad_words_channels: # Bad Word Moderation
			for x in bad_words:
				if x in message.content.lower():
					embed_6 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.now(), color=0xff0000)
					embed_6.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_6.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_6.add_field(name="__**:newspaper: Reason:**__", value=f"Said a Bad Word", inline=False)
					embed_6.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_6.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_6.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
					embed_6.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					await message.channel.send(embed=embed_3)
					if not mod_log is None:
						await mod_log.send(embed=embed_6)
					await message.delete()

		if message.channel.id in spam_mentions: # Spam Mention Moderation
			if len(message.mentions) >= 3:
				embed_8 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.now(), color=0xff0000)
				embed_8.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
				embed_8.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
				embed_8.add_field(name="__**:newspaper: Reason:**__", value=f"Spam Mentioned", inline=False)
				embed_8.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
				embed_8.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
				embed_8.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
				embed_8.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
				await message.channel.send(embed=embed_9)
				if not mod_log is None:
					await mod_log.send(embed=embed_8)
				await message.delete()

		if message.channel.id in spam: # Spam Moderation
			counter = 0
			async for x in message.channel.history(limit=100):
				if x.author.id == message.author.id:
					if message.content.lower() in x.content.lower():
						counter += 1
			if counter >= 3:
				if not message.author.id == self.bot.user.id:
					embed_31 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.now(), color=0xff0000)
					embed_31.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_31.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_31.add_field(name="__**:newspaper: Reason:**__", value=f"Spam Text", inline=False)
					embed_31.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_31.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_31.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
					embed_31.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					await message.channel.send(embed=embed_32)
					if not mod_log is None:
						await mod_log.send(embed=embed_31)
					await message.delete()

		if message.channel.id in spam_caps: # Spam Caps Moderation
			try:
				if int((sum(1 for x in message.content if str.isupper(x))/len(message.content))*100) >= 70:
					embed_22 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.now(), color=0xff0000)
					embed_22.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_22.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_22.add_field(name="__**:newspaper: Reason:**__", value=f"Excessive Caps", inline=False)
					embed_22.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_22.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_22.set_thumbnail(url=message.author.display_avatar.replace(format="png", static_format="png"))
					embed_22.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					await message.channel.send(embed=embed_21)
					if not mod_log is None:
						await mod_log.send(embed=embed_22)
					await message.delete()
			except ZeroDivisionError:
				pass

		if message.channel.id in sticky_channels:
			msg = ":white_check_mark: No Viruses, Malware, Spyware, or Malicious Links Allowed\n"
			msg += ":white_check_mark: Once you **LEAVE** this Server. All your Advertisements will be Auto-Deleted\n"
			msg += ":white_check_mark: You can post `4` Advertisements every **24** hours\n"
			msg += ":white_check_mark: Your Advertisement **MUST** contain a Description\n"
			collection = self.bot.db["ad"]
			collection_4 = self.bot.db["Mod_member_ads"]
			collection_5 = self.bot.db["Config_ad_roles"]
			
			posted_ads = []
			limit_roles = []
			limit = []

			async for x in collection_5.find({"Guild": message.guild.id}, {"_id": 0}).sort("Limit", pymongo.ASCENDING):
				limit_roles += {x["Role"]}
				limit += {x["Limit"]}
			async for z in collection_4.find({"Guild": message.guild.id}, {"_id": 0}):
				posted_ads += {z["Member"]}
			async for m in collection_3.find({"Guild": message.guild.id, "Channel": message.channel.id}, {"_id": 0}):
				msg = m["Message"]
			async for m in collection.find({"Channel": message.channel.id}, {"_id": 0}):
				ad_message = m["Message"]

			if not message.author.bot:
				if len(message.content) < 150:
					embed = discord.Embed(title="__**Error**__", description=f"{message.author.mention} you must Include a Good Description.", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
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
							embed = discord.Embed(title="__**Error**__", description=f"{message.author.mention} you have Reached your Daily Limit of {Ad_Limit} Posts.", timestamp=datetime.now(), color=0xff0000)
							embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
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

				embed = discord.Embed(title="__**Channel Information**__", description=f"{msg}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
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
	
	@commands.Cog.listener() # Auto-Role & Welcome and Private Message Upon Join
	async def on_member_join(self, member):
		await self.bot.wait_until_ready()
		collection = self.bot.db["AM_welcome_channel"]
		collection_2 = self.bot.db["AM_welcome"]
		collection_3 = self.bot.db["AM_welcome_dm"]
		collection_4 = self.bot.db["AM_autorole"]
		welcome = None
		role = None
		server_dm = None
		server_message = ""
		grab_dm = collection_3.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0})
		grab_message = collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0})
		grab_memberz = collection.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0})
		async for m in collection_4.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		async for x in grab_memberz:
			welcomez = x["Channel"]
			get_welcome = member.guild.get_channel(welcomez)
			welcome = get_welcome.guild
		async for x in grab_message:
			server_message = x["Message"]
			new = server_message.replace(f"%member", f"{member}")
			new = new.replace(f"%mention", f"{member.mention}")
			new = new.replace(f"%server", f"{member.guild}")
		async for x in grab_dm:
			server_dm = x["Message"]
			new_dm = server_dm.replace(f"%member", f"{member}")
			new_dm = new_dm.replace(f"%mention", f"{member.mention}")
			new_dm = new_dm.replace(f"%server", f"{member.guild}")
		if member.guild is welcome:
			card = await make_welcome_card(member=member, position=len(member.guild.members))
			embed = discord.Embed(title=f"__**Welcome**__", description=f"{new}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed.set_image(url=f"attachment://{card.filename}")
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			await get_welcome.send(embed=embed, file=card)
		if not server_dm is None:
			embed_2 = discord.Embed(title="Server Info:", description=f"{new_dm}", timestamp=datetime.now(), color=0xac5ece)
			embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			try:
				await member.send(embed=embed_2)
			except:
				pass
		if not role is None:
			await member.add_roles(role)
	
	@commands.Cog.listener() # Goodbye Message Upon Leave
	async def on_member_remove(self, member):
		await self.bot.wait_until_ready()
		if self.bot.user.id == member.id:
			return
		collection = self.bot.db["AM_welcome_channel"]
		collection_2 = self.bot.db["AM_goodbye"]
		welcome = None
		grab_message = collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0})
		grab_memberz = collection.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_memberz:
			welcomez = x["Channel"]
			get_welcome = member.guild.get_channel(welcomez)
			welcome = get_welcome.guild
		async for x in grab_message:
			server_message = x["Message"]
			new = server_message.replace(f"%member", f"{member}")
			new = new.replace(f"%mention", f"{member.mention}")
			new = new.replace(f"%server", f"{member.guild}")
		if member.guild is welcome:
			embed = discord.Embed(title=f"__**Goodbye**__", description=f"{new}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			await get_welcome.send(embed=embed)

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
		embed = discord.Embed(title="__**Member Left**__", description=f"{member.mention}\n*{member}* had {num_ads} Ads Deleted.", timestamp=datetime.now(), color=0xff0000)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		if not mod_log is None:
			await mod_log.send(embed=embed)

	@commands.Cog.listener() # Rolemenu Event (Add Role on Reaction)
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		reaction = payload.emoji
		guild = self.bot.get_guild(int(payload.guild_id))
		member = guild.get_member(int(payload.user_id))
		embed = discord.Embed(title="__**Role Assigned**__", description=f"You have a new role in **{guild}**", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		
		collection = self.bot.db["Mod_rolemenu"]
		grab_menu = {"Message": payload.message_id}
		message = 0
		roles = None
		async for x in collection.find(grab_menu):
			message = x["Message"]
			roles = x["Roles"]
		if message == payload.message_id:
			if roles is None:
				return
			counter = 0
			for x in reactions:
				if str(payload.emoji) == x:
					rolez = guild.get_role(roles[counter])
					await member.add_roles(rolez)
					try:
						await member.send(embed=embed)
					except:
						pass
					counter +=1

		collection = self.bot.db["Fun_giveaways"]
		collection_2 = self.bot.db["Fun_giveaways_entries"]
		gmessage = 0
		async for x in collection.find(grab_menu):
			gmessage = x["Message"]
		gcheck = True
		async for m in collection_2.find(grab_menu):
			current = m["Member"]
			if current == payload.user_id:
				gcheck = False
		if payload.message_id == gmessage:
			if payload.user_id != self.bot.user.id:
				if str(payload.emoji) == "\U0001F389":
					if gcheck == True:
						log = {}
						log ["Guild"] = payload.guild_id
						log ["Message"] = payload.message_id
						log ["Member"] = payload.user_id
						collection_2.insert_one(log)

		collection = self.bot.db["Ticket_watchers"]
		collection_2 = self.bot.db["Ticket_roles"]
		collection_3 = self.bot.db["Ticket_category"]
		tmessage = 0
		async for t in collection.find(grab_menu):
			tmessage = t["Message"]
			tchannel = t["Channel"]
		rolez = []
		overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False), member: discord.PermissionOverwrite(read_messages=True, send_messages=True)}
		async for r in collection_2.find({"Guild": guild.id}):
			rolez += {r["Role"]}
		if len(rolez) == 0:
			support = guild.owner.mention
		if len(rolez) == 1:
			role = guild.get_role(rolez[0])
			support = role.mention
		if len(rolez) > 1:
			rcount = 1
			support = ""
			for o in rolez:
				role = guild.get_role(o)
				overwrites [role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
				if rcount < len(rolez):
					support += f"{role.mention}, "
				if rcount == len(rolez):
					support += f"or {role.mention}"
				rcount += 1
		tcat = None
		async for c in collection_3.find({"Guild": guild.id}):
			cat = c["Category"]
			tcat = self.bot.get_channel(cat)
		if payload.message_id == tmessage:
			if payload.user_id != self.bot.user.id:
				if str(payload.emoji) == "\U0001f4e9":
					ticket = await guild.create_text_channel(name=member.name, category=tcat, overwrites=overwrites)
					embed = discord.Embed(title="__**Support Ticket**__", description=f"Support will be with you shortly.\nTo close this ticket react with :lock:", timestamp=datetime.now(), color=0xac5ece)
					embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
					closer = await ticket.send(f"Welcome {member.mention}! {support} will be with you soon!!", embed=embed)
					await closer.add_reaction("\U0001f512")

					log = {}
					log ["Guild_Name"] = guild.name
					log ["Guild"] = guild.id
					log ["Channel"] = ticket.id
					log ["Message"] = closer.id
					await collection.insert_one(log)

					channel = self.bot.get_channel(tchannel)
					messagez = await channel.fetch_message(payload.message_id)
					for r in messagez.reactions:
						if r.emoji == "\U0001f4e9":
							reaction = r
					try:
						await reaction.remove(member)
					except:
						pass

				if str(payload.emoji) == "\U0001f512":
					ticket = self.bot.get_channel(tchannel)
					messagez = await ticket.fetch_message(tmessage)
					for r in messagez.reactions:
						if r.emoji == "\U0001f512":
							reaction = r
					try:
						await reaction.remove(member)
					except:
						pass
					closer = await ticket.send(f"Are you sure you would like to close this ticket? {member.mention}")
					await closer.add_reaction("\U00002705")
					await closer.add_reaction("\U0000274c")
					def check(r, u):
						return u == member and str(r.emoji) == "\U00002705"
					try:
						react, usr = await self.bot.wait_for('reaction_add', timeout=30, check=check)
					except asyncio.TimeoutError:
						await closer.delete()
					else:
						await closer.delete()
						await ticket.send("Ticket will be deleted in 15 seconds!")
						await asyncio.sleep(15)
						await ticket.delete()
						log = {"Message": payload.message_id}
						collection.delete_one(log)

	@commands.Cog.listener() # Rolemenu Event (Remove Role on Reaction)
	async def on_raw_reaction_remove(self, payload):
		await self.bot.wait_until_ready()
		reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		guild = self.bot.get_guild(int(payload.guild_id))
		member = guild.get_member(int(payload.user_id))
		embed = discord.Embed(title="__**Role Unassigned**__", description=f"You have lost role in **{guild}**", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		
		collection = self.bot.db["Mod_rolemenu"]
		grab_menu = {"Message": payload.message_id}
		message = 0
		roles = None
		async for x in collection.find(grab_menu):
			message = x["Message"]
			roles = x["Roles"]
		if message == payload.message_id:
			if roles is None:
				return
			counter = 0
			for x in reactions:
				if str(payload.emoji) == x:
					rolez = guild.get_role(roles[counter])
					await member.remove_roles(rolez)
					try:
						await member.send(embed=embed)
					except:
						pass
					counter += 1

		collection = self.bot.db["Fun_giveaways"]
		collection_2 = self.bot.db["Fun_giveaways_entries"]
		gmessage = 0
		async for x in collection.find(grab_menu):
			gmessage = x["Message"]
		gcheck = True
		async for m in collection_2.find(grab_menu):
			current = m["Member"]
			if current == payload.user_id:
				gcheck = False
		if payload.message_id == gmessage:
			if payload.user_id != self.bot.user.id:
				if str(payload.emoji) == "\U0001F389":
					if gcheck == False:
						log = {"Guild": payload.guild_id, "Message": payload.message_id, "Member": payload.user_id}
						collection_2.delete_one(log)

async def setup(bot):
	await bot.add_cog(Events(bot))