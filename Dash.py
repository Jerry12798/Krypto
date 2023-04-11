import motor.motor_asyncio, sys, datetime, json, re, os, asyncio, aiohttp, pymongo
from quart import Quart, g, request, abort, jsonify, redirect, url_for, render_template, session, flash, Response
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

Domain = config['Domain']
IPC_Key = config['IPC_Key']
IPC_Header = config['IPC_Header']

User_Start = config['User_Start']
Guild_Start = config['Guild_Start']
Bag_Limit = config['Bag_Limit']
Box_Limit = config['Box_Limit']

Hastebin_Link = "https://paste.krypto.codes"



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
	return dict(bot=bot, bot_id=bot_id, IPC_Header=IPC_Header, Bot_Support_Server=Bot_Support_Server, hastebin=Hastebin_Link)

@app.before_serving
async def startup():
	app.client = aiohttp.ClientSession()

@app.after_serving
async def shutdown():
	app.client.close()

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

@app.route("/embed")
async def embedder():
	return await render_template("Visualizer.html")

@app.route("/ios", methods=["POST", "GET"])
async def ios_login():
	code = request.headers["Key"]
	udid = request.headers["UDID"]
	print(code, udid)
	collection = db['Site_h5gg']
	keys = []
	async for u in collection.find({}, {"_id": 0}):
		keys += {u["Key"]}
	if code == "" or code is None:
		return Response("Enter Your Key!", status=403)
	async for u in collection.find({"Key": code}):
		user_code = u["Key"]
		user_udid = u["UDID"]
		try:
			end = u["Expire"]
		except:
			end = None
		try:
			isAdmin = u["Admin"]
		except:
			isAdmin = 0
	if not code in keys:
		return Response("Entered Key NOT Found!", status=403)
	if user_code == code and user_udid == None:
		await collection.update_one({"Key": code}, {"$set":{"UDID": udid}})
		user_udid = udid
	if user_udid != udid:
		return Response("UDID is Incorrect!", status=403)
	if not end is None:
		td = end - datetime.utcnow()
		if int(td.total_seconds()) < 0:
			return Response("Your Key has Expired!", status=403)

	return Response(f"{isAdmin},Login Successful!", status=201)

@app.route("/h5gg", methods=["POST", "GET"])
async def h5gg_launcher():
	agent = request.headers["User-Agent"]
	if "Windows" in agent:
		abort(403, "PC Login Denied!")
	if request.method == "GET":
		return await render_template("H5GG.html")
	else:
		code = request.headers["Key"]
		udid = request.headers["UDID"]
		print(code, udid)
		collection = db['Site_h5gg']
		keys = []
		async for u in collection.find({}, {"_id": 0}):
			keys += {u["Key"]}
		if code == "" or code is None:
			return Response("Enter Your Key!", status=403)
		async for u in collection.find({"Key": code}):
			user_code = u["Key"]
			user_udid = u["UDID"]
			try:
				end = u["Expire"]
			except:
				end = None
		if not code in keys:
			return Response("Entered Key NOT Found!", status=403)
		if user_code == code and user_udid == None:
			await collection.update_one({"Key": code}, {"$set":{"UDID": udid}})
			user_udid = udid
		if user_udid != udid:
			return Response("UDID is Incorrect!", status=403)
		if not end is None:
			td = end - datetime.utcnow()
			if int(td.total_seconds()) < 0:
				return Response("Your Key has Expired!", status=403)

		ios_html = open('templates/iOS2.html', 'r')

		data = {
			"code": code, 
			"ui": ios_html.read(), 
			"m_src": "/public/js/sdom.js",
			"e_src": "/public/js/PSE.js",
		}

		return data, 201

@app.route("/show/<html>/", methods=["POST", "GET"])
async def show_data(html):
	if request.method == 'GET':
		if 'PASTE-' in html:
			fix = html.split('-')
			html = fix[1]
			async with app.client.get(f'{Hastebin_Link}/raw/{html}') as r:
				haste_data = await r.text()
			temp = open(f'templates/tmp/{html}.html', 'w+')
			temp.write(haste_data)
			temp.seek(0)
			return await render_template(f"tmp/{html}.html")
		else:
			return await render_template(f"tmp/{html}.html")
	if html == 'NEW':
		data = await request.get_data()
		data = json.loads(data)
		return await render_template("Show.html", data=data)

@app.route("/commands/")
async def commands():
	with open('Commands.json', 'r') as cmd_list:
		data = json.load(cmd_list)
	return await render_template("Commands.html", data=data, Bot_Prefix=Bot_Prefix)

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
			await flash(f"{bot} is Offline or isn't in this Server!", "info")
			return redirect(url_for("dashboard"))
		#channels = await ipc_client.request("get_channels", guild_id=int(server))
		if channels is None:
			await flash(f"{bot} isn't in this Server or can't see Any Channels!", "info")
			return redirect(url_for("dashboard"))
		try:
			roles = discord.get(f"http://127.0.0.1:7777/roles?server={server}", headers=request_header).json()
		except:
			await flash(f"{bot} is Offline or isn't in this Server!", "info")
			return redirect(url_for("dashboard"))
		#roles = await ipc_client.request("get_roles", guild_id=int(server))
		if roles is None:
			await flash(f"{bot} isn't in this Server or can't see Any Roles!", "info")
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