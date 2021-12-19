import discord
import asyncio
import aiohttp
import asyncpraw
import json
import time
import psutil
import pkg_resources
import sys
import pymongo
import platform
import motor.motor_asyncio
import pytz
import unicodedata
import random
import re
from akinator.async_aki import Akinator
from discord.ext import commands
from datetime import datetime, timedelta
from pytz import timezone
from Utils.Helpers import server_stats, convert_seconds
from Utils.GFX import make_rank_card
from Utils.Fun import play_aki

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

Reddit_Client_ID = config['Reddit_Client_ID']
Reddit_Client_Secret = config['Reddit_Client_Secret']
Reddit_Username = config['Reddit_Username']
Reddit_Password = config['Reddit_Password']
Reddit_User_Agent = config['Reddit_User_Agent']



class Everyone(commands.Cog, name="Everyone"):
	def __init__(self,bot):
		self.bot = bot
		self.bot.aki = Akinator()
		self.bot.playing_aki = []
		self.reddit = asyncpraw.Reddit(client_id=Reddit_Client_ID, client_secret=Reddit_Client_Secret, password=Reddit_Password, user_agent=Reddit_User_Agent, username=Reddit_Username)
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)
	def cleanup_definition(self, definition, *, regex=re.compile(r'(\[(.+?)\])')):
		def repl(m):
			word = m.group(2)
			return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'
		ret = regex.sub(repl, definition)
		if len(ret) >= 2048:
			return ret[0:2000] + ' [...]'
		return ret
	
	@commands.command() # Akinator Command
	async def aki(self, ctx):
		start_aki = await play_aki(self=self, ctx=ctx)
		await ctx.message.delete()		

	@commands.command() # Uptime Command
	async def uptime(self, ctx):
		now = datetime.utcnow()
		delta = now - self.bot.start_time
		hours, remainder = divmod(int(delta.total_seconds()), 3600)
		minutes, seconds = divmod(remainder, 60)
		days, hours = divmod(hours, 24)
		if days:
			time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
		else:
			time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."
		uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)
		embed = discord.Embed(title="__**Uptime**__", description=f"**{self.bot.user.mention}** has been Online for {uptime_stamp}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Guild Rank Command
	async def rank(self, ctx, *, memberz: discord.Member=None):
		collection_2 = self.bot.db["AM_guild_levels"]
		counter = 0
		if memberz is None:
			memberz = ctx.author
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			member = m["Member"]
			exp = m["EXP"]
			lvl = m["Level"]
			counter += 1
			if member == memberz.id:
				card = await make_rank_card(exp=exp, lvl=lvl, rank=counter, member=memberz)
				embed = discord.Embed(title="__**Server Rank**__", description=f":trophy: __**Rank:**__ {counter}  :space_invader: __**Level:**__ {lvl}\n:bar_chart: __**Expierence:**__ {exp} / {(lvl+1)**4}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				if not memberz.id == ctx.author.id:
					embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_image(url="attachment://Rank-Card.png")
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed, file=card)
				await ctx.message.delete()

	@commands.command() # Global Rank Command
	async def grank(self, ctx, *, memberz: discord.Member=None):
		collection_2 = self.bot.db["AM_levels"]
		counter = 0
		if memberz is None:
			memberz = ctx.author
		async for m in collection_2.find({}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			member = m["Member"]
			exp = m["EXP"]
			lvl = m["Level"]
			counter += 1
			if member == memberz.id:
				card = await make_rank_card(exp=exp, lvl=lvl, rank=counter, member=memberz, global_rank=True)
				embed = discord.Embed(title="__**Global Rank**__", description=f":trophy: __**Rank:**__ {counter}  :space_invader: __**Level:**__ {lvl}\n:bar_chart: __**Expierence:**__ {exp} / {(lvl+1)**4}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				if not memberz.id == ctx.author.id:
					embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_image(url="attachment://Rank-Card.png")
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed, file=card)
				await ctx.message.delete()

	@commands.command() # Check Votes Command
	async def votes(self, ctx, param: discord.User=None):
		if param is None:
			param = ctx.author
		collection = self.bot.db["Eco_dbl_votes"]
		collection_2 = self.bot.db["Eco_db_votes"]

		counter = 0
		lcounter = 0
		member_log = False
		votes = 0
		life = 0
		pos = 0
		async for z in collection.find({}, {"_id": 0}).sort("Votes", pymongo.DESCENDING):
			member_log = True
			top = z["Votes"]
			ltop = z["Lifetime"]
			counter += 1
			if z["Member"] == param.id:
				votes = top
				life = ltop
				pos += counter

		db_counter = 0
		db_lcounter = 0
		db_member_log = False
		db_votes = 0
		db_life = 0
		db_pos = 0
		async for z in collection_2.find({}, {"_id": 0}).sort("Votes", pymongo.DESCENDING):
			db_member_log = True
			db_top = z["Votes"]
			db_ltop = z["Lifetime"]
			db_counter += 1
			if z["Member"] == param.id:
				db_votes = db_top
				db_life = db_ltop
				db_pos += db_counter

		if pos == 0:
			pos = "N/A"
		if db_pos == 0:
			db_pos = "N/A"

		embed = discord.Embed(title="__**Votes**__", description=f"__**Top.gg**__\n**Total Votes:** `{votes}`\n**Rank:** `{pos}`\n[Vote Now](<https://top.gg/bot/555820515965534208/vote>)\n__**Discord Bot List**__\n**Total Votes:** `{db_votes}`\n**Rank:** `{db_pos}`\n[Vote Now](<https://discordbotlist.com/bots/krypto-6851/upvote>)", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if not param.id == ctx.author.id:
			embed.set_author(name=f"{param}", icon_url=str(param.avatar_url_as(format=None, static_format="png")))
		await ctx.send(embed=embed)

	@commands.command() # Server Leaderboard Command
	async def leaderboard(self, ctx, serverz:int=None):
		if serverz is None:
			serverz = ctx.guild.id
		server = self.bot.get_guild(serverz)
		collection_2 = self.bot.db["AM_guild_levels"]
		order = ""
		counter = 1
		people = []
		levels = []
		limit = 0
		async for m in collection_2.find({"Guild": server.id}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			if limit < 500:
				people += {m["Member_Name"]}
				levels += {m["Level"]}
			limit += 1
			if limit > 500:
				break
		for x in range(len(people)):
			order += f"__**{counter}:**__ ***{people[x]}:*** *{levels[x]}*\n"
			counter += 1
			if counter == 11:
				embed = discord.Embed(title=f"__**{server.name} Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=server.icon_url_as(format=None, static_format="png"))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if counter <= 10:
			embed = discord.Embed(title=f"__**{server.name} Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=server.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		pages = 1
		if counter > 10:
			page = counter/10
			pages = int(page)
		message = await ctx.send(embed=embed)
		if counter <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_rank"]
		log = {}
		log ["Guild_Name"] = server.name
		log ["Guild"] = server.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Order"] = order
		log ["People"] = people
		log ["Levels"] = levels
		log ["Member_Count"] = counter
		log ["Counter"] = 1
		log ["Pages"] = pages
		await collection.insert_one(log)
		reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
		for x in reactions:
			await message.add_reaction(x)
		try:
			await ctx.message.delete()
		except:
			print(f"{self.bot.user} can't Delete Help CTX Message in {server}.")
		await asyncio.sleep(300)
		old_log = {"Message": message.id}
		await collection.delete_one(old_log)
		await message.delete()

	@commands.command() # Global Leaderboard Command
	async def gleaderboard(self, ctx):
		collection_2 = self.bot.db["AM_levels"]
		order = ""
		people = []
		levels = []
		counter = 1
		limit = 0
		async for m in collection_2.find({}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			if limit < 500:
				people += {m["Member_Name"]}
				levels += {m["Level"]}
			limit += 1
			if limit > 500:
				break
		for x in range(len(people)):
			order += f"__**{counter}:**__ ***{people[x]}:*** *{levels[x]}*\n"
			counter += 1
			if counter == 11:
				embed = discord.Embed(title="__**Global Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if counter <= 10:
			embed = discord.Embed(title=f"__**Global Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		
		pages = 1
		if counter > 10:
			page = counter/10
			pages = int(page)
		message = await ctx.send(embed=embed)
		if counter <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_rank"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Order"] = order
		log ["People"] = people
		log ["Levels"] = levels
		log ["Global"] = 1
		log ["Member_Count"] = counter
		log ["Counter"] = 1
		log ["Pages"] = pages
		await collection.insert_one(log)
		reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
		for x in reactions:
			await message.add_reaction(x)
		try:
			await ctx.message.delete()
		except:
			print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
		await asyncio.sleep(300)
		old_log = {"Message": message.id}
		await collection.delete_one(old_log)
		await message.delete()

	@commands.command() # Vote Leaderboard Command
	async def vleaderboard(self, ctx):
		collection = self.bot.db["Eco_total_votes"]
		order = ""
		people = []
		levels = []
		levels_2 = []
		counter = 1
		limit = 0
		async for m in collection.find({}, {"_id": 0}).sort("Votes", pymongo.DESCENDING):
			if limit < 500:
				people += {m["Member_Name"]}
				levels += {m["Votes"]}
				levels_2 += {m["Lifetime"]}
			limit += 1
			if limit > 500:
				break
		for x in range(len(people)):
			order += f"__**{counter}:**__ ***{people[x]}:*** *{levels[x]}*\n"
			counter += 1
			if counter == 11:
				embed = discord.Embed(title="__**Vote Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if counter <= 10:
			embed = discord.Embed(title=f"__**Vote Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		
		pages = 1
		if counter > 10:
			page = counter/10
			pages = int(page)
		message = await ctx.send(embed=embed)
		if counter <= 10:
			await ctx.message.delete()
			return

		collection = self.bot.db["AM_votes"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Order"] = order
		log ["People"] = people
		log ["Votes"] = levels
		log ["Lifetime"] = levels_2
		log ["Global"] = 1
		log ["Member_Count"] = counter
		log ["Counter"] = 1
		log ["Pages"] = pages
		await collection.insert_one(log)
		reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
		for x in reactions:
			await message.add_reaction(x)
		try:
			await ctx.message.delete()
		except:
			print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
		await asyncio.sleep(300)
		old_log = {"Message": message.id}
		await collection.delete_one(old_log)
		await message.delete()

	@commands.command() # Shows All Servers Command
	@is_owner()
	async def servers(self, ctx):
		servers = []
		server_names = []
		counter = 0
		pages = 1
		for x in self.bot.guilds:
			servers += [f"`{x.id}` *({x.member_count})*\n**Owned By:** {x.owner}"]
			server_names += [f"{x}"]

		embed = discord.Embed(title="__**Server List**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		for x in servers[:10]:
			counter += 1
			embed.add_field(name=f"__***{server_names[counter-1]}***__", value=f"{x}", inline=False)

		if len(servers) <= 10:
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if len(servers) > 10:
			page = len(servers)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)

		collection = self.bot.db["AM_server_list"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Servers"] = servers
		log ["Server_Names"] = server_names
		log ["Counter"] = 1
		log ["Pages"] = pages
		await collection.insert_one(log)
		reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
		for x in reactions:
			await message.add_reaction(x)
		try:
			await ctx.message.delete()
		except:
			print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
		await asyncio.sleep(300)
		old_log = {"Message": message.id}
		await collection.delete_one(old_log)
		await message.delete()
	@servers.error
	async def servers_error(ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Server List Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s Servers.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Shows Premium Servers Command
	@is_owner()
	async def pservers(self, ctx):
		servers = []
		server_names = []
		counter = 0
		pages = 1
		collection = self.bot.db["Bump_autobump"]
		async for m in collection.find({}, {"_id": 0}):
			print(m)
			try:
				count = m['Members']
			except:
				count = "N/A"
			servers += [f"`{m['Guild']}` *({count})*\n**Owned By:** {m['Owner']}"]
			server_names += [f"{m['Guild_Name']}"]

		embed = discord.Embed(title="__**Premium Servers**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		for x in servers[:10]:
			counter += 1
			embed.add_field(name=f"__***{server_names[counter-1]}***__", value=f"{x}", inline=False)

		if len(servers) <= 10:
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if len(servers) > 10:
			page = len(servers)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)

		collection = self.bot.db["AM_premium_servers"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Servers"] = servers
		log ["Server_Names"] = server_names
		log ["Counter"] = 1
		log ["Pages"] = pages
		await collection.insert_one(log)
		reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
		for x in reactions:
			await message.add_reaction(x)
		try:
			await ctx.message.delete()
		except:
			print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
		await asyncio.sleep(300)
		old_log = {"Message": message.id}
		await collection.delete_one(old_log)
		await message.delete()
	@pservers.error
	async def pservers_error(ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Premium Server List Error**__", description=f"You are not Authorized to View {self.bot.user.mention}'s Premium Servers.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Reminder Command
	async def remind(self, ctx, time:str=None, *, reminder:str=None):
		if time is None:
			embed = discord.Embed(title="__**Reminder Error**__", description=f"Specify an Amount of Time.\n*Days: d, Hours: h, Minutes: m, Seconds: s*\n`{self.bot.prefix}remind <Amount of Time> <Reminder Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reminder is None:
			embed = discord.Embed(title="__**Reminder Error**__", description=f"Provide a Message to be Reminded of.\n`{self.bot.prefix}remind <Amount of Time> <Reminder Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["AM_alarms"]
		
		to_fix = convert_seconds(time)
		fix = to_fix.astimezone(timezone("US/Eastern"))
				
		embed = discord.Embed(title="__**Reminder Set**__", description=f"You will be reminded in {string} to {reminder}.", timestamp=date.astimezone(timezone("US/Eastern")), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		message = await ctx.send(embed=embed)

		auto = {}
		auto ["Member"] = ctx.author.id
		auto ["Guild"] = ctx.guild.id
		auto ["Channel"] = ctx.channel.id
		auto ["Message"] = message.id
		auto ["Reminder"] = reminder
		auto ["Begin"] = current
		auto ["End"] = date
		await collection.insert_one(auto)
		await ctx.message.delete()

	@commands.command() # Bot Listing Information Command
	async def about(self, ctx, param:int=None):
		if param is None:
			embed = discord.Embed(title="__**Information Error**__", description=f"Mention a Bot ID to get Information on.\n`{self.bot.prefix}info <Bot ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		TOPGG_Token = commands.Bot.topgg_token
		data = {}
		count = 0
		embed = None
		header = {"Authorization":TOPGG_Token}
		async with self.bot.session.get(f"https://top.gg/api/bots/{param}", headers=header) as url:
			if url.status == 200:
				info = await url.json()
				bio = info["shortdesc"]
				desc = info["longdesc"][0:1024]
				prefix = info["prefix"]
				lib = info["lib"]
				if lib == "":
					lib = "N/A"
				try:
					guilds = info["server_count"]
				except:
					guilds = "N/A"
				votes = info["monthlyPoints"]
				total = info["points"]
				owners = ""
				end = len(info["owners"])
				for x in info["owners"]:
					if not len(info["owners"]) <= 1:
						if not end <= 1:
							owners += f"{x}, "
						if end <= 1:
							owners += f"{x}"
					if len(info["owners"]) <= 1:
						owners += f"{x}"
					end -= 1
				certified = info["certifiedBot"]
				invite = info["invite"]
				support = f"[Click to Add](<{invite}>)"
				server = info["support"]
				if not server is None:
					support += f"\n[Support Server](<https://discord.gg/{server}>)"
				site = info["website"]
				if not site is None:
					support += f"\n[Website](<{site}>)"
				github = info["github"]
				if not github is None:
					support += f"[GitHub](<{github}>)"
				name = info["username"]
				logo = info["avatar"]
				log ={}
				log["bio"] = bio
				log["desc"] = desc
				log["prefix"] = prefix
				log["lib"] = lib
				log["servers"] = guilds
				log["votes"] = votes
				log["tvotes"] = total
				log["owners"] = owners
				log["certified"] = certified
				log["support"] = support
				log["username"] = name
				log["avatar"] = logo
				log["param"] = param
				data["topgg"] = log
				count += 1
				embed = discord.Embed(title="__**Top.gg Information**__", url=f"https://top.gg/bot/{param}", description=f"{bio}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.add_field(name=f"__**Description**__", value=f"{desc}", inline=False)
				embed.add_field(name=f"__**Misc**__", value=f"**Prefix:** {prefix}\n**Library:** {lib}\n**Servers:** {guilds}\n**Monthly Votes:** {votes}\n**Total Votes:** {total}\n**Certified:** {certified}\n**Owners:** {owners}\n{support}", inline=False)
				embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/264445053596991498/a_a8aec6ad1a286d0cfeae8845886dfe2a.gif")
				embed.set_author(name=f"{name}", icon_url=f"https://cdn.discordapp.com/avatars/{param}/{logo}.webp")
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			

		async with self.bot.session.get(f"https://discord.bots.gg/api/v1/bots/{param}") as url:
			if url.status == 200:
				info = await url.json()
				bio = info["shortDescription"]
				desc = info["longDescription"][0:1024]
				prefix = info["prefix"]
				lib = info["libraryName"]
				try:
					guilds = info["guildCount"]
				except:
					guilds = "N/A"
				nick = info["owner"]["username"]
				discrim = info["owner"]["discriminator"]
				oid = info["owner"]["userId"]
				owners = f"{nick}#{discrim} ({oid})"
				verified = info["verified"]
				invite = info["botInvite"]
				support = f"[Click to Add](<{invite}>)"
				server = info["supportInvite"]
				if not server is None:
					support += f"\n[Support Server](<https://discord.gg/{server}>)"
				site = info["website"]
				if not site is None:
					support += f"\n[Website](<{site}>)"
				source = info["openSource"]
				if not source is None:
					support += f"\n[Source Code](<{source}>)"
				name = info["username"]
				logo = info["avatarURL"]
				log ={}
				log["bio"] = bio
				log["desc"] = desc
				log["prefix"] = prefix
				log["lib"] = lib
				log["servers"] = guilds
				log["owners"] = owners
				log["verified"] = verified
				log["support"] = support
				log["username"] = name
				log["avatar"] = logo
				log["param"] = param
				data["db"] = log
				count += 1
				if embed is None:
					embed = discord.Embed(title="__**Discord Bots Information**__", url=f"https://discord.bots.gg/bots/{param}", description=f"{bio}", timestamp=datetime.utcnow(), color=0xac5ece)
					embed.add_field(name=f"__**Description**__", value=f"{desc}", inline=False)
					embed.add_field(name=f"__**Misc**__", value=f"**Prefix:** {prefix}\n**Library:** {lib}\n**Servers:** {guilds}\n**Verified:** {verified}\n**Owners:** {owners}\n{support}", inline=False)
					embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/110373943822540800/a_280f68348c167703bec255e18184f7b0.gif")
					embed.set_author(name=f"{name}", icon_url=logo)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))

		if count == 0:
			embed = discord.Embed(title="__**Information Error**__", description=f"There was no Bots with the ID `{param}` found on Top.gg or Discord Bots..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return			

		message = await ctx.send(embed=embed)
		if count > 1:
			collection = self.bot.db["AM_binfo"]
			log = {}
			log ["Guild_Name"] = ctx.guild.name
			log ["Guild"] = ctx.guild.id
			log ["Author"] = ctx.author.id
			log ["Channel"] = ctx.channel.id
			log ["Message"] = message.id
			log ["Data"] = data
			log ["Counter"] = 1
			log ["Pages"] = count
			await collection.insert_one(log)
			reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
			for x in reactions:
				await message.add_reaction(x)
			try:
				await ctx.message.delete()
			except:
				print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
			await asyncio.sleep(300)
			old_log = {"Message": message.id}
			await collection.delete_one(old_log)
			await message.delete()
			return
		try:
			await ctx.message.delete()
		except:
			pass

	@commands.command() # Bot Information Command
	async def binfo(self, ctx):
		current_os = f"{platform.system()} {platform.release()} ({platform.version()})"
		dpy = pkg_resources.get_distribution("discord.py").version
		embed = discord.Embed(title=f"__**{self.bot.user.name} Information**__", description=f":satellite: __**Servers:**__ {len(self.bot.guilds)}\n:busts_in_silhouette: __**Members:**__ {len(self.bot.users)}\n:ping_pong: __**Ping:**__ **{int(self.bot.latency*1000)}** *ms*\n:bar_chart: __**RAM Usage:**__ {int(psutil.virtual_memory()[2])}% ({round(psutil.virtual_memory()[3]*10**-9, 2)}/{round(psutil.virtual_memory()[0]*10**-9, 2)} *GB*)\n:microscope: __**CPU Usage:**__ {int(psutil.cpu_percent())}%\n:globe_with_meridians: __**Host OS**__ {current_os}\n:electric_plug: __**Library:**__ discord.py {dpy}\n:snake: __**Language**__ Python {sys.version[0:6]}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Ping Command (Latency)
	async def ping(self, ctx):
		embed = discord.Embed(title=f"__**{self.bot.user.name}'s Latency**__", description=f"**{int(self.bot.latency*1000)}** *ms*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Embedded Echo Command
	async def echo(self, ctx, *, content:str=None):
		if content is None:
			embed = discord.Embed(title="__**Echo Error**__", description=f"Write a Message to Echo it.\n`{self.bot.prefix}echo <Create Echo Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Echo Embed**__", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="Message:", value=f"{content}", inline=False)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Advanced Echo Command
	async def aecho(self, ctx, title=None, *, content:str=None):
		if title is None:
			embed = discord.Embed(title="__**Advanced Echo Error**__", description=f"Create a Title for the Embed.\n`{self.bot.prefix}aecho <Create Title> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**Advanced Echo Error**__", description=f"Create a Title and Write a Message to Echo it.\n`{self.bot.prefix}aecho <Create Title> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title=f"__**{title}**__", description=f"{content}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Clean Echo Command
	async def cecho(self, ctx, *, title=None):
		if title is None:
			embed = discord.Embed(title="__**Clean Echo Error**__", description=f"Create a Message for the Embed.\n`{self.bot.prefix}cecho <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(description=f"**{title}**", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Weather Command
	async def weather(self, ctx, zipcode:int=None):
		if zipcode is None:
			embed = discord.Embed(title="__**Weather Error**__", description=f"Mention a zipcode to get the weather for.\n`{self.bot.prefix}weather <Zipcode>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async with self.bot.session.get(f"https://api.openweathermap.org/data/2.5/weather?zip={zipcode}&units=imperial&APPID=986ef6da00c77e47e6fe6a5eba0e369a") as url:
			if url.status != 200:
				embed = discord.Embed(title="__**Weather Error**__", description=f"**Response {url.status_code}:** *{url.reason}*", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			data = await url.json()
			if not data:
				embed = discord.Embed(title="__**Weather Error**__", description=f"No Results for the Zipcode `{zipcode}`..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			
			location = data["name"]
			country = data["sys"]["country"]
			condition = data["weather"][0]["main"]
			desc = data["weather"][0]["description"]
			humidity = data["main"]["humidity"]
			wind = int(data["wind"]["speed"])
			temp = int(data["main"]["temp"])
			temp_max = int(data["main"]["temp_max"])
			temp_min = int(data["main"]["temp_min"])
			lat_cord = data["coord"]["lat"]
			lon_cord = data["coord"]["lon"]

			embed = discord.Embed(title=f"__**{location}** *({country})*__", description=f":thermometer: **Temperature:** {temp} *({temp_max}/{temp_min})*\n:earth_americas: **{condition}:** {desc}\n:wind_blowing_face: **Wind:** {wind} *mph*\n:droplet: **Humidity:** {humidity}%\n:globe_with_meridians: **Coordinates:** {lat_cord}, {lon_cord}", timestamp=datetime.utcnow(), color=0xac5ece)
			#embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()

	@commands.command() # Definition Command
	async def define(self, ctx, word:str=None):
		if word is None:
			embed = discord.Embed(title="__**Definition Error**__", description=f"You must Include a Word to Define.\n`{self.bot.prefix}define <Word>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async with self.bot.session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as url:
			if url.status != 200:
				embed = discord.Embed(title="__**Definition Error**__", description=f"**Response {url.status_code}:** *{url.reason}*", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			data = await url.json()
			if not data:
				embed = discord.Embed(title="__**Definition Error**__", description=f"No Results for the Word `{word}`..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			word = data[0]['word']
			pronunciation = data[0]['phonetics']
			pronunciationz = ""
			for x in pronunciation:
				pronunciationz += f"[{x['text']}](<{x['audio']}>)\n"
			"""try:
				origin = data[0]['origin']
			except:
				origin = "Origin Not Available" """
			grab_meanings = data[0]['meanings']
			#embed = discord.Embed(title=f"__**Word Definition**__", description=f"**{word}**\n*{origin}*\n{pronunciationz}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed = discord.Embed(title=f"__**Word Definition**__", description=f"`{word}`\n{pronunciationz}", timestamp=datetime.utcnow(), color=0xac5ece)
			#embed = discord.Embed(title=f"__**Definition of {word.capitalize()}**__", description=f"{pronunciationz}", timestamp=datetime.utcnow(), color=0xac5ece)
			for x in grab_meanings:
				pos = x['partOfSpeech']
				defs = ""
				counter = 0
				for z in x['definitions']:
					counter += 1
					try:
						defs += f"\n\n**{counter})** {z['definition']}\n**Example:** *{z['example']}*"
					except:
						defs += f"\n\n**{counter})** {z['definition']}"
				embed.add_field(name=f"__**{pos.capitalize()}**__", value=f"{defs}", inline=False)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()

	@commands.command() # Urban Dictionary Command
	async def udefine(self, ctx, *, word: str=None):
		if word is None:
			embed = discord.Embed(title="__**Definition Error**__", description=f"You must Include a Word to Define.\n`{self.bot.prefix}udefine <Word>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		"""if not ctx.channel.is_nsfw():
			embed = discord.Embed(title="__**Definition Error**__", description=f"You can only use this in NSFW channels.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return"""
		async with self.bot.session.get(f'http://api.urbandictionary.com/v0/define?term={word}') as url:
			if url.status != 200:
				embed = discord.Embed(title="__**Definition Error**__", description=f"**Response {url.status_code}:** *{url.reason}*", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			data = await url.json()
			if not data:
				embed = discord.Embed(title="__**Definition Error**__", description=f"No Results for the Word `{word}`..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			query = data['list']
			#print(query)
			embed = discord.Embed(title=f"__**Urban Dictionary**__", description=f"`{word}`\n__**Top Definitions**__", timestamp=datetime.utcnow(), color=0xac5ece)
			#order = ""
			counter = 0
			amount = len(query[0:3])
			for x in query[0:3]:
				counter += 1
				definition = x['definition']
				poster = x['author']
				link = x['permalink']
				upvote = x['thumbs_up']
				downvote =x['thumbs_down']
				#order += f"\n\n**[{counter})](<{link}>)** {definition}\n:thumbsup: {upvote} | :thumbsdown: {downvote}"
				embed.add_field(name=f"**[Definition] {counter}/{amount}**", value=f"*{self.cleanup_definition(definition)}*\n**:thumbsup: [{upvote}](<{link}>) | :thumbsdown: [{downvote}](<{link}>)**", inline=False)
			#embed.add_field(name=f"__**Top Definitions**__", value=f"{order}", inline=False)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()

	@commands.command() # Emoji Unicode Command
	async def uni(self, ctx, *, characters:str=None):
		"""Shows you information about a number of characters.
		Only up to 25 characters at a time.
		"""
		if characters is None:
			embed = discord.Embed(title="__**Unicode Error**__", description=f"Include an Emoji to get its Unicode Information.\n`{self.bot.prefix}uni <Emoji>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		def to_string(c):
			digit = f'{ord(c):x}'
			name = unicodedata.name(c, 'Name Not Found')
			return f'[\\U{digit:>08}](<http://www.fileformat.info/info/unicode/char/{digit}>): **{name}** | {c}'
		msg = '\n'.join(map(to_string, characters))
		if len(msg) > 2000:
			embed = discord.Embed(title="__**Unicode Error**__", description=f"The ouput of this is too long to display..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title=f"__**Emoji Unicode**__", description=f"{msg}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Meme Command
	async def meme(self, ctx):
		await ctx.channel.trigger_typing()
		posts = []
		sub = await self.reddit.subreddit('memes')
		async for x in sub.hot():
			posts.append(x.id)
		data = await self.reddit.submission(id=posts[random.randint(0, len(posts))])
		embed = discord.Embed(title=f"", description=f"[{data.title}](<https://reddit.com/r/memes/comments/{data.id}>)", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_image(url=f"{data.url}")
		comments = await data.comments()
		embed.set_footer(text=f"\U0001F44D {data.score} | \U0001F5EF {len(comments)}\n{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		#embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Report Command
	async def report(self, ctx, member: discord.User=None, *, reason=None):
		collection = self.bot.db["logs"]
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member and reason is None:
			embed = discord.Embed(title="__**Report Error**__", description=f"You must mention the member you are reporting as well as give a reason.\n`{self.bot.prefix}report <Mention User> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Report Error**__", description=f"Give a reason as to why you are reporting this member.\n`{self.bot.prefix}report <Mention User> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__***Report Success***__", description=f"{ctx.author.mention} your report has been received.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name="__**:busts_in_silhouette: Reported:**__", value=f"{member.mention}", inline=False)
		embed.add_field(name="__**:newspaper: Reason:**__", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		try:
			await ctx.author.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__***Report***__", description=f"{ctx.author.mention} has reported {member.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name="__**:link: Reporter ID:**__", value=f"{ctx.author.id}", inline=False)
		embed_2.add_field(name="__**:link: Offender ID:**__", value=f"{member.id}", inline=False)
		embed_2.add_field(name="__**:newspaper: Reason:**__", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Server Stats Command
	async def stats(self, ctx, serverz:int=None):
		if serverz is None:
			serverz = ctx.guild.id
		await self.bot.wait_until_ready()
		server = self.bot.get_guild(serverz)

		online, idle, offline, dnd = server_stats(server)
		bot_count = 0
		for b in server.members:
			if b.bot:
				bot_count += 1
		fmt = "%I:%M%p %B %d, %Y %Z"
		creation_date = server.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime(fmt)
		if len(server.emojis) == 0:
			embed = discord.Embed(title=f"__**{server.name} Stats**__", description=f":crown: __**Owner:**__ {server.owner}\n:earth_americas: __**Region:**__ {server.region}\n:link: __**ID:**__ `{server.id}`\n:beginner: __**Shard:**__ {server.shard_id}\n:calendar: __**Created:**__ {create_date}" , timestamp=datetime.utcnow(), color=0xac5ece)
			embed.add_field(name=f":busts_in_silhouette: Members[{len(server.members)}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`\n:robot: **Bots:** `{bot_count}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Categories:**__ `{len(server.categories)}`\n__**Channels:**__ `{len(server.channels)}`\n__**Roles:**__ `{len(server.roles)}`\n__**Features:**__ {server.features}\n__**Verification:**__ {server.verification_level}\n__**Content Filter:**__ {server.explicit_content_filter}", inline=False)
			embed.add_field(name=f":100: Emotes [{len(server.emojis)}]", value="None", inline=False)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
		if len(server.emojis) <= 10:
			embed = discord.Embed(title=f"__**{server.name} Stats**__", description=f":crown: __**Owner:**__ {server.owner}\n:link: __**ID:**__ `{server.id}`\n:earth_americas: __**Region:**__ {server.region}\n:beginner: __**Shard:**__ {server.shard_id}\n:calendar: __**Created:**__ {create_date}" , timestamp=datetime.utcnow(), color=0xac5ece)
			embed.add_field(name=f":busts_in_silhouette: Members[{len(server.members)}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`\n:robot: **Bots:** `{bot_count}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Categories:**__ `{len(server.categories)}`\n__**Channels:**__ `{len(server.channels)}`\n__**Roles:**__ `{len(server.roles)}`\n__**Features:**__ {server.features}\n__**Verification:**__ {server.verification_level}\n__**Content Filter:**__ {server.explicit_content_filter}", inline=False)
			embed.add_field(name=f":100: Emotes [{len(server.emojis)}]", value=" ".join(map(lambda o: str(o), server.emojis)), inline=False)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
		if len(server.emojis) > 10:
			embed = discord.Embed(title=f"__**{server.name} Stats**__", description=f":crown: __**Owner:**__ {server.owner}\n:link: __**ID:**__ `{server.id}`\n:earth_americas: __**Region:**__ {server.region}\n:beginner: __**Shard:**__ {server.shard_id}\n:calendar: __**Created:**__ {create_date}" , timestamp=datetime.utcnow(), color=0xac5ece)
			embed.add_field(name=f":busts_in_silhouette: Members[{len(server.members)}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`\n:robot: **Bots:** `{bot_count}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Categories:**__ `{len(server.categories)}`\n__**Channels:**__ `{len(server.channels)}`\n__**Roles:**__ `{len(server.roles)}`\n__**Features:**__ {server.features}\n__**Verification:**__ {server.verification_level}\n__**Content Filter:**__ {server.explicit_content_filter}", inline=False)
			embed.add_field(name=f":100: Emotes [{len(server.emojis)}]", value=f"{server.emojis[0]} {server.emojis[1]} {server.emojis[2]} {server.emojis[3]} {server.emojis[4]} {server.emojis[5]} {server.emojis[6]} {server.emojis[7]} {server.emojis[8]} {server.emojis[9]}", inline=False)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()

	@commands.command() # Channel Information Command
	async def cinfo(self, ctx, *, channelz=None):
		if channelz is None:
			channelz = ctx.channel.id
		try:
			grab = discord.utils.get(ctx.guild.channels, name=str(channelz))
			if grab.id > 0:
				channel = grab
		except:
			channel = self.bot.get_channel(int(channelz))
		fmt = "%I:%M%p %B %d, %Y %Z"
		creation_date = channel.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime(fmt)
		embed_2 = discord.Embed(title="__**Channel Information**__", description=f":tv: __**Channel:**__ **{channel.mention}**\n:link: __**Channel ID:**__ `{channel.id}`\n:globe_with_meridians: __**Server:**__ `{channel.guild.name}`\n:link: __**Server ID:**__ `{channel.guild.id}`\n:card_box: __**Category:**__ {channel.category}\n:thought_balloon: __**Topic:**__ {channel.topic}\n:calendar: __**Created:**__ {create_date}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.add_field(name=f":busts_in_silhouette: Members[{len(channel.members)}]", value=", ".join(map(lambda o: str(o), channel.members[0:49])), inline=False)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Role Information Command
	async def rinfo(self, ctx, *, rolez=None):
		if rolez is None:
			embed = discord.Embed(title="__**Role Information Error**__", description=f"You must mention the Role ID you want to see information about.\n`{self.bot.prefix}rinfo <Role ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		grab = discord.utils.get(ctx.guild.roles, name=str(rolez))
		try:
			if grab.id > 0:
				role = grab
		except:
			for z in self.bot.guilds:
				grab = discord.utils.get(z.roles, id=int(rolez))
				if not grab is None:
					role = grab
		fmt = "%I:%M%p %B %d, %Y %Z"
		creation_date = role.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime(fmt)
		permz = ""
		for z in role.permissions:
			if z[1] is True:
				permz += f"{z[0]}, "
		if len(role.members) == 0:
			embed_2 = discord.Embed(title="__**Role Information**__", description=f":pencil: __**Role:**__ `{role}`\n:link: __**Role ID:**__ `{role.id}`\n:satellite: __**Server:**__ `{role.guild}`\n:link: __**Server ID:**__ `{role.guild.id}`\n:art: __**Color:**__ {role.colour}\n:bell: __**Mentionable:**__ {role.mentionable}\n:calendar: __**Created:**__ {create_date}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_2.add_field(name=f":lock: __**Permissions**__", value=f"{permz}", inline=False)
			embed_2.add_field(name=":busts_in_silhouette: __**Members[0]**__", value="None", inline=False)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
		if len(role.members) >= 1:
			embed_2 = discord.Embed(title="__**Role Information**__", description=f":pencil: __**Role:**__ `{role}`\n:link: __**Role ID:**__ `{role.id}`\n:satellite: __**Server:**__ `{role.guild}`\n:link: __**Server ID:**__ `{role.guild.id}`\n:art: __**Color:**__ {role.colour}\n:bell: __**Mentionable:**__ {role.mentionable}\n:calendar: __**Created:**__ {create_date}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_2.add_field(name=f":lock: __**Permissions**__", value=f"{permz}", inline=False)
			embed_2.add_field(name=f":busts_in_silhouette: __**Members[{len(role.members)}]**__", value=", ".join(map(lambda o: str(o), role.members[0:49])), inline=False)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			await ctx.message.delete()

	@commands.command() # Member Information Command
	async def minfo(self, ctx, *, memberz=None):
		if not memberz is None:
			grab = discord.utils.get(self.bot.users, name=memberz)
			if grab is None:
				counter = 0
				new = ""
				for x in str(memberz):
					if x.isdigit():
						new += x
					counter += 1
				if not new == "":
					new = int(new)
				grab = discord.utils.get(self.bot.users, id=int(new))
			member = discord.utils.get(ctx.guild.members, id=grab.id)
			if member is None:
				for z in self.bot.guilds:
					final = discord.utils.get(z.members, id=grab.id)
					if not final is None:
						member = final
		if memberz is None:
			member = ctx.author
		fmt = "%I:%M%p %B %d, %Y %Z"
		creation_date = member.created_at
		creation_datez = member.joined_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		azz = creation_datez.astimezone(timezone("US/Eastern"))
		correct_zonez = azz.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime(fmt)
		create_datez = correct_zonez.strftime(fmt)
		embed = discord.Embed(title="__***Member Information***__",timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name=f"__**:busts_in_silhouette: Member:**__", value=f"**{member}**", inline=False)
		embed.add_field(name=f"__**:link: User ID:**__", value=f"`{member.id}`", inline=False)
		embed.add_field(name=f"__**:computer: Status:**__", value=f"`{member.status}`", inline=False)
		if not member.activity is None:
			try:
				active = member.activity.type[0:13]
				act = active[0].capitalize()
				embed.add_field(name=f"__**:video_game: Activity:**__", value=f"**{act}** {member.activity.name}", inline=False)
			except:
				embed.add_field(name=f"__**:video_game: Activity:**__", value=f"{member.activity.name}", inline=False)
		if not member.nick is None:
			embed.add_field(name="__**:100: Nickname:**__", value=f"{member.nick}", inline=False)
		embed.add_field(name=f"__**:alien: Highest Role:**__", value=f"`{member.top_role}`", inline=False)
		embed.add_field(name=f"__**:mortar_board:  Roles[{len(member.roles[1:])}]**__", value=f", ".join(map(lambda o: o.mention, member.roles[1:])), inline=False)
		embed.add_field(name=f"__**:calendar: Account Created:**__", value=f"{create_date}", inline=False)
		embed.add_field(name=f"__**:calendar: Joined:**__", value=f"{create_datez}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Invite Command
	async def invite(self, ctx):
		embed = discord.Embed(title=f"__***{self.bot.user.name}***__", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="__**:robot: Auto-Moderation:**__", value="\n```Toggleable Bad Word, Server Invite, External Link, & Spam Mention Auto-Moderation.\nSet an Auto-Role as well as Logs for Modertion & Join/Leave.```\n", inline=False)
		embed.add_field(name="__**:lock: Moderation Commands:**__", value="\n```Kick, Ban, Mute, Unmute, Warn, Clear, Hire, Report, Rolemenu (Similar to YAGPDB) & Many More Commands.```\n", inline=False)
		embed.add_field(name="__**:musical_note: Music Commands:**__", value="\n```Play, Queue, Join, Pause, Resume, Skip, Stop, & Queued Commands.```\n", inline=False)
		embed.add_field(name="__**:slot_machine: Entertainment Commands:**__", value="\n```Phone Calls, Words of Wisdom (8-Ball), Dice Roll, Coin Flip, & Rock Paper Scissors.```\n", inline=False)
		embed.add_field(name="__**:chart_with_upwards_trend: Stats & Information:**__", value="\n```Commands to Show Information of a Member, Channel, or Role as well as Detailed Server Stats.```\n", inline=False)
		embed.add_field(name="__**:newspaper: Bump Advertise:**__", value=f"\n```Bump Your Server in {self.bot.user.name}'s Support Server & Servers with Bump.```\n", inline=False)
		embed.add_field(name="__**:e_mail: DM Support:**__", value=f"\n```Simply just Message {self.bot.user.name} if you need Help or have any Questions or Suggestions for {self.bot.user.name}'s Support Team.```\n", inline=False)
		embed.add_field(name=f"__**:loudspeaker: {self.bot.user.name} Announcements:**__", value=f"\n```Set Channel to receive {self.bot.user.name}'s Official Announcements.```\n", inline=False)
		embed.add_field(name="__**:crown: Owner:**__", value=f"***{self.bot.bot_owner}***")
		embed.add_field(name="__**:satellite: Servers:**__", value=f"**{len(self.bot.guilds)}**")
		embed.add_field(name="__**:gem: Server Invite:**__", value=f"[Click to Join](<{self.bot.support_server}>)")
		embed.add_field(name="__**:link: Bot Invite:**__", value=f"[Click to Invite](<https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot>)")
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Help Command
	#@commands.bot_has_permissions(add_reactions=True)
	async def help(self, ctx):
		amount = 13
		current_amount = 1
		if ctx.author.id in self.bot.owners:
			amount = 14
		embed = discord.Embed(title=f"__***(1/2) General Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="__**:mailbox: Report:**__", value=f"*Sends Report to Servers Mod Log*\n`{self.bot.prefix}report <Mention User> <Reason>`", inline=False)
		embed.add_field(name="__**:space_invader: Server Rank:**__", value=f"*Sends your Current Server Rank with* {self.bot.user.mention} *in Current Server or Checks Mentioned Member's Rank*\n`{self.bot.prefix}rank` or `{self.bot.prefix}rank <Mention Member>`", inline=False)
		embed.add_field(name="__**:globe_with_meridians: Global Rank:**__", value=f"*Sends your Current Global Rank with* {self.bot.user.mention} *or Checks Mentioned Member's Rank*\n`{self.bot.prefix}grank` or `{self.bot.prefix}grank <Mention Member>`", inline=False)
		embed.add_field(name="__**:ballot_box: Votes:**__", value=f"*Sends your Upvotes for* {self.bot.user.mention} *or Checks Mentioned Member's Upvotes for {self.bot.user.name}*\n`{self.bot.prefix}votes` or `{self.bot.prefix}votes <Mention Member>`", inline=False)
		embed.add_field(name="__**:beginner: Server Leaderboard:**__", value=f"*Shows Top 500 Users on Server's Leaderboard*\n`{self.bot.prefix}leaderboard` *or* `{self.bot.prefix}leaderboard <Server ID>`", inline=False)
		embed.add_field(name="__**:fleur_de_lis: Global Leaderboard:**__", value=f"*Shows Top 500 Users on Global Leaderboard*\n`{self.bot.prefix}gleaderboard`", inline=False)
		embed.add_field(name="__**:card_box: Vote Leaderboard:**__", value=f"*Shows Top 500 Users on Vote Leaderboard*\n`{self.bot.prefix}vleaderboard`", inline=False)
		embed.add_field(name="__**:alarm_clock: Reminder:**__", value=f"*Sets a Reminder for the Mentioned Message*\n**Days: d, Hours: h, Minutes: m, Seconds: s**\n`{self.bot.prefix}remind <Amount of Time> <Reminder Message>`", inline=False)
		embed.add_field(name="__**:white_sun_small_cloud: Weather:**__", value=f"*Sends the Weather of the Mentioned Zipcode*\n`{self.bot.prefix}weather <Zipcode>`", inline=False)
		embed.add_field(name="__**:books: Word Definition:**__", value=f"*Sends the Definition of the Mentioned Word*\n`{self.bot.prefix}define <word>`", inline=False)
		embed.add_field(name="__**:scroll: Urban Dictionary:**__", value=f"*Sends the Definition from the Urban Dictionary of the Mentioned Word*\n`{self.bot.prefix}udefine <word>`", inline=False)
		embed.add_field(name="__**:rofl: Meme:**__", value=f"*Sends a random Meme to the Current Channel*\n`{self.bot.prefix}meme`", inline=False)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		message = await ctx.send(embed=embed)
		collection = self.bot.db["AM_help"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Counter"] = 1
		await collection.insert_one(log)
		reactions = ["\U000023ea", "\U000025c0", "\U000025b6", "\U000023ed"]
		for x in reactions:
			await message.add_reaction(x)
		try:
			await ctx.message.delete()
		except:
			print(f"{self.bot.user} can't Delete Help CTX Message in {ctx.guild}.")
		await asyncio.sleep(300)
		old_log = {"Message": message.id}
		await collection.delete_one(old_log)
		await message.delete()

	@commands.Cog.listener() # Paginate Events
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		if payload.user_id == self.bot.user.id:
			return
		amount = 13 # Paginate Help Event
		current_amount = 1
		if payload.user_id in self.bot.owners:
			amount = 14
		embed = discord.Embed(title=f"__***(1/2) General Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="__**:mailbox: Report:**__", value=f"*Sends Report to Servers Mod Log*\n`{self.bot.prefix}report <Mention User> <Reason>`", inline=False)
		embed.add_field(name="__**:space_invader: Server Rank:**__", value=f"*Sends your Current Server Rank with* {self.bot.user.mention} *in Current Server or Checks Mentioned Member's Rank*\n`{self.bot.prefix}rank` or `{self.bot.prefix}rank <Mention Member>`", inline=False)
		embed.add_field(name="__**:globe_with_meridians: Global Rank:**__", value=f"*Sends your Current Global Rank with* {self.bot.user.mention} *or Checks Mentioned Member's Rank*\n`{self.bot.prefix}grank` or `{self.bot.prefix}grank <Mention Member>`", inline=False)
		embed.add_field(name="__**:ballot_box: Votes:**__", value=f"*Sends your Upvotes for* {self.bot.user.mention} *or Checks Mentioned Member's Upvotes for {self.bot.user.name}*\n`{self.bot.prefix}votes` or `{self.bot.prefix}votes <Mention Member>`", inline=False)
		embed.add_field(name="__**:beginner: Server Leaderboard:**__", value=f"*Shows Top 500 Users on Server's Leaderboard*\n`{self.bot.prefix}leaderboard` *or* `{self.bot.prefix}leaderboard <Server ID>`", inline=False)
		embed.add_field(name="__**:fleur_de_lis: Global Leaderboard:**__", value=f"*Shows Top 500 Users on Global Leaderboard*\n`{self.bot.prefix}gleaderboard`", inline=False)
		embed.add_field(name="__**:card_box: Vote Leaderboard:**__", value=f"*Shows Top 500 Users on Vote Leaderboard*\n`{self.bot.prefix}vleaderboard`", inline=False)
		embed.add_field(name="__**:alarm_clock: Reminder:**__", value=f"*Sets a Reminder for the Mentioned Message*\n**Days: d, Hours: h, Minutes: m, Seconds: s**\n`{self.bot.prefix}remind <Amount of Time> <Reminder Message>`", inline=False)
		embed.add_field(name="__**:white_sun_small_cloud: Weather:**__", value=f"*Sends the Weather of the Mentioned Zipcode*\n`{self.bot.prefix}weather <Zipcode>`", inline=False)
		embed.add_field(name="__**:books: Word Definition:**__", value=f"*Sends the Definition of the Mentioned Word*\n`{self.bot.prefix}define <word>`", inline=False)
		embed.add_field(name="__**:scroll: Urban Dictionary:**__", value=f"*Sends the Definition from the Urban Dictionary of the Mentioned Word*\n`{self.bot.prefix}udefine <word>`", inline=False)
		embed.add_field(name="__**:rofl: Meme:**__", value=f"*Sends a random Meme to the Current Channel*\n`{self.bot.prefix}meme`", inline=False)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_0 = discord.Embed(title=f"__***(2/2) General Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_0.add_field(name="__**:man_genie: Akinator:**__", value=f"*Start a Game of Akinator (Guess Your Character)*\n`{self.bot.prefix}aki`", inline=False)
		embed_0.add_field(name="__**:telephone: Phone:**__", value=f"*Sends your Message to All Servers with Phone Setup*\n`{self.bot.prefix}phone <Create Message>`", inline=False)
		embed_0.add_field(name="__**:crystal_ball: Words of Wisdom (8-Ball):**__", value=f"*Sends Words of Wisdom to Answer Your Question*\n`{self.bot.prefix}wisdom <Create Question>`", inline=False)
		embed_0.add_field(name="__**:game_die: Dice Roll:**__", value=f"*Rolls a Standard Dice with 6 Sides*\n***(You may include Number to Change the Amount of Sides however it's Not Required)***\n`{self.bot.prefix}dice` or `{self.bot.prefix}dice <Sides of Dice>`", inline=False)
		embed_0.add_field(name="__**:moyai: Coin Flip:**__", value=f"*Flips a Coin & Reveals the Side*\n***(You may include Your Guess however it's Not Required)***\n`{self.bot.prefix}flip` or `{self.bot.prefix}flip <Your Guess>`", inline=False)
		embed_0.add_field(name="__**:scissors: Rock Paper Scissors:**__", value=f"*Play RPS with* {self.bot.user.mention}*... Best 2 out of 3?*\n***(Paper->Rock->Scissors->Paper)***\n`{self.bot.prefix}rps <Your Choice>`", inline=False)
		embed_0.add_field(name="__**:clipboard: Echo:**__", value=f"*Sends your Message but in an Embed*\n`{self.bot.prefix}echo <Create Message>`", inline=False)
		embed_0.add_field(name="__**:file_folder: Advanced Echo Embed:**__", value=f"*Sends your Title & Message in an Embed*\n`{self.bot.prefix}aecho <Create Title> <Create Message>`", inline=False)
		embed_0.add_field(name="__**:speech_balloon: Clean Echo Embed:**__", value=f"*Sends your Message in an Embed*\n`{self.bot.prefix}cecho <Create Message>`", inline=False)
		embed_0.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		
		current_amount += 1

		embed_1 = discord.Embed(title=f"__***(1/2) Information Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_1.add_field(name="__**:satellite: Server Stats:**__", value=f"*Sends Detailed Stats of Current Server or Mentioned Server*\n`{self.bot.prefix}stats` *or* `{self.bot.prefix}stats <Server ID>`", inline=False)
		embed_1.add_field(name="__**:page_facing_up: Member Info:**__", value=f"*Sends Detailed Information on You or Mentioned User*\n`{self.bot.prefix}minfo` *or* `{self.bot.prefix}minfo <User ID or Name>`", inline=False)
		embed_1.add_field(name="__**:tv: Channel Info:**__", value=f"*Sends Detailed Information on Current Channel or Mentioned Channel*\n`{self.bot.prefix}cinfo <Channel ID or Name>`", inline=False)
		embed_1.add_field(name="__**:alien: Role Info:**__", value=f"*Sends Detailed Information on Mentioned Role*\n`{self.bot.prefix}rinfo <Role ID or Name>`", inline=False)
		embed_1.add_field(name="__**:money_mouth: Emoji Info:**__", value=f"*Sends Unicode Information on an Emoji*\n`{self.bot.prefix}uni <Emoji>`", inline=False)
		embed_1.add_field(name="__**:microscope: Discord.py Lookup:**__", value=f"*Sends Links of Search Results from Discord.py Documentation*\n`{self.bot.prefix}rtd <Document Reference>`", inline=False)
		embed_1.add_field(name="__**:snake: Python Lookup:**__", value=f"*Sends Links of Search Results from Python Documentation*\n`{self.bot.prefix}rtd py <Document Reference>`", inline=False)
		embed_1.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_2 = discord.Embed(title=f"__***(2/2) Information Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.add_field(name="__**:robot: Bot Information:**__", value=f"*Sends Information from Top.gg & Discord Bots for Mentioned Bot*\n`{self.bot.prefix}about <Bot ID>`", inline=False)
		embed_2.add_field(name="__**:apple: Signed iOS Versions:**__", value=f"*Sends All iOS Versions currently beinged signed by Apple*\n`{self.bot.prefix}signed` *or* `{self.bot.prefix}signed <Device Type>`", inline=False)
		embed_2.add_field(name="__**:tools: iOS Tweak Lookup:**__", value=f"*Sends Information about the Mentioned Tweak*\n`{self.bot.prefix}tweak <Tweak Name>`", inline=False)
		embed_2.add_field(name="__**:crossed_swords: CoC Player Info:**__", value=f"*Sends Information on about Mentioned Clash of Clans Player Tag*\n`{self.bot.prefix}pinfo <Player Tag>`", inline=False)
		embed_2.add_field(name="__**:beginner: CoC Clan Info:**__", value=f"*Sends Information on about Mentioned Clash of Clans Clan Tag*\n`{self.bot.prefix}clan <Clan Tag>`", inline=False)
		embed_2.add_field(name="__**:ping_pong: Ping:**__", value=f"*Sends {self.bot.user.name}'s Latency*\n`{self.bot.prefix}ping`", inline=False)
		embed_2.add_field(name=f"__**:robot: {self.bot.user.name} Info:**__", value=f"*Sends Detailed Information on {self.bot.user.name}*\n`{self.bot.prefix}binfo`", inline=False)
		embed_2.add_field(name="__**:chart_with_upwards_trend: Uptime:**__", value=f"*Sends {self.bot.user.name}'s Uptime*\n***(Amount of Time Online)***\n`{self.bot.prefix}uptime`", inline=False)
		embed_2.add_field(name="__**:link: Invite:**__", value=f"*Sends Invite for* {self.bot.user.mention} *& the* [Support Server](<{self.bot.support_server}>)\n`{self.bot.prefix}invite`", inline=False)
		embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1
		
		embed_3 = discord.Embed(title=f"__***Music Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_3.add_field(name="__**:arrow_forward: Play:**__", value=f"*Plays the Song you Mention*\n***(You or*** {self.bot.user.mention} ***must be Connected to a Voice Channel)***\n`{self.bot.prefix}play <Song Name>`", inline=False)
		embed_3.add_field(name="__**:arrow_double_down: Queue:**__", value=f"*Adds Song you Mentioned to the Queue to be Played*\n***(***{self.bot.user.mention} ***must be Connected to a Voice Channel & Playing Music Already)***\n`{self.bot.prefix}queue <Song Name>`", inline=False)
		embed_3.add_field(name="__**:twisted_rightwards_arrows: Join:**__", value=f"*Connects* {self.bot.user.mention} *to the Mentioned Voice Channel*\n`{self.bot.prefix}join <Voice Channel Name>`", inline=False)
		embed_3.add_field(name="__**:pause_button: Pause:**__", value=f"*Pauses the Music that is Currently being Played*\n`{self.bot.prefix}pause`", inline=False)
		embed_3.add_field(name="__**:play_pause: Resume:**__", value=f"*Resumes Playing the Music that is Paused*\n`{self.bot.prefix}resume`", inline=False)
		embed_3.add_field(name="__**:next_track: Skip:**__", value=f"*Skips the Song that is Currently being Played*\n`{self.bot.prefix}skip`", inline=False)
		embed_3.add_field(name="__**:stop_button: Stop:**__", value=f"*Stops the Music that is Currently being Played & Disconnects* {self.bot.user.mention} *from Voice Chat*\n`{self.bot.prefix}stop`", inline=False)
		embed_3.add_field(name="__**:information_source: Queue List:**__", value=f"*Shows All Songs that is Currently in the Queue*\n`{self.bot.prefix}queued`", inline=False)
		embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_4 = discord.Embed(title=f"__***(1/2) Economy Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_4.add_field(name="__**:handbag: Bag:**__", value=f"*Shows Mentioned Member or your Items in the Server*\n`{self.bot.prefix}bag` *or* `{self.bot.prefix}bag <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:file_cabinet: Storage:**__", value=f"*Shows Currency & Items in your or Mentioned Member's Storage*\n`{self.bot.prefix}storage` *or* `{self.bot.prefix}storage <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:credit_card: Balance:**__", value=f"*Shows Balance for you or Mentioned Member*\n`{self.bot.prefix}balance` *or* `{self.bot.prefix}balance <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:classical_building: Server Balance:**__", value=f"*Shows Balance of the Server*\n`{self.bot.prefix}gbalance`", inline=False)
		embed_4.add_field(name="__**:shopping_cart: Shop:**__", value=f"*Shows Shop for the Server or Mentioned Member*\n`{self.bot.prefix}shop` *or* `{self.bot.prefix}shop <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:moneybag: Buy:**__", value=f"*Purchase Item from Server Shop or Mentioned Member*\n`{self.bot.prefix}buy <Item Index>` *or* `{self.bot.prefix}buy <Item Index> <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:confetti_ball: Daily Rewards:**__", value=f"*Grants Random Amount of Currency every 24 hours*\n`{self.bot.prefix}daily`", inline=False)
		embed_4.add_field(name="__**:scroll: Selling:**__", value=f"*Shows Shop for you or Mentioned Member*\n`{self.bot.prefix}selling` *or* `{self.bot.prefix}selling <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:money_with_wings: Sell:**__", value=f"*Lists Item in your Shop for the given Price*\n`{self.bot.prefix}sell <Price> <Item Index>`", inline=False)
		embed_4.add_field(name="__**:x: Remove Listing:**__", value=f"*Removes Item from your Shop*\n`{self.bot.prefix}rsell <Item Index>`", inline=False)
		embed_4.add_field(name="__**:wastebasket: Clear Listings:**__", value=f"*Clears All Items in your Shop*\n`{self.bot.prefix}csell`", inline=False)
		embed_4.add_field(name="__**:gem: Transfer:**__", value=f"*Transfers Currency from your Balance to Mentioned Member*\n`{self.bot.prefix}transfer <Amount> <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:gift: Give:**__", value=f"*Transfers Item from your Bag to Mentioned Member*\n`{self.bot.prefix}give <Item Index> <Mention Member>`", inline=False)
		embed_4.add_field(name="__**:heavy_plus_sign: Deposit:**__", value=f"*Deposit Currency into your Savings Account*\n`{self.bot.prefix}deposit <Amount>`", inline=False)
		embed_4.add_field(name="__**:heavy_minus_sign: Withdraw:**__", value=f"*Withdraw Currency from Savings Account*\n`{self.bot.prefix}withdraw <Amount>`", inline=False)
		embed_4.add_field(name="__**:inbox_tray: Store:**__", value=f"*Removes Item from Bag and Adds it into your Storage Box*\n`{self.bot.prefix}store <Item Index>`", inline=False)
		embed_4.add_field(name="__**:outbox_tray: Take:**__", value=f"*Removes Item from Storage Box and Adds it into your Bag*\n`{self.bot.prefix}take <Item Index>`", inline=False)
		embed_4.add_field(name="__**:put_litter_in_its_place: Drop:**__", value=f"*Drops Item from your Bag*\n`{self.bot.prefix}drop <Item Index>`", inline=False)
		embed_4.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_5 = discord.Embed(title=f"__***(2/2) Economy Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_5.add_field(name="__**:pencil: Apply:**__", value=f"*Apply for an Account to use the Economy System*\n`{self.bot.prefix}apply`", inline=False)
		embed_5.add_field(name="__**:stopwatch: Rent:**__", value=f"*Apply for a Savings Account & Security Box*\n`{self.bot.prefix}rent`", inline=False)
		embed_5.add_field(name="__**:ballot_box: Register:**__", value=f"*Registers the Server to use the Economy System.*\n`{self.bot.prefix}register`", inline=False)
		embed_5 .add_field(name="__**:heavy_plus_sign: Admin Deposit:**__", value=f"*Deposits Currency from to Mentioned Member.*\n`{self.bot.prefix}udeposit <Amount> <Mention Member>`", inline=False)
		embed_5.add_field(name="__**:heavy_minus_sign: Admin Withdraw:**__", value=f"*Withdrawa Currency from Mentioned Member.*\n`{self.bot.prefix}uwithdraw <Amount> <Mention Member>`", inline=False)
		embed_5.add_field(name="__**:package: Item:**__", value=f"*Adds Item to Server Shop for the given Price.*\n`{self.bot.prefix}item <Price> <Item Index>`", inline=False)
		embed_5.add_field(name="__**:bomb: Remove Item:**__", value=f"*Removes Item from Server Shop.*\n`{self.bot.prefix}ritem <Item Index>`", inline=False)
		embed_5.add_field(name="__**:recycle: Clear Shop:**__", value=f"*Clears All Items in Server Shop.*\n`{self.bot.prefix}cshop`", inline=False)
		embed_5.add_field(name="__**:lock_with_ink_pen: Bag Limit:**__", value=f"*Sets the Limit for Bag Storage.*\n`{self.bot.prefix}lbag <Amount>`", inline=False)
		embed_5.add_field(name="__**:closed_lock_with_key: Security Box Limit:**__", value=f"*Sets the Limit for Security Box Storage.*\n`{self.bot.prefix}lbox <Amount>`", inline=False)
		embed_5.add_field(name="__**:satellite: Server Start Balance:**__", value=f"*Sets the Starting Amount of Currency for the Server.*\n`{self.bot.prefix}sstart <Amount>`", inline=False)
		embed_5.add_field(name="__**:busts_in_silhouette: User Start Balance:**__", value=f"*Sets the Starting Amount of Currency for New Member's for the Server.*\n`{self.bot.prefix}ustart <Amount>`", inline=False)
		embed_5.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_6 = discord.Embed(title=f"__***Vouch Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_6.add_field(name="__**:scroll: Check Vouches:**__", value=f"*Shows Mentioned Member or Your Vouches*\n`{self.bot.prefix}vouches <Mention Member>`", inline=False)
		embed_6.add_field(name="__**:white_check_mark: Vouch:**__", value=f"*Sends Vouch for Mentioned Member to Vouch Queue for Approval*\n`{self.bot.prefix}vouch <Mention Member> <Vouch Description>`", inline=False)
		embed_6.add_field(name="__**:repeat: Revouch:**__", value=f"*Revouches for a Vouch you Submitted*\n`{self.bot.prefix}revouch <Vouch ID> <Vouch Description>`", inline=False)
		embed_6.add_field(name="__**:link: Add Profile Link:**__", value=f"*Sets Your Profile's Shop Link*\n`{self.bot.prefix}vlink <Shop URL>`", inline=False)
		embed_6.add_field(name="__**:flag_white: Add Profile Banner:**__", value=f"*Sets Your Profile's Banner*\n`{self.bot.prefix}vbanner <Banner URL>`", inline=False)
		embed_6.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_7 = discord.Embed(title=f"__***Bump Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_7.add_field(name="__**:satellite: Bump:**__", value=f"*Bumps Server in* [{self.bot.user.name}'s Support Server](<{self.bot.support_server}>) *and All Servers with Bump Setup*\n***(Server's Description, & Server's Invite Before you can Successfully Bump)***\n`{self.bot.prefix}bump`", inline=False)
		embed_7.add_field(name="__**:page_facing_up: Bumpset Description:**__", value=f"*Sets Servers Bump Description*\n`{self.bot.prefix}sdescription <Create Description>`", inline=False)
		embed_7.add_field(name="__**:link: Bumpset Invite:**__", value=f"*Sets Servers Bump Invite*\n`{self.bot.prefix}sinvite <Invite Link>`", inline=False)
		embed_7.add_field(name="__**:flag_white: Bumpset Banner:**__", value=f"*Sets Servers Bump Banner*\n`{self.bot.prefix}sbanner <Banner URL>`", inline=False)
		embed_7.add_field(name="__**:clipboard: Bumpset:**__", value=f"*Sets Channel to Receive Bump Feed in*\n`{self.bot.prefix}bumpset <Mention Channel>`", inline=False)
		embed_7.add_field(name="__**:scroll: Preview:**__", value=f"*Shows Preview of Current Server's Bump Advertisement*\n`{self.bot.prefix}spreview`", inline=False)
		embed_7.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_8 = discord.Embed(title=f"__***(1/2) Moderation Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_8.add_field(name="__**:wastebasket: Clear:**__", value=f"*Deletes Specified Amount of Messages*\n`{self.bot.prefix}clear <Number of Messages>`", inline=False)
		embed_8.add_field(name="__**:no_entry_sign: Warn:**__", value=f"*Warns Mentioned User for Specified Reason*\n`{self.bot.prefix}warn <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:pencil: Warnings:**__", value=f"*Shows Warnings for Mentioned User*\n`{self.bot.prefix}warnings <Mention User>`", inline=False)
		embed_8.add_field(name="__**:warning: Remove Warning:**__", value=f"*Removes Specified Warning from Mentioned User for Specified Reason*\n`{self.bot.prefix}rwarn <Mention User> <Warning Index> <Reason>`", inline=False)
		embed_8.add_field(name="__**:white_check_mark: Clear Warnings:**__", value=f"*Clears Warnings from Mentioned User for Specified Reason*\n`{self.bot.prefix}cwarn <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:zipper_mouth: Mute:**__", value=f"*Adds Muted Role to Mentioned User for Specified Reason*\n`{self.bot.prefix}mute <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:open_mouth: Unmute:**__", value=f"*Removes Muted Role from Mentioned User for Specified Reason*\n`{self.bot.prefix}unmute <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:alarm_clock: Timed Mute:**__", value=f"*Adds Muted Role to Mentioned User for Specified Specified Time & Reason*\n**Days: d, Hours: h, Minutes: m, Seconds: s**\n`{self.bot.prefix}tmute <Amount of Time> <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:mans_shoe: Kick:**__", value=f"*Kicks Mentioned User for Specified Reason*\n`{self.bot.prefix}kick <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:lock: Ban:**__", value=f"*Bans Mentioned User for Specified Reason*\n`{self.bot.prefix}ban <Mention User> <Reason>`", inline=False)
		embed_8.add_field(name="__**:unlock: Soft Ban:**__", value=f"*Soft Bans Mentioned User for Specified Reason*\n`{self.bot.prefix}sban <Mention User> <Reason>`", inline=False)
		embed_8.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_9 = discord.Embed(title=f"__***(2/2) Moderation Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_9.add_field(name="__**:heavy_plus_sign: Add Role:**__", value=f"*Adds Mentioned Role to Mentioned User*\n`{self.bot.prefix}arole <Mention Role> <Mention User>`", inline=False)
		embed_9.add_field(name="__**:heavy_minus_sign: Remove Role:**__", value=f"*Removes Mentioned Role from Mentioned User*\n`{self.bot.prefix}rrole <Mention Role> <Mention User>`", inline=False)
		embed_9.add_field(name="__**:ballot_box_with_check: Mass Add Role:**__", value=f"*Adds Mentioned Role to All Members*\n`{self.bot.prefix}marole <Mention Role>`", inline=False)
		embed_9.add_field(name="__**:no_entry_sign:  Mass Remove Role:**__", value=f"*Removes Mentioned Role from All Members*\n`{self.bot.prefix}mrrole <Mention Role>`", inline=False)
		embed_9.add_field(name="__**:bell: Ping Role:**__", value=f"*Sends your Message in an Embed & Pings the Mentioned Role*\n`{self.bot.prefix}prole <Mention Role> <Create Message>`", inline=False)
		embed_9.add_field(name="__**:clipboard: Hire Role Message:**__", value=f"*Sets Message for Hire Role*\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", inline=False)
		embed_9.add_field(name="__**:handshake: Hire:**__", value=f"*Sends Configured Message for Role to Mentioned Member*\n`{self.bot.prefix}hire <Mention Role> <Mention Member>`", inline=False)
		embed_9.add_field(name="__**:alien: Rolemenu:**__", value=f"*Rolemenu that Users React to get Corresponding Role*\n***(Up to 10 Roles)***\n`{self.bot.prefix}rolemenu <Menu Name> <Mention Role 1> <Mention Role 2>`", inline=False)
		embed_9.add_field(name="__**:scales:self.bot.prefix Poll:**__", value=f"*Creates Poll for Users to Vote On*\n***(Up to 10 Answers)***\n`{self.bot.prefix}poll <Poll Name> <Choice 1> <Choice 2>`", inline=False)
		embed_9.add_field(name="__**:tada: Giveaway:**__", value=f"*Starts Giveaway in Mentioned Channel for Specified Amount of Time with Specified Amount of Winners for the Specified Prize*\n**Days: d, Hours: h, Minutes: m, Seconds: s**\n***The Prize Description is Optional. You Must put Quotes Before & After 2 or More Word Prizes***\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", inline=False)
		embed_9.add_field(name="__**:confetti_ball: End Giveaway:**__", value=f"*Ends the Specified Giveaway*\n`{self.bot.prefix}gend <Giveaway Message ID>`", inline=False)
		embed_9.add_field(name="__**:arrows_counterclockwise: Reroll Giveaway:**__", value=f"*Rerolls the Specified Giveaway*\n`{self.bot.prefix}reroll <Giveaway Message ID> <Amount to Reroll>`", inline=False)
		embed_9.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_10 = discord.Embed(title=f"__***Auto-Moderation Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_10.add_field(name="__**:speaking_head: Auto-Mod (Bad Words):**__", value=f"*Turns On Bad Words Auto-Moderation for Channel*\n***(If On it will turn Off in Channel)***\n`{self.bot.prefix}bwords <Mention Channel>`", inline=False)
		embed_10.add_field(name="__**:paperclip: Auto-Mod (Invites):**__", value=f"*Turns On Discord Invite Auto-Moderation for Channel*\n***(If On it will turn Off in Channel)***\n`{self.bot.prefix}invites <Mention Channel>`", inline=False)
		embed_10.add_field(name="__**:link: Auto-Mod (Links):**__", value=f"*Turns On External Link Auto-Moderation for Channel*\n***(If On it will turn Off in Channel)***\n`{self.bot.prefix}links <Mention Channel>`", inline=False)
		embed_10.add_field(name="__**:no_pedestrians: Auto-Mod (Mentions):**__", value=f"*Turns On Spam Mention Auto-Moderation for Channel*\n***(If On it will turn Off in Channel)***\n`{self.bot.prefix}mentions <Mention Channel>`", inline=False)
		embed_10.add_field(name="__**:no_entry_sign: Auto-Mod (Caps):**__", value=f"*Turns On Excessive Caps Auto-Moderation for Channel*\n***(If On it will turn Off in Channel)***\n`{self.bot.prefix}caps <Mention Channel>`", inline=False)
		embed_10.add_field(name="__**:speech_balloon: Auto-Mod (Spam):**__", value=f"*Turns On Spam Text Auto-Moderation for Channel*\n***(If On it will turn Off in Channel)***\n`{self.bot.prefix}spam <Mention Channel>`", inline=False)
		embed_10.add_field(name="__**:alien: Auto-Role:**__", value=f"*Sets Role to Auto-Assign on Join*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}autorole <Mention Role>`", inline=False)
		embed_10.add_field(name="__**:notepad_spiral: Welcome Message:**__", value=f"*Sets Welcome Message*\n**(Mention Member: %mention, Member Username: %member, Server Name: %server)**\n***(If Enabled it will Disable)***\n`{self.bot.prefix}wmessage <Create Message>`", inline=False)
		embed_10.add_field(name="__**:e_mail: Welcome Direct Message:**__", value=f"*Sets Welcome Direct Message*\n**(Mention Member: %mention, Member Username: %member, Server Name: %server)**\n***(If Enabled it will Disable)***\n`{self.bot.prefix}dmessage <Create Message>`", inline=False)
		embed_10.add_field(name="__**:hand_splayed: Goodbye Message:**__", value=f"*Sets Goodbye Message*\n**(Mention Member: %mention, Member Username: %member, Server Name: %server)**\n***(If Enabled it will Disable)***\n`{self.bot.prefix}gmessage <Create Message>`", inline=False)
		embed_10.add_field(name="__**:pencil: Information Message & Channel:**__", value=f"*Sets the Channel & Information Message*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}info <Mention Channel> <Create Message>`", inline=False)
		embed_10.add_field(name="__**:newspaper: Information Limit Role:**__", value=f"*Sets Limit for Messages per 24 Hours for Mentioned Role in Information Channels*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}set <Amount of Message> <Mention Role>`", inline=False)
		embed_10.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_11 = discord.Embed(title=f"__***Configuration Commands***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_11.add_field(name="__**:gear: Prefix:**__", value=f"*Adds or Removes Prefix from Server's Prefixes.*\n`{self.bot.prefix}prefix <Create Prefix>`", inline=False)
		embed_11.add_field(name="__**:clipboard: Mod Log:**__", value=f"*Sets the Channel to Receive Moderation Actions Taken*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}log <Mention Channel>`", inline=False)
		embed_11.add_field(name="__**:hand_splayed: Join & Leave Log:**__", value=f"*Sets Channel to Receive Join & Leave Logs*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}welcome <Mention Channel>`", inline=False)
		embed_11.add_field(name="__**:chart_with_downwards_trend: Information Channel Logs:**__", value=f"*Sets the Channel to Receive Information Channel Advertisement Logs in*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}ilog <Mention Channel>`", inline=False)
		embed_11.add_field(name="__**:trophy: Level System Message:**__", value=f"*Enables Server Leveling System Mesages*\n***(If Enabled it will Disable Level Up Messages)***\n`{self.bot.prefix}levels`", inline=False)
		embed_11.add_field(name="__**:globe_with_meridians: Global Level System Message:**__", value=f"*Enables Global Leveling System Mesages*\n***(If Enabled it will Disable Level Up Messages)***\n`{self.bot.prefix}glevels`", inline=False)
		embed_11.add_field(name="__**:zipper_mouth: Muted Role:**__", value=f"*Sets Muted Role*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}muted <Mention Role>`", inline=False)
		embed_11.add_field(name="__**:alarm_clock: Phone Call Channel:**__", value=f"*Sets Channel to Receive Phone Calls in*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}psetup <Mention Channel>`", inline=False)
		embed_11.add_field(name="__**:arrows_counterclockwise: Reset:**__", value=f"*Resets Information Channel Limits for the Server.*\n`{self.bot.prefix}reset`", inline=False)
		embed_11.add_field(name="__**:arrows_clockwise: Member Reset:**__", value=f"*Resets Information Channel Limits for a Member in the Server.*\n`{self.bot.prefix}mreset <Mention Member>`", inline=False)
		embed_11.add_field(name="__**:leftwards_arrow_with_hook: Member Remove:**__", value=f"*Removes Specified Number of Posts from Information Channel Limit for a Member in the Server.*\n`{self.bot.prefix}mremove <Amount to Remove> <Mention Member>`", inline=False)
		embed_11.add_field(name=f"__**:apple: iOS Updates:**__", value=f"*Sets Channel to Receive iOS Updates in*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}iupdates <Mention Channel>`", inline=False)
		embed_11.add_field(name=f"__**:loudspeaker: {self.bot.user.name} Announcements:**__", value=f"*Sets Channel to Receive {self.bot.user.mention}'s Announcements in*\n***(If Enabled it will Disable)***\n`{self.bot.prefix}updates <Mention Channel>`", inline=False)
		embed_11.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		current_amount += 1

		embed_12 = discord.Embed(title=f"__***Commands for Support***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_12.add_field(name="__**:calling: Reply:**__", value=f"*Sends Support Replies threw {self.bot.user.name}'s DM's*\n`{self.bot.prefix}reply <Ticket ID> <Create Message>`", inline=False)
		embed_12.add_field(name="__**:ballot_box_with_check: Approve:**__", value=f"*Approves the Mentioned Vouch ID*\n`{self.bot.prefix}approve <Vouch ID>`", inline=False)
		embed_12.add_field(name="__**:no_entry_sign: Deny:**__", value=f"*Denies the Mentioned Vouch ID*\n`{self.bot.prefix}deny <Vouch ID>`", inline=False)
		embed_12.add_field(name="__**:robot: Auto-Bump:**__", value=f"*Enables Auto-Bump for Mentioned Server ID*\n`{self.bot.prefix}autobump <Server ID> <User ID>`", inline=False)
		embed_12.add_field(name="__**:satellite: Server List:**__", value=f"*Displays All Servers {self.bot.user.name} is Currently in*\n`{self.bot.prefix}servers`", inline=False)
		embed_12.add_field(name="__**:gem: Premium Servers:**__", value=f"*Displays All Premium Servers*\n`{self.bot.prefix}pservers`", inline=False)
		embed_12.add_field(name="__**:white_check_mark: Load:**__", value=f"*Loads a Cog for {self.bot.user.name}*\n`{self.bot.prefix}load <Mention Cog>`", inline=False)
		embed_12.add_field(name="__**:x: Unload:**__", value=f"*Unloads a Cog for {self.bot.user.name}*\n`{self.bot.prefix}unload <Mention Cog>`", inline=False)
		embed_12.add_field(name="__**:arrows_counterclockwise: Reload:**__", value=f"*Reloads a Cog for {self.bot.user.name}*\n`{self.bot.prefix}reload <Mention Cog>`", inline=False)
		embed_12.add_field(name="__**:repeat: Restart:**__", value=f"*Restarts {self.bot.user.name}'s Startup Cogs*\n`{self.bot.prefix}restart`", inline=False)
		embed_12.add_field(name="__**:hand_splayed: Logout:**__", value=f"*Logouts {self.bot.user.name}*\n`{self.bot.prefix}logout`", inline=False)
		embed_12.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

		collection = self.bot.db["AM_help"]
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				counter = x["Counter"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)

		if payload.message_id in helps:
			if not payload.user_id == author:
				return

			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = 13
				if payload.user_id in self.bot.owners:
					counter = 14
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if not payload.user_id in self.bot.owners:
				if counter > 13:
					counter = 13

			if payload.user_id in self.bot.owners:
				if counter > 14:
					counter = 14

			if counter == 1:
				await message.edit(embed=embed)

			if counter == 2:
				await message.edit(embed=embed_0)

			if counter == 3:
				await message.edit(embed=embed_1)

			if counter == 4:
				await message.edit(embed=embed_2)

			if counter == 5:
				await message.edit(embed=embed_3)

			if counter == 6:
				await message.edit(embed=embed_4)

			if counter == 7:
				await message.edit(embed=embed_5)

			if counter == 8:
				await message.edit(embed=embed_6)

			if counter == 9:
				await message.edit(embed=embed_7)

			if counter == 10:
				await message.edit(embed=embed_8)

			if counter == 11:
				await message.edit(embed=embed_9)

			if counter == 12:
				await message.edit(embed=embed_10)

			if counter == 13:
				await message.edit(embed=embed_11)

			if counter == 14:
				await message.edit(embed=embed_12)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})



		collection = self.bot.db["AM_rank"] # Paginate Leaderboards
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				warnings = x["Member_Count"]
				order = x["Order"]
				people = x["People"]
				levels = x["Levels"]
				try:
					world = x["Global"]
				except:
					world = 0
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)
		
		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages
			
			max_items = counter*10
			min_items = max_items-10
			place = 1
			if min_items >= 10:
				place = min_items+1
			order = ""
			for x in range(10):
				order += f"__**{place}:**__ **{people[min_items]}** *{levels[min_items]}*\n"
				min_items += 1
				place += 1
			if world == 0:
				embed = discord.Embed(title="__**Server Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=guild.icon_url_as(format=None, static_format="png"))
				embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			if world == 1:
				embed = discord.Embed(title="__**Global Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
				embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		collection = self.bot.db["AM_binfo"] # Paginate Bot Information
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				data = x["Data"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)
		
		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages

			info = data["topgg"]
			bio = info["bio"]
			desc = info["desc"]
			prefix = info["prefix"]
			lib = info["lib"]
			guilds = info["servers"]
			votes = info["votes"]
			total = info["tvotes"]
			ownerz = info["owners"]
			certified = info["certified"]
			support = info["support"]
			name = info["username"]
			logo = info["avatar"]
			param = info["param"]
			embed = discord.Embed(title="__**Top.gg Information**__", url=f"https://top.gg/bot/{param}", description=f"{bio}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.add_field(name=f"__**Description**__", value=f"{desc}", inline=False)
			embed.add_field(name=f"__**Misc**__", value=f"**Prefix:** {prefix}\n**Library:** {lib}\n**Servers:** {guilds}\n**Monthly Votes:** {votes}\n**Total Votes:** {total}\n**Certified:** {certified}\n**Owners:** {ownerz}\n{support}", inline=False)
			embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/264445053596991498/a_a8aec6ad1a286d0cfeae8845886dfe2a.gif")
			embed.set_author(name=f"{name}", icon_url=f"https://cdn.discordapp.com/avatars/{param}/{logo}.webp")
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))

			info = data["db"]
			bio = info["bio"]
			desc = info["desc"]
			prefix = info["prefix"]
			lib = info["lib"]
			guilds = info["servers"]
			ownerz = info["owners"]
			verified = info["verified"]
			support = info["support"]
			name = info["username"]
			logo = info["avatar"]
			param = info["param"]
			embed_0 = discord.Embed(title="__**Discord Bots Information**__", url=f"https://discord.bots.gg/bots/{param}", description=f"{bio}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_0.add_field(name=f"__**Description**__", value=f"{desc}", inline=False)
			embed_0.add_field(name=f"__**Misc**__", value=f"**Prefix:** {prefix}\n**Library:** {lib}\n**Servers:** {guilds}\n**Verified:** {verified}\n**Owners:** {ownerz}\n{support}", inline=False)
			embed_0.set_thumbnail(url=f"https://cdn.discordapp.com/icons/110373943822540800/a_280f68348c167703bec255e18184f7b0.gif")
			embed_0.set_author(name=f"{name}", icon_url=logo)
			embed_0.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))

			if counter == 1:
				await message.edit(embed=embed)

			if counter == 2:
				await message.edit(embed=embed_0)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		collection = self.bot.db["AM_votes"] # Paginate Votes
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				warnings = x["Member_Count"]
				order = x["Order"]
				people = x["People"]
				levels = x["Votes"]
				levels_2 = x["Lifetime"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)
		
		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages
			
			max_items = counter*10
			min_items = max_items-10
			place = 1
			if min_items >= 10:
				place = min_items+1
			order = ""
			for x in range(10):
				order += f"__**{place}:**__ **{people[min_items]}** *{levels[min_items]}*\n"
				min_items += 1
				place += 1
			embed = discord.Embed(title="__**Vote Leaderboard**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		collection = self.bot.db["AM_server_list"] # Paginate Server List
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				server_names = x["Server_Names"]
				servers = x["Servers"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)

		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages

			max_items = counter*10
			min_items = max_items-10

			place = 1
			if min_items >= 10:
				place = min_items+1
			
			embed = discord.Embed(title="__**Server List**__", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))

			for x in servers[min_items:max_items]:
				embed.add_field(name=f"__***{server_names[place-1]}***__", value=f"{x}", inline=False)
				place += 1

			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		collection = self.bot.db["AM_premium_servers"] # Paginate Premium Servers
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				server_names = x["Server_Names"]
				servers = x["Servers"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)

		if payload.message_id in helps:
			if not payload.user_id == author:
				return
			if str(payload.emoji) == "\U000023ea":
				counter = 1
				for x in message.reactions:
					if x.emoji == "\U000023ea":
						reaction = x

			if str(payload.emoji) == "\U000025c0":
				counter -= 1
				for x in message.reactions:
					if x.emoji == "\U000025c0":
						reaction = x

			if str(payload.emoji) == "\U000025b6":
				counter += 1
				for x in message.reactions:
					if x.emoji =="\U000025b6":
						reaction = x

			if str(payload.emoji) == "\U000023ed":
				counter = pages
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > pages:
				counter = pages

			max_items = counter*10
			min_items = max_items-10

			place = 1
			if min_items >= 10:
				place = min_items+1
			
			embed = discord.Embed(title="__**Premium Servers**__", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))

			for x in servers[min_items:max_items]:
				embed.add_field(name=f"__***{server_names[place-1]}***__", value=f"{x}", inline=False)
				place += 1

			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

def setup(bot):
	bot.add_cog(Everyone(bot))