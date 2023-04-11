import asyncio, datetime, json, motor.motor_asyncio, os, pymongo
import discord, topgg
from quart import Quart, request
from discord.ext import commands, tasks
from datetime import datetime

app = Quart(__name__)

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

TOPGG_Token = config['TOPGG_Token']
TOPGG_Vote_Link = config['TOPGG_Vote_Link']
TOPGG_Secret = config['TOPGG_Secret']
DBL_Token = config['DBL_Token']
DBL_Vote_Link = config['DBL_Vote_Link']
DBL_Secret = config['DBL_Secret']
DB_Token = config['DB_Token']



class Server(commands.Cog, name="Server"):
	def __init__(self, bot):
		self.bot = bot
		self.bot.topggpy = topgg.DBLClient(bot=self.bot, token=TOPGG_Token, autopost=True)
		self.bot.topgg_token = TOPGG_Token
		self.bot.topgg_link = TOPGG_Vote_Link
		self.bot.topgg_secret = TOPGG_Secret
		self.bot.dbl_token = DBL_Token
		self.bot.dbl_link = DBL_Vote_Link
		self.bot.dbl_secret = DBL_Secret
		self.bot.db_token = DB_Token
		

		@app.route('/')
		async def welcome():
			return f"Hello World, this is {self.bot.bot_owner}'s Webserver for {self.bot.user}."

		@app.route('/ggwebhook')
		async def ggwebhook():
			if request.headers.get('authorization') == TOPGG_Secret:
				data = await request.json()
				user = int(data["user"])
				vote_type = data["type"]
				log = self.bot.get_channel(self.bot.vote_log)
				member = self.bot.get_user(user)
				embed = discord.Embed(title=f"Upvote on Top.gg", url=TOPGG_Vote_Link, description=f"{member.mention} has Successfully Upvoted {self.bot.user.mention}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				await log.send(embed=embed)

				collection = self.bot.db["Eco_dbl_votes"]
				member_log = False
				async for z in collection.find({"Member": user}, {"_id": 0}):
					member_log = True
					votes = z["Votes"]
					life = z["Lifetime"]

				if member_log is True: # Add Vote to System
					votes += 1
					await collection.update_one({"Member": user}, {"$set":{"Votes": votes, "Member_Name": f"{member}"}})

				member_stats = {}
				member_stats ["Member"] = user
				member_stats ["Member_Name"] = f"{member}"
				member_stats ["Votes"] = 1
				member_stats ["Lifetime"] = 0

				if member_log is False: # Add Member to System
					await collection.insert_one(member_stats)

				collection_2 = self.bot.db["Eco_total_votes"]
				member_log = False
				async for z in collection_2.find({"Member": user}, {"_id": 0}):
					member_log = True
					votes = z["Votes"]
					life = z["Lifetime"]

				if member_log is True: # Add Vote to Leaderboard
					votes += 1
					await collection_2.update_one({"Member": user}, {"$set":{"Votes": votes, "Member_Name": f"{member}"}})

				member_stats = {}
				member_stats ["Member"] = user
				member_stats ["Member_Name"] = f"{member}"
				member_stats ["Votes"] = 1
				member_stats ["Lifetime"] = 0

				if member_log is False: # Add Member to Leaderboard
					await collection_2.insert_one(member_stats)

				print(f"[Upvote] Member {user} has voted on Top.gg | {vote_type}")
			return 200

		@app.route('/dblwebhook')
		async def dbwebhook():
			if request.headers.get('authorization') == DBL_Secret:
				data = await request.json()
				user = int(data["id"])
				log = self.bot.get_channel(self.bot.vote_log)
				member = self.bot.get_user(user)
				embed = discord.Embed(title=f"Upvote on Discord Bot List", url=DBL_Vote_Link, description=f"{member.mention} has Successfully Upvoted {self.bot.user.mention}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				await log.send(embed=embed)

				collection = self.bot.db["Eco_db_votes"]
				member_log = False
				async for z in collection.find({"Member": user}, {"_id": 0}):
					member_log = True
					votes = z["Votes"]
					life = z["Lifetime"]

				if member_log is True: # Add Vote to System
					votes += 1
					await collection.update_one({"Member": user}, {"$set":{"Votes": votes, "Member_Name": f"{member}"}})

				member_stats = {}
				member_stats ["Member"] = user
				member_stats ["Member_Name"] = f"{member}"
				member_stats ["Votes"] = 1
				member_stats ["Lifetime"] = 0

				if member_log is False: # Add Member to System
					await collection.insert_one(member_stats)

				collection_2 = self.bot.db["Eco_total_votes"]
				member_log = False
				async for z in collection_2.find({"Member": user}, {"_id": 0}):
					member_log = True
					votes = z["Votes"]
					life = z["Lifetime"]

				if member_log is True: # Add Vote to Leaderboard
					votes += 1
					await collection_2.update_one({"Member": user}, {"$set":{"Votes": votes, "Member_Name": f"{member}"}})

				member_stats = {}
				member_stats ["Member"] = user
				member_stats ["Member_Name"] = f"{member}"
				member_stats ["Votes"] = 1
				member_stats ["Lifetime"] = 0

				if member_log is False: # Add Member to Leaderboard
					await collection_2.insert_one(member_stats)
					
				print(f"[Upvote] Member {user} has voted on Discord Bot List")
			return 200

		@app.route('/member_count')
		async def get_member_count():
			if request.headers['Key'] != self.bot.ipc_key:
				return "Access Denied"
			server = request.args['server']
			guild = self.bot.get_guild(int(server))
			return guild.member_count

		@app.route('/guilds')
		async def bot_guilds():
			if request.headers['Key'] != self.bot.ipc_key:
				return "Access Denied"
			guilds = []
			for x in self.bot.guilds:
				#log = {}
				#log ["ID"] = x.id
				#log ["Name"] = str(x)
				#guilds [str(x.id)] = log
				guilds += {x.id}
			return guilds

		@app.route('/members')
		async def get_members():
			if request.headers['Key'] != self.bot.ipc_key:
				return "Access Denied"
			server = request.args['server']
			try:
				members = {}
				guild = self.bot.get_guild(int(server))
				for x in guild.members:
					log = {}
					log ["ID"] = x.id
					log ["Name"] = str(x)
					members [str(x.id)] = log
			except:
				members = None
			return members

		@app.route('/channels')
		async def get_channels():
			if request.headers['Key'] != self.bot.ipc_key:
				return "Access Denied"
			server = request.args['server']
			try:
				channels = {}
				guild = self.bot.get_guild(int(server))
				for x in guild.text_channels:
					log = {}
					log ["ID"] = x.id
					log ["Name"] = str(x)
					channels [str(x.id)] = log
			except:
				channels = None
			return channels

		@app.route('/roles')
		async def get_roles():
			if request.headers['Key'] != self.bot.ipc_key:
				return "Access Denied"
			server = request.args['server']
			try:
				roles = {}
				guild = self.bot.get_guild(int(server))
				for x in guild.roles:
					log = {}
					log ["ID"] = x.id
					log ["Name"] = str(x)
					if not "@everyone" in str(x):
						roles [str(x.id)] = log
			except:
				roles = None
			return roles

	async def cog_load(self):
		self.web_server = self.bot.loop.create_task(app.run_task('0.0.0.0', port=os.environ.get('PORT', 7777)))
		self.update_data.start()

	async def cog_unload(self):
		self.update_data.cancel()
		self.web_server.cancel()

	@tasks.loop()
	async def web_server(self):
		app.run(debug=True, host='0.0.0.0', port=7777)

	@web_server.before_loop
	async def web_server_before_loop(self):
		await self.bot.wait_until_ready()

	@tasks.loop(minutes=30)
	async def update_data(self):
		try:
			DBL_API = f"https://discordbotlist.com/api/v1/bots/{self.bot.user.id}/stats"
			header = {"Authorization":DBL_Token}
			data ={"guilds":len(self.bot.guilds), "users":len(self.bot.users)}
			async with self.bot.session.post(DBL_API, data=data, headers=header) as r:
				if r.status == 200:
					print("Successfully Updated Discord Bot List Stats")
				if r.status != 200:
					print("Could Not Update Discord Bot List Stats")
		except Exception as e:
			print(str(e))
		try:
			DB_API = f"https://discord.bots.gg/api/v1/bots/{self.bot.user.id}/stats"
			header = {"Authorization":DB_Token}
			data ={"guildCount":len(self.bot.guilds)}
			async with self.bot.session.post(DB_API, json=data, headers=header) as r:
				if r.status == 200:
					print("Successfully Updated Discord Bots Stats")
				if r.status != 200:
					print("Could Not Update Discord Bots Stats")
		except Exception as e:
			print(str(e))

	@update_data.before_loop
	async def before_update_data(self):
		await self.bot.wait_until_ready()

async def setup(bot):
	await bot.add_cog(Server(bot))