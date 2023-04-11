import aiohttp
import asyncio
import discord
import psutil, pkg_resources, sys, platform
import pymongo, motor.motor_asyncio
import unicodedata
import pytz
import time
import zlib
import heapq
import io
import os
import lxml.etree as etree
from discord.ext import commands
from discord import app_commands
from difflib import SequenceMatcher
from Utils.API import do_rtfm, refresh_faq_cache, extract_matches
from datetime import datetime, timedelta
from pytz import timezone
from Utils.Helpers import server_stats
from Utils.Menus import Formatter, Pager



class Info(commands.Cog, app_commands.Group, name="info", description="Information & Lookup Commands"):
	def __init__(self, bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="server", description="Sends Stats of Current or Specified Server") # Server Stats Command
	@app_commands.describe(server="Server ID to Lookup Stats of")
	async def server(self, interaction:discord.Interaction, server:str=None):
		if not server is None:
			server = discord.utils.get(self.bot.guilds, id=int(server))
		if server is None:
			server = interaction.guild
		online, idle, offline, dnd = server_stats(server)
		bot_count = 0
		for b in server.members:
			if b.bot:
				bot_count += 1
		features = ""
		for f in server.features:
			features += f"{f}, "
		creation_date = server.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		if len(server.emojis) == 0:
			embed = discord.Embed(title=f"__**{server.name} Stats**__", description=f":crown: __**Owner:**__ {server.owner}\n:link: __**ID:**__ `{server.id}`\n:beginner: __**Shard:**__ {server.shard_id}\n:calendar: __**Created:**__ {create_date}" , timestamp=datetime.now(), color=0xac5ece)
			embed.add_field(name=f":busts_in_silhouette: Members[{len(server.members)}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`\n:robot: **Bots:** `{bot_count}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Categories:**__ `{len(server.categories)}`\n__**Channels:**__ `{len(server.channels)}`\n__**Roles:**__ `{len(server.roles)}`\n__**Features:**__ {features}\n__**Verification:**__ {server.verification_level}\n__**Content Filter:**__ {server.explicit_content_filter}", inline=False)
			embed.add_field(name=f":100: Emotes [{len(server.emojis)}]", value="None", inline=False)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
		if len(server.emojis) <= 10:
			embed = discord.Embed(title=f"__**{server.name} Stats**__", description=f":crown: __**Owner:**__ {server.owner}\n:link: __**ID:**__ `{server.id}`\n:beginner: __**Shard:**__ {server.shard_id}\n:calendar: __**Created:**__ {create_date}" , timestamp=datetime.now(), color=0xac5ece)
			embed.add_field(name=f":busts_in_silhouette: Members[{len(server.members)}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`\n:robot: **Bots:** `{bot_count}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Categories:**__ `{len(server.categories)}`\n__**Channels:**__ `{len(server.channels)}`\n__**Roles:**__ `{len(server.roles)}`\n__**Features:**__ {features}\n__**Verification:**__ {server.verification_level}\n__**Content Filter:**__ {server.explicit_content_filter}", inline=False)
			embed.add_field(name=f":100: Emotes [{len(server.emojis)}]", value=" ".join(map(lambda o: str(o), server.emojis)), inline=False)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
		if len(server.emojis) > 10:
			embed = discord.Embed(title=f"__**{server.name} Stats**__", description=f":crown: __**Owner:**__ {server.owner}\n:link: __**ID:**__ `{server.id}`\n:beginner: __**Shard:**__ {server.shard_id}\n:calendar: __**Created:**__ {create_date}" , timestamp=datetime.now(), color=0xac5ece)
			embed.add_field(name=f":busts_in_silhouette: Members[{len(server.members)}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`\n:robot: **Bots:** `{bot_count}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Categories:**__ `{len(server.categories)}`\n__**Channels:**__ `{len(server.channels)}`\n__**Roles:**__ `{len(server.roles)}`\n__**Features:**__ {features}\n__**Verification:**__ {server.verification_level}\n__**Content Filter:**__ {server.explicit_content_filter}", inline=False)
			embed.add_field(name=f":100: Emotes [{len(server.emojis)}]", value=f"{server.emojis[0]} {server.emojis[1]} {server.emojis[2]} {server.emojis[3]} {server.emojis[4]} {server.emojis[5]} {server.emojis[6]} {server.emojis[7]} {server.emojis[8]} {server.emojis[9]}", inline=False)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()

	@app_commands.command(name="member", description="Sends Information About You or Specified User") # User Information Command
	@app_commands.describe(member="User to Lookup Information on")
	async def member(self, interaction:discord.Interaction, *, member:discord.User=None):
		if member is None:
			member = interaction.user
		creation_date = member.created_at
		creation_datez = member.joined_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		azz = creation_datez.astimezone(timezone("US/Eastern"))
		correct_zonez = azz.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		create_datez = correct_zonez.strftime("%B %d, %Y %I:%M%p %Z")
		embed = discord.Embed(title="__***Member Information***__",timestamp=datetime.now(), color=0xac5ece)
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
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="channel", description="Sends Information About Current or Specified Channel") # Channel Information Command
	@app_commands.describe(channel="Channel Name or ID to Lookup Information on")
	async def channel(self, interaction:discord.Interaction, *, channel:discord.TextChannel=None):
		if channel is None:
			channel = interaction.channel
		creation_date = channel.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		embed_2 = discord.Embed(title="__**Channel Information**__", description=f":tv: __**Channel:**__ **{channel.mention}**\n:link: __**Channel ID:**__ `{channel.id}`\n:globe_with_meridians: __**Server:**__ `{channel.guild.name}`\n:link: __**Server ID:**__ `{channel.guild.id}`\n:card_box: __**Category:**__ {channel.category}\n:thought_balloon: __**Topic:**__ {channel.topic}\n:calendar: __**Created:**__ {create_date}", timestamp=datetime.now(), color=0xac5ece)
		embed_2.add_field(name=f":busts_in_silhouette: Members[{len(channel.members)}]", value=", ".join(map(lambda o: str(o), channel.members[0:49])), inline=False)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="role", description="Sends Information About Specified Role") # Role Information Command
	@app_commands.describe(role="Role Name or ID to Lookup Information on")
	async def role(self, interaction:discord.Interaction, *, role:discord.Role):
		if role is None:
			embed = discord.Embed(title="__**Role Information Error**__", description=f"You must mention the Role ID you want to see information about.\n`{self.bot.prefix}rinfo <Role ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		creation_date = role.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		permz = ""
		for z in role.permissions:
			if z[1] is True:
				permz += f"{z[0]}, "
		if len(role.members) == 0:
			embed_2 = discord.Embed(title="__**Role Information**__", description=f":pencil: __**Role:**__ `{role}`\n:link: __**Role ID:**__ `{role.id}`\n:satellite: __**Server:**__ `{role.guild}`\n:link: __**Server ID:**__ `{role.guild.id}`\n:art: __**Color:**__ {role.colour}\n:bell: __**Mentionable:**__ {role.mentionable}\n:calendar: __**Created:**__ {create_date}", timestamp=datetime.now(), color=0xac5ece)
			embed_2.add_field(name=f":lock: __**Permissions**__", value=f"{permz}", inline=False)
			embed_2.add_field(name=":busts_in_silhouette: __**Members[0]**__", value="None", inline=False)
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
		if len(role.members) >= 1:
			embed_2 = discord.Embed(title="__**Role Information**__", description=f":pencil: __**Role:**__ `{role}`\n:link: __**Role ID:**__ `{role.id}`\n:satellite: __**Server:**__ `{role.guild}`\n:link: __**Server ID:**__ `{role.guild.id}`\n:art: __**Color:**__ {role.colour}\n:bell: __**Mentionable:**__ {role.mentionable}\n:calendar: __**Created:**__ {create_date}", timestamp=datetime.now(), color=0xac5ece)
			embed_2.add_field(name=f":lock: __**Permissions**__", value=f"{permz}", inline=False)
			embed_2.add_field(name=f":busts_in_silhouette: __**Members[{len(role.members)}]**__", value=", ".join(map(lambda o: str(o), role.members[0:49])), inline=False)
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()

	@app_commands.command(name="emoji", description="Lookup Unicode of Specified Emoji") # Emoji Unicode Command
	@app_commands.describe(characters="Emoji or Characters to Lookup Unicode of")
	async def emoji(self, interaction:discord.Interaction, *, characters:str):
		def to_string(c):
			digit = f'{ord(c):x}'
			name = unicodedata.name(c, 'Name Not Found')
			return f'[\\U{digit:>08}](<http://www.fileformat.info/info/unicode/char/{digit}>): **{name}** | {c}'
		msg = '\n'.join(map(to_string, characters))
		if len(msg) > 2000:
			embed = discord.Embed(title="__**Unicode Error**__", description=f"The ouput of this is too long to display..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		embed = discord.Embed(title=f"__**Emoji Unicode**__", description=f"{msg}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="bot", description="Shows Bot Listing Information on Specified Bot") # Bot Listing Information Command
	@app_commands.describe(bot="Bot ID to Request Information on")
	async def bot(self, interaction:discord.Interaction, bot:str):
		
		TOPGG_Token = self.bot.topgg_token
		embeds = []
		count = 0
		header = {"Authorization":TOPGG_Token}
		async with self.bot.session.get(f"https://top.gg/api/bots/{bot}", headers=header) as url:
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
				count += 1
				embed = discord.Embed(title="__**Top.gg Information**__", url=f"https://top.gg/bot/{bot}", description=f"{bio}", timestamp=datetime.now(), color=0xac5ece)
				embed.add_field(name=f"__**Description**__", value=f"{desc}", inline=False)
				embed.add_field(name=f"__**Misc**__", value=f"**Prefix:** {prefix}\n**Library:** {lib}\n**Servers:** {guilds}\n**Monthly Votes:** {votes}\n**Total Votes:** {total}\n**Certified:** {certified}\n**Owners:** {owners}\n{support}", inline=False)
				embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/264445053596991498/a_a8aec6ad1a286d0cfeae8845886dfe2a.gif")
				embed.set_author(name=f"{name}", icon_url=f"https://cdn.discordapp.com/avatars/{bot}/{logo}.webp")
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)			

		async with self.bot.session.get(f"https://discord.bots.gg/api/v1/bots/{bot}") as url:
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
				count += 1
				embed = discord.Embed(title="__**Discord Bots Information**__", url=f"https://discord.bots.gg/bots/{bot}", description=f"{bio}", timestamp=datetime.now(), color=0xac5ece)
				embed.add_field(name=f"__**Description**__", value=f"{desc}", inline=False)
				embed.add_field(name=f"__**Misc**__", value=f"**Prefix:** {prefix}\n**Library:** {lib}\n**Servers:** {guilds}\n**Verified:** {verified}\n**Owners:** {owners}\n{support}", inline=False)
				embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/110373943822540800/a_280f68348c167703bec255e18184f7b0.gif")
				embed.set_author(name=f"{name}", icon_url=logo)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)

		if count == 0:
			embed = discord.Embed(title="__**Information Error**__", description=f"There was no Bots with the ID `{bot}` found on Top.gg or Discord Bots..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		formatter = Formatter([i for i in embeds], per_page=10)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="stats", description="Shows Detailed Information About Me") # Bot Information Command
	async def stats(self, interaction:discord.Interaction):
		current_os = f"{platform.system()} {platform.release()} ({platform.version()})"
		dpy = pkg_resources.get_distribution("discord.py").version
		embed = discord.Embed(title=f"__**{self.bot.user.name} Information**__", description=f":satellite: __**Servers:**__ {len(self.bot.guilds)}\n:busts_in_silhouette: __**Members:**__ {len(self.bot.users)}\n:ping_pong: __**Ping:**__ **{int(self.bot.latency*1000)}** *ms*\n:bar_chart: __**RAM Usage:**__ {int(psutil.virtual_memory()[2])}% ({round(psutil.virtual_memory()[3]*10**-9, 2)}/{round(psutil.virtual_memory()[0]*10**-9, 2)} *GB*)\n:microscope: __**CPU Usage:**__ {int(psutil.cpu_percent())}%\n:globe_with_meridians: __**Host OS:**__ {current_os}\n:electric_plug: __**Library:**__ discord.py {dpy}\n:snake: __**Language:**__ Python {sys.version[0:6]}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="votes", description="Shows Your or Mentioned Member's Votes") # Check Votes Command
	@app_commands.describe(user="User to Check Votes of")
	async def votes(self, interaction:discord.Interaction, user:discord.User=None):
		
		if user is None:
			user = interaction.user
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
			if z["Member"] == user.id:
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
			if z["Member"] == user.id:
				db_votes = db_top
				db_life = db_ltop
				db_pos += db_counter

		if pos == 0:
			pos = "N/A"
		if db_pos == 0:
			db_pos = "N/A"

		embed = discord.Embed(title="__**Votes**__", description=f"__**Top.gg**__\n**Total Votes:** `{votes}`\n**Rank:** `{pos}`\n[Vote Now](<https://top.gg/bot/{self.bot.user.id}/vote>)\n__**Discord Bot List**__\n**Total Votes:** `{db_votes}`\n**Rank:** `{db_pos}`\n[Vote Now](<https://discordbotlist.com/bots/{self.bot.user.name.lower()}-{self.bot.user.discriminator}/upvote>)", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if not user.id == interaction.user.id:
			embed.set_author(name=f"{user}", icon_url=str(user.display_avatar.replace(format="png", static_format="png")))
		await interaction.followup.send(embed=embed)

	@app_commands.command(name="uptime", description=f"Shows Current Uptime (Time Online)") # Uptime Command
	async def uptime(self, interaction:discord.Interaction):
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
		embed = discord.Embed(title="__**Uptime**__", description=f"**{self.bot.user.mention}** has been Online for {uptime_stamp}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="ping", description="Shows Current Latency") # Ping Command (Latency)
	async def ping(self, interaction:discord.Interaction):
		latency_check = 'Still Determining..'
		start = time.perf_counter()
		embed = discord.Embed(title=f"__**{self.bot.user.name}'s Latency**__", description=f"**{int(self.bot.latency*1000)}** *ms*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		message = await interaction.followup.send(embed=embed)
		end = time.perf_counter()
		latency_check = int((end-start)*1000)
		embed = discord.Embed(title=f"__**{self.bot.user.name}'s Latency**__", description=f"**WebSocket Latency**: `{int(self.bot.latency*1000)}` *ms*\n**Message Latency**: `{latency_check}` *ms*", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await message.edit(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="refer_to_docs", description="Search discord.py or Python Documentation")
	@app_commands.describe(lib="Library to Search on", obj="Documentation Objects to Search for")
	async def refer_to_docs(self, interaction, lib:str=None, *, obj:str):
		if lib is None:
			lib = 'stable'
		if lib == 'py' or lib == 'python':
			await do_rtfm(self, interaction, 'python', obj)
			return
		if lib == 'latest' or lib == '2.0':
			await do_rtfm(self, interaction, 'latest', obj)
			return
		if lib == 'd.py' or lib == 'stable' or lib == 'discord.py':
			await do_rtfm(self, interaction, 'stable', obj)
			return

	@app_commands.command(name="dpy_faq", description="Search discord.py for Frequently Asked Questions")
	@app_commands.describe(query="Question or Words/Phrase to Search for")
	async def dpy_faq(self, interaction, *, query:str):
		if not hasattr(self, 'faq_entries'):
			await refresh_faq_cache(self)
		if query is None:
			e = discord.Embed(title="__**Discord.py FAQ Lookup**__", description=f'[Click to View Discord.py FAQs](<https://discordpy.readthedocs.io/en/latest/faq.html>)\nYou may also search for a FAQ.\n`{self.bot.prefix}faq <Question>`', colour=discord.Colour.blurple(),  timestamp=datetime.now(), color=0xac5ece)
			e.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=e)
			#await ctx.message.delete()
			return
		matches = extract_matches(query, self.faq_entries(), scorer=partial_ratio, score_cutoff=40)
		if len(matches) == 0:
			return await interaction.followup.send('Nothing found...')
		e = discord.Embed(title="__**Discord.py FAQ Lookup**__", colour=discord.Colour.blurple(),  timestamp=datetime.now(), color=0xac5ece)
		e.description = '\n'.join(f'[**{key}**]({value})' for key, _, value in matches)
		e.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=e)
		#await ctx.message.delete()

	ios = app_commands.Group(name="ios", description="Apple & iOS Commands")

	@ios.command(name="versions", description="Display All Current Signed iOS Versions") # Signed Versions Command
	@app_commands.describe(device="Device to Lookup iOS Versions for")
	async def versions(self, interaction:discord.Interaction, *, device:str=None):
		
		async with self.bot.session.get("https://api.ipsw.me/v2.1/firmwares.json/condensed") as url:
			data = await url.json()
			devices = data['devices']
			itunes = data['iTunes']
			signed = 0
			embeds = []
			build_ids = []
			builds = {}

			for z in devices:
				versions = []
				ids = []
				sizes = []
				dates = []
				urls = []
				name = devices[f'{z}']['name']
				firmwares = devices[f'{z}']['firmwares']
				regex = [f"{device}"]
				if device is None:
					regex = ["iPhone", "iPad", "iPod"]
				regex_2 = ["China", "Global", "WiFi"]
				
				counter = 0
				if any(x.lower() in name.lower() for x in regex):
					if not any(x.lower() in name.lower() for x in regex_2):
						for x in firmwares:
							if x['signed'] is True:
								versions += {x['version']}
								ids += {x['buildid']}
								org = x['size']
								size = org*10**-9
								show = f"{size:.2f} GB"
								if int(size) < 1:
									size = org*10**-6
									show = f"{size:.2f} MB"
								sizes += {show}
								try:
									grab = x['releasedate']
								except:
									grab = x['uploaddate']
								fix = datetime.strptime(grab, "%Y-%m-%dT%H:%M:%SZ")
								date = fix.strftime("%B %d, %Y %I:%M%p %Z")
								dates += {date}
								urls += {x['url']}
						embed = discord.Embed(title=f"**{name}**", timestamp=datetime.now(), color=0xac5ece)
						embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
						for x in versions:
							if not "iPad".lower() in name.lower():
								embed.add_field(name=f"__**iOS Version {versions[counter]}**__", value=f"**Build ID:** [{ids[counter]}]({urls[counter]})\n**Size:** {sizes[counter]}\n**Release Date:** {dates[counter]}", inline=False)
							if "iPad".lower() in name.lower():
								embed.add_field(name=f"__**iPadOS Version {versions[counter]}**__", value=f"**Build ID:** [{ids[counter]}]({urls[counter]})\n**Size:** {sizes[counter]}\n**Release Date:** {dates[counter]}", inline=False)
							counter += 1
						if not versions == []:
							signed += 1
							embeds.append(embed)
			if signed == 0:
				embed = discord.Embed(title="__**iOS Updates Error**__", description=f"No Results with the Keyword `{device}`..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		
		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@ios.command(name="tweak", description="Display Information About Specified iOS Tweak") # Tweak Lookup Command
	@app_commands.describe(tweak="Tweak to Lookup")
	async def tweak(self, interaction:discord.Interaction, *, tweak:str):
		
		async with self.bot.session.get(f"https://api.parcility.co/db/search?q={tweak}") as url:
			data = await url.json()
			results = []
			counter = 0
			if int(data['code']) != 200:
				embed = discord.Embed(title="__**Tweak Lookup Error**__", description=f"No Results with the Keyword `{tweak}`..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			for x in data['data']:
				tweak = x['normalizedName']
				icon = x['Icon']
				desc = x['Description']
				try:
					link = x['Depiction']
				except:
					link = "N/A"
				author = x['Author']
				maintainer = x['Maintainer']
				version = x['Version']
				build_id = x['Package']
				section = x['Section']
				try:
					req = x['Depends']
				except:
					req = "N/A"
				b = x['builds'][len(x['builds'])-1]
				r = x['repo']
				repo = r['label']
				repo_link = r['url']
				repo_icon = r['icon']
				if not repo_link.endswith('/'):
					repo_link+"/"
				download = repo_link+b['Filename']
				org = int(b['Size'])
				size = org*10**-9
				show = f"{size:.2f} GB"
				if int(size) < 1:
					size = org*10**-6
					show = f"{size:.2f} MB"
				if int(size) < 1:
					size = org/1000
					show = f"{size:.2f} KB"

				embed = discord.Embed(title=f"", description=f"**{tweak}**\n{desc}", timestamp=datetime.now(), color=0xac5ece)
				if not link == "N/A":
					embed = discord.Embed(title=f"", description=f"**[{tweak}](<{link}>)**\n{desc}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embed.set_author(name=f"{repo}", icon_url=repo_icon)
				if not icon.startswith('file'):
					embed.set_thumbnail(url=icon)
				embed.add_field(name=f"__**Author**__", value=f"*{author}*", inline=False)
				embed.add_field(name=f"__**Maintainer**__", value=f"*{maintainer}*", inline=False)
				embed.add_field(name=f"__**Version**__", value=f"*{version}*", inline=False)
				embed.add_field(name=f"__**Size**__", value=f"*{show}*", inline=False)
				embed.add_field(name=f"__**Bundle ID**__", value=f"*{build_id}*", inline=False)
				embed.add_field(name=f"__**Section**__", value=f"*{section}*", inline=False)
				embed.add_field(name=f"__**Requirements**__", value=f"*{req}*", inline=False)
				embed.add_field(name=f"__**Download**__", value=f"*[Click Here to Download](<{download}>)*", inline=False)
				results.append(embed)

		formatter = Formatter([i for i in results], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@ios.command(name="updates", description="Set Channel to Receive iOS Version Updates in") # Set iOS Updates Channel
	@app_commands.describe(channel="Channel to Receive Updates in")
	@app_commands.checks.has_permissions(administrator=True)
	async def updates(self, interaction:discord.Interaction, *, channel:discord.TextChannel):
		collection = self.bot.db["Config_iOS_channel"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will no longer be sent to {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**iOS Updates**__", description=f"iOS Update Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@updates.error
	async def updates_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	pogo = app_commands.Group(name="pogo", description="Pokemon Go Commands")

	@pogo.command(name="events", description="Display All Current Pokemon Go Events") # PoGo Event Checker Command
	async def events(self, interaction:discord.Interaction):
		
		to_paginate = []
		async with self.bot.session.get("https://raw.githubusercontent.com/ccev/pogoinfo/v2/active/events.json") as url:
			page = await url.read()
			data = json.loads(page)
			for x in data:
				name = x['name']
				typing = x['type']
				start = x['start']
				try:
					start = datetime.strptime(start, "%Y-%m-%d %H:%M")
					start = start.strftime("%B %d, %Y %H:%M")
				except:
					pass
				end = x['end']
				try:
					end = datetime.strptime(end, "%Y-%m-%d %H:%M")
					end = end.strftime("%B %d, %Y %H:%M")
				except:
					pass
				spawns = x['spawns']
				eggs = x['eggs']
				raids = x['raids']
				shinies = x['shinies']
				bonuses = x['bonuses']
				features = x['features']
				has_quests = x['has_quests']
				has_spawnpoints = x['has_spawnpoints']

				order = f"__**{name}**__\n`{start}` - `{end}`\n\n"

				if not spawns == []:
					mons = "**Pokemon Spawns**\n"
					for x in spawns:
						mon_id = x['id']
						mon_name = x['template']
						try:
							mon_form = x['form']
						except:
							pass
						mons += f"{mon_name} ({mon_id})\n"
					order += f"{mons}\n"

				if not eggs == []:
					egg_mons = "**Egg Spawns**\n"
					for x in eggs:
						mon_id = x['id']
						mon_name = x['template']
						try:
							mon_form = x['form']
						except:
							pass
						egg_mons += f"{mon_name} ({mon_id})\n"
					order += f"{egg_mons}\n"

				if not raids == []:
					event_raids = "**Raids**\n"
					for x in raids:
						mon_id = x['id']
						mon_name = x['template']
						try:
							mon_form = x['form']
						except:
							pass
						event_raids += f"{mon_name} ({mon_id})\n"
					order += f"{event_raids}\n"

				if not shinies == []:
					shiny_mons = "**Shinies**\n"
					for x in shinies:
						mon_id = x['id']
						mon_name = x['template']
						try:
							mon_form = x['form']
						except:
							pass
						shiny_mons += f"{mon_name} ({mon_id})\n"
					order += f"{shiny_mons}\n"

				if not bonuses == []:
					bonus = "**Bonuses**\n"
					counter = 1
					for x in bonuses:
						bonus_info = x['text']
						bonus += f"**{counter})** {bonus_info}"
						#try:
						#	bonus_type = x['template']
						#	bonus += f"\n{bonus_type}"
						#	try:
						#		bonus_amount = x['value']
						#		bonus += f" ({bonus_amount})"
						#	except:
						#		pass
						#except:
						#	pass
						bonus += f"\n"
						counter += 1
					order += f"{bonus}\n"

				if not features == []:
					event_features = "**Features**\n"
					for x in features:
						event_features += f"{x}\n"
					order += f"{event_features}\n"

				order += f"**Quests:** {has_quests}\n**Added Spawnpoints:** {has_spawnpoints}\n\n\n"

				embed = discord.Embed(title="__**PoGo Events**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))

				to_paginate.append(embed)

		formatter = Formatter([i for i in to_paginate], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()
		
	@pogo.command(name="updates", description="Set Channel to Receive Pokemon Go News and Updates in") # Set PoGo Event Updates Channel
	@app_commands.describe(channel="Channel to Receive Events in")
	@app_commands.checks.has_permissions(administrator=True)
	async def updates(self, interaction:discord.Interaction, *, channel: discord.TextChannel):
		collection = self.bot.db["Config_pogo_channel"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**PoGo Events**__", description=f"PoGo Event Logs will be sent to {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**PoGo Events**__", description=f"PoGo Event Logs will now be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
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
		embed_2 = discord.Embed(title="__**PoGo Events**__", description=f"PoGo Event Logs will no longer be sent to {old_channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**PoGo Events**__", description=f"PoGo Event Logs will no longer be sent to this channel.", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@updates.error
	async def updates_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	server_sub = app_commands.Group(name="server_subscription", description="Server Subscription Commands")

	@server_sub.command(name="account", description="Shows Information About Current Server's Subscription Account") # Server Account Information Command
	@app_commands.describe(member="Member to View Server Subscription of")
	async def account(self, interaction:discord.Interaction, member:discord.Member=None):
		if member is None:
			member = interaction.user
		email = None
		collection = self.bot.db["Config_server_subs"]
		async for m in collection.find({"guild": interaction.guild.id, "user": member.id}, {"_id": 0}):
			email = m["email"]
		if email is None:
			embed = discord.Embed(title="__**Account Error**__", description=f"There is no {interaction.guild.name} Account Linked to {member.mention}'s Discord Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		endpoint = None
		collection = self.bot.db["Config_server_endpoints"]
		grab_endpoint = collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_endpoint:
			endpoint = x["Endpoint"]
		if endpoint is None:
			embed = discord.Embed(title="__**Account Error**__", description=f"{interaction.guild.name} must first setup the Server's Subscriber Endpoint..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		endpoint = endpoint.replace(f"%EMAIL", f"{email}")
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
			except:
				pass
			if access is None:
				try:
					access = data['data']['subscriber']
					order += f"**Status**: *{access}*\n"
				except:
					pass
		if access is None:
			embed = discord.Embed(title="__**Account Error**__", description=f"No Account Found for *{email}*..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		embed = discord.Embed(title=f"__**{interaction.guild.name} Account Information**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
		if interaction.user.id != member.id:
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@server_sub.command(name="link", description="Links Your Server Subscription Account to Your Discord Account") # Link Server Account Command
	@app_commands.describe(email="Server Subscription Email Address to Link")
	async def link(self, interaction:discord.Interaction, *, email:str):
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
		async for m in collection.find({"guild": interaction.guild.id, "user": interaction.user.id}, {"_id": 0}):
			member = m["user"]
		async for m in collection.find({"guild": interaction.guild.id, "email": email}, {"_id": 0}):
			email_check = m["email"]
		if not member is None:
			embed = discord.Embed(title="__**Link Error**__", description=f"Your Discord account is already linked to a {interaction.guild.name} account", timestamp=datetime.now(), color=0xff0000)
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
		log ["user"] = interaction.user.id
		log ["email"] = email
		log ["access"] = access
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Account Linked**__", description=f"*You have successfully linked* `{email}` *to your Discord account*\n{order}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		confirmation = await interaction.followup.send(embed=embed)
		embed = discord.Embed(title="__**Account Linked**__", description=f"**User**: {interaction.user.mention}\n**Email**: *{email}*\n{order}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if mod_log is None:
			#await ctx.message.delete()
			return	
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
		await asyncio.sleep(5)
		await confirmation.delete()

async def setup(bot):
	await bot.add_cog(Info(bot))