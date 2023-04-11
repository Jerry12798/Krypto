import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime



class Configuration(commands.Cog, name="Configuration", description="Configuration & Setup Commands"):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command() # Set Server Prefixes
	@commands.has_permissions(administrator=True)
	async def prefix(self, ctx, Prefix: str=None):
		if Prefix is None:
			embed = discord.Embed(title="__**Prefix Error**__", description=f"You must Specify a Prefix.\n`{self.bot.prefix}prefix <Create Prefix>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_prefixes"]
		prefix = []
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			prefix += m["Prefix"]
		if Prefix in prefix:
			prefixes = []
			for m in prefix:
				if m is Prefix:
					continue
				prefixes += m
			old_log = {"Guild": ctx.guild.id}
			await collection.delete_one(old_log)
			if len(prefixes) == 0:
				prefixes = [f"{self.bot.prefix}"]
			log = {}
			log ["Guild_Name"] = ctx.guild.name
			log ["Guild"] = ctx.guild.id
			log ["Prefix"] = prefixes
			await collection.insert_one(log)
			embed = discord.Embed(title="__**Prefix Removed**__", description=f"You have Removed {Prefix} from {ctx.guild}'s Prefixes.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		prefixes = [Prefix]
		for m in prefix:
			prefixes += m
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Prefix"] = prefixes
		old_log = {"Guild": ctx.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Prefix Added**__", description=f"You have Added {Prefix} to {ctx.guild}'s Prefixes.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
	@prefix.error
	async def prefix_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Log Command
	@commands.has_permissions(administrator=True)
	async def log(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Logging Error**__", description=f"Mention Channel to Receive Logs in.\n`{self.bot.prefix}log <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["logs"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Logging**__", description=f"Mod Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed_2 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will no longer be Received in {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@log.error
	async def log_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Join & Leave Channel
	@commands.has_permissions(administrator=True)
	async def welcome(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Welcome & Goodbye Error**__", description=f"Mention Channel to Receive Your Join & Leave Logs.\n`{self.bot.prefix}welcome <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_welcome_channel"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will no longer be sent to {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@welcome.error
	async def welcome_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			
	@commands.command() # Set Role for Muted
	@commands.has_permissions(administrator=True)
	async def muted(self, ctx, *, role: discord.Role=None):
		if role is None:
			embed = discord.Embed(title="__**Mute Role Error**__", description=f"Mention a Role to set as Muted Role.\n`{self.bot.prefix}muted <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_mute_role"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = role.id
		embed = discord.Embed(title="__**Mute Role**__", description=f"Muted Role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Mute Role**__", description=f"Muted Role has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@muted.error
	async def muted_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Announcement Channels
	@commands.has_permissions(administrator=True)
	async def updates(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Announcements Error**__", description=f"Mention Channel to Receive {self.bot.user.name}'s Announcements in.\n`{self.bot.prefix}updates <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_announcements"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will now be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Announcements**__", description=f"**{ctx.guild}** will no longer receive {self.bot.user.name}'s Announcements.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		channelz = []
		async for x in collection.find({}, {"_id": 0, "Guild": 0}):
			channelz += {x["Channel"]}
		if channel.id not in channelz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await channel.send(embed=embed_3)
			await ctx.message.delete()
			return
		if channel.id in channelz:
			old_log = {"Channel": channel.id}
			await collection.delete_one(old_log)
			await channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@updates.error
	async def updates_errors(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Level Messages Command
	@commands.has_permissions(administrator=True)
	async def levels(self, ctx):
		collection = self.bot.db["Config_level_prompt"]
		grab_servers = collection.find({}, {"_id": 0})
		serverz = []
		async for m in grab_servers:
			serverz += {m["Guild"]}
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id

		if not ctx.guild.id in serverz:
			embed = discord.Embed(title="__**Level Messages**__", description=f"Level Up Messages has been **Enabled** in **{ctx.guild.name}**.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if ctx.guild.id in serverz:
			embed_2 = discord.Embed(title="__**Level Messages**__", description=f"Level Up Messages has been **Disabled** in **{ctx.guild.name}**.", timestamp=datetime.now(), color=0xac5ece)
			embed_2.set_thumbnail(url=ctx.guild.icon.replace(format="png", static_format="png"))
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			old_log = {"Guild": ctx.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@levels.error
	async def levels_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Global Level Messages Command
	async def glevels(self, ctx):
		collection = self.bot.db["Config_global_level_prompt"]
		grab_servers = collection.find({}, {"_id": 0})
		serverz = []
		async for m in grab_servers:
			serverz += {m["Member"]}
		log = {}
		log ["Member_Name"] = ctx.author.name
		log ["Member"] = ctx.author.id

		if not ctx.author.id in serverz:
			embed = discord.Embed(title="__**Level Messages**__", description=f"You have **Enabled** Global Level Messages for **{self.bot.user.mention}**.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			try:
				await ctx.author.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Level Message Error**__", description=f"Please Enable DM's to Receive Global Level Messages from {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
				await ctx.send(embed=embed)
				return
			await collection.insert_one(log)
			await ctx.message.delete()
			return
		if ctx.author.id in serverz:
			embed_2 = discord.Embed(title="__**Level Messages**__", description=f"You have **Disabled** Global Level Messages for **{self.bot.user.mention}**.", timestamp=datetime.now(), color=0xac5ece)
			embed_2.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			old_log = {"Member": ctx.author.id}
			try:
				await ctx.author.send(embed=embed_2)
			except:
				await ctx.send(embed=embed_2)
			await collection.delete_one(old_log)
			await ctx.message.delete()
			return

	@commands.command() # Set Phone Call Channel
	@commands.has_permissions(administrator=True)
	async def psetup(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Phone Setup Error**__", description=f"Mention Channel to Receive Phone Calls in.\n`{self.bot.prefix}psetup <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
		collection = self.bot.db["Config_phone"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Phone Setup**__", description=f"Phone Calls will be directed to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Phone Setup**__", description=f"This channel will now receive Phone Calls.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed_2 = discord.Embed(title="__**Phone Setup**__", description=f"Phone Calls will no longer be Received in {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Phone Setup**__", description=f"This Channel will no longer Receive Phone Calls.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@psetup.error
	async def psetup_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	#server_sub = commands.Group(name="server_subscription", description="Server Subscription Configuration & Setup Commands")

	@commands.command() # Admin Link Server Account Command
	@commands.has_permissions(administrator=True)
	async def alink(self, ctx, user:discord.Member=None, *, email:str=None):
		if user is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"You must Specify the Member to Link Subscription Account to.\n`{self.bot.prefix}link <member> <email>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if email is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"You must include the email address your linking to your Discord account.\n`{self.bot.prefix}link <member> <email>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		endpoint = None
		collection = self.bot.db["Config_server_endpoints"]
		grab_endpoint = collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_endpoint:
			endpoint = x["Endpoint"]
		if endpoint is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"{ctx.guild.name} must first setup the Server's Subscriber Endpoint..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
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
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		member = None
		email_check = None
		collection = self.bot.db["Config_server_subs"]
		collection_2 = self.bot.db["logs"]
		async for m in collection.find({"guild": ctx.guild.id, "user": user.id}, {"_id": 0}):
			member = m["user"]
		async for m in collection.find({"guild": ctx.guild.id, "email": email}, {"_id": 0}):
			email_check = m["email"]
		if not member is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"{user.mention}'s Discord account is already linked to a {ctx.guild.name} account", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if not email_check is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"*{email}* is already linked to a Discord  account", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		mod_log = None
		async for m in collection_2.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channel = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channel)
		log = {}
		log ["guild"] = ctx.guild.id
		log ["user"] = user.id
		log ["email"] = email
		log ["access"] = access
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Account Linked**__", description=f"*You have successfully linked* `{email}` *to {user.mention}'s Discord account*\n{order}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		confirmation = await ctx.send(embed=embed)
		embed = discord.Embed(title="__**Account Linked**__", description=f"**User**: {user.mention}\n**Email**: *{email}*\n{order}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if mod_log is None:
			await ctx.message.delete()
			return	
		await mod_log.send(embed=embed)
		await ctx.message.delete()
		await asyncio.sleep(5)
		await confirmation.delete()
	@alink.error
	async def alink_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Unlink Member's Server Account Command
	@commands.has_permissions(administrator=True)
	async def unlink(self, ctx, *, member:discord.Member=None):
		if member is None:
			embed = discord.Embed(title="__**Unlink Error**__", description=f"You must specify the Member your unlinking the {ctx.guild.name} account for.\n`{self.bot.prefix}unlink <member>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		endpoint = None
		collection = self.bot.db["Config_server_endpoints"]
		grab_endpoint = collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_endpoint:
			endpoint = x["Endpoint"]
		if endpoint is None:
			embed = discord.Embed(title="__**Unlink Error**__", description=f"{ctx.guild.name} must first setup the Server's Subscriber Endpoint..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_server_subs"]
		collection_2 = self.bot.db["logs"]
		check = False
		async for m in collection.find({"guild": ctx.guild.id, "user": member.id}, {"_id": 0}):
			email = m["email"]
			access = m["access"]
			check = True
		if check is False:
			embed = discord.Embed(title="__**Unlink Error**__", description=f"No Account Found for {member.mention}..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		mod_log = None
		async for m in collection_2.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channel = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channel)
		old_log = {"guild": ctx.guild.id, "user": member.id}
		await collection.delete_one(old_log)
		embed = discord.Embed(title="__**Account Unlinked**__", description=f"*You have successfully unlinked* `{email}` *from {member.mention}'s Discord account*\n**Access**: *{access}*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		embed = discord.Embed(title="__**Account Unlinked**__", description=f"**User**: {member.mention}\n**Email**: *{email}*\n**Access**: *{access}*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if mod_log is None:
			await ctx.message.delete()
			return	
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@unlink.error
	async def unlink_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to configure {self.bot.user.mention} in this server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Server Subscription Endpoint
	@commands.has_permissions(administrator=True)
	async def endpoint(self, ctx, *, endpoint_url: str=None):
		if endpoint_url is None:
			embed = discord.Embed(title="__**Endpoint Error**__", description=f"Attach Subscription Endpoint URL.\n`{self.bot.prefix}endpoint <Endpoint URL>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_server_endpoints"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Endpoint"] = endpoint_url
		embed = discord.Embed(title="__**Endpoint Setup**__", description=f"Server Subscription Endpoint has been set as\n{endpoint_url}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Endpoint Setup**__", description=f"Server Subscription Endpoint has been changed to\n{endpoint_url}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@endpoint.error
	async def endpoint_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Role for Subscribers
	@commands.has_permissions(administrator=True)
	async def srole(self, ctx, role: discord.Role=None, *, sub_type:str=None):
		if role is None:
			embed = discord.Embed(title="__**Subscriber Role Error**__", description=f"Mention a role to set as {sub_type} role.\n`{self.bot.prefix}srole <Subscription Type> <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_sub_role"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = role.id
		log ["Type"] = sub_type
		if not sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"{sub_type} role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		if sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"Subscriber role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guilds = []
		async for x in collection.find({"Type": sub_type}, {"_id": 0, "Channel": 0}):
			guilds += {x["Guild"]}
		if ctx.message.guild.id not in guilds:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"Subscriber role has been disabled.", timestamp=datetime.now(), color=0xff0000)
		if not sub_type is None:
			embed = discord.Embed(title="__**Subscriber Role**__", description=f"{sub_type} role has been disabled.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guilds:
			old_log = {"Guild": ctx.message.guild.id, "Type": sub_type}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
	@srole.error
	async def srole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to configure {self.bot.user.mention} in this server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Configuration(bot))