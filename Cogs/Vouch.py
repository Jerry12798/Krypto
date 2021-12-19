import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime



class Vouch(commands.Cog, name="Vouch"):
	def __init__(self,bot):
		self.bot = bot
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)

	@commands.command() # Vouch Command
	async def vouch(self, ctx, member_user: discord.Member=None, *, reason=None):
		if not member_user:
			embed = discord.Embed(title="__**Vouch Error**__", description=f"Specify a Member to Vouch for.\n`{self.bot.prefix}vouch <Mention Member> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if member_user.id == ctx.author.id:
			embed = discord.Embed(title="__**Vouch Error**__", description=f"You can't Vouch for yourself.\n`{self.bot.prefix}vouch <Mention Member> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Vouch Error**__", description=f"Specify the Description of your Vouch.\n`{self.bot.prefix}vouch <Mention Member> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		collection = self.bot.db["Eco_total_vouches"]
		total = 0
		grab_total = collection.find({}, {"_id": 0, "Guild": 0})
		async for m in grab_total:
			total = m["Total_Vouches"]
		total += 1
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		embed_2 = discord.Embed(title=f"__**Incoming Vouch**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
		embed_2.add_field(name="Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name="Vouch ID:", value=f"**{total}**", inline=False)
		embed_2.add_field(name="Details:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		message = await mod_log.send(embed=embed_2)
		counter = {}
		counter ["Total_Vouches"] = total
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = message.id
		log ["Member"] = member_user.id
		log ["Buyer"] = ctx.author.id
		log ["Vouch_ID"] = total
		log ["Vouch"] = reason
		old_counter = {}
		await collection_2.insert_one(log)
		await collection.delete_one(old_counter)
		await collection.insert_one(counter)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Submitted**\n**Vouch ID:** `{total}`\n*You MUST Clearly State Items Received & Amount if Applicable. If you have not use the Revouch Command below.*\n`{Bot_Prefix}revouch <Vouch ID> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		message = await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Revouch Command
	async def revouch(self, ctx, total: int=None, *, reason=None):
		if not total:
			embed = discord.Embed(title="__**Revouch Error**__", description=f"Specify the Vouch ID.\n`{self.bot.prefix}revouch <Vouch ID> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Revouch Error**__", description=f"Specify the Description of your Vouch.\n`{self.bot.prefix}revouch <Vouch ID> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": total}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_message = x["Message"]
		if not grab_buyer == ctx.author.id:
			embed = discord.Embed(title="__**Revouch Error**__", description=f"You can only Revouch for your Vouches.\n`{self.bot.prefix}revouch <Vouch ID> <Vouch Details>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		member_user = ctx.guild.get_member(member_user_id)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		message = await mod_log.fetch_message(grab_message)
		embed_2 = discord.Embed(title=f"__**Incoming Vouch**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
		embed_2.add_field(name="Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name="Vouch ID:", value=f"**{total}**", inline=False)
		embed_2.add_field(name="Details:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await message.edit(embed=embed_2)
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Member"] = member_user.id
		log ["Message"] = message.id
		log ["Buyer"] = ctx.author.id
		log ["Vouch_ID"] = total
		log ["Vouch"] = reason
		old_log = {"Vouch_ID": total}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Resubmitted**\n**Vouch ID:** `{total}`\n*{reason}*", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Vouches Command
	async def vouches(self, ctx, memberz: discord.Member=None):
		if memberz is None:
			memberz = ctx.author
		collection_2 = self.bot.db["Eco_member_vouches"]
		collection_3 = self.bot.db["Eco_profile_banner"]
		collection_4 = self.bot.db["Eco_profile_link"]

		profile_banner = None
		grab_banner = collection_3.find({"Member": memberz.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			profile_banner = x["Message"]
		profile_link = "-"
		grab_banner = collection_4.find({"Member": memberz.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			profile_link = x["Message"]

		bag = None
		order = ""
		counter = 1
		grab_bag = collection_2.find({"Member": memberz.id}, {"_id": 0})
		async for m in grab_bag:
			bag = m["Items"]
		if bag is None:
			embed = discord.Embed(title=f"**{memberz}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** 0\n**Positive:** 0\n**Negative:** 0\n__**Shop Link**__\n{profile_link}\n{memberz} has no Vouches..\nBe sure to use a Middleman", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=memberz.avatar_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.avatar_url_as(format=None, static_format="png")))
			if not profile_banner is None:
				embed.set_image(url=f"{profile_banner}")
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		for m in bag[0:10]:
			order += f"**{counter}:** {m}\n"
			counter += 1
		if len(bag) <= 0:
			embed = discord.Embed(title=f"**{memberz}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** 0\n**Positive:** 0\n**Negative:** 0\n__**Shop Link**__\n{profile_link}\n{memberz} has no Vouches..\nBe sure to use a Middleman", timestamp=datetime.utcnow(), color=0xff0000)
			embed.add_field(name="__**Vouches**__", value=f"{order}", inline=False)
			embed.set_thumbnail(url=memberz.avatar_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.avatar_url_as(format=None, static_format="png")))
			if not profile_banner is None:
				embed.set_image(url=f"{profile_banner}")
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed = discord.Embed(title=f"**{memberz}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** {len(bag)}\n**Positive:** {len(bag)}\n**Negative:** 0\n__**Shop Link**__\n{profile_link}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="__**Vouches**__", value=f"{order}", inline=False)
		embed.set_thumbnail(url=memberz.avatar_url_as(format=None, static_format="png"))
		embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.avatar_url_as(format=None, static_format="png")))
		if not profile_banner is None:
			embed.set_image(url=f"{profile_banner}")
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		
		pages = 1
		if len(bag) > 10:
			page = len(bag)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)
		if len(bag) <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_vouches"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["User"] = memberz.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Reasons"] = bag
		log ["Warnings"] = len(bag)
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

	@commands.command() # Set Profile Banner
	async def vbanner(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Setup Error**__", description=f"Attach Banner URL.\n`{self.bot.prefix}vbanner <Banner URL>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if not content.startswith("https://"):
			embed = discord.Embed(title="__**Setup Error**__", description=f"Please Enter a Valid Invite.\n`{self.bot.prefix}vbanner <Banner URL>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_profile_banner"]
		log = {}
		log ["Member"] = ctx.author.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Profile Setup**__", description=f"Your Banner has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Member"]}
		if ctx.author.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Profile Setup**__", description=f"Your Banner has been changed to\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.author.id in guildz:
			old_log = {"Member": ctx.author.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return

	@commands.command() # Set Profile Link
	async def vlink(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Setup Error**__", description=f"Attach Shop URL.\n`{self.bot.prefix}vlink <Shop URL>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if not content.startswith("https://"):
			embed = discord.Embed(title="__**Setup Error**__", description=f"Please Enter a Valid URL.\n`{self.bot.prefix}vlink <Shop URL>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_profile_link"]
		log = {}
		log ["Member"] = ctx.author.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Profile Setup**__", description=f"Your Shop Link has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Member"]}
		if ctx.author.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Profile Setup**__", description=f"Your Shop Link has been changed to\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.author.id in guildz:
			old_log = {"Member": ctx.author.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return



	@commands.command() # Approve Command
	@is_owner()
	async def approve(self, ctx, total: int=None):
		if not total:
			embed = discord.Embed(title="__**Approve Error**__", description=f"Specify the Vouch ID.\n`{self.bot.prefix}approve <Vouch ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": total}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_guild = x["Guild"]
			grab_message = x["Vouch"]
			guild = self.bot.get_guild(grab_guild)
			member_user = guild.get_member(member_user_id)
			buyer = guild.get_member(grab_buyer)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		collection_4 = self.bot.db["Eco_member_vouches"]
		order = [f"**{grab_message}** *~Vouched by {buyer}*"]
		grab_items = collection_4.find({"Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_items:
			bag = m["Items"]
			order += bag
		log = {}
		log ["Member"] = member_user.id
		log ["Items"] = order
		old_log = {"Member": member_user.id}
		await collection_4.delete_one(old_log)
		await collection_4.insert_one(log)
		pending_log = {"Vouch_ID": total}
		await collection_2.delete_one(pending_log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Approved**\n**Vouch ID:** `{total}`\n__**Receiver:**__\n{member_user}\n__**Vouched By:**__\n{buyer}\n{order[0]}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
		embed.set_thumbnail(url=buyer.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		try:
			await member_user.send(embed=embed)
		except:
			pass
		try:
			await buyer.send(embed=embed)
		except:
			pass
		await ctx.message.delete()
	@approve.error
	async def approve_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Approve Error**__", description=f"You are not Authorized to Approve Vouches with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Deny Command
	@is_owner()
	async def deny(self, ctx, total: int=None):
		if not total:
			embed = discord.Embed(title="__**Deny Error**__", description=f"Specify the Vouch ID.\n`{self.bot.prefix}deny <Vouch ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": total}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_guild = x["Guild"]
			grab_message = x["Vouch"]
			guild = self.bot.get_guild(grab_guild)
			member_user = guild.get_member(member_user_id)
			buyer = guild.get_member(grab_buyer)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		pending_log = {"Vouch_ID": total}
		await collection_2.delete_one(pending_log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Denied**\n**Vouch ID:** `{total}`\n__**Receiver:**__\n{member_user}\n__**Vouched By:**__\n{buyer}\n{grab_message}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
		embed.set_thumbnail(url=buyer.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		try:
			await member_user.send(embed=embed)
		except:
			pass
		try:
			await buyer.send(embed=embed)
		except:
			pass
		await ctx.message.delete()
	@deny.error
	async def deny_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Deny Error**__", description=f"You are not Authorized to Deny Vouches with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		collection = self.bot.db["AM_vouches"] # Paginate Vouches
		collection_3 = self.bot.db["Eco_profile_banner"]
		collection_4 = self.bot.db["Eco_profile_link"]
		menu = collection.find({})
		helps = []
		counter = 1
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				checking = x["User"]
				Channel = x["Channel"]
				reasons = x["Reasons"]
				warnings = x["Warnings"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				member_user = guild.get_member(checking)
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
			for x in reasons[min_items:max_items]:
				order += f"**{place}:** {x}\n"
				place += 1
			profile_banner = None
			grab_banner = collection_3.find({"Member": member_user.id}, {"_id": 0, "Guild": 0})
			async for x in grab_banner:
				profile_banner = x["Message"]
			profile_link = "-"
			grab_banner = collection_4.find({"Member": member_user.id}, {"_id": 0, "Guild": 0})
			async for x in grab_banner:
				profile_link = x["Message"]
			embed = discord.Embed(title=f"**{member_user}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** {warnings}\n**Positive:** {warnings}\n**Negative:** 0\n__**Shop Link**__\n{profile_link}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.add_field(name="__**Vouches**__", value=f"{order}", inline=False)
			embed.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.avatar_url_as(format=None, static_format="png")))
			if not profile_banner is None:
				embed.set_image(url=f"{profile_banner}")
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

def setup(bot):
	bot.add_cog(Vouch(bot))