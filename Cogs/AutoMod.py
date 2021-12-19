import discord
import time
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime
from Utils.GFX import make_welcome_card



class AutoMod(commands.Cog, name="AutoMod"):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command() # Set No Link Channels
	@commands.has_permissions(administrator=True)
	async def links(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle External Link Auto-Moderation in.\n`{self.bot.prefix}links <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_no_links"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"External Link Moderation has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Links are not allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Link Moderation has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Links are allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
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
	@links.error
	async def links_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Excessive Caps Channels
	@commands.has_permissions(administrator=True)
	async def caps(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Excessive Caps Auto-Moderation in.\n`{self.bot.prefix}caps <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_spam_caps"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps Moderation has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps are not allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps Moderation has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps are allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
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
	@caps.error
	async def caps_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Invite Channels
	@commands.has_permissions(administrator=True)
	async def invites(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Server Invite Auto-Moderation in.\n`{self.bot.prefix}invites <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_no_invites"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invite Moderation has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invites are not allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invite Moderation has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invites are allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
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
	@invites.error
	async def invites_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Bad Word Channels
	@commands.has_permissions(administrator=True)
	async def bwords(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Bad Word Auto-Moderation in.\n`{self.bot.prefix}bwords <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_no_bad_words"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Word Moderation has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Words are not allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Word Moderation has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Words are allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
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
	@bwords.error
	async def bwords_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Spam Mention Channels
	@commands.has_permissions(administrator=True)
	async def mentions(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Spam Mention Auto-Moderation in.\n`{self.bot.prefix}mentions <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_spam_mentions"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mention Moderation has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mentions are not allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mention Moderation has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mentions are allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
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
	@mentions.error
	async def mentions_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set No Spam Channels
	@commands.has_permissions(administrator=True)
	async def spam(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Auto-Moderation Error**__", description=f"Mention Channel to Toggle Spam Auto-Moderation in.\n`{self.bot.prefix}mentions <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_spam"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Moderation has been activated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam are not allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Moderation has been deactivated for {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam are allowed in this channel now.", timestamp=datetime.utcnow(), color=0xff0000)
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
	@spam.error
	async def spam_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Role for Auto-Role
	@commands.has_permissions(administrator=True)
	async def autorole(self, ctx, *, content: discord.Role=None):
		if content is None:
			embed = discord.Embed(title="__**Auto-Role Error**__", description=f"Mention a Role to Auto-Assign.\n`{self.bot.prefix}autorole <Mention Role>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_autorole"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = content.id
		embed = discord.Embed(title="__**Auto-Role**__", description=f"Auto-Role role has been set as {content.mention}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Auto-Role**__", description=f"Auto-Role upon join has been Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@autorole.error
	async def autorole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Goodbye Message
	@commands.has_permissions(administrator=True)
	async def gmessage(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Welocme & Goodbye Error**__", description=f"Create Goodbye Message.\n(Mention Member: %mention, Member Username: %member, Server Name: %server)\n`{self.bot.prefix}gmessage <Create Goodbye Message>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_goodbye"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Goodbye Message has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Goodbye Message on Leave has been Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@gmessage.error
	async def gmessage_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Welcome DM Message
	@commands.has_permissions(administrator=True)
	async def dmessage(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Welcome & Goodbye Error**__", description=f"Create Welcome DM Message.\n(Mention Member: %mention, Member Username: %member, Server Name: %server)\n`{self.bot.prefix}dmessage <Create DM Message>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_welcome_dm"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Direct Message has been set as\n{content}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Direct Messages upon join has been Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@dmessage.error
	async def dmessage_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Welcome Message
	@commands.has_permissions(administrator=True)
	async def wmessage(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Welcome & Goodbye Error**__", description=f"Create Welcome Message.\n(Mention Member: %mention, Member Username: %member, Server Name: %server)\n`{self.bot.prefix}wmessage <Create Message>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_welcome"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Message has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Messages on Join have been Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@wmessage.error
	async def wmessage_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



	# Bot Events
	@commands.Cog.listener()
	async def on_message(self, message):
		await self.bot.wait_until_ready()
		mod_mail = self.bot.get_channel(self.bot.mod_mail)
		krypto_announcement = self.bot.get_channel(self.bot.news)
		if message.guild is None:
			if message.content == "":
				return
			embed_7 = discord.Embed(title=f"__**{self.bot.user.name} Support**__", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_7.add_field(name="Ticket:", value=f"{message.author.id}", inline=False)
			embed_7.add_field(name="Message:", value=f"{message.content}", inline=False)
			embed_7.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
			embed_7.set_footer(text=f"{message.author}", icon_url=message.author.avatar_url_as(format=None, static_format="png"))
			await mod_mail.send(embed=embed_7)
			await mod_mail.send(f"{message.author.id}")
			embed = discord.Embed(title="__**Support Ticket**__", description=f"**Your Message was Received.**\n*Please Wait Patiently for a Support Agent to Reply to your Ticket.*", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			await message.author.send(embed=embed)
			return
		no_invite_channels = None
		no_link_channels = None
		no_bad_words_channels = None
		external_links = ["https", ".com", ".net", ".org", ".tv"]
		bad_words = ["fuck", "shit", "damn", "dick", "asshole", "pussy", "cunt", "faggot", "quier", "bullshit", "bitch" "rape", "ass", "skank", "slut", "hoe", "whore", "prick", "bastard", "nigger", "kracker"]

		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = message.guild.get_channel(Channelz)
		
		collection_2 = self.bot.db["AM_no_links"]
		grab_nl_channels = collection_2.find({}, {"_id": 0, "Guild": 0})
		no_link_channels = []
		async for x in grab_nl_channels:
			no_link_channels += {x["Channel"]}

		collection_3 = self.bot.db["AM_no_invites"]
		grab_ni_channels = collection_3.find({}, {"_id": 0, "Guild": 0})
		no_invite_channels = []
		async for x in grab_ni_channels:
			no_invite_channels += {x["Channel"]}

		collection_4 = self.bot.db["AM_no_bad_words"]
		grab_bw_channels = collection_4.find({}, {"_id": 0, "Guild": 0})
		no_bad_words_channels = []
		async for x in grab_bw_channels:
			no_bad_words_channels += {x["Channel"]}

		collection_6 = self.bot.db["AM_spam_mentions"]
		grab_spam_mentions = collection_6.find({}, {"_id": 0, "Guild": 0})
		spam_mentions = []
		async for x in grab_spam_mentions:
			spam_mentions += {x["Channel"]}

		collection_33 = self.bot.db["AM_spam"]
		grab_spam = collection_33.find({}, {"_id": 0, "Guild": 0})
		spam = []
		async for x in grab_spam:
			spam += {x["Channel"]}

		collection_22 = self.bot.db["AM_spam_caps"]
		grab_spam_caps = collection_22.find({}, {"_id": 0, "Guild": 0})
		spam_caps = []
		async for x in grab_spam_caps:
			spam_caps += {x["Channel"]}

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
		async for m in collection_13.find({}, {"_id": 0}):
			levels += {m["Guild"]}

		collection_42 = self.bot.db["Config_global_level_prompt"]
		glevels =  []
		async for m in collection_42.find({}, {"_id": 0}):
			glevels += {m["Member"]}

		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Please do not advertise here {message.author.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please do not post links here {message.author.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't use that kind of language here {message.author.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
		embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed_9 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't spam mention here {message.author.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_9.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
		embed_9.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed_21 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't use excessive caps here {message.author.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_21.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
		embed_21.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed_32 = discord.Embed(title="__**Auto-Moderation**__", description=f"Please don't spam here {message.author.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_32.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
		embed_32.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		if guild_member_level is True: # Add EXP to Guild Rank
			guild_exp += 5
			guild_lvl_end = int(guild_exp ** (1/4))
			await collection_11.update_one({"Member": message.author.id, "Guild": message.guild.id}, {"$set":{"EXP": guild_exp, "Level": guild_lvl_end, "Member_Name": f"{message.author}"}})
			if guild_lvl_end > guild_lvl_start:
				if message.guild.id in levels:
					embed = discord.Embed(title="__**Level Up**__", description=f"You have Advanced to Level {guild_lvl_end}!", timestamp=datetime.utcnow(), color=0xac5ece)
					embed.set_footer(text=f"{message.author}", icon_url=message.author.avatar_url_as(format=None, static_format="png"))
					await message.channel.send(embed=embed)

		if member_level is True: # Add EXP to Global Rank
			exp += 5
			lvl_end = int(exp ** (1/4))
			await collection_44.update_one({"Member": message.author.id}, {"$set":{"EXP": exp, "Level": lvl_end, "Member_Name": f"{message.author}"}})
			if lvl_end > lvl_start:
				if message.author.id in glevels:
					embed = discord.Embed(title="__**Level Up**__", description=f"You have Advanced to Level {lvl_end}!", timestamp=datetime.utcnow(), color=0xac5ece)
					embed.set_footer(text=f"{message.author}", icon_url=message.author.avatar_url_as(format=None, static_format="png"))
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
					embed_4 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.utcnow(), color=0xff0000)
					embed_4.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_4.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_4.add_field(name="__**:newspaper: Reason:**__", value=f"Posted a Link", inline=False)
					embed_4.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_4.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_4.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
					embed_4.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
					await message.channel.send(embed=embed)
					if not mod_log is None:
						await mod_log.send(embed=embed_4)
					await message.delete()

		if message.channel.id in no_link_channels: # External Links Moderation
			if message.author.id != self.bot.user.id:
				for x in external_links:
					if x in message.content.lower():
						embed_5 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.utcnow(), color=0xff0000)
						embed_5.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
						embed_5.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
						embed_5.add_field(name="__**:newspaper: Reason:**__", value=f"Posted an Invite", inline=False)
						embed_5.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
						embed_5.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
						embed_5.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
						embed_5.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
						await message.channel.send(embed=embed_2)
						if not mod_log is None:
							await mod_log.send(embed=embed_5)
						await message.delete()

		if message.channel.id in no_bad_words_channels: # Bad Word Moderation
			for x in bad_words:
				if x in message.content.lower():
					embed_6 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.utcnow(), color=0xff0000)
					embed_6.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_6.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_6.add_field(name="__**:newspaper: Reason:**__", value=f"Said a Bad Word", inline=False)
					embed_6.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_6.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_6.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
					embed_6.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
					await message.channel.send(embed=embed_3)
					if not mod_log is None:
						await mod_log.send(embed=embed_6)
					await message.delete()

		if message.channel.id in spam_mentions: # Spam Mention Moderation
			if len(message.mentions) >= 3:
				embed_8 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.utcnow(), color=0xff0000)
				embed_8.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
				embed_8.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
				embed_8.add_field(name="__**:newspaper: Reason:**__", value=f"Spam Mentioned", inline=False)
				embed_8.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
				embed_8.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
				embed_8.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
				embed_8.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
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
					embed_31 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.utcnow(), color=0xff0000)
					embed_31.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_31.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_31.add_field(name="__**:newspaper: Reason:**__", value=f"Spam Text", inline=False)
					embed_31.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_31.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_31.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
					embed_31.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
					await message.channel.send(embed=embed_32)
					if not mod_log is None:
						await mod_log.send(embed=embed_31)
					await message.delete()

		if message.channel.id in spam_caps: # Spam Caps Moderation
			try:
				if int((sum(1 for x in message.content if str.isupper(x))/len(message.content))*100) >= 70:
					embed_22 = discord.Embed(title="__***Auto-Moderation***__", timestamp=datetime.utcnow(), color=0xff0000)
					embed_22.add_field(name="__**:busts_in_silhouette: User:**__", value=f"{message.author.mention}", inline=False)
					embed_22.add_field(name="__**:link: User ID:**__", value=f"{message.author.id}", inline=False)
					embed_22.add_field(name="__**:newspaper: Reason:**__", value=f"Excessive Caps", inline=False)
					embed_22.add_field(name="__**:tv: Channel:**__", value=f"{message.channel.mention}", inline=False)
					embed_22.add_field(name="__**:envelope: Message:**__", value=f"{message.content}", inline=False)
					embed_22.set_thumbnail(url=message.author.avatar_url_as(format=None, static_format="png"))
					embed_22.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
					await message.channel.send(embed=embed_21)
					if not mod_log is None:
						await mod_log.send(embed=embed_22)
					await message.delete()
			except ZeroDivisionError:
				pass

	# Auto-Role & Welcome and Private Message Upon Join
	@commands.Cog.listener()
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
			embed = discord.Embed(title=f"__**Welcome**__", description=f"{new}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
			embed.set_image(url="attachment://Welcome-Card.png")
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			await get_welcome.send(embed=embed, file=card)
		if not server_dm is None:
			embed_2 = discord.Embed(title="Server Info:", description=f"{new_dm}", timestamp=datetime.utcnow(), inline=False, color=0xac5ece)
			embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
			embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			try:
				await member.send(embed=embed_2)
			except:
				pass
		if not role is None:
			await member.add_roles(role)

	# Goodbye Message Upon Leave
	@commands.Cog.listener()
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
			embed = discord.Embed(title=f"__**Goodbye**__", description=f"{new}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			await get_welcome.send(embed=embed)

def setup(bot):
	bot.add_cog(AutoMod(bot))