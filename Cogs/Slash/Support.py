import discord
import asyncio
import contextlib
import io
import json
import time
import motor.motor_asyncio
import os
import pymongo
import textwrap
import traceback
from discord.ext import commands, menus
from discord import ui, app_commands
from Utils.Helpers import convert_seconds
from Utils.Menus import Formatter, Pager
from datetime import datetime



class Support(commands.Cog, app_commands.Group, name="support", description="Bot Staff & Support Commands"):
	def __init__(self, bot):
		super().__init__()
		self.bot = bot
	def is_owner():
		def predicate(interaction:discord.Interaction):
			with open('Config.json', 'r') as configuration:
				config = json.load(configuration)
			return interaction.user.id in config['Owners']
		return app_commands.check(predicate)

	@app_commands.command(name="eval", description="Executes Code and Returns the Output") # Execute Code Command
	@app_commands.describe(code="Code to Execute")
	@is_owner()
	async def eval(self, interaction:discord.Interaction, *, code:str):
		if code.startswith("```") and code.endswith("```"):
			code = "\n".join(code.split("\n")[1:][:-3])

		local_variables = {
			"discord": discord,
			"commands": commands,
			"app_commands": app_commands,
			"bot": self.bot,
			"interaction": interaction,
			"channel": interaction.channel,
			"user": interaction.user,
			"guild": interaction.guild,
			"message": interaction.message
		}

		stdout = io.StringIO()
		try:
			with contextlib.redirect_stdout(stdout):
				exec(
					f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
				)

				obj = await local_variables["func"]()
				result = f"{stdout.getvalue()}\n-- {obj}\n"
				#result = f"{stdout.getvalue()}\n"

		except Exception as e:
			result = "".join(traceback.format_exception(e, e, e.__traceback__))

		entries = [result[i: i + 1991] for i in range(0, len(result), 1991)]

		formatter = Formatter(entries, per_page=1)
		#menu = menus.MenuPages(formatter)
		menu = Pager(formatter)
		await menu.start(interaction)
	@eval.error
	async def eval_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Eval Error**__", description=f"You are not Authorized to Eval with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="servers", description="Shows All the Servers I'm in") # Shows All Servers Command
	@is_owner()
	async def servers(self, interaction:discord.Interaction):
		servers = []
		counter = 0
		embed = discord.Embed(title="__**Server List**__", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		for x in self.bot.guilds:
			embed.add_field(name=f"__***{x}***__", value=f"`{x.id}` *({x.member_count})*\n**Owned By:** {x.owner}", inline=False)
			counter += 1
			if counter == 10:
				counter = 0
				servers.append(embed)
				embed = discord.Embed(title="__**Server List**__", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if counter < 10 and counter > 0:
			servers.append(embed)

		formatter = Formatter([i for i in servers], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()
	@servers.error
	async def servers_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Server List Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s Servers.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="servers_premium", description="Shows All Premium Servers") # Shows Premium Servers Command
	@is_owner()
	async def servers_premium(self, interaction:discord.Interaction):
		servers = []
		server_names = []
		counter = 0
		embed = discord.Embed(title="__**Premium Servers**__", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		collection = self.bot.db["Bump_autobump"]
		async for m in collection.find({}, {"_id": 0}):
			try:
				count = m['Members']
			except:
				count = "N/A"
			embed.add_field(name=f"__***{m['Guild_Name']}***__", value=f"`{m['Guild']}` *({count})*\n**Owned By:** {m['Owner']}", inline=False)
			counter += 1
			if counter == 10:
				counter = 0
				servers.append(embed)
				embed = discord.Embed(title="__**Premium Servers**__", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		
		if counter < 10 and counter > 0:
			servers.append(embed)

		formatter = Formatter([i for i in servers], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()
	@servers_premium.error
	async def servers_premium_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Premium Server List Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s Premium Servers.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="keys", description="Shows All of Krypto's iOS Mod Keys") # Shows iOS Krypto Mod Users Command
	@is_owner()
	async def ikrypto(self, interaction: discord.Interaction):
		keys = []
		counter = 0
		embed = discord.Embed(title="__**Krypto iOS Keys**__", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		collection = self.bot.db["Site_h5gg"]
		async for m in collection.find({}, {"_id": 0}):
			try:
				end = m['Expire']
			except:
				end = None
			try:
				isAdmin = m['Admin']
			except:
				isAdmin = 0
			if end is None:
				embed.add_field(name=f"__***{m['Key']}***__", value=f"`{m['UDID']}`\n**Issued To:** {m['Owner']} *({isAdmin})*", inline=False)
			if not end is None:
				embed.add_field(name=f"__***{m['Key']}***__", value=f"`{m['UDID']}`\n**Issued To:** {m['Owner']} *({isAdmin})*\n*{m['Create']} - {m['Expire']}*", inline=False)
			counter += 1
			if counter == 10:
				counter = 0
				keys.append(embed)
				embed = discord.Embed(title="__**Krypto iOS Keys**__", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		
		if counter < 10 and counter > 0:
			keys.append(embed)

		formatter = Formatter([i for i in keys], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()
	@ikrypto.error
	async def ikrypto_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Krypto iOS Keys Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s iOS Mod Keys.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="key_reset", description="Reset Krypto iOS Mod Key") # Reset iOS Krypto Mod Key Command
	@app_commands.describe(key="The Key to Reset")
	@is_owner()
	async def ireset(self, interaction: discord.Interaction, key: str):
		collection = self.bot.db["Site_h5gg"]
		lookup = None
		async for x in collection.find({"Key": key}, {"_id": 0}):
			lookup = x["Key"]
			Owner = x["Owner"]
			Owner_ID = x["Owner_ID"]
		if lookup is None:
			embed = discord.Embed(title="__**Key Reset Error**__", description=f"The Key **{key}** was Not Found..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		await collection.update_one({"Key": key}, {"$set":{"UDID": None}})
		embed = discord.Embed(title="__**Key Reset**__", description=f"**{key}** has been Reset.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		if not Owner == "N/A":
			Owner = interaction.guild.get_member(Owner_ID)
			embed = discord.Embed(title="__**Krypto Key**__", description=f"Congratulations, Your Krypto Key **{key}** has been Reset.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			try:
				await Owner.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Key Reset Error**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.response.send_message(embed=embed)
				return
		#await ctx.message.delete()
	@ireset.error
	async def ireset_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Krypto iOS Keys Error**__", description=f"You are not Authorized to Reset {self.bot.user.mention}'s iOS Mod Keys.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="key_create", description="Create or Delete Krypto iOS Mod Key") # Set iOS Mod Keys
	@app_commands.describe(Key="The Key Name to Create", isAdmin="Whether or Not the User is Admin", time="Amount of Time for Key to be Valid", Owner="Discord User Receiving the Key")
	@is_owner()
	async def ikey(self, interaction: discord.Interaction, Key: str, isAdmin: int=None, time: str=None, *, Owner: discord.Member=None):
		if not Owner is None:
			Owner_ID = Owner.id
		if Owner is None:
			Owner = "N/A"
			Owner_ID = 0
		if not time is None:		
			date, string, current = convert_seconds(time)
		collection = self.bot.db["Site_h5gg"]
		log = {}
		log ["Key"] = Key
		log ["Owner"] = str(Owner)
		log ["Owner_ID"] = Owner_ID
		log ["UDID"] = None
		if time is None:
			log ["Create"] = None
			log ["Expire"] = None
		if not time is None:
			log ["Create"] = current
			log ["Expire"] = date
		if isAdmin is None:
			log ["Admin"] = 0
		if not isAdmin is None:
			log ["Admin"] = isAdmin
		lookup = None
		async for x in collection.find({"Key": Key}, {"_id": 0}):
			lookup = x["Key"]
		if not lookup is None:
			old_log = {"Key": Key}
			await collection.delete_one(old_log)
			embed = discord.Embed(title="__**Key Generation**__", description=f"The Key **{Key}** has been Deleted.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			#await ctx.message.delete()
			return
		await collection.insert_one(log)
		if time is None:
			embed = discord.Embed(title="__**Key Generation**__", description=f"The Key **{Key}** has been Created.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if not time is None:
			embed = discord.Embed(title="__**Key Generation**__", description=f"The Key **{Key}** has been Created for {string}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		if not Owner == "N/A":
			if time is None:
				embed = discord.Embed(title="__**Krypto Key**__", description=f"Congratulations, Your Krypto Key is **{Key}**.\n*(VIP Role will be Given if Purchased Monthly or Permanent)*", timestamp=datetime.now(), color=0xac5ece)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			if not time is None:
				embed = discord.Embed(title="__**Krypto Key**__", description=f"Congratulations, Your Krypto Key is **{Key}** and will Expire in {string}.\n*(VIP Role will be Given if Purchased Monthly or Permanent)*", timestamp=datetime.now(), color=0xac5ece)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			try:
				await Owner.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Key Generation Error**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.response.send_message(embed=embed)
				return
		#await ctx.message.delete()
	@ikey.error
	async def ikey_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="reply", description="Respond to User via DMs") # Direct Message Command
	@app_commands.describe(member="The Ticket ID to Reply to", message="The Message You are Sending")
	#@app_commands.guilds(discord.Object(id=self.bot.support_server_id))
	@is_owner()
	async def reply(self, interaction:discord.Interaction, member:discord.User, *, message:str):
		embed = discord.Embed(title=f"__**{self.bot.user.name} Support**__", timestamp=datetime.now(), color=0xac5ece)
		embed.add_field(name="Ticket:", value=f"{member.id}", inline=False)
		embed.add_field(name="Message:", value=f"{message}", inline=False)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		embed = discord.Embed(title="__**Support Ticket**__", description=f"Your Message was Successfully Sent.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
	@reply.error
	async def reply_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Reply Error**__", description=f"You are not Authorized to Send Messages with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="load", description="Loads Specified Cog") # Load Cog Command
	@app_commands.describe(extension_name="Cog Path and Name to Lo")
	@is_owner()
	async def load(self, interaction:discord.Interaction, *, extension_name:str):
		try:
			await self.bot.load_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Loaded**__", description=f"{extension_name} has been Loaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		#await ctx.message.delete()
	@load.error
	async def load_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Load Error**__", description=f"You are not Authorized to Load Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="unload", description="Unloads Specified Cog") # Unload Cog Command
	@app_commands.describe(extension_name="Cog Path and Name to Unload\nCogs.Everyone")
	@is_owner()
	async def unload(self, interaction:discord.Interaction, *, extension_name:str):
		try:
			await self.bot.unload_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Unloaded**__", description=f"{extension_name} has been Unloaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		#await ctx.message.delete()
	@unload.error
	async def unload_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Unload Error**__", description=f"You are not Authorized to Unload Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="reload", description="Reloads Specified Cog") # Reload Cog Command
	@app_commands.describe(extension_name="Cog Path and Name to Reload\nCogs.Everyone")
	@is_owner()
	async def reload(self, interaction:discord.Interaction, *, extension_name:str):
		try:
			await self.bot.unload_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		try:
			await self.bot.load_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Reloaded**__", description=f"{extension_name} has been Reloaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		#await ctx.message.delete()
	@reload.error
	async def reload_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Reload Error**__", description=f"You are not Authorized to Reload Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="reload_all", description="Reloads All Cogs") # Restart All Cogs Command
	@is_owner()
	async def reload_all(self, interaction:discord.Interaction):
		for extension in self.coggers:
			try:
				await self.bot.unload_extension(extension)
			except Exception as e:
				embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.response.send_message(embed=embed)
				return
			try:
				await self.bot.load_extension(extension)
			except Exception as e:
				embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.response.send_message(embed=embed)
				return
			embed = discord.Embed(title="__**Cog Reloaded**__", description=f"{extension} has been Reloaded.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			await asyncio.sleep(1)
		embed = discord.Embed(title="__**Cogs Restarted**__", description=f"All Cogs have been Reloaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		#await ctx.message.delete()
	@reload_all.error
	async def reload_all_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Restart Error**__", description=f"You are not Authorized to Restart Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="sync", description="Syncs the Bot Tree with Discord") # Sync App Commands Command
	@is_owner()
	async def sync(self, interaction:discord.Interaction):
		cmds = await self.bot.tree.sync()
		#await self.bot.tree.sync(guild=discord.Object(id=self.bot.support_server_id))
		self.bot.tree.copy_global_to(guild=discord.Object(id=self.bot.support_server_id))
		embed = discord.Embed(title="__**App Commands Synced**__", description=f"You have Successfully Synced `{len(cmds)}` App Commands to {self.bot.user.mention}!", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
	@sync.error
	async def sync_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Sync Error**__", description=f"You are not Authorized to Sync {self.bot.user.mention}'s Commands.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	vouch = app_commands.Group(name="vouch", description="Vouch Approval Commands")

	@vouch.command(name="approve", description="Approve Incoming Vouch") # Approve Command
	@app_commands.describe(vouch="Vouch ID to Approve")
	#@app_commands.guilds(discord.Object(id=self.bot.support_server_id))
	@is_owner()
	async def approve(self, interaction:discord.Interaction, vouch:int):
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": vouch}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_guild = x["Guild"]
			grab_message = x["Vouch"]
			guild = self.bot.get_guild(grab_guild)
			member_user = guild.get_member(member_user_id)
			buyer = guild.get_member(grab_buyer)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		collection_4 = self.bot.db["Eco_member_vouches"]
		order = [f"**{grab_message}** *~Vouched by {buyer}*"]
		grab_items = collection_4.find({"Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_items:
			bag = m["Items"]
			order += bag
		log = {}
		log ["Member"] = member_user.id
		log ["Items"] = order
		old_log = {"Member": member_user.id}
		await collection_4.delete_one(old_log)
		await collection_4.insert_one(log)
		pending_log = {"Vouch_ID": vouch}
		await collection_2.delete_one(pending_log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Approved**\n**Vouch ID:** `{vouch}`\n__**Receiver:**__\n{member_user}\n__**Vouched By:**__\n{buyer}\n{order[0]}", timestamp=datetime.now(), color=0xff0000)
		embed.set_author(name=f"{member_user}", icon_url=str(member_user.display_avatar.replace(format="png", static_format="png")))
		embed.set_thumbnail(url=buyer.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		await mod_log.send(embed=embed)
		try:
			await member_user.send(embed=embed)
		except:
			pass
		try:
			await buyer.send(embed=embed)
		except:
			pass
		#await ctx.message.delete()
	@approve.error
	async def approve_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Approve Error**__", description=f"You are not Authorized to Approve Vouches with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@vouch.command(name="deny", description="Deny Incoming Vouch") # Deny Command
	@app_commands.describe(vouch="Vouch ID to Deny")
	#@app_commands.guilds(discord.Object(id=self.bot.support_server_id))
	@is_owner()
	async def deny(self, interaction:discord.Interaction, vouch:int):
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": vouch}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_guild = x["Guild"]
			grab_message = x["Vouch"]
			guild = self.bot.get_guild(grab_guild)
			member_user = guild.get_member(member_user_id)
			buyer = guild.get_member(grab_buyer)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		pending_log = {"Vouch_ID": vouch}
		await collection_2.delete_one(pending_log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Denied**\n**Vouch ID:** `{vouch}`\n__**Receiver:**__\n{member_user}\n__**Vouched By:**__\n{buyer}\n{grab_message}", timestamp=datetime.now(), color=0xff0000)
		embed.set_author(name=f"{member_user}", icon_url=str(member_user.display_avatar.replace(format="png", static_format="png")))
		embed.set_thumbnail(url=buyer.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		await mod_log.send(embed=embed)
		try:
			await member_user.send(embed=embed)
		except:
			pass
		try:
			await buyer.send(embed=embed)
		except:
			pass
		#await ctx.message.delete()
	@deny.error
	async def deny_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Deny Error**__", description=f"You are not Authorized to Deny Vouches with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="autobump", description="Setup Auto-Bump for Specified Server and User") # Set AutoBump Servers
	@app_commands.describe(server="Server ID to Add to AutoBump", owner="User ID of Requesting User")
	#@app_commands.guilds(discord.Object(id=self.bot.support_server_id))
	@is_owner()
	async def autobump(self, interaction:discord.Interaction, server:str, *, owner:discord.User):
		collection = self.bot.db["Bump_autobump"]
		server = self.bot.get_guild(int(server))
		owner = server.get_member(owner)
		log = {}
		log ["Guild_Name"] = str(server)
		log ["Owner"] = str(owner)
		log ["Guild"] = server.id
		log ["Owner_ID"] = owner.id
		log ["Members"] = server.member_count
		guildz = None
		async for x in collection.find({"Guild": server.id}, {"_id": 0, "Guild_Name": 0}):
			guildz = x["Guild"]
		if not guildz is None:
			old_log = {"Guild": server.id}
			await collection.delete_one(old_log)
			embed = discord.Embed(title="__**Auto-Bump Setup**__", description=f"Auto-Bump has been Disabled for **{server}**.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			#await ctx.message.delete()
			return
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Auto-Bump Setup**__", description=f"Auto-Bump has been Enabled for *{owner}* in **{server}**.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.response.send_message(embed=embed)
		embed = discord.Embed(title="__**Auto-Bump**__", description=f"Congratulations, Auto-Bump has been Enabled for {self.bot.user.mention} in {server}.\n*(Please Wait for Bump Cycle. You can still use {Bot_Prefix}bump)*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await owner.send(embed=embed)
		except:
			embed = discord.Embed(title="__**Auto-Bump**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)
			return
		#await ctx.message.delete()
	@autobump.error
	async def autobump_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

	@app_commands.command(name="logout", description="Logs Me Out") # Logout Command
	@is_owner()
	async def logout(self, interaction:discord.Interaction):
		embed = discord.Embed(title="__**Logging Out...**__", description=f"Goodnight...", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		self.mongo_client.close()
		await interaction.response.send_message(embed=embed)
		#await ctx.message.delete()
		await self.bot.close()
	@logout.error
	async def logout_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Logout Error**__", description=f"You are not Authorized to Logout {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.response.send_message(embed=embed)

async def setup(bot):
	await bot.add_cog(Support(bot))