import motor.motor_asyncio



async def remove_guild_data(db=None, guild_id=None):
	guild_cursor = {"Guild": guild_id}
	collection = db["AM_autorole"]
	await collection.delete_one(guild_cursor)
	collection = db["AM_goodbye"]
	await collection.delete_one(guild_cursor)
	collection = db["AM_no_bad_words"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_no_invites"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_no_links"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_spam"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_spam_mentions"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_spam_caps"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_tmute"]
	await collection.delete_many(guild_cursor)
	collection = db["AM_welcome"]
	await collection.delete_one(guild_cursor)
	collection = db["AM_welcome_channel"]
	await collection.delete_one(guild_cursor)
	collection = db["AM_welcome_dm"]
	await collection.delete_one(guild_cursor)

	collection = db["Bump_guild_banner"]
	await collection.delete_one(guild_cursor)
	collection = db["Bump_guild_channels"]
	await collection.delete_one(guild_cursor)
	collection = db["Bump_guild_description"]
	await collection.delete_one(guild_cursor)
	collection = db["Bump_guild_invite"]
	await collection.delete_one(guild_cursor)

	collection = db["Config_ad_roles"]
	await collection.delete_many(guild_cursor)
	collection = db["Config_announcements"]
	await collection.delete_one(guild_cursor)
	collection = db["Config_global_level_prompt"]
	await collection.delete_one(guild_cursor)
	collection = db["Config_hire"]
	await collection.delete_many(guild_cursor)
	collection = db["Config_iOS_channel"]
	await collection.delete_one(guild_cursor)
	collection = db["Config_level_prompt"]
	await collection.delete_one(guild_cursor)
	collection = db["Config_mute_role"]
	await collection.delete_one(guild_cursor)
	collection = db["Config_phone"]
	await collection.delete_one(guild_cursor)
	collection = db["Config_prefixes"]
	await collection.delete_one(guild_cursor)

	collection = db["Eco_guild_balance"]
	await collection.delete_one(guild_cursor)
	collection = db["Ecp_guild_shop"]
	await collection.delete_one(guild_cursor)
	collection = db["Eco_member_balance"]
	await collection.delete_one(guild_cursor)
	collection = db["Eco_member_shop"]
	await collection.delete_many(guild_cursor)
	collection = db["Eco_purchased"]
	await collection.delete_many(guild_cursor)

	collection = db["Mod_info"]
	await collection.delete_many(guild_cursor)
	collection = db["Mod_member_ads"]
	await collection.delete_many(guild_cursor)
	collection = db["Mod_rolemenu"]
	await collection.delete_many(guild_cursor)
	collection = db["Mod_warnings"]
	await collection.delete_many(guild_cursor)

	collection = db["ad"]
	await collection.delete_many(guild_cursor)
	collection = db["ad_logs"]
	await collection.delete_many(guild_cursor)
	collection = db["logs"]
	await collection.delete_one(guild_cursor)

async def get_user_data(db=None, user_id=None):
	vBanner = False
	vLink = False
	collection = db["Eco_profile_banner"]
	async for m in collection.find({"Member": user_id}, {"_id": 0}):
		vBanner = m["Message"]
	collection = db["Eco_profile_link"]
	async for m in collection.find({"Member": user_id}, {"_id": 0}):
		vLink = m["Message"]
	return dict(vBanner=vBanner, vLink=vLink)

