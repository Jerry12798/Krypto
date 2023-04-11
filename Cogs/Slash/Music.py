import discord
import asyncio
import io
import youtube_dl
from discord.ext import commands
from discord import app_commands
from datetime import datetime

que = {}

def check_que(bot, id):
	if not que is {}:
		player = que[id].pop(0)
		server = bot.get_guild(id)
		server.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else check_que(id))

ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
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

class YTDLSource(discord.PCMVolumeTransformer):
	def __init__(self, source, *, data, volume=1.0):
		super().__init__(source, volume)
		self.data = data
		self.title = data.get('title')
		self.url = data.get('url')

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=False):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
		if "entries" in data:
			data = data['entries'][0]
		filename = data['url'] if stream else ytdl.prepare_filename(data)
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), data=data)



class Music(commands.Cog, app_commands.Group, name="music", description="Music Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="play", description="Play Music on Discord") # Play Command
	@app_commands.describe(song="Song Name or URL to Play")
	async def play(self, interaction:discord.Interaction, *, song:str):
		if interaction.guild.voice_client is None:
			if interaction.user.voice is None:
				embed_2 = discord.Embed(title="__**Music Error**__", description=f"You First must Join a Voice Channel or Connect {self.bot.user.mention} to a Voice Channel.\n`{self.bot.prefix}join <Channel Name>`", timestamp=datetime.now(), color=0xff0000)
				embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed_2)
				return
			channel = interaction.user.voice.channel
			await channel.connect(timeout=180.0)
		if interaction.guild.voice_client is not None:
			player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
			interaction.guild.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else check_que(self.bot, interaction.guild.id))
			embed_3 = discord.Embed(title="__**Music**__", description=f":musical_note: __**Now playing:**__ {player.title}", timestamp=datetime.now(), color=0xac5ece)
			embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_3)
			#await ctx.message.delete()
	@play.error
	async def play_error(self, interaction, error):
		if isinstance(error, app_commands.CommandInvokeError):
			embed = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is already Playing Music. Add the Song to the Queue instead.\n`{self.bot.prefix}queue <Song Name>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="queue", description="Queue Song to be Played") # Queue Command
	@app_commands.describe(song="Song Name or URL to Queue")
	async def queue(self, interaction:discord.Interaction, *, song:str):
		if interaction.guild.voice_client.is_playing():
			player = await YTDLSource.from_url(song, loop=self.bot.loop, stream=True)
			embed = discord.Embed(title="__**Song Queued**__", description=f"**{player.title}** has been Queued.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			if interaction.guild.id in que:
				que[interaction.guild.id].append(player)
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
			if interaction.guild.id not in que:
				que[interaction.guild.id] = [player]
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
	@queue.error
	async def queue_error(self, interaction, error):
		if isinstance(error, app_commands.CommandInvokeError):
			embed = discord.Embed(title="__**Music Error**__", description="You First must Start Playing Music to Queue Songs.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="queued", description="Show All Currently Queued Songs") # List Queued Songs Command
	async def queued(self, interaction:discord.Interaction):
		queue = que[interaction.guild.id]
		songs = []
		for x in queue:
			songs += {x.title}
		embed = discord.Embed(title="__**Queue List**__", description=f"**{songs}**", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@queued.error
	async def queued_error(self, interaction, error):
		if isinstance(error, app_commands.CommandInvokeError):
			embed = discord.Embed(title="__**Queue List Error**__", description=f"There is No Songs in {interaction.guild}'s Queue.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="join", description="Add Me to Specified Voice Channel") # Join Command
	@app_commands.describe(channel="Voice Channel for Me to Join")
	async def join(self, interaction:discord.Interaction, *, channel:discord.VoiceChannel):
		if interaction.guild.voice_client is not None:
			embed_2 = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is already Connected to **{interaction.guild.voice_client.channel}**.", timestamp=datetime.now(), color=0xac5ece)
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
		embed_3 = discord.Embed(title="__**Music**__", description=f"{self.bot.user.mention} has Connected to **{channel.name}**.", timestamp=datetime.now(), color=0xac5ece)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await channel.connect(timeout=180.0)
		await interaction.followup.send(embed=embed_3)
		#await ctx.message.delete()

	@app_commands.command(name="pause", description="Pauses the Music if Any is Playing") # Pause Command
	async def pause(self, interaction:discord.Interaction):
		if interaction.guild.voice_client is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel\n`{self.bot.prefix}join <Channel Name>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Music Paused**__", description=f"{self.bot.user.mention} has `Paused` the Music in **{interaction.guild.voice_client.channel.name}**.", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		interaction.guild.voice_client.pause()
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="resume", description="Resumes the Music if Any is Paused") # Resume Command
	async def resume(self, interaction:discord.Interaction):
		if interaction.guild.voice_client is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel\n`{self.bot.prefix}join <Channel Name>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Music Resumed**__", description=f"{self.bot.user.mention} has `Resumed` the Music in **{interaction.guild.voice_client.channel.name}**.", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		interaction.guild.voice_client.resume()
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()

	@app_commands.command(name="skip", description="Skips the Music to Next Song in Queue") # Skip Command
	@app_commands.checks.has_permissions(kick_members=True)
	async def skip(self, interaction:discord.Interaction):
		if interaction.guild.voice_client is not None:
			embed = discord.Embed(title="__**Song Skipped**__", description=f"{self.bot.user.mention} has `Skipped` the Music in **{interaction.guild.voice_client.channel.name}**.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			interaction.guild.voice_client.stop()
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if interaction.guild.voice_client is None:
			embed_2 = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel.", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_2)
	@skip.error
	async def skip_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Skip Songs in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="stop", description="Stops and Disconnects the Music and Queue") # Stop/Disconnect Command
	@app_commands.checks.has_permissions(kick_members=True)
	async def stop(self, interaction:discord.Interaction):
		if interaction.guild.voice_client is not None:
			embed = discord.Embed(title="__**Music Stopped**__", description=f"{self.bot.user.mention} has been Disconnected from Voice Chat.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.guild.voice_client.disconnect()
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if interaction.guild.voice_client is None:
			embed_2 = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel.", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_2)
	@stop.error
	async def stop_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Stop the Music in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="download", description="Creates a MP3 Download for Specified Song") # Download Song Command
	@app_commands.describe(song="Song Name or URL to Download")
	async def download(self, interaction:discord.Interaction, *, song:str):
		loop = self.bot.loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(song, download=False))
		if "entries" in data:
			data = data['entries'][0]
		filename = data['url']
		async with self.bot.session.get(f"{filename}") as resp:
			file = discord.File(fp=io.BytesIO(await resp.read()), filename=f"{data['title']}.mp3", spoiler=False)
		embed = discord.Embed(title=f"__**MP3 Converter**__", description=f"I have Successfully Prepared *{data['title']}* as a MP3 to be Downloaded.\n[Click Here to Download or Stream Online](<{filename}>)", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed, file=file)

async def setup(bot):
	await bot.add_cog(Music(bot))