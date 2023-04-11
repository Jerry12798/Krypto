import discord
import time
import asyncio
import motor.motor_asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from Utils.GFX import make_welcome_card



class Automod(commands.Cog, app_commands.Group, name="automod", description="Auto-Moderation Configuration & Toggle Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot
		
	@app_commands.command(name="no_links", description="Toggle External Link Auto-Moderation in Specified Channel") # Set No Link Channels
	@app_commands.describe(channel="Channel to Toggle External Link Auto-Mod in")
	@app_commands.checks.has_permissions(administrator=True)
	async def no_links(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_no_links"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"External Link Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Links are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Link Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"External Links are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@no_links.error
	async def no_links_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="no_caps", description="Toggle Excessive Caps Auto-Moderation in Specified Channel") # Set Excessive Caps Channels
	@app_commands.describe(channel="Channel to Toggle Excessive Caps Auto-Mod in")
	@app_commands.checks.has_permissions(administrator=True)
	async def no_caps(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_spam_caps"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Excessive Caps are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@no_caps.error
	async def no_caps_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="no_invites", description="Toggle Invite Link Auto-Moderation in Specified Channel") # Set No Invite Channels
	@app_commands.describe(channel="Channel to Toggle Invite Link Auto-Mod in")
	@app_commands.checks.has_permissions(administrator=True)
	async def no_invites(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_no_invites"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invite Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invites are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invite Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Server Invites are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@no_invites.error
	async def no_invites_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="no_bad_words", description="Toggle Bad Word Auto-Moderation in Specified Channel") # Set No Bad Word Channels
	@app_commands.describe(channel="Channel to Toggle Bad Word Auto-Mod in")
	@app_commands.checks.has_permissions(administrator=True)
	async def no_bad_words(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_no_bad_words"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Word Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Words are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Word Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Bad Words are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@no_bad_words.error
	async def no_bad_words_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="no_spam", description="Toggle Duplicate/Spam Text Auto-Moderation in Specified Channel") # Set No Spam Channels
	@app_commands.describe(channel="Channel to Toggle Duplicate/Spam Text Auto-Mod in")
	@app_commands.checks.has_permissions(administrator=True)
	async def no_spam(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_spam"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@no_spam.error
	async def no_spam_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="no_spam_mentions", description="Toggle Spam Mentions Auto-Moderation in Specified Channel") # Set No Spam Mention Channels
	@app_commands.describe(channel="Channel to Toggle Spam Mentions Auto-Mod in")
	@app_commands.checks.has_permissions(administrator=True)
	async def no_spam_mentions(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["AM_spam_mentions"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mention Moderation has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mentions are not allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mention Moderation has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Auto-Moderation**__", description=f"Spam Mentions are allowed in this channel now.", timestamp=datetime.now(), color=0xff0000)
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
	@no_spam_mentions.error
	async def no_spam_mentions_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="autorole", description="Set Role to Auto-Assign to New Members") # Set Role for Auto-Role
	@app_commands.describe(role="Role to Auto-Assign")
	@app_commands.checks.has_permissions(administrator=True)
	async def autorole(self, interaction:discord.Interaction, *, role: discord.Role):
		collection = self.bot.db["AM_autorole"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Role"] = role.id
		embed = discord.Embed(title="__**Auto-Role**__", description=f"Auto-Role role has been set as {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Auto-Role**__", description=f"Auto-Role upon join has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@autorole.error
	async def autorole_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="message_on_join_dm", description="Set Direct Message to be Sent on Member Join") # Set Welcome DM Message
	@app_commands.describe(message="Direct Message to be Sent on Member Join")
	@app_commands.checks.has_permissions(administrator=True)
	async def message_on_join_dm(self, interaction:discord.Interaction, *, message: str):
		collection = self.bot.db["AM_welcome_dm"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = message
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Direct Message has been set as\n{message}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Direct Messages upon join has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@message_on_join_dm.error
	async def message_on_join_dm_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="message_on_join", description="Set Join Message for Join/Leave Log") # Set Welcome Message
	@app_commands.describe(message="Message to be Sent on Member Join")
	@app_commands.checks.has_permissions(administrator=True)
	async def message_on_join(self, interaction:discord.Interaction, *, message: str):
		collection = self.bot.db["AM_welcome"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = message
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Message has been set as\n{message}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Welcome Messages on Join have been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@message_on_join.error
	async def message_on_join_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="message_on_leave", description="Set Leave Message for Join/Leave Log") # Set Goodbye Message
	@app_commands.describe(message="Message to be Sent on Member Leave")
	@app_commands.checks.has_permissions(administrator=True)
	async def message_on_leave(self, interaction:discord.Interaction, *, message: str):
		collection = self.bot.db["AM_goodbye"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = message
		embed = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Goodbye Message has been set as\n{message}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		embed_2 = discord.Embed(title="__**Welcome & Goodbye**__", description=f"Goodbye Message on Leave has been Disabled.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@message_on_leave.error
	async def message_on_leave_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	sticky = app_commands.Group(name="sticky", description="Sticky Configuration & Management Commands")

	@sticky.command(name="setup", description="Set Channel and Message for Sticky Advertisement") # Set Sticky Channel & Message
	@app_commands.describe(channel="Channel to Setup Sticky Advertisements in", message="Sticky Message to be Displayed")
	@app_commands.checks.has_permissions(administrator=True)
	async def setup(self, interaction:discord.Interaction, channel:discord.TextChannel, *, message:str):
		collection = self.bot.db["Mod_info"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Channel"] = channel.id
		log ["Message"] = message
		embed = discord.Embed(title="__**Information**__", description=f"Message has been set as\n{message}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Information**__", description=f"Sticky Information has been activated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Information**__", description=f"Sticky Information will be shown in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_5 = discord.Embed(title="__**Information**__", description=f"Sticky Information has been deactivated for {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_5.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_6 = discord.Embed(title="__**Information**__", description=f"Sticky Information will not be shown in this channel now.", timestamp=datetime.now(), color=0xff0000)
		embed_6.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		channelz = []
		async for x in collection.find({}, {"_id": 0, "Guild": 0}):
			channelz += {x["Channel"]}
		if channel.id not in channelz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			await channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_3)
			#await ctx.message.delete()
			return
		async for x in collection.find({"Guild": interaction.guild.id, "Channel": channel.id}, {"_id": 0, "Guild": 0}):
			grab_old_message = x["Message"]
		#embed_2 = discord.Embed(title="__**Advertisement Information**__", description=f"Advertisement Information Message has been Deleted.", timestamp=datetime.now(), color=0xff0000)
		#embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if channel.id in channelz:
			old_log = {"Guild": interaction.guild.id, "Channel": channel.id}
			await collection.delete_one(old_log)
			await channel.send(embed=embed_6)
			await interaction.followup.send(embed=embed_5)
			#await ctx.message.delete()
			return
	@setup.error
	async def setup_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@sticky.command(name="role", description="Set Role Limit for Sticky Advertisement Channels") # Set Sticky Role Limit
	@app_commands.describe(ads="Amount of Advertisements Allowed for Role", role="Role to Set Limit for")
	@app_commands.checks.has_permissions(administrator=True)
	async def role(self, interaction:discord.Interaction, ads:int, *, role:discord.Role):
		collection = self.bot.db["Config_ad_roles"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Role"] = role.id
		log ["Limit"] = ads
		embed = discord.Embed(title="__**Ad Limit**__", description=f"Sticky Advertisement Role Limit has been set as {ads} for {role.mention}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		rolez = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			rolez += {x["Role"]}
		if role.id not in rolez:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Ad Limit**__", description=f"Sticky Advertisement Role has been Disabled for {role.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if role.id in rolez:
			old_log = {"Guild": interaction.guild.id, "Role": role.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@role.error
	async def role_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@sticky.command(name="log", description="Set Channel to Receive Sticky Advertisement Logs in") # Set Sticky Log Command
	@app_commands.describe(channel="Channel to Receive Logs in")
	@app_commands.checks.has_permissions(kick_members=True)
	async def log(self, interaction:discord.Interaction, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Logging Error**__", description=f"Mention Channel to Receive Sticky Channel Logs in.\n`{self.bot.prefix}ilog <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
		collection = self.bot.db["ad_logs"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will no longer be Received in {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Logging**__", description=f"Sticky Channel Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@log.error
	async def log_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@sticky.command(name="remove", description="Remove Specified Amount of Advertisements for Member") # Remove Member Limit
	@app_commands.describe(amount="Amount of Ads to Remove", member="Member to Remove Ads from")
	@app_commands.checks.has_permissions(kick_members=True)
	async def remove(self, interaction:discord.Interaction, amount:int, *, member:discord.Member):
		collection = self.bot.db["Mod_member_ads"]
		ads = None
		async for x in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0}):
			ads = x["Ads"]
		if ads is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"{member.mention} doesn't have any Advertisements.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection.update_one({"Guild": interaction.guild.id, "Member": member.id}, {"$set":{"Ads": ads-amount}})
		embed = discord.Embed(title="__**Removed Successfully**__", description=f"{member.mention} had {amount} of Advertisements Removed from Daily Limit.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@remove.error
	async def remove_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@sticky.command(name="clear", description="Reset Sticky Limit for Specified Member") # Clear Member Limit
	@app_commands.describe(member="Member to Reset Ads for")
	@app_commands.checks.has_permissions(kick_members=True)
	async def clear(self, interaction:discord.Interaction, *, member: discord.Member):
		collection = self.bot.db["Mod_member_ads"]
		old_log = {"Guild": interaction.guild.id, "Member": member.id}
		await collection.delete_one(old_log)
		embed = discord.Embed(title="__**Cleared Successfully**__", description=f"{member.mention}'s Sticky Limit has been Cleared.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@clear.error
	async def clear_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Member Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@sticky.command(name="reset", description="Reset Sticky Advertisement Limits for Entire Server") # Clear Server Limit
	@app_commands.checks.has_permissions(kick_members=True)
	async def reset(self, interaction:discord.Interaction):
		collection = self.bot.db["Mod_member_ads"]
		await collection.delete_many({"Guild": interaction.guild.id})
		embed = discord.Embed(title="__**Cleared Successfully**__", description=f"{interaction.guild}'s Sticky Advertisement Limit has been Cleared.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@reset.error
	async def reset_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Reset Ad Limit with {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Automod(bot))