async def update_profile(db=None, data=None, username=None, user_id=None):
	for x, y in data.items():
		if y == "":
			continue
		log = {}
		log ["Member_Name"] = str(username)
		log ["Member"] = int(user_id)
		old_log = {"Member": int(user_id)}
		if x == "vBanner":
			collection = db["Eco_profile_banner"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "vLink":
			collection = db["Eco_profile_link"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

	return dict(status_code=200, status=f"{username} has Successfully Updated their Profile Information!")

async def get_guild_data(db=None, guild_id=None):
	lcID = False
	jcID = False
	mrID = False
	arID = False
	ambID = []
	amiID = []
	amlID = []
	ammID = []
	amcID = []
	Prefixes = False
	jlMessage = False
	llMessage = False
	jdMessage = False
	uStart = False
	sStart = False
	bLimit = False
	sbLimit = False
	sFeed = False
	sInvite = False
	sBanner = False
	sDescription = False
	iID = False
	kID = False
	pID = False
	sLevels = False
	gLevels = False
	collection = db["logs"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		lcID = m["Channel"]
	collection = db["AM_welcome_channel"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		jcID = m["Channel"]
	collection = db["Config_mute_role"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		mrID = m["Role"]
	collection = db["AM_autorole"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		arID = m["Role"]
	collection = db["AM_no_bad_words"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		ambID += {m["Channel"]}
	if ambID == []:
		ambID = False
	collection = db["AM_no_invites"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		amiID += {m["Channel"]}
	if amiID == []:
		amiID = False
	collection = db["AM_no_links"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		amlID += {m["Channel"]}
	if amlID == []:
		amlID = False
	collection = db["AM_spam_mentions"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		ammID += {m["Channel"]}
	if ammID == []:
		ammID = False
	collection = db["AM_spam_caps"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		amcID += {m["Channel"]}
	if amcID == []:
		amcID = False
	collection = db["Config_prefixes"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		Prefixes = m["Prefix"]
	collection = db["AM_welcome"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		jlMessage = m["Message"]
	collection = db["AM_goodbye"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		llMessage = m["Message"]
	collection = db["AM_welcome_DM"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		jdMessage = m["Message"]
	collection = db["Eco_limits"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		uStart = m["User"]
		sStart = m["Server"]
		bLimit = m["Bag"]
		sbLimit = m["Box"]
	collection = db["Bump_guild_channels"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		sFeed = m["Channel"]
	collection = db["Bump_guild_invite"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		sInvite = m["Message"]
	collection = db["Bump_guild_banner"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		sBanner = m["Message"]
	collection = db["Bump_guild_description"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		sDescription = m["Message"]
	collection = db["Config_iOS_channel"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		iID = m["Channel"]
	collection = db["Config_announcements"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		kID = m["Channel"]
	collection = db["Config_phone"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		pID = m["Channel"]
	collection = db["Config_level_prompt"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		test = m["Guild"]
		if test == guild_id:
			sLevels = True
	collection = db["Config_global_level_prompt"]
	async for m in collection.find({"Guild": guild_id}, {"_id": 0}):
		test = m["Guild"]
		if test == guild_id:
			gLevels = True
	return dict(lcID=lcID, jcID=jcID, mrID=mrID, arID=arID, ambID=ambID, amiID=amiID, amlID=amlID, ammID=ammID, amcID=amcID, Prefixes=Prefixes, jlMessage=jlMessage, llMessage=llMessage, jdMessage=jdMessage, uStart=uStart, sStart=sStart, bLimit=bLimit, sbLimit=sbLimit, sFeed=sFeed, sInvite=sInvite, sBanner=sBanner, sDescription=sDescription, iID=iID, kID=kID, pID=pID, sLevels=sLevels, gLevels=gLevels)



async def update_server(db=None, data=None, guild=None, server=None):
	for x, y in data.items():
		if y == "":
			continue
		log = {}
		log ["Guild_Name"] = str(guild)
		log ["Guild"] = int(server)
		old_log = {"Guild": int(server)}
		if x == "lcID":
			if y == "Select Channel":
				continue
			collection = db["logs"]
			log ["Channel"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "jcID":
			if y == "Select Channel":
				continue
			collection = db["AM_welcome_channel"]
			log ["Channel"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "mrID":
			if y == "Select Role":
				continue
			collection = db["Config_mute_role"]
			log ["Role"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "arID":
			if y == "Select Role":
				continue
			collection = db["AM_autorole"]
			log ["Role"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "ambID":
			collection = db["AM_no_bad_words"]
			channels = []
			async for x in collection.find({"Guild": int(server)}, {"_id": 0, "Guild": 0}):
				channels += {x["Channel"]}
			if int(y) not in channels:
				log ["Channel"] = int(y)
				await collection.insert_one(log)
			if int(y) in channels:
				old_log = {"Channel": int(y)}
				await collection.delete_one(old_log)
			continue

		if x == "amiID":
			collection = db["AM_no_invites"]
			channels = []
			async for x in collection.find({"Guild": int(server)}, {"_id": 0, "Guild": 0}):
				channels += {x["Channel"]}
			if int(y) not in channels:
				log ["Channel"] = int(y)
				await collection.insert_one(log)
			if int(y) in channels:
				old_log = {"Channel": int(y)}
				await collection.delete_one(old_log)
			continue

		if x == "amlID":
			collection = db["AM_no_links"]
			channels = []
			async for x in collection.find({"Guild": int(server)}, {"_id": 0, "Guild": 0}):
				channels += {x["Channel"]}
			if int(y) not in channels:
				log ["Channel"] = int(y)
				await collection.insert_one(log)
			if int(y) in channels:
				old_log = {"Channel": int(y)}
				await collection.delete_one(old_log)
			continue

		if x == "ammID":
			collection = db["AM_spam_mentions"]
			channels = []
			async for x in collection.find({"Guild": int(server)}, {"_id": 0, "Guild": 0}):
				channels += {x["Channel"]}
			if int(y) not in channels:
				log ["Channel"] = int(y)
				await collection.insert_one(log)
			if int(y) in channels:
				old_log = {"Channel": int(y)}
				await collection.delete_one(old_log)
			continue

		if x == "amcID":
			collection = db["AM_spam_caps"]
			channels = []
			async for x in collection.find({"Guild": int(server)}, {"_id": 0, "Guild": 0}):
				channels += {x["Channel"]}
			if int(y) not in channels:
				log ["Channel"] = int(y)
				await collection.insert_one(log)
			if int(y) in channels:
				old_log = {"Channel": int(y)}
				await collection.delete_one(old_log)
			continue

		if x == "Prefixes":
			new = ""
			new_prefixes = y.split(" ")
			for x in new_prefixes:
				new += x
			to_add = new.split(",")
			collection = db["Config_prefixes"]
			prefixes = []
			async for m in collection.find({"Guild": int(server)}, {"_id": 0}):
				prefixes += m["Prefix"]
			for z in to_add:
				if z in prefixes:
					continue
				prefixes += z
			log ["Prefix"] = prefixes
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "jlMessage":
			collection = db["AM_welcome"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "llMessage":
			collection = db["AM_goodbye"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "jdMessage":
			collection = db["AM_welcome_DM"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue



		if x == "uStart":
			collection = db["Eco_limits"]
			async for m in collection.find({"Guild": int(server)}, {"_id": 0}):
				Bag_Limit = m["Bag"]
				Box_Limit = m["Box"]
				Guild_Start =m["Server"]
			log = {}
			log ["Guild"] = int(server)
			log ["Bag"] = Bag_Limit
			log ["Box"] = Box_Limit
			log ["Server"] = Guild_Start
			log ["User"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "sStart":
			collection = db["Eco_limits"]
			async for m in collection.find({"Guild": int(server)}, {"_id": 0}):
				Bag_Limit = m["Bag"]
				Box_Limit = m["Box"]
				User_Start= m["User"]
			log = {}
			log ["Guild"] = int(server)
			log ["Bag"] = Bag_Limit
			log ["Box"] = Box_Limit
			log ["Server"] = int(y)
			log ["User"] = User_Start
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "bLimit":
			collection = db["Eco_limits"]
			async for m in collection.find({"Guild": int(server)}, {"_id": 0}):
				Box_Limit = m["Box"]
				Guild_Start = m["Server"]
				User_Start = m["User"]
			log = {}
			log ["Guild"] = int(server)
			log ["Bag"] = int(y)
			log ["Box"] = Box_Limit
			log ["Server"] = Guild_Start
			log ["User"] = User_Start
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "sbLimit":
			collection = db["Eco_limits"]
			async for m in collection.find({"Guild": int(server)}, {"_id": 0}):
				Bag_Limit = m["Bag"]
				Guild_Start = m["Server"]
				User_Start = m["User"]
			log = {}
			log ["Guild"] = int(server)
			log ["Bag"] = Bag_Limit
			log ["Box"] = int(y)
			log ["Server"] = Guild_Start
			log ["User"] = User_Start
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue



		if x == "sFeed":
			if y == "Select Channel":
				continue
			collection = db["Bump_guild_channels"]
			log ["Channel"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "sInvite":
			collection = db["Bump_guild_invite"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "sBanner":
			collection = db["Bump_guild_banner"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "sDescription":
			collection = db["Bump_guild_description"]
			log ["Message"] = str(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue



		if x == "iID":
			if y == "Select Channel":
				continue
			collection = db["Config_iOS_channel"]
			log ["Channel"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "kID":
			if y == "Select Channel":
				continue
			collection = db["Config_announcements"]
			log ["Channel"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "pID":
			if y == "Select Channel":
				continue
			collection = db["Config_phone"]
			log ["Channel"] = int(y)
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			continue

		if x == "sLevels":
			collection = db["Config_level_prompt"]
			if y == "Enable":
				await collection.delete_one(old_log)
				await collection.insert_one(log)
			if y == "Disable":
				await collection.delete_one(old_log)
			continue

		if x == "gLevels":
			collection = db["Config_global_level_prompt"]
			if y == "Enable":
				await collection.delete_one(old_log)
				await collection.insert_one(log)
			if y == "Disable":
				await collection.delete_one(old_log)
			continue

	return dict(status_code=200, status=f"{guild} has Successfully Updated their Server Information!")