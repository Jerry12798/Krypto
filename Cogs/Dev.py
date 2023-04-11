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
from discord import ui
from Utils.Helpers import convert_seconds
from Utils.Menus import Formatter, Pager
from datetime import datetime



class Dev(commands.Cog, name="Dev", description="Bot Staff & Support Commands"):
	def __init__(self, bot):
		self.bot = bot
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)

	@commands.command(name="eval", alias=["exec"])
	@is_owner()
	async def eval(self, ctx, *, code: str=None):
		if code is None:
			embed = discord.Embed(title="__**Eval Error**__", description=f"You need to Attach Code to Execute.\n`{self.bot.prefix}eval <Insert Code to Execute>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return

		if code.startswith("```") and code.endswith("```"):
			code = "\n".join(code.split("\n")[1:][:-3])

		local_variables = {
			"discord": discord,
			"commands": commands,
			"bot": self.bot,
			"ctx": ctx,
			"channel": ctx.channel,
			"author": ctx.author,
			"guild": ctx.guild,
			"message": ctx.message
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
		await menu.start(ctx)
	@eval.error
	async def eval_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Eval Error**__", description=f"You are not Authorized to Eval with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Shows All Servers Command
	@is_owner()
	async def servers(self, ctx):
		servers = []
		counter = 0
		embed = discord.Embed(title="__**Server List**__", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		for x in self.bot.guilds:
			embed.add_field(name=f"__***{x}***__", value=f"`{x.id}` *({x.member_count})*\n**Owned By:** {x.owner}", inline=False)
			counter += 1
			if counter == 10:
				counter = 0
				servers.append(embed)
				embed = discord.Embed(title="__**Server List**__", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if counter < 10 and counter > 0:
			servers.append(embed)

		formatter = Formatter([i for i in servers], per_page=1)
		menu = Pager(formatter)
		await menu.start(ctx)
		await ctx.message.delete()
	@servers.error
	async def servers_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Server List Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s Servers.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Shows Premium Servers Command
	@is_owner()
	async def pservers(self, ctx):
		servers = []
		server_names = []
		counter = 0
		embed = discord.Embed(title="__**Premium Servers**__", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		
		if counter < 10 and counter > 0:
			servers.append(embed)

		formatter = Formatter([i for i in servers], per_page=1)
		menu = Pager(formatter)
		await menu.start(ctx)
		await ctx.message.delete()
	@pservers.error
	async def pservers_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Premium Server List Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s Premium Servers.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Shows iOS Krypto Mod Users Command
	@is_owner()
	async def ikrypto(self, ctx):
		keys = []
		counter = 0
		embed = discord.Embed(title="__**Krypto iOS Keys**__", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		
		if counter < 10 and counter > 0:
			keys.append(embed)

		formatter = Formatter([i for i in keys], per_page=1)
		menu = Pager(formatter)
		await menu.start(ctx)
		await ctx.message.delete()
	@ikrypto.error
	async def ikrypto_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Krypto iOS Keys Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s iOS Mod Keys.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Reset iOS Krypto Mod Key Command
	@is_owner()
	async def ireset(self, ctx, key: str=None):
		if key is None:
			embed = discord.Embed(title="__**Key Reset Error**__", description=f"Mention the Key Name to Reset.\n`{self.bot.prefix}ireset <Key Name>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Site_h5gg"]
		lookup = None
		async for x in collection.find({"Key": key}, {"_id": 0}):
			lookup = x["Key"]
			Owner = x["Owner"]
			Owner_ID = x["Owner_ID"]
		if lookup is None:
			embed = discord.Embed(title="__**Key Reset Error**__", description=f"The Key **{key}** was Not Found..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Key": key}, {"$set":{"UDID": None}})
		embed = discord.Embed(title="__**Key Reset**__", description=f"**{key}** has been Reset.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		if not Owner == "N/A":
			Owner = ctx.guild.get_member(Owner_ID)
			embed = discord.Embed(title="__**Krypto Key**__", description=f"Congratulations, Your Krypto Key **{key}** has been Reset.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			try:
				await Owner.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Key Reset Error**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
				await ctx.send(embed=embed)
				return
		await ctx.message.delete()
	@ireset.error
	async def ireset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Krypto iOS Keys Error**__", description=f"You are not Authorized to Reset {self.bot.user.mention}'s iOS Mod Keys.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set iOS Mod Keys
	@is_owner()
	async def ikey(self, ctx, Key: str=None, isAdmin: int=None, time: str=None, *, Owner: discord.Member=None):
		if Key is None:
			embed = discord.Embed(title="__**Key Generation Error**__", description=f"Mention the Key Name & Buyer's Discord User ID.\n`{self.bot.prefix}ikey <Key Name> <Key Time> <User ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
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
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		await collection.insert_one(log)
		if time is None:
			embed = discord.Embed(title="__**Key Generation**__", description=f"The Key **{Key}** has been Created.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if not time is None:
			embed = discord.Embed(title="__**Key Generation**__", description=f"The Key **{Key}** has been Created for {string}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		if not Owner == "N/A":
			if time is None:
				embed = discord.Embed(title="__**Krypto Key**__", description=f"Congratulations, Your Krypto Key is **{Key}**.\n*(VIP Role will be Given if Purchased Monthly or Permanent)*", timestamp=datetime.now(), color=0xac5ece)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			if not time is None:
				embed = discord.Embed(title="__**Krypto Key**__", description=f"Congratulations, Your Krypto Key is **{Key}** and will Expire in {string}.\n*(VIP Role will be Given if Purchased Monthly or Permanent)*", timestamp=datetime.now(), color=0xac5ece)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			try:
				await Owner.send(embed=embed)
			except:
				embed = discord.Embed(title="__**Key Generation Error**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
				await ctx.send(embed=embed)
				return
		await ctx.message.delete()
	@ikey.error
	async def ikey_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Direct Message Command
	@is_owner()
	async def reply(self, ctx, member: discord.User=None, *, content:str=None):
		if member is None:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"You need to Mention a Ticket ID & Create Message to Send.\n`{self.bot.prefix}reply <Ticket ID> <Create Reply Message>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"Write a Message to DM with {self.bot.user.mention}.\n`{self.bot.prefix}reply <Ticket ID> <Create Reply Message>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title=f"__**{self.bot.user.name} Support**__", timestamp=datetime.now(), color=0xac5ece)
		embed.add_field(name="Ticket:", value=f"{member.id}", inline=False)
		embed.add_field(name="Message:", value=f"{content}", inline=False)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Support Ticket**__", description=f"Your Message was Successfully Sent.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
	@reply.error
	async def reply_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Reply Error**__", description=f"You are not Authorized to Send Messages with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Load Cog Command
	@is_owner()
	async def load(self, ctx, *, extension_name : str=None):
		if extension_name is None:
			embed = discord.Embed(title="__**Load Error**__", description=f"Mention the Cog you want to Load.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			await self.bot.load_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Loaded**__", description=f"{extension_name} has been Loaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@load.error
	async def load_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Load Error**__", description=f"You are not Authorized to Load Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Unload Cog Command
	@is_owner()
	async def unload(self, ctx, *, extension_name : str=None):
		if extension_name is None:
			embed = discord.Embed(title="__**Unload Error**__", description=f"Mention the Cog you want to Unload.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			await self.bot.unload_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Unloaded**__", description=f"{extension_name} has been Unloaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@unload.error
	async def unload_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Unload Error**__", description=f"You are not Authorized to Unload Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Reload Cog Command
	@is_owner()
	async def reload(self, ctx, *, extension_name : str=None):
		if extension_name is None:
			embed = discord.Embed(title="__**Reload Error**__", description=f"Mention the Cog you want to Reload.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			await self.bot.unload_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			await self.bot.load_extension(extension_name)
		except Exception as e:
			embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Reloaded**__", description=f"{extension_name} has been Reloaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@reload.error
	async def reload_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Reload Error**__", description=f"You are not Authorized to Reload Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Restart All Cogs Command
	@is_owner()
	async def restart(self, ctx):
		for extension in self.bot.coggers:
			try:
				await self.bot.unload_extension(extension)
			except Exception as e:
				embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
				await ctx.send(embed=embed)
				return
			try:
				await self.bot.load_extension(extension)
			except Exception as e:
				embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
				await ctx.send(embed=embed)
				return
			embed = discord.Embed(title="__**Cog Reloaded**__", description=f"{extension} has been Reloaded.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			await asyncio.sleep(1)
		embed = discord.Embed(title="__**Cogs Restarted**__", description=f"All Cogs have been Reloaded.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@restart.error
	async def restart_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Restart Error**__", description=f"You are not Authorized to Restart Cogs with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Sync App Commands Command
	@is_owner()
	async def sync(self, ctx):
		cmds = await self.bot.tree.sync()
		#await self.bot.tree.sync(guild=discord.Object(id=self.bot.support_server_id))
		self.bot.tree.copy_global_to(guild=discord.Object(id=self.bot.support_server_id))
		embed = discord.Embed(title="__**App Commands Synced**__", description=f"You have Successfully Synced `{len(cmds)}` App Commands to {self.bot.user.mention}!", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@sync.error
	async def sync_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Sync Error**__", description=f"You are not Authorized to Sync {self.bot.user.mention}'s Commands.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	#vouch = commands.Group(name="vouch", description="Vouch Approval Commands")

	@commands.command() # Approve Command
	@is_owner()
	async def approve(self, ctx, total: int=None):
		if not total:
			embed = discord.Embed(title="__**Approve Error**__", description=f"Specify the Vouch ID.\n`{self.bot.prefix}approve <Vouch ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": total}, {"_id": 0})
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
		pending_log = {"Vouch_ID": total}
		await collection_2.delete_one(pending_log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Approved**\n**Vouch ID:** `{total}`\n__**Receiver:**__\n{member_user}\n__**Vouched By:**__\n{buyer}\n{order[0]}", timestamp=datetime.now(), color=0xff0000)
		embed.set_author(name=f"{member_user}", icon_url=str(member_user.display_avatar.replace(format="png", static_format="png")))
		embed.set_thumbnail(url=buyer.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		try:
			await member_user.send(embed=embed)
		except:
			pass
		try:
			await buyer.send(embed=embed)
		except:
			pass
		await ctx.message.delete()
	@approve.error
	async def approve_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Approve Error**__", description=f"You are not Authorized to Approve Vouches with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Deny Command
	@is_owner()
	async def deny(self, ctx, total: int=None):
		if not total:
			embed = discord.Embed(title="__**Deny Error**__", description=f"Specify the Vouch ID.\n`{self.bot.prefix}deny <Vouch ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": total}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_guild = x["Guild"]
			grab_message = x["Vouch"]
			guild = self.bot.get_guild(grab_guild)
			member_user = guild.get_member(member_user_id)
			buyer = guild.get_member(grab_buyer)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		pending_log = {"Vouch_ID": total}
		await collection_2.delete_one(pending_log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Denied**\n**Vouch ID:** `{total}`\n__**Receiver:**__\n{member_user}\n__**Vouched By:**__\n{buyer}\n{grab_message}", timestamp=datetime.now(), color=0xff0000)
		embed.set_author(name=f"{member_user}", icon_url=str(member_user.display_avatar.replace(format="png", static_format="png")))
		embed.set_thumbnail(url=buyer.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		try:
			await member_user.send(embed=embed)
		except:
			pass
		try:
			await buyer.send(embed=embed)
		except:
			pass
		await ctx.message.delete()
	@deny.error
	async def deny_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Deny Error**__", description=f"You are not Authorized to Deny Vouches with {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set AutoBump Servers
	@is_owner()
	async def autobump(self, ctx, Guild: int=None, *, Owner: int=None):
		if Guild is None:
			embed = discord.Embed(title="__**Auto-Bump Error**__", description=f"Mention the Server's ID & Owner's User ID that's Receiving Auto-Bump.\n`{self.bot.prefix}autobump <Server ID> <User ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if Owner is None:
			embed = discord.Embed(title="__**Auto-Bump Error**__", description=f"Mention the Owner's User ID of the Guild who is Receiving Auto-Bump.\n`{self.bot.prefix}autobump <Server ID> <User ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_autobump"]
		Guild = self.bot.get_guild(Guild)
		Owner = Guild.get_member(Owner)
		log = {}
		log ["Guild_Name"] = str(Guild)
		log ["Owner"] = str(Owner)
		log ["Guild"] = Guild.id
		log ["Owner_ID"] = Owner.id
		log ["Members"] = Guild.member_count
		guildz = None
		async for x in collection.find({"Guild": Guild.id}, {"_id": 0, "Guild_Name": 0}):
			guildz = x["Guild"]
		if not guildz is None:
			old_log = {"Guild": Guild.id}
			await collection.delete_one(old_log)
			embed = discord.Embed(title="__**Auto-Bump Setup**__", description=f"Auto-Bump has been Disabled for **{Guild}**.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Auto-Bump Setup**__", description=f"Auto-Bump has been Enabled for *{Owner}* in **{Guild}**.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		embed = discord.Embed(title="__**Auto-Bump**__", description=f"Congratulations, Auto-Bump has been Enabled for {self.bot.user.mention} in {Guild}.\n*(Please Wait for Bump Cycle. You can still use {Bot_Prefix}bump)*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await Owner.send(embed=embed)
		except:
			embed = discord.Embed(title="__**Auto-Bump**__", description=f"User has DM's Disabled.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		await ctx.message.delete()
	@autobump.error
	async def autobump_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Logout Command
	@is_owner()
	async def logout(self, ctx):
		embed = discord.Embed(title="__**Logging Out...**__", description=f"Goodnight...", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		self.mongo_client.close()
		await ctx.send(embed=embed)
		await ctx.message.delete()
		await self.bot.close()
	@logout.error
	async def logout_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Logout Error**__", description=f"You are not Authorized to Logout {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Dev(bot))