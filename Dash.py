import motor.motor_asyncio, sys, datetime, json, re, os, asyncio, pymongo
from quart import Quart, g, request, abort, jsonify, redirect, url_for, render_template, session, flash
from bson.objectid import ObjectId
from requests_oauthlib import OAuth2Session
from Utils.Database import get_guild_data, update_server, get_user_data, update_profile
from datetime import datetime, timedelta


with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

OAUTH2_CLIENT_ID = config['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = config['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = config['OAUTH2_REDIRECT_URI']

API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_BASE_URL = "https://discordapp.com/api/oauth2/authorize"
TOKEN_URL = "https://discordapp.com/api/oauth2/token"
ICON_BASE_URL = "https://cdn.discordapp.com/icons/"
AVATAR_BASE_URL = "https://cdn.discordapp.com/avatars/"

MongoDB_Client = config['MongoDB_Client']
client = motor.motor_asyncio.AsyncIOMotorClient(MongoDB_Client)
client.get_io_loop = asyncio.get_running_loop
db = client.Krypto_Configs

owners = config['Owners']
Bot_Prefix = config['Bot_Prefix']
bot = config['Bot_Name']
bot_id = config['Bot_ID']
Bot_Support_Server = config['Bot_Support_Server']

IPC_Key = config['IPC_Key']
IPC_Header = config['IPC_Header']

User_Start = config['User_Start']
Guild_Start = config['Guild_Start']
Bag_Limit = config['Bag_Limit']
Box_Limit = config['Box_Limit']



app = Quart(__name__, static_folder="public", static_url_path="/public")
app.secret_key = IPC_Key
app.permanent_session_lifetime = timedelta(days=30)
app.config["SECRET_KEY"] = OAUTH2_CLIENT_SECRET
#ipc_client = ipc.Client(secret_key=IPC_Key)
request_header = {"Key": IPC_Key}

if "http://" in OAUTH2_REDIRECT_URI:
	os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

def token_updater(token):
	session["oauth2_token"] = token

def make_session(token=None, state=None, scope=None):
	return OAuth2Session(client_id=OAUTH2_CLIENT_ID, token=token, state=state, scope=scope, redirect_uri=OAUTH2_REDIRECT_URI, auto_refresh_kwargs={"client_id": OAUTH2_CLIENT_ID, "client_secret": OAUTH2_CLIENT_SECRET}, auto_refresh_url=TOKEN_URL, token_updater=token_updater)



@app.context_processor
def context_processor():
	return dict(bot=bot, bot_id=bot_id, IPC_Header=IPC_Header, Bot_Support_Server=Bot_Support_Server)

@app.route("/")
async def home():
	collection = db["Site_post"]
	posts = {}
	counter = 1
	all_posts = collection.find({}).sort('Timestamp', pymongo.DESCENDING)
	async for z in all_posts:
		posts [counter] = z
		counter +=1
	return await render_template("Index.html", posts=posts)

@app.route("/commands/")
async def commands():
	return await render_template("Commands.html", Bot_Prefix=Bot_Prefix)

@app.route("/news/<post>/", methods=["POST", "GET"])
async def view_post(post):
	admin = False
	collection = db["Site_post"]
	async for z in collection.find({"_id": ObjectId(f"{post}")}):
		post_data = z
	if "oauth2_token" in session:			
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		user_id = user["id"]
		if int(user_id) in owners:
			admin = True
	return await render_template("News.html", post=post_data, admin=admin)

@app.route("/dashboard/")
async def dashboard():
	if "oauth2_token" in session:
		admin = False
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		name = user["username"]
		tag = user["discriminator"]
		username = f"{name}#{tag}"
		user_id = user["id"]
		if int(user_id) in owners:
			admin = True
		user_avatar = AVATAR_BASE_URL + str(user_id) + "/" + str(user["avatar"])
		guilds_data = discord.get(API_BASE_URL + "/users/@me/guilds").json()
		try:
			if guilds_data['message'] == "You are being rate limited.":
				return redirect(url_for("dashboard"))
		except:
			pass
		#print(guilds_data)
		admin_guilds = {}
		for x in guilds_data:
			if x["permissions"] == 2147483647:
				log = {}
				log ["ID"] = x["id"]
				log ["Name"] = x["name"]
				log ["Icon"] = ICON_BASE_URL + str(x["id"]) + "/" + str(x["icon"])
				admin_guilds [x["id"]] = log
		return await render_template("Dashboard.html", user=username, user_id=user_id, user_avatar=user_avatar, guilds=admin_guilds, admin=admin)
	else:
		return redirect(url_for("login"))

@app.route("/dashboard/<server>/", methods=["POST", "GET"])
async def server_dashboard(server):
	if "oauth2_token" in session:
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		name = user["username"]
		tag = user["discriminator"]
		username = f"{name}#{tag}"
		user_id = user["id"]
		user_avatar = AVATAR_BASE_URL + str(user_id) + "/" + str(user["avatar"])
		guilds_data = discord.get(API_BASE_URL + "/users/@me/guilds").json()
		try:
			if guilds_data['message'] == "You are being rate limited.":
				await flash(f"You are being Rate Limited!", "info")
				return redirect(url_for("dashboard"))
		except:
			pass
		for x in guilds_data:
			if x["permissions"] == 2147483647:
				if x["id"] == str(server):
					guild = x["name"]
					guild_icon = ICON_BASE_URL + str(x["id"]) + "/" + str(x["icon"])
		#members = await ipc_client.request("get_members", guild_id=int(server))
		#bot_guilds = await ipc_client.request("bot_guilds")

		try:
			channels = discord.get(f"http://127.0.0.1:7777/channels?server={server}", headers=request_header).json()
		except:
			await flash(f"Krypto is Offline!", "info")
			return redirect(url_for("dashboard"))
		#channels = await ipc_client.request("get_channels", guild_id=int(server))
		if channels is None:
			await flash(f"Krypto isn't in this Server!", "info")
			return redirect(url_for("dashboard"))
		try:
			roles = discord.get(f"http://127.0.0.1:7777/roles?server={server}", headers=request_header).json()
		except:
			await flash(f"Krypto is Offline!", "info")
			return redirect(url_for("dashboard"))
		#roles = await ipc_client.request("get_roles", guild_id=int(server))
		if roles is None:
			await flash(f"Krypto isn't in this Server!", "info")
			return redirect(url_for("dashboard"))

		role_order = []
		for x in reversed(roles):
			role_order += {x}

		data = await get_guild_data(db=db, guild_id=int(server))

		if request.method == "POST":
			await flash(f"You have Updated Your Server Settings!", "info")
			data = await request.form
			updater = await update_server(db=db, data=data, guild=guild, server=server)
			print(updater)

		return await render_template("Server.html", user=username, user_id=user_id, guild=guild, guild_id=int(server), guild_icon=guild_icon, channels=channels, roles=roles, role_order=role_order, data=data)
		
	else:
		return redirect(url_for("login"))
	

@app.route("/dashboard/user/<user>/", methods=["POST", "GET"])
async def user_dashboard(user):
	if "oauth2_token" in session:
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		name = user["username"]
		tag = user["discriminator"]
		username = f"{name}#{tag}"
		user_id = user["id"]
		user_avatar = AVATAR_BASE_URL + str(user_id) + "/" + str(user["avatar"])

		data = await get_user_data(db=db, user_id=int(user_id))

		if request.method == "POST":
			await flash(f"You have Updated Your Personal Settings!", "info")
			data = await request.form
			updater = await update_profile(db=db, data=data, username=username, user_id=user_id)
			print(updater)

		return await render_template("Profile.html", user=username, user_id=user_id, user_avatar=user_avatar, data=data)
	else:
		return redirect(url_for("login"))

@app.route("/login/", methods=["POST", "GET"])
async def login():
	if "oauth2_token" in session:
		await flash(f"You are Already Logged In!", "info")
		return redirect(url_for("home"))
	else:
		scope = request.args.get("scope", "identify guilds")
		discord = make_session(scope=scope.split(' '))
		authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
		session.permanent = True
		session['oauth2_state'] = state
		return redirect(authorization_url)

@app.route("/logout/")
async def logout():
	if "oauth2_token" in session:
		token = session["oauth2_token"]  
		await flash(f"You have Successfully Logged Out!", "info")
	session.pop("oauth2_token", None)
	return redirect(url_for("home"))

@app.route("/auth/")
async def login_redirect():
	values = await request.values
	if values.get("error"):
		return await request.values["error"]
	else:
		discord = make_session(state=session.get("oauth2_state"))
		token = discord.fetch_token(TOKEN_URL, client_secret=OAUTH2_CLIENT_SECRET, authorization_response=request.url)
		session["oauth2_token"] = token
		return redirect(url_for("dashboard"))

@app.route("/post/", methods=["POST", "GET"])
async def new_post():
	if "oauth2_token" in session:
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		name = user["username"]
		tag = user["discriminator"]
		username = f"{name}#{tag}"
		user_id = user["id"]
		if not int(user_id) in owners:
			await flash(f"You are Not Authorized to Post Announcements!", "info")
			return redirect(url_for("home"))
		user_avatar = AVATAR_BASE_URL + str(user_id) + "/" + str(user["avatar"])

		if request.method == "POST":
			await flash(f"You have Successfully Posted an Announcement!", "info")
			data = await request.form
			collection = db["Site_post"]
			log = {}
			log ["Member_Name"] = str(username)
			log ["Member"] = int(user_id)
			log ["Avatar"] = str(user_avatar)
			log ["Timestamp"] = datetime.utcnow()
			for x, y in data.items():
				if y == "":
					continue
				if x == "pTitle":
					log ["Title"] = str(y)
				if x == "pContent":
					log ["Message"] = str(y)
			await collection.insert_one(log)
			return redirect(url_for("home"))

		return await render_template("Post.html", legend="Create", post=False)
	else:
		return redirect(url_for("login"))

@app.route("/news/<post>/edit/", methods=["POST", "GET"])
async def edit_post(post):
	if "oauth2_token" in session:
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		post_data = False
		collection = db["Site_post"]
		async for z in collection.find({"_id": ObjectId(f"{post}")}):
			post_data = z
		name = user["username"]
		tag = user["discriminator"]
		username = f"{name}#{tag}"
		user_id = user["id"]
		if not int(user_id) in owners:
			await flash(f"You are Not Authorized to Edit Announcements!", "info")
			return redirect(url_for("home"))
		user_avatar = AVATAR_BASE_URL + str(user_id) + "/" + str(user["avatar"])

		if request.method == "POST":
			await flash(f"You have Successfully Edited an Announcement!", "info")
			data = await request.form
			collection = db["Site_post"]
			edit_time = datetime.utcnow()
			for x, y in data.items():
				if y == "":
					continue
				if x == "pTitle":
					title = str(y)
				if x == "pContent":
					content = str(y)
			await collection.update_one({"_id": ObjectId(f"{post}")}, {"$set":{"Title": title, "Message": content, "Edited": edit_time}})
			return redirect(url_for("view_post", post=post))

		return await render_template("Post.html", legend="Edit", post=post_data)
	else:
		return redirect(url_for("login"))

@app.route("/news/<post>/delete/", methods=["POST", "GET"])
async def delete_post(post):
	if "oauth2_token" in session:
		try:
			discord = make_session(token=session.get("oauth2_token"))
			user = discord.get(API_BASE_URL + "/users/@me").json()
		except:
			session.pop("oauth2_token", None)
			return redirect(url_for("login"))
		post_data = False
		collection = db["Site_post"]
		async for z in collection.find({"_id": ObjectId(f"{post}")}):
			post_data = z
		name = user["username"]
		tag = user["discriminator"]
		username = f"{name}#{tag}"
		user_id = user["id"]
		if not int(user_id) in owners:
			await flash(f"You are Not Authorized to Delete Announcements!", "info")
			return redirect(url_for("home"))
		user_avatar = AVATAR_BASE_URL + str(user_id) + "/" + str(user["avatar"])

		#if request.method == "POST":
		if int(user_id) in owners:
			await flash(f"You have Successfully Deleted an Announcement!", "info")
			data = await request.form
			collection = db["Site_post"]
			edit_time = datetime.utcnow()
			await collection.delete_one({"_id": ObjectId(f"{post}")})
			return redirect(url_for("home"))

		return redirect(url_for("view_post", post=post))
	else:
		return redirect(url_for("login"))



if __name__ == "__main__":
	app.run(debug=True, host="0.0.0.0", port=5000)