import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime



class AutoMod(commands.Cog, name="AutoMod", description="Auto-Moderation Configuration & Toggle Commands"):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command() # Set No Link Channels
	@commands.has_permissions(administrator=True)
	async def links(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle External Link Auto-Moderation in.\n`{self.bot.prefix}links <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_no_links"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"External Link Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Links are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Link Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Links are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@links.error
	async def links_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Excessive Caps Channels
	@commands.has_permissions(administrator=True)
	async def caps(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Excessive Caps Auto-Moderation in.\n`{self.bot.prefix}caps <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_spam_caps"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@caps.error
	async def caps_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Invite Channels
	@commands.has_permissions(administrator=True)
	async def invites(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Server Invite Auto-Moderation in.\n`{self.bot.prefix}invites <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_no_invites"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invite Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invites are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invite Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invites are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@invites.error
	async def invites_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Bad Word Channels
	@commands.has_permissions(administrator=True)
	async def bwords(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Bad Word Auto-Moderation in.\n`{self.bot.prefix}bwords <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_no_bad_words"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Word Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Words are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Word Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Words are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@bwords.error
	async def bwords_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Spam Mention Channels
	@commands.has_permissions(administrator=True)
	async def mentions(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Spam Mention Auto-Moderation in.\n`{self.bot.prefix}mentions <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_spam_mentions"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mention Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mentions are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mention Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mentions are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@mentions.error
	async def mentions_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Spam Channels
	@commands.has_permissions(administrator=True)
	async def spam(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Spam Auto-Moderation in.\n`{self.bot.prefix}mentions <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_spam"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@spam.error
	async def spam_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Role for Auto-Role
	@commands.has_permissions(administrator=True)
	async def autorole(self, ctx, *, content: discord.Role=None):
		if content is None:
			embed = discord.Embed(title="__**Auto-Role Error**__", description=f"Mention a Role to Auto-Assign.\n`{self.bot.prefix}autorole <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_autorole"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = content.id
		embed = discord.Embed(title="__**Auto-Role**__", description=f"Auto-Role role has been set as {content.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Auto-Role**__", description=f"Auto-Role upon join has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@autorole.error
	async def autorole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Welcome DM Message
	@commands.has_permissions(administrator=True)
	async def dmessage(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Welcome & Goodbye Error**__", description=f"Create Welcome DM Message.\n(Mention Member: %mention, Member Username: %member, Server Name: %server)\n`{self.bot.prefix}dmessage <Create DM Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_welcome_dm"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Direct Message has been set as\n{content}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		async for x in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Direct Messages upon join has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@dmessage.error
	async def dmessage_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Welcome Message
	@commands.has_permissions(administrator=True)
	async def wmessage(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Welcome & Goodbye Error**__", description=f"Create Welcome Message.\n(Mention Member: %mention, Member Username: %member, Server Name: %server)\n`{self.bot.prefix}wmessage <Create Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_welcome"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Message has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		async for x in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Messages on Join have been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@wmessage.error
	async def wmessage_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Goodbye Message
	@commands.has_permissions(administrator=True)
	async def gmessage(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Welocme & Goodbye Error**__", description=f"Create Goodbye Message.\n(Mention Member: %mention, Member Username: %member, Server Name: %server)\n`{self.bot.prefix}gmessage <Create Goodbye Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_goodbye"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Goodbye Message has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		async for x in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Goodbye Message on Leave has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@gmessage.error
	async def gmessage_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	#sticky = commands.Group(name="sticky", description="Sticky Configuration & Management Commands")

	@commands.command() # Set Sticky Channel & Message
	@commands.has_permissions(administrator=True)
	async def sticky(self, ctx, channel: discord.TextChannel=None, *, content: str=None):
		if channel is None:
			embed = discord.Embed(title="__**Information**__", description=f"Mention Channel & Create Sticky Message to Display.\n`{self.bot.prefix}info <Mention Channel> <Create Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**Information**__", description=f"Create Sticky Message to Display.\n`{self.bot.prefix}info <Mention Channel> <Create Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Mod_info"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Channel"] = channel.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Information**__", description=f"Message has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Information**__", description=f"Sticky Information has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Information**__", description=f"Sticky Information will be shown in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_5 = discord.Embed(title="__**Information**__", description=f"Sticky Information has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_5.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_6 = discord.Embed(title="__**Information**__", description=f"Sticky Information will not be shown in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_6.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		#embed_2 = discord.Embed(title="__**Advertisement Information**__", description=f"Advertisement Information Message has been Deleted.", timestamp=datetime.now(), color=0xff0000)
		#embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if channel.id in channelz:
			old_log = {"Guild": ctx.message.guild.id, "Channel": channel.id}
			await collection.delete_one(old_log)
			await channel.send(embed=embed_6)
			await ctx.send(embed=embed_5)
			await ctx.message.delete()
			return
	@sticky.error
	async def sticky_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Sticky Role Limit
	@commands.has_permissions(administrator=True)
	async def set(self, ctx, ads: int=None, *, role: discord.Role=None):
		if ads is None:
			embed = discord.Embed(title="__**Ad Limit Error**__", description=f"Specify Amount of Ads for a Role's Daily Limit.\n`{self.bot.prefix}set <Ad Limit> <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if role is None:
			embed = discord.Embed(title="__**Ad Limit Error**__", description=f"Mention a Role to set it's Daily Limit.\n`{self.bot.prefix}set <Ad Limit> <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_ad_roles"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = role.id
		log ["Limit"] = ads
		embed = discord.Embed(title="__**Ad Limit**__", description=f"Sticky Advertisement Role Limit has been set as {ads} for {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		rolez = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			rolez += {x["Role"]}
		if role.id not in rolez:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Ad Limit**__", description=f"Sticky Advertisement Role has been Disabled for {role.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if role.id in rolez:
			old_log = {"Guild": ctx.message.guild.id, "Role": role.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@set.error
	async def set_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Sticky Log Command
	@commands.has_permissions(kick_members=True)
	async def ilog(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Logging Error**__", description=f"Mention Channel to Receive Sticky Channel Logs in.\n`{self.bot.prefix}ilog <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
		collection = self.bot.db["ad_logs"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will no longer be Received in {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Remove Member Sticky Limit
	@commands.has_permissions(kick_members=True)
	async def mremove(self, ctx, amount: int=None, *, memberz: discord.Member):
		collection = self.bot.db["Mod_member_ads"]
		ads = None
		if amount is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"Specify Amount to Remove from Sticky Advertisement Limit.\n`{self.bot.prefix}mreset <Amount of Ads> <Mention Member>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if memberz is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"Mention a Member to Clear their Sticky Advertisement Limit for this 24 hours.\n`{self.bot.prefix}mreset <Amount of Ads> <Mention Member>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		async for x in collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0, "Guild": 0}):
			ads = x["Ads"]
		if ads is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"{memberz.mention} doesn't have any Advertisements.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Guild": ctx.guild.id, "Member": memberz.id}, {"$set":{"Ads": ads-amount}})
		embed = discord.Embed(title="__**Removed Successfully**__", description=f"{memberz.mention} had {amount} of Advertisements Removed from Daily Limit.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@mremove.error
	async def mremove_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Member Sticky Limit
	@commands.has_permissions(kick_members=True)
	async def mreset(self, ctx, *, memberz: discord.Member):
		collection = self.bot.db["Mod_member_ads"]
		old_log = {"Guild": ctx.guild.id, "Member": memberz.id}
		await collection.delete_one(old_log)
		if memberz is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"Mention a Member to Clear their Sticky Advertisement Limit for this 24 hours.\n`{self.bot.prefix}mreset <Mention Member>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cleared Successfully**__", description=f"{memberz.mention}'s Sticky Advertisement Limit has been Cleared.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@mreset.error
	async def mreset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Member Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Sticky Server Limit
	@commands.has_permissions(kick_members=True)
	async def reset(self, ctx):
		collection = self.bot.db["Mod_member_ads"]
		await collection.delete_many({"Guild": ctx.guild.id})
		embed = discord.Embed(title="__**Cleared Successfully**__", description=f"{ctx.guild}'s Sticky Advertisement Limit has been Cleared.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@reset.error
	async def reset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Sticky Advertisement Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(AutoMod(bot))