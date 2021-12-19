import discord
import time
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime



class Config(commands.Cog, name="Config"):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command() # Set Server Prefixes
	@commands.has_permissions(administrator=True)
	async def prefix(self, ctx, Prefix: str=None):
		if Prefix is None:
			embed = discord.Embed(title="__**Prefix Error**__", description=f"You must Specify a Prefix.\n`{self.bot.prefix}prefix <Create Prefix>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
			embed = discord.Embed(title="__**Prefix Removed**__", description=f"You have Removed {Prefix} from {ctx.guild}'s Prefixes.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed = discord.Embed(title="__**Prefix Added**__", description=f"You have Added {Prefix} to {ctx.guild}'s Prefixes.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
	@prefix.error
	async def prefix_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			
	@commands.command() # Set Role for Muted
	@commands.has_permissions(administrator=True)
	async def muted(self, ctx, *, role: discord.Role=None):
		if role is None:
			embed = discord.Embed(title="__**Mute Role Error**__", description=f"Mention a Role to set as Muted Role.\n`{self.bot.prefix}muted <Mention Role>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_mute_role"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = role.id
		embed = discord.Embed(title="__**Mute Role**__", description=f"Muted Role has been set as {role.mention}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Mute Role**__", description=f"Muted Role has been Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@muted.error
	async def muted_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Join & Leave Channel
	@commands.has_permissions(administrator=True)
	async def welcome(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Welcome & Goodbye Error**__", description=f"Mention Channel to Receive Your Join & Leave Logs.\n`{self.bot.prefix}welcome <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_welcome_channel"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will be sent to {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will now be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will no longer be sent to {old_channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Join & Leave Logs will no longer be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Announcement Channels
	@commands.has_permissions(administrator=True)
	async def updates(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Announcements Error**__", description=f"Mention Channel to Receive {self.bot.user.name}'s Announcements in.\n`{self.bot.prefix}updates <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_announcements"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will now be sent to {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Announcements**__", description=f"**{ctx.guild}** will no longer receive {self.bot.user.name}'s Announcements.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Announcements**__", description=f"{self.bot.user.name}'s Announcements will no longer be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Log Command
	@commands.has_permissions(administrator=True)
	async def log(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Logging Error**__", description=f"Mention Channel to Receive Logs in.\n`{self.bot.prefix}log <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["logs"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Logging**__", description=f"Mod Logs will be sent to {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will now be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will no longer be Received in {old_channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Logging**__", description=f"Mod Logs will no longer be sent to this channel.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
			embed = discord.Embed(title="__**Level Messages**__", description=f"Level Up Messages has been **Enabled** in **{ctx.guild.name}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if ctx.guild.id in serverz:
			embed_2 = discord.Embed(title="__**Level Messages**__", description=f"Level Up Messages has been **Disabled** in **{ctx.guild.name}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_2.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			old_log = {"Guild": ctx.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@levels.error
	async def levels_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
			embed = discord.Embed(title="__**Level Messages**__", description=f"You have **Enabled** Global Level Messages for **{self.bot.user.mention}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			try:
				await ctx.author.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Level Message Error**__", description=f"Please Enable DM's to Receive Global Level Messages from {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			await collection.insert_one(log)
			await ctx.message.delete()
			return
		if ctx.author.id in serverz:
			embed_2 = discord.Embed(title="__**Level Messages**__", description=f"You have **Disabled** Global Level Messages for **{self.bot.user.mention}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_2.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			old_log = {"Member": ctx.author.id}
			try:
				await ctx.author.send(embed=embed_2)
			except:
				await ctx.send(embed=embed_2)
			await collection.delete_one(old_log)
			await ctx.message.delete()
			return

def setup(bot):
	bot.add_cog(Config(bot))