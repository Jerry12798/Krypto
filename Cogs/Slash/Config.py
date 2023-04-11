import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime



class Config(commands.Cog, app_commands.Group, name="config", description="Configuration & Setup Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot
		
	@app_commands.command(name="prefix", description="Adds Prefix or Removes if Already Added") # Set Server Prefixes
	@app_commands.describe(prefix="Prefix to Add/Remove")
	@app_commands.checks.has_permissions(administrator=True)
	async def prefix(self, interaction:discord.Interaction, prefix:str):
		collection = self.bot.db["Config_prefixes"]
		prefixes = []
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			prefixes += m["Prefix"]
		if prefix in prefixes:
			prefixes = []
			for m in prefixes:
				if m is prefix:
					continue
				prefixes += m
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			if len(prefixes) == 0:
				prefixes = [f"{self.bot.prefix}"]
			log = {}
			log ["Guild_Name"] = interaction.guild.name
			log ["Guild"] = interaction.guild.id
			log ["Prefix"] = prefixes
			await collection.insert_one(log)
			embed = discord.Embed(title="__**Prefix Removed**__", description=f"You have Removed {prefix} from {interaction.guild}'s Prefixes.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		new_prefixes = [prefix]
		for m in prefixes:
			new_prefixes += m
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Prefix"] = new_prefixes
		old_log = {"Guild": interaction.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Prefix Added**__", description=f"You have Added {prefix} to {interaction.guild}'s Prefixes.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
	@prefix.error
	async def prefix_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	log = app_commands.Group(name="log", description="Logging Configuration Commands")

	@log.command(name="mod", description="Set Channel to Receive Moderation Logs in") # Set Log Command
	@app_commands.describe(channel="Channel to Receive Logs in")
	@app_commands.checks.has_permissions(administrator=True)
	async def mod(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["logs"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Logging**__", description=f"Mod Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			await channel.send(embed=embed_3)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_channel = x["Channel"]
			old_channel = interaction.guild.get_channel(grab_old_channel)
		embed_2 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will no longer be Received in {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@mod.error
	async def mod_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@log.command(name="join", description="Set Join/Leave Log Channel") # Set Join & Leave Channel
	@app_commands.describe(channel="Channel to Receive Logs in")
	@app_commands.checks.has_permissions(administrator=True)
	async def join(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_welcome_channel"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			await channel.send(embed=embed_3)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_channel = x["Channel"]
			old_channel = interaction.guild.get_channel(grab_old_channel)
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will no longer be sent to {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@join.error
	async def join_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			
	@app_commands.command(name="mute_role", description="Set Role for Muted Members") # Set Role for Muted
	@app_commands.describe(role="Role for Mute")
	@app_commands.checks.has_permissions(administrator=True)
	async def mute_role(self, interaction:discord.Interaction, *, role:discord.Role):
		collection = self.bot.db["Config_mute_role"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Role"] = role.id
		embed = discord.Embed(title="__**Mute Role**__", description=f"Muted Role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Mute Role**__", description=f"Muted Role has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@mute_role.error
	async def mute_role_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="news", description="Set Channel to Receive Changelogs and News in") # Set Announcement Channels
	@app_commands.describe(channel="Channel to Receive Logs in")
	@app_commands.checks.has_permissions(administrator=True)
	async def news(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["Config_announcements"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will now be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Announcements**__", description=f"**{interaction.guild}** will no longer receive {self.bot.user.name}'s Announcements.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		channelz = []
		async for x in collection.find({}, {"_id": 0, "Guild": 0}):
			channelz += {x["Channel"]}
		if channel.id not in channelz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			await channel.send(embed=embed_3)
			#await ctx.message.delete()
			return
		if channel.id in channelz:
			old_log = {"Channel": channel.id}
			await collection.delete_one(old_log)
			await channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@news.error
	async def news_errors(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="levels", description="Toggle Server Level Messages") # Level Messages Command
	@app_commands.checks.has_permissions(administrator=True)
	async def levels(self, interaction:discord.Interaction):
		collection = self.bot.db["Config_level_prompt"]
		grab_servers = collection.find({}, {"_id": 0})
		serverz = []
		async for m in grab_servers:
			serverz += {m["Guild"]}
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id

		if not interaction.guild.id in serverz:
			embed = discord.Embed(title="__**Level Messages**__", description=f"Level Up Messages has been **Enabled** in **{interaction.guild.name}**.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if interaction.guild.id in serverz:
			embed_2 = discord.Embed(title="__**Level Messages**__", description=f"Level Up Messages has been **Disabled** in **{interaction.guild.name}**.", timestamp=datetime.now(), color=0xac5ece)
			embed_2.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@levels.error
	async def levels_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="levels_global", description="Toggle Global Level Messages") # Global Level Messages Command
	async def levels_global(self, interaction:discord.Interaction):
		collection = self.bot.db["Config_global_level_prompt"]
		grab_servers = collection.find({}, {"_id": 0})
		serverz = []
		async for m in grab_servers:
			serverz += {m["Member"]}
		log = {}
		log ["Member_Name"] = interaction.user.name
		log ["Member"] = interaction.user.id

		if not interaction.user.id in serverz:
			embed = discord.Embed(title="__**Level Messages**__", description=f"You have **Enabled** Global Level Messages for **{self.bot.user.mention}**.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			try:
				await interaction.user.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Level Message Error**__", description=f"Please Enable DM's to Receive Global Level Messages from {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			await collection.insert_one(log)
			#await ctx.message.delete()
			return
		if interaction.user.id in serverz:
			embed_2 = discord.Embed(title="__**Level Messages**__", description=f"You have **Disabled** Global Level Messages for **{self.bot.user.mention}**.", timestamp=datetime.now(), color=0xac5ece)
			embed_2.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			old_log = {"Member": interaction.user.id}
			try:
				await interaction.user.send(embed=embed_2)
			except:
				await interaction.followup.send(embed=embed_2)
			await collection.delete_one(old_log)
			#await ctx.message.delete()
			return

	@app_commands.command(name="phone_line", description="Set Channel to Receive Phone Calls in") # Set Phone Call Channel
	@app_commands.describe(channel="Channel to Receive Calls in")
	@app_commands.checks.has_permissions(administrator=True)
	async def phone_line(self, interaction:discord.Interaction, *, channel:discord.TextChannel):
		collection = self.bot.db["Config_phone"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Phone Setup**__", description=f"Phone Calls will be directed to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Phone Setup**__", description=f"This channel will now receive Phone Calls.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			await channel.send(embed=embed_3)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_channel = x["Channel"]
			old_channel = interaction.guild.get_channel(grab_old_channel)
		embed_2 = discord.Embed(title="__**Phone Setup**__", description=f"Phone Calls will no longer be Received in {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Phone Setup**__", description=f"This Channel will no longer Receive Phone Calls.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@phone_line.error
	async def phone_line_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	server_sub = app_commands.Group(name="server_subscription", description="Server Subscription Configuration & Setup Commands")

	@server_sub.command(name="link", description="Links Specified Member's Server Subscription Account to their Discord Account") # Admin Link Server Account Command
	@app_commands.describe(user="Member to Link Server Subscription to", email="Server Subscription Email Address to Link")
	@app_commands.checks.has_permissions(administrator=True)
	async def link(self, interaction:discord.Interaction, user:discord.Member, *, email:str):
		endpoint = None
		collection = self.bot.db["Config_server_endpoints"]
		grab_endpoint = collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_endpoint:
			endpoint = x["Endpoint"]
		if endpoint is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"{interaction.guild.name} must first setup the Server's Subscriber Endpoint..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		endpoint = endpoint.replace(f"%EMAIL", f"{email}")
		check = False
		async with self.bot.session.get(f"{endpoint}") as url:
			data = await url.json()
			access = None
			sub_type = None
			order = ""
			try:
				sub_type = data['data']['subscription_type']
				order += f"**Type**: *{sub_type}*\n"
			except:
				pass
			try:
				access = data['data']['subscription_active']
				order += f"**Status**: *{access}*\n"
				check = True
			except:
				pass
			if access is None:
				try:
					access = data['data']['subscriber']
					order += f"**Status**: *{access}*\n"
					check = True
				except:
					pass
		if check is False:
			embed = discord.Embed(title="__**Link Error**__", description=f"No Account Found..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		member = None
		email_check = None
		collection = self.bot.db["Config_server_subs"]
		collection_2 = self.bot.db["logs"]
		async for m in collection.find({"guild": interaction.guild.id, "user": user.id}, {"_id": 0}):
			member = m["user"]
		async for m in collection.find({"guild": interaction.guild.id, "email": email}, {"_id": 0}):
			email_check = m["email"]
		if not member is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"{user.mention}'s Discord account is already linked to a {interaction.guild.name} account", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if not email_check is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"*{email}* is already linked to a Discord  account", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		mod_log = None
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channel = m["Channel"]
			mod_log = interaction.guild.get_channel(Channel)
		log = {}
		log ["guild"] = interaction.guild.id
		log ["user"] = user.id
		log ["email"] = email
		log ["access"] = access
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Account Linked**__", description=f"*You have successfully linked* `{email}` *to {user.mention}'s Discord account*\n{order}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		confirmation = await interaction.followup.send(embed=embed)
		embed = discord.Embed(title="__**Account Linked**__", description=f"**User**: {user.mention}\n**Email**: *{email}*\n{order}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if mod_log is None:
			#await ctx.message.delete()
			return	
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
		await asyncio.sleep(5)
		await confirmation.delete()
	@link.error
	async def link_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@server_sub.command(name="unlink", description="Unlinks Specified Member's Server Subscription Account from their Discord Account") # Unlink Member's Server Account Command
	@app_commands.describe(member="Member to Unlink Server Subscription of")
	@app_commands.checks.has_permissions(administrator=True)
	async def unlink(self, interaction:discord.Interaction, *, member:discord.Member):
		endpoint = None
		collection = self.bot.db["Config_server_endpoints"]
		grab_endpoint = collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_endpoint:
			endpoint = x["Endpoint"]
		if endpoint is None:
			embed = discord.Embed(title="__**Unlink Error**__", description=f"{interaction.guild.name} must first setup the Server's Subscriber Endpoint..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Config_server_subs"]
		collection_2 = self.bot.db["logs"]
		check = False
		async for m in collection.find({"guild": interaction.guild.id, "user": member.id}, {"_id": 0}):
			email = m["email"]
			access = m["access"]
			check = True
		if check is False:
			embed = discord.Embed(title="__**Unlink Error**__", description=f"No Account Found for {member.mention}..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		mod_log = None
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channel = m["Channel"]
			mod_log = interaction.guild.get_channel(Channel)
		old_log = {"guild": interaction.guild.id, "user": member.id}
		await collection.delete_one(old_log)
		embed = discord.Embed(title="__**Account Unlinked**__", description=f"*You have successfully unlinked* `{email}` *from {member.mention}'s Discord account*\n**Access**: *{access}*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		embed = discord.Embed(title="__**Account Unlinked**__", description=f"**User**: {member.mention}\n**Email**: *{email}*\n**Access**: *{access}*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if mod_log is None:
			#await ctx.message.delete()
			return	
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@unlink.error
	async def unlink_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to configure {self.bot.user.mention} in this server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@server_sub.command(name="endpoint", description="Sets Server's Subscriber Endpoint Use %EMAIL to Specify Where to Insert Subscriber Emails") # Set Server Subscription Endpoint
	@app_commands.describe(endpoint="URL for Server's Subscriber Check Endpoint")
	@app_commands.checks.has_permissions(administrator=True)
	async def endpoint(self, interaction:discord.Interaction, *, endpoint: str):
		collection = self.bot.db["Config_server_endpoints"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Endpoint"] = endpoint
		embed = discord.Embed(title="__**Endpoint Setup**__", description=f"Server Subscription Endpoint has been set as\n{endpoint}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Endpoint Setup**__", description=f"Server Subscription Endpoint has been changed to\n{endpoint}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@endpoint.error
	async def endpoint_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@server_sub.command(name="role", description="Sets Subscriber Role") # Set Role for Subscribers
	@app_commands.describe(role="Role for Subscribers", sub_type="Subscription Type to Assign Role to")
	@app_commands.checks.has_permissions(administrator=True)
	async def role(self, interaction:discord.Interaction, role:discord.Role, *, sub_type:str=None):
		collection = self.bot.db["Config_sub_role"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Role"] = role.id
		log ["Type"] = sub_type
		if not sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"{sub_type} role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		if sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"Subscriber role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guilds = []
		async for x in collection.find({"Type": sub_type}, {"_id": 0, "Channel": 0}):
			guilds += {x["Guild"]}
		if interaction.guild.id not in guilds:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"Subscriber role has been disabled.", timestamp=datetime.now(), color=0xff0000)
		if not sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"{sub_type} role has been disabled.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guilds:
			old_log = {"Guild": interaction.guild.id, "Type": sub_type}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
	@role.error
	async def role_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to configure {self.bot.user.mention} in this server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Config(bot))