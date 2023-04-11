# Client ID - 555820515965534208
# Permissions - 2146958839
# https://discordapp.com/oauth2/authorize?client_id=555820515965534208&permissions=8&scope=bot+applications.commands

import discord
import asyncio
import aiohttp
import time
import json
import pytz
import motor.motor_asyncio
import logging
import traceback
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
from pytz import timezone
from Utils.Database import remove_guild_data


with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

Bot_Prefix = config['Bot_Prefix']
Bot_Token = config['Bot_Token']
owners = config['Owners']
Support_Staff_Role_ID = config['Support_Staff_Role_ID']
Vote_Log = config['Vote_Log']
Mod_Mail_Channel = config['Mod_Mail_Channel']
Announcement_Channel = config['Announcement_Channel']
Vouch_Queue = config['Vouch_Queue']
Your_Username = config['Your_Username']
Bot_Support_Server = config['Bot_Support_Server']
Bot_Support_Server_ID = config['Bot_Support_Server_ID']
MongoDB_Client = config['MongoDB_Client']
IPC_Key = config['IPC_Key']
CoC_Email = config['CoC_Email']
CoC_Pass = config['CoC_Pass']
CoC_Key_Name = config['CoC_Key_Name']
Google_API_Keys = config['Google_API_Keys']
Thum_IO_Base_URL = config['Thum_IO_Base_URL']



async def get_prefix(bot, ctx):
	await bot.wait_until_ready()
	collection = bot.db["Config_prefixes"]
	try:
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			prefix = m["Prefix"]
		return commands.when_mentioned_or(*prefix)(bot, ctx)
	except:
		return commands.when_mentioned_or(*f"{bot.prefix}")(bot, ctx)

		

logging.basicConfig(level=logging.INFO)
extensions = [
	"Cogs.AutoMod", 
	"Cogs.Bump", 
	"Cogs.COC", 
	"Cogs.Configuration", 
	"Cogs.Dev", 
	"Cogs.Eco", 
	"Cogs.Events", 
	"Cogs.General", 
	"Cogs.Information", 
	"Cogs.Moderation", 
	"Cogs.MP3", 
	"Cogs.Reputation", 
	"Cogs.Server", 
	"Cogs.Tasks", 
	"Cogs.Ticket",

	"Cogs.Slash.Automod", 
	"Cogs.Slash.Bumpset", 
	"Cogs.Slash.CoC", 
	"Cogs.Slash.Config", 
	"Cogs.Slash.Economy", 
	"Cogs.Slash.Everyone", 
	"Cogs.Slash.Info", 
	"Cogs.Slash.Mod", 
	"Cogs.Slash.Music", 
	"Cogs.Slash.Support", 
	"Cogs.Slash.Ticketer",
	"Cogs.Slash.Vouch",
	]



class Krypto(commands.AutoShardedBot):
	def __init__(self):
		intents = discord.Intents(
			bans=True, 
			emojis=True, 
			guilds=True, 
			invites=True, 
			members=True, 
			message_content=True, 
			messages=True, 
			reactions=True, 
			typing=True, 
			voice_states=True, 
			webhooks=True
			)
		super().__init__(
			#chunk_guilds_at_startup=False, 
			command_prefix=get_prefix, 
			#heartbeat_timeout=120.0
			intents=intents
			)
		self.remove_command('help')
		self.start_time = datetime.utcnow()
		self.prefix = Bot_Prefix
		self.coggers = extensions
		self.owners = owners
		self.support = Support_Staff_Role_ID
		self.vote_log = Vote_Log
		self.mod_mail = Mod_Mail_Channel
		self.news = Announcement_Channel
		self.vouch_queue = Vouch_Queue
		self.bot_owner = Your_Username
		self.support_server = Bot_Support_Server
		self.support_server_id = Bot_Support_Server_ID
		self.ipc_key = IPC_Key
		self.google_keys = Google_API_Keys
		self.thum_io = Thum_IO_Base_URL
	async def close(self):
		await super().close()
		await self.session.close()
	async def main(self):
		async with aiohttp.ClientSession() as session:
			async with self:
				self.session = session
				self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MongoDB_Client)
				self.db = self.mongo_client.Krypto_Configs
				await super().start(Bot_Token, reconnect=True)

	async def setup_hook(self):
		for extension in extensions:
			try:
				await self.load_extension(extension)
				print(f"Loaded {extension}")
			except Exception as e:
				lines = traceback.format_exception(type(e), e, e.__traceback__)
				print("".join(lines))

	async def on_message(self, message): # Fix Lag of Command Replies
		if message.author.bot:
			return
		await self.process_commands(message)

	async def on_guild_remove(self, guild): # Removes Guild Info from Database
		await remove_guild_data(db=self.db, guild_id=guild.id)

	async def on_interaction(self, interaction): # Log Interactions
		try:
			print(f"[Interaction Ran] {interaction.user} Used `{interaction.command.name}` in {interaction.guild}.")
			await interaction.response.defer(thinking=True)
		except:
			pass

	async def on_command(self, ctx): # Log Commands
		print(f"[Command Ran] {ctx.author} Used `{ctx.message.content}` in {ctx.guild}.")

	async def on_command_error(self, ctx, error): # Global Command Error Handler
		if isinstance(error, commands.MissingRequiredArgument):
			msg = f'You need to Specify `{error.param.name}`'
		elif isinstance(error, commands.BadArgument):
			msg = error.args[0].replace('"', '`')
			msg += f'\n\nUse `{self.prefix}help` to View All Commands'
			await ctx.send(msg)
		elif isinstance(error, commands.MissingPermissions):
			permissions = '\n'.join(f'- {p.title().replace("_", " ")}' for p in error.missing_permissions)
			await ctx.send(f'**You need the Following Permissions:**\n{permissions}')
		elif isinstance(error, commands.BotMissingPermissions):
			permissions = '\n'.join(f'- {p.title().replace("_", " ")}' for p in error.missing_permissions)
			await ctx.send(f'**{self.user.mention} is Missing Required Permissions:**\n{permissions}')
		elif isinstance(error,discord.NotFound):
			print('nfnd')
		else:
			print(error)

	async def on_ready(self): # Print Login Info
		print(self.db)
		print("Logged in as ")
		print(self.user)
		print(discord.utils.oauth_url(self.user.id))
		print("------------------------------------------------------------------------------")

if __name__ == "__main__":
	asyncio.run(Krypto().main())