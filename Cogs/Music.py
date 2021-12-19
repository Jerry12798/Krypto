import discord
import asyncio
import youtube_dl
from discord.ext import commands
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



class Music(commands.Cog, name="Music"):
	def __init__(self,bot):
		self.bot = bot

	@commands.command() # Play Command
	async def play(self, ctx, *, url=None):
		if url is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"You must Name a Song to Play.\n`{self.bot.prefix}play <Song Name>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if ctx.voice_client is None:
			if ctx.message.author.voice is None:
				embed_2 = discord.Embed(title="__**Music Error**__", description=f"You First must Join a Voice Channel or Connect {self.bot.user.mention} to a Voice Channel.\n`{self.bot.prefix}join <Channel Name>`", timestamp=datetime.utcnow(), color=0xff0000)
				embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed_2)
				return
			channel = ctx.author.voice.channel
			await channel.connect(timeout=180.0)
		if ctx.voice_client is not None:
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else check_que(self.bot, ctx.guild.id))
			embed_3 = discord.Embed(title="__**Music**__", description=f":musical_note: __**Now playing:**__ {player.title}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_3)
			await ctx.message.delete()
	@play.error
	async def play_error(self, ctx, error):
		if isinstance(error, commands.CommandInvokeError):
			embed = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is already Playing Music. Add the Song to the Queue instead.\n`{self.bot.prefix}queue <Song Name>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Queue Command
	async def queue(self, ctx, *, url=None):
		if url is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"You must Name a Song to Queue.\n`{self.bot.prefix}queue <Song Name>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if ctx.voice_client.is_playing():
			player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
			embed = discord.Embed(title="__**Song Queued**__", description=f"**{player.title}** has been Queued.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			if ctx.guild.id in que:
				que[ctx.guild.id].append(player)
				await ctx.send(embed=embed)
				await ctx.message.delete()
			if ctx.guild.id not in que:
				que[ctx.guild.id] = [player]
				await ctx.send(embed=embed)
				await ctx.message.delete()
	@queue.error
	async def queue_error(self, ctx, error):
		if isinstance(error, commands.CommandInvokeError):
			embed = discord.Embed(title="__**Music Error**__", description="You First must Start Playing Music to Queue Songs.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Join Command
	async def join(self, ctx, *, channel:discord.VoiceChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"You must Mention a Voice Channel for {self.bot.user.mention} to Join.\n`{self.bot.prefix}join <Channel Name>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if ctx.voice_client is not None:
			embed_2 = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is already Connected to **{ctx.voice_client.channel}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
		embed_3 = discord.Embed(title="__**Music**__", description=f"{self.bot.user.mention} has Connected to **{channel.name}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await channel.connect(timeout=180.0)
		await ctx.send(embed=embed_3)
		await ctx.message.delete()

	@commands.command() # Pause Command
	async def pause(self, ctx):
		if ctx.voice_client is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel\n`{self.bot.prefix}join <Channel Name>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Music Paused**__", description=f"{self.bot.user.mention} has `Paused` the Music in **{ctx.voice_client.channel.name}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		ctx.voice_client.pause()
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Resume Command
	async def resume(self, ctx):
		if ctx.voice_client is None:
			embed = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel\n`{self.bot.prefix}join <Channel Name>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Music Resumed**__", description=f"{self.bot.user.mention} has `Resumed` the Music in **{ctx.voice_client.channel.name}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		ctx.voice_client.resume()
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Skip Command
	@commands.has_permissions(kick_members=True)
	async def skip(self, ctx):
		if ctx.voice_client is not None:
			embed = discord.Embed(title="__**Song Skipped**__", description=f"{self.bot.user.mention} has `Skipped` the Music in **{ctx.voice_client.channel.name}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			ctx.voice_client.stop()
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if ctx.voice_client is None:
			embed_2 = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel.", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
	@skip.error
	async def skip_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Skip Songs in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Stop/Disconnect Command
	@commands.has_permissions(kick_members=True)
	async def stop(self, ctx):
		if ctx.voice_client is not None:
			embed = discord.Embed(title="__**Music Stopped**__", description=f"{self.bot.user.mention} has been Disconnected from Voice Chat.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.voice_client.disconnect()
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if ctx.voice_client is None:
			embed_2 = discord.Embed(title="__**Music Error**__", description=f"{self.bot.user.mention} is Not Connected to a Voice Channel.", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
	@stop.error
	async def stop_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Stop the Music in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # List Queued Songs Command
	async def queued(self, ctx):
		queue = que[ctx.guild.id]
		songs = []
		for x in queue:
			songs += {x.title}
		embed = discord.Embed(title="__**Queue List**__", description=f"**{songs}**", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@queued.error
	async def queued_error(self, ctx, error):
		if isinstance(error, commands.CommandInvokeError):
			embed = discord.Embed(title="__**Queue List Error**__", description=f"There is No Songs in {ctx.guild}'s Queue.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
		await ctx.message.delete()

def setup(bot):
	bot.add_cog(Music(bot))