import discord
import asyncio
import asyncpraw
import json
import pymongo, motor.motor_asyncio
import random
import re
import io, os, traceback
import async_cse
import googletrans
import youtube_dl, ffmpeg
from akinator.async_aki import Akinator
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from Utils.Helpers import convert_seconds, create_random_string, create_random_digits
from Utils.GFX import make_rank_card, create_captcha, create_ascii_art
from Utils.Fun import play_aki
from Utils.Menus import Formatter, Pager

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

Reddit_Client_ID = config['Reddit_Client_ID']
Reddit_Client_Secret = config['Reddit_Client_Secret']
Reddit_Username = config['Reddit_Username']
Reddit_Password = config['Reddit_Password']
Reddit_User_Agent = config['Reddit_User_Agent']

async def create_ytdl_client(formating=None, merge=None):
	if formating is None:
		formating = 'bestvideo+bestaudio/best'
	if merge is None:
		ytdl_format_options = {
			'format': formating,
			'outtmpl': 'public/tmp/%(extractor)s-%(id)s-%(title)s-%(format_id)s.%(ext)s',
			'restrictfilenames': True,
			'noplaylist': True,
			'nocheckcertificate': True,
			'ignoreerrors': False,
			'logtostderr': False,
			'quiet': True,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'}
	if not merge is None:
		ytdl_format_options = {
			'format': formating,
			'merge-output-format': merge,
			'outtmpl': 'public/tmp/%(extractor)s-%(id)s-%(title)s-%(format_id)s.%(ext)s',
			'restrictfilenames': True,
			'noplaylist': True,
			'nocheckcertificate': True,
			'ignoreerrors': False,
			'logtostderr': False,
			'quiet': True,
			'no_warnings': True,
			'default_search': 'auto',
			'source_address': '0.0.0.0'}

	ffmpeg_options = {'options': '-vn'}
	ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
	return ytdl



class Everyone(commands.Cog, name="Everyone"):
	def __init__(self,bot):
		self.bot = bot
		self.bot.aki = Akinator()
		self.bot.playing_aki = []
		self.reddit = asyncpraw.Reddit(client_id=Reddit_Client_ID, client_secret=Reddit_Client_Secret, password=Reddit_Password, user_agent=Reddit_User_Agent, username=Reddit_Username)
		self.google = async_cse.Search(self.bot.google_keys)
		self.trans = googletrans.Translator()
	async def cog_unload(self):
		await self.google.close()
	def cleanup_definition(self, definition, *, regex=re.compile(r'(\[(.+?)\])')):
		def repl(m):
			word = m.group(2)
			return f'[{word}](http://{word.replace(" ", "-")}.urbanup.com)'
		ret = regex.sub(repl, definition)
		if len(ret) >= 2048:
			return ret[0:2000] + ' [...]'
		return ret
	
	@app_commands.command(name="akinator", description="Starts an Akinator Match") # Akinator Command
	async def akinator(self, interaction:discord.Interaction):
		start_aki = await play_aki(self=self, interaction=interaction)
		#await ctx.message.delete()

	@app_commands.command(name="ascii_art", description="Create ASCII Art of Avatar or Attached Photo") # ASCII Art Command
	@app_commands.describe(scale="Scale of ASCII Art", gray_scale="Gray Scale of ASCII Art", width_correction="Width Correction of ASCII Art", if_file="Used as Width Correction if Specifying Member")
	async def ascii_art(self, interaction:discord.Interaction, scale:float=.1, gray_scale:float=.1, width_correction:float=7/4, if_file:float=None):
		
		try:
			file = interaction.message.attachments[0]
		except:
			file = interaction.user.display_avatar.url
		if scale == discord.Member:
			file = scale.display_avatar.url
			scale = gray_scale
			if not width_correction == 7/4:
				gray_scale = width_correction
				width_correction = if_file
		if isinstance(scale, str):
			if "http" in scale or "https" in scale:
				file = scale
				scale = gray_scale
				if not width_correction == 7/4:
					gray_scale = width_correction
					width_correction = if_file

		result = await create_ascii_art(file, scale, gray_scale, width_correction)
		data = result.replace("#", "-")
		data = data.replace("&", "_")
		data = data.replace("\n", "k")
		data = data.replace(" ", "l")
		post_url = f"https://paste.krypto.industries/documents"
		async with self.bot.session.post(post_url, data=result) as response:
			response_json = await response.json()
		paste_link = f"https://paste.krypto.industries/{response_json['key']}"

		#if len(data) >= 4000:
			#embed = discord.Embed(title="__**ASCII Art Error**__", description=f"The output is too large.. try a smaller scale?", timestamp=datetime.now(), color=0xff0000)
			#embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			#await interaction.followup.send(embed=embed)
			##await ctx.message.delete()	
			#return
			
		embed = discord.Embed(title="__**ASCII Art**__", description=f"{paste_link}", timestamp=datetime.now(), color=0xac5ece)
		#embed.set_image(url=file)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="rank_server", description="Shows Your or Mentioned Member's Rank in Current Server") # Guild Rank Command
	@app_commands.describe(member="Member to Check Rank of")
	async def rank_server(self, interaction:discord.Interaction, *, member:discord.Member=None):
		
		collection_2 = self.bot.db["AM_guild_levels"]
		counter = 0
		if member is None:
			member = interaction.user
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			current_member = m["Member"]
			exp = m["EXP"]
			lvl = m["Level"]
			counter += 1
			if current_member == member.id:
				card = await make_rank_card(exp=exp, lvl=lvl, rank=counter, member=member)
				embed = discord.Embed(title="__**Server Rank**__", description=f":trophy: __**Rank:**__ {counter}  :space_invader: __**Level:**__ {lvl}\n:bar_chart: __**Expierence:**__ {exp} / {(lvl+1)**4}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				if not member.id == interaction.user.id:
					embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_image(url=f"attachment://{card.filename}")
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed, file=card)
				#await ctx.message.delete()

	@app_commands.command(name="rank_global", description="Shows Your or Mentioned Member's Global Rank") # Global Rank Command
	@app_commands.describe(member="Member to Check Rank of")
	async def rank_global(self, interaction:discord.Interaction, *, member:discord.Member=None):
		
		collection_2 = self.bot.db["AM_levels"]
		counter = 0
		if member is None:
			member = interaction.user
		async for m in collection_2.find({}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			current_member = m["Member"]
			exp = m["EXP"]
			lvl = m["Level"]
			counter += 1
			if current_member == member.id:
				card = await make_rank_card(exp=exp, lvl=lvl, rank=counter, member=member, global_rank=True)
				embed = discord.Embed(title="__**Global Rank**__", description=f":trophy: __**Rank:**__ {counter}  :space_invader: __**Level:**__ {lvl}\n:bar_chart: __**Expierence:**__ {exp} / {(lvl+1)**4}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
				if not member.id == interaction.user.id:
					embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_image(url=f"attachment://{card.filename}")
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed, file=card)
				#await ctx.message.delete()

	@app_commands.command(name="captcha_test", description="Sends Visual or Audio CAPTCHA Test") # CAPTCHA Command
	@app_commands.describe(audio="Can be 'audio, num, number' to Obtain Number Test")
	async def captcha_test(self, interaction:discord.Interaction, audio:str=None):
		def check(m):
			if m.author.id == interaction.user.id and m.channel.id == interaction.channel.id:
				return m
		
		param = create_random_string(length=7)
		if audio == "num" or audio == "number" or audio == "audio":
			param = create_random_digits(length=7)
		files = await create_captcha(param=param)

		embed = discord.Embed(title="__**CAPTCHA**__", description=f"", timestamp=datetime.now(), color=0xac5ece)
		if len(files) >= 2:
			embed = discord.Embed(title="__**CAPTCHA**__", description=f"", timestamp=datetime.now(), color=0xac5ece)
		embed.set_image(url="attachment://CAPTCHA.png")
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		msg = await interaction.followup.send(embed=embed, files=files)
		answer = await self.bot.wait_for('message', check=check)
		if answer.content.lower() == param or answer.content.lower() == param:
			await msg.add_reaction("\U00002705")
		if answer.content.lower() != param and answer.content.lower() != param:
			await msg.add_reaction("\U0000274c")
		#await ctx.message.delete()

	@app_commands.command(name="leaderboard_server", description="Shows Current Server's or Mentioned Server's Server Leaderboard") # Server Leaderboard Command
	@app_commands.describe(server="Server to Check Leaderboard of")
	async def leaderboard_server(self, interaction:discord.Interaction, server:str=None):
		
		if isinstance(server, str):
			server = discord.utils.get(self.bot.guilds, id=int(server))
		if server is None:
			server = interaction.guild
		collection_2 = self.bot.db["AM_guild_levels"]
		orders = []
		people = []
		levels = []
		counter = 1
		limit = 0
		async for m in collection_2.find({"Guild": server.id}, {"_id": 0}).sort("EXP", pymongo.DESCENDING):
			if limit < 500:
				people += {m["Member_Name"]}
				levels += {m["Level"]}
			limit += 1
			if limit > 500:
				break

		for x in range(len(people)):
			orders.append(f"__**{counter}:**__ ***{people[x]}:*** *{levels[x]}*\n")
			counter += 1

		formatter = Formatter([i for i in orders], per_page=10)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="leaderboard_global", description="Shows Global Leaderboard") # Global Leaderboard Command
	async def leaderboard_global(self, interaction:discord.Interaction):
		
		collection_2 = self.bot.db["AM_levels"]
		orders = []
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
			orders.append(f"__**{counter}:**__ ***{people[x]}:*** *{levels[x]}*\n")
			counter += 1

		formatter = Formatter([i for i in orders], per_page=10)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="leaderboard_votes", description="Shows Vote Leaderboard") # Vote Leaderboard Command
	async def leaderboard_votes(self, interaction:discord.Interaction):
		
		collection = self.bot.db["Eco_total_votes"]
		orders = []
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
			orders.append(f"__**{counter}:**__ ***{people[x]}:*** *{levels[x]}*\n")
			counter += 1

		formatter = Formatter([i for i in orders], per_page=10)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="google", description="Searches Google for Your Query") # Google Search Command
	@app_commands.describe(query="Query/Phrase to Search for")
	async def google(self, interaction:discord.Interaction, *, query:str):
		results = await self.google.search(f"{query}", safesearch=False)
		embeds = []
		order = ""
		result_count = 0
		for result in results:
			title = result.title
			desc = result.description
			url = result.url
			order += f"[{title}](<{url}>)\n*{desc}*\n\n"
			result_count += 1
			if result_count == 10:
				embed = discord.Embed(title="__**Google Search**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_author(name=f"{query}")
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)
				result_count = 0
		if result_count > 0 and result_count < 10:
			embed = discord.Embed(title="__**Google Search**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_author(name=f"{query}")
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)

		await interaction.followup.send(embed=embeds[0])

	@app_commands.command(name="screenshot", description="Sends Screenshot of the Mentioned Website") # Screenshot Site Command
	@app_commands.describe(site="Website to Take Screenshot of")
	async def ss(self, interaction:discord.Interaction, site:str, delay:int=None):
		if not site.startswith("http://") and not site.startswith("https://"):
			site = f"https://{site}"
		if not delay is None:
			url = f"{self.bot.thum_io}wait/{delay}/{site}"
		if delay is None:
			url = f"{self.bot.thum_io}{site}"
		async with self.bot.session.get(url) as photo:
			if photo.status ==200:
				embed = discord.Embed(title="__**Site Screenshot**__", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_image(url=f"{self.bot.thum_io}{site}")
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
			else:
				embed = discord.Embed(title="__**Screenshot Error**__", description=f"Sorry I Cannot Screenshot *{site}*..\nPlease Try Again Later or Notify Support", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)

	@app_commands.command(name="tiktok", description="Downloads & Displays Specified TikTok Video") # Download TikTok Video Command
	@app_commands.describe(url="Video URL to Download")
	async def tiktok(self, interaction:discord.Interaction, *, url:str):
		correct_url = await self.bot.session.get(url)
		url = str(correct_url.url)
		regexes = ["https?://www\.tiktok\.com/(?:@.+)/video/(?P<id>\d+)/?", "https?://vm\.tiktok\.com/(?P<id>.+)/?", "https?://vt\.tiktok\.com/(?P<id>.+)/?", "https?://m\.tiktok\.com/v/(?P<id>.+)\.html"]
		video_id = None
		for r in regexes:
			current_video_id = re.match(r, url)
			if not current_video_id is None:
				video_id  = current_video_id['id'].replace('/', '')
		if video_id is None:
			embed = discord.Embed(title="__**TikTok Error**__", description=f"Couldn't Extract Video ID from URL", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async with self.bot.session.get(f"https://toolav.herokuapp.com/id/?video_id={video_id}") as url:
			resp = await url.read()
			data = json.loads(resp)
			video_id = data['item']['aweme_id']
		final_url = f"https://api-h2.tiktokv.com/aweme/v1/play/?video_id={video_id}"
		async with self.bot.session.get(f"{final_url}") as resp:
			temp_filename = f'/tmp/{video_id}.mp4'
			temp = open(temp_filename, 'w+b')
			temp.write(await resp.read())
			temp.seek(0)
			file = discord.File(fp=io.BytesIO(await resp.read()), filename=f"{video_id}.mp4", spoiler=False)
		await interaction.followup.send(file=file)

	@app_commands.command(name="download", description="Downloads & Displays Specified Song or Video") # Download Video/Song Command
	@app_commands.describe(url="Video or Song URL to Download", formating="Format to Download (Show to Display All)", final_format="Desired File Type for Video/Song")
	async def download(self, interaction:discord.Interaction, url:str, formating:str=None, *, final_format:str=None):
		if formating is None:
			formating = 'bestvideo+bestaudio/best'
		if formating == 'show' or formating == 'formats':
			try:
				loop = self.bot.loop or asyncio.get_event_loop()
				ytdl = await create_ytdl_client()
				data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
				#data = json.dumps(ytdl.sanitize_info(data))
				#data = json.loads(data)
				if "entries" in data:
					data = data['entries'][0]
				available_formats = ""
				results = 0
				embeds = []
				for f in data['formats']:
					format_info = f['format']
					format_id = f['format_id']
					format_note = f['format_note']
					try:
						vheight = f['height']
						vwidth = f['width']
						if not format_note is None:
							deminsion = f"{vwidth}x{vheight} ({format_note})"
						else:
							deminsion = f"{vwidth}x{vheight}"
					except:
						if not format_note is None:
							deminsion = f"Audio Only ({format_note})"
						else:
							deminsion = f"Audio Only"
					ext_type = f['ext']
					video_codec = f['vcodec']
					audio_codec = f['acodec']
					try:
						container = f['container']
					except:
						container = 'N/A'
					try:
						filesize = f['filesize']
						size = filesize*10**-9
						show = f"{size:.2f} GB"
						if int(size) < 1:
							size = filesize*10**-6
							show = f"{size:.2f} MB"
					except:
						show = "N/A"
					available_formats += f"**{format_id}**: *{deminsion}* | **EXT**: *{ext_type}* | **VCodec**: *{video_codec}* | **ACodec**: *{audio_codec}* | **{show}**\n"
					results += 1
					if results == 10:
						embed = discord.Embed(title="__**Available Download Formats**__", description=f"{available_formats}", timestamp=datetime.now(), color=0xac5ece)
						embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
						embeds.append(embed)
						available_formats = ""
						results = 0
				if results > 0 and results < 10:
					embed = discord.Embed(title="__**Available Download Formats**__", description=f"{available_formats}", timestamp=datetime.now(), color=0xac5ece)
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					embeds.append(embed)
				formatter = Formatter([i for i in embeds], per_page=1)
				menu = Pager(formatter)
				await menu.start(interaction)
				return
			except:
				embed = discord.Embed(title="__**Download Error**__", description=f"I've Encountered an Error & Couldn't Complete Your Request..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		try:
			loop = self.bot.loop or asyncio.get_event_loop()
			ytdl = await create_ytdl_client(formating=formating, merge=final_format)
			data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=True))
			#data = json.dumps(ytdl.sanitize_info(data))
			#data = json.loads(data)
			if "entries" in data:
				data = data['entries'][0]
			filename = ytdl.prepare_filename(data)
			file = discord.File(fp=filename, filename=f"{data['title']}.{data['ext']}", spoiler=False)
			temp_html = f"{interaction.user.id}-{data['title']}".replace(' ', '_')
			post_url = f"https://krypto.industries/show/"
			embed = discord.Embed(title=f"__**Video Downloader**__", description=f"I have Successfully Prepared *{data['title']}* to be Downloaded.\n[Click Here to Download or Stream Online](<{post_url}{temp_html}>)", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			post_data = {"filename": f"{filename}", "ext": f"{data['ext']}"}
			async with self.bot.session.post(f"{post_url}NEW", json=post_data) as response:
				response_json = await response.read()
			temp = open(f"templates/tmp/{temp_html}.html", 'w+b')
			temp.write(response_json)
			temp.seek(0)
			await interaction.followup.send(embed=embed, file=file)
			await asyncio.sleep(900)
			os.remove(filename)
		except Exception as e:
			embed = discord.Embed(title="__**Download Error**__", description=f"I've Encountered an Error & Couldn't Complete Your Request..\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="translate", description="Translates Text with Google Translator") # Translate Command
	@app_commands.describe(message="Text to Translate", language="Translate Text to this Language")
	async def translate(self, interaction:discord.Interaction, *, message:str, language:str=None):
		loop = self.bot.loop or asyncio.get_event_loop()
		try:
			if language is None:
				translation = await loop.run_in_executor(None, self.trans.translate, message)
			if not language is None:
				translation = await loop.run_in_executor(None, self.trans.translate, message, language)
		except Exception as e:
			embed = discord.Embed(title="__**Translate Error**__", description=f"**{e.__class__.__name__}**: *{e}*```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		src = googletrans.LANGUAGES.get(translation.src, '(auto-detected)').title()
		dest = googletrans.LANGUAGES.get(translation.dest, 'Unknown').title()

		embed = discord.Embed(title='__**Google Translation**__', timestamp=datetime.now(), color=0xac5ece)
		embed.set_author(name=f"{src} -> {dest}")
		embed.add_field(name=f'**From {src}**:', value=translation.origin, inline=False)
		embed.add_field(name=f'**To {dest}**:', value=translation.text, inline=False)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)

	@app_commands.command(name="reminder", description="Sets Reminder for Specified Time") # Reminder Command
	@app_commands.describe(time="Time of Reminder (d=days h=hours m=minutes s=seconds)", reminder="Reminder Message")
	async def remind(self, interaction:discord.Interaction, time:str, *, reminder:str):
		collection = self.bot.db["AM_alarms"]
		
		date, string, current = convert_seconds(time)
				
		embed = discord.Embed(title="__**Reminder Set**__", description=f"You will be reminded in {string} to {reminder}.", timestamp=date, color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		message = await interaction.followup.send(embed=embed)

		auto = {}
		auto ["Member"] = interaction.user.id
		auto ["Guild"] = interaction.guild.id
		auto ["Channel"] = interaction.channel.id
		auto ["Message"] = message.id
		auto ["Reminder"] = reminder
		auto ["Begin"] = current
		auto ["End"] = date
		await collection.insert_one(auto)
		#await ctx.message.delete()

	@app_commands.command(name="echo", description="Echo Your Message but in an Embed") # Embedded Echo Command
	@app_commands.describe(message="Message to be Echoed")
	async def echo(self, interaction:discord.Interaction, *, message:str):
		embed = discord.Embed(title="__**Echo Embed**__", timestamp=datetime.now(), color=0xac5ece)
		embed.add_field(name="Message:", value=f"{message}", inline=False)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="echo_advanced", description="Echo Message & Title but in an Embed") # Advanced Echo Command
	@app_commands.describe(title="Title of the Embed", message="Message to be Echoed")
	async def echo_advanced(self, interaction:discord.Interaction, title:str, *, message:str):
		embed = discord.Embed(title=f"__**{title}**__", description=f"{message}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="echo_clean", description="Echo Message but in a Minimalistic Embed") # Clean Echo Command
	@app_commands.describe(message="Message to be Echoed")
	async def echo_clean(self, interaction:discord.Interaction, *, message:str):
		embed = discord.Embed(description=f"**{message}**", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="weather", description="Checks Weather in Specified Zipcode") # Weather Command
	@app_commands.describe(zipcode="Zipcode to Check Weather in")
	async def weather(self, interaction:discord.Interaction, zipcode:int):
		async with self.bot.session.get(f"https://api.openweathermap.org/data/2.5/weather?zip={zipcode}&units=imperial&APPID=986ef6da00c77e47e6fe6a5eba0e369a") as url:
			if url.status != 200:
				embed = discord.Embed(title="__**Weather Error**__", description=f"**Response {url.status_code}:** *{url.reason}*", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			data = await url.json()
			if not data:
				embed = discord.Embed(title="__**Weather Error**__", description=f"No Results for the Zipcode `{zipcode}`..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
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

			embed = discord.Embed(title=f"__**{location}** *({country})*__", description=f":thermometer: **Temperature:** {temp} *({temp_max}/{temp_min})*\n:earth_americas: **{condition}:** {desc}\n:wind_blowing_face: **Wind:** {wind} *mph*\n:droplet: **Humidity:** {humidity}%\n:globe_with_meridians: **Coordinates:** {lat_cord}, {lon_cord}", timestamp=datetime.now(), color=0xac5ece)
			#embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()

	@app_commands.command(name="definition", description="Lookup Definition of Specified Word") # Definition Command
	@app_commands.describe(word="Word to Lookup Definition of")
	async def definition(self, interaction:discord.Interaction, word:str):
		async with self.bot.session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as url:
			if url.status != 200:
				embed = discord.Embed(title="__**Definition Error**__", description=f"**Response {url.status_code}:** *{url.reason}*", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			data = await url.json()
			if not data:
				embed = discord.Embed(title="__**Definition Error**__", description=f"No Results for the Word `{word}`..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
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
			#embed = discord.Embed(title=f"__**Word Definition**__", description=f"**{word}**\n*{origin}*\n{pronunciationz}", timestamp=datetime.now(), color=0xac5ece)
			embed = discord.Embed(title=f"__**Word Definition**__", description=f"`{word}`\n{pronunciationz}", timestamp=datetime.now(), color=0xac5ece)
			#embed = discord.Embed(title=f"__**Definition of {word.capitalize()}**__", description=f"{pronunciationz}", timestamp=datetime.now(), color=0xac5ece)
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
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()

	@app_commands.command(name="definition_urban", description="Lookup Urban Definition of Specified Word or Phrase") # Urban Dictionary Command
	@app_commands.describe(word="Word or Phrase to Lookup Urban Definition of")
	async def definition_urban(self, interaction:discord.Interaction, *, word:str):
		async with self.bot.session.get(f'http://api.urbandictionary.com/v0/define?term={word}') as url:
			if url.status != 200:
				embed = discord.Embed(title="__**Definition Error**__", description=f"**Response {url.status_code}:** *{url.reason}*", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			data = await url.json()
			if not data:
				embed = discord.Embed(title="__**Definition Error**__", description=f"No Results for the Word `{word}`..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			query = data['list']
			#print(query)
			embed = discord.Embed(title=f"__**Urban Dictionary**__", description=f"`{word}`\n__**Top Definitions**__", timestamp=datetime.now(), color=0xac5ece)
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
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()

	@app_commands.command(name="meme", description="Sends a Meme") # Meme Command
	async def meme(self, interaction:discord.Interaction):
		posts = []
		sub = await self.reddit.subreddit('memes')
		async for x in sub.hot():
			posts.append(x.id)
		data = await self.reddit.submission(id=posts[random.randint(0, len(posts))])
		embed = discord.Embed(title=f"", description=f"[{data.title}](<https://reddit.com/r/memes/comments/{data.id}>)", timestamp=datetime.now(), color=0xac5ece)
		embed.set_image(url=f"{data.url}")
		comments = await data.comments()
		embed.set_footer(text=f"\U0001F44D {data.score} | \U0001F5EF {len(comments)}\n{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		#embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="report", description="Reports Specified Member for Specified Reason") # Report Command
	@app_commands.describe(member="Member to Report", reason="Reason for Reporting Member")
	async def report(self, interaction:discord.Interaction, member:discord.User, *, reason:str):
		collection = self.bot.db["logs"]
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		embed = discord.Embed(title="__***Report Success***__", description=f"{interaction.user.mention} your report has been received.", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name="__**:busts_in_silhouette: Reported:**__", value=f"{member.mention}", inline=False)
		embed.add_field(name="__**:newspaper: Reason:**__", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await interaction.user.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__***Report***__", description=f"{interaction.user.mention} has reported {member.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name="__**:link: Reporter ID:**__", value=f"{interaction.user.id}", inline=False)
		embed_2.add_field(name="__**:link: Offender ID:**__", value=f"{member.id}", inline=False)
		embed_2.add_field(name="__**:newspaper: Reason:**__", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await mod_log.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="wisdom", description="Provides Words of Wisdom to Your Question") # Words of Wisdom (8-Ball) Command
	@app_commands.describe(question="Question to Receive Answer to")
	async def wisdom(self, interaction:discord.Interaction, *,  question:str):
		wisdom_quotes = ["Yes", "No", "Maybe", "Ask Again Later", "Sometimes Answers can only be Found by the Questioner.", "Fate may Predict the Future but Free Will Creates Opportunity to Change it.", "Knowledge should be Shared... but Should we Share it, if the Information may Negatively Effect the Receivers Perspective of the Future?", "Some Answers are better being left Unkown."]
		embed_2 = discord.Embed(title="__**Words of Wisdom**__", description=f":question: __**Q:**__ {question}\n:crystal_ball: __**A:**__ {random.choice(wisdom_quotes)}", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="roll_dice", description="Rolls a Dice with 6 Sides") # Dice Roll Command
	@app_commands.describe(sides="Amount of Sides for Dice")
	async def roll_dice(self, interaction:discord.Interaction, sides:int=None):
		if sides is None:
			embed = discord.Embed(title="__**Dice Roll**__", description=f":game_die: __**Dice Sides:**__ `6`\n:question: __**Number:**__ `{random.randint(1,6)}`", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Dice Roll**__", description=f":game_die: __**Dice Sides:**__ `{sides}`\n:question: __**Number:**__ `{random.randint(1,sides)}`", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="flip_coin", description="Flip a Coin") # Coin Flip Command
	@app_commands.describe(choice="Your Choice of Side")
	async def flip_coin(self, interaction:discord.Interaction, choice:str=None):
		sides = ["Heads", "Tails"]
		if choice is None:
			embed = discord.Embed(title="__**Coin Flip**__", description=f":moyai: __**Side:**__ {random.choice(sides)}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Coin Flip**__", description=f":pencil: __**Your Choice:**__ {choice}\n:moyai: __**Side:**__ {random.choice(sides)}", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="rock_paper_scissors", description="Play a Match of Rock Paper Scissors") # Rock, Paper, Scissors Command
	@app_commands.describe(choice="Your Choice")
	async def rock_paper_scissors(self, interaction:discord.Interaction, *, choice:str):
		choices = ["Rock", "Paper", "Scissors"]
		bot_choice = random.choice(choices)
		embed_2 = discord.Embed(title="__**Rock, Paper, Scissors**__", description=f":robot: __**{self.bot.user.name}'s Choice:**__ {bot_choice}\n:pencil: __**Your Choice:**__ {choice}", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="phone", description="Send Message to All Servers with Phone Setup") # Phone Call Command
	@app_commands.describe(message="Message to be Sent")
	async def phone(self, interaction:discord.Interaction, *, message:str):
		external_links = ["https", ".com", ".net", ".org", ".tv"]
		for x in external_links:
			if x in message.lower():
				embed = discord.Embed(title="__**Phone Error**__", description=f"Please Do Not Send Links.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		if "discord.gg" in message.lower():
			embed = discord.Embed(title="__**Phone Error**__", description=f"Please Do Not Send Invites.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Config_phone"]
		servers = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			servers = interaction.guild.get_channel(Channelz)
		if servers is None:
			embed = discord.Embed(title="__**Phone Error**__", description=f"You must Setup a Line to Use the Phone.\n`{self.bot.prefix}psetup <Mention Channel>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		linez = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			linez += {x["Guild"]}
		lines = len(linez)-1
		embed = discord.Embed(title="__**Incoming Call**__", timestamp=datetime.now(), color=0xac5ece)
		embed.add_field(name="Caller's Message:", value=f"{message}", inline=False)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild is servers.guild:
			embed_2 = discord.Embed(title="__**Message Sent**__", timestamp=datetime.now(), color=0xac5ece)
			embed_2.add_field(name="Receiving Servers:", value=f"Message received in {lines} servers.", inline=False)
			embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_2)
		grab_channelz = collection.find({}, {"_id": 0, "Guild": 0})
		channelz = []
		async for x in grab_channelz:
			channelz += {x["Channel"]}
		for x in channelz:
			try:
				lines = self.bot.get_channel(x)
				if lines.guild is not interaction.guild: 
					await lines.send(embed=embed)
			except:
				print(f"Server {x} has Altered their Phone Line Channel.")
		#await ctx.message.delete()

	@app_commands.command(name="invite", description="Sends Invite & Overview") # Invite Command
	async def invite(self, interaction:discord.Interaction):
		embed = discord.Embed(title=f"__***{self.bot.user.name}***__", timestamp=datetime.now(), color=0xac5ece)
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
		embed.add_field(name="__**:link: Bot Invite:**__", value=f"[Click to Invite](<https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot+applications.commands>)")
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="help", description="Shows All Commands & Information About Them") # Help Command
	#@app_commands.bot_checks.has_permissions(add_reactions=True)
	async def help(self, interaction:discord.Interaction):
		
		with open('Commands.json', 'r') as r:
			cmd_json = json.load(r)
		amount = len(cmd_json)
		if not interaction.user.id in self.bot.owners:
			amount -= 2
		embeds = []
		current_amount = 1
		for category in cmd_json:
			if not current_amount > amount:
				embed = discord.Embed(title=f"__***{category}***__ *({current_amount}/{amount})*", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				current_amount += 1
				for cmd in cmd_json[category]:
					if not "%bot" in cmd:
						new_cmd = cmd
					if "%bot" in cmd:
						new_cmd = cmd.replace(f"%bot", f"{self.bot.user.name}")
					desc = cmd_json[category][cmd]['Description']
					if "%bot" in desc:
						desc = desc.replace(f"%bot", f"{self.bot.user.name}").replace(f"%support_server", f"{self.bot.support_server}")
					emoji = cmd_json[category][cmd]['Emoji']

					infos = ""
					info_check = False
					info_count = 0
					if len(cmd_json[category][cmd]['Info']) > 1:
						for info in cmd_json[category][cmd]['Info']:
							if "%bot" in info:
								info = info.replace(f"%bot", f"{self.bot.user.name}")
							infos += f"{info}"
							info_count += 1
							info_check = True
							if info_count != len(cmd_json[category][cmd]['Info']):
								infos += "\n"

					invokes = ""
					invoke_count = 0
					for invoke in cmd_json[category][cmd]['Invoke']:
						invokes += f"`{self.bot.prefix}{invoke}`"
						invoke_count += 1
						if invoke_count != len(cmd_json[category][cmd]['Invoke']):
							invokes += " *or* "

					if info_check is False:
						embed.add_field(name=f":{emoji}: __**{new_cmd}:**__", value=f"*{desc}*\n{invokes}", inline=False)
					if info_check is True:
						embed.add_field(name=f":{emoji}: __**{new_cmd}:**__", value=f"*{desc}*\n***{infos}***\n{invokes}", inline=False)
				embeds.append(embed)

		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter, dropdown=True, titles=True)
		await menu.start(interaction)
		#await ctx.message.delete()

async def setup(bot):
	await bot.add_cog(Everyone(bot))