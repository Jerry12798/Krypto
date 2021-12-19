import discord
import asyncio
import json
import time
import pymongo
import motor.motor_asyncio
import pytz
import random
from discord.ext import commands
from datetime import datetime
from pytz import timezone

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

User_Start = config['User_Start']
Guild_Start = config['Guild_Start']
Bag_Limit = config['Bag_Limit']
Box_Limit = config['Box_Limit']



class Economy(commands.Cog, name="Economy"):
	def __init__(self, bot):
		self.bot = bot
		self.bot.user_start = User_Start
		self.bot.guild_start = Guild_Start
		self.bot.bag_limit = Bag_Limit
		self.bot.box_limit = Box_Limit
		
	@commands.command() # Apply Command
	async def apply(self, ctx):
		collection_2 = self.bot.db["Eco_member_balance"]
		collection = self.bot.db ["Eco_guild_balance"]
		collection_3 = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_limits"]
		collection_5 = self.bot.db["Eco_member_shop"]
		check = None
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			check = m["Guild"]
		if check is None:
			embed = discord.Embed(title="__**Apply Error**__", description=f"**{ctx.guild}** has not Registered with {self.bot.user.mention} to use Currency Exchange.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		User_Start = 0
		async for m in collection_4.find({"Guild": ctx.guild.id}, {"_id": 0}):
			User_Start = m["User"]
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Member"] = ctx.author.id
		log ["Currency"] = User_Start
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}):
			member = m["Member"]
			if member == ctx.author.id:
				embed = discord.Embed(title="__**Apply Error**__", description=f"You already have an Account.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
		await collection_2.insert_one(log)
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Member"] = ctx.author.id
		log ["Items"] = []
		await collection_3.insert_one(log)
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Member"] = ctx.author.id
		log ["Items"] = []
		log ["Price"] = []
		await collection_5.insert_one(log)
		embed = discord.Embed(title="__**Account Created**__", description="You have Successfully Created an Account.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Bag Command
	async def bag(self, ctx, memberz: discord.Member=None):
		if memberz is None:
			memberz = ctx.author
		collection_2 = self.bot.db["Eco_purchased"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection = self.bot.db["Eco_member_balance"]
		sender = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Bag Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Bag Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		bag = None
		order = ""
		counter = 1
		grab_bag = collection_2.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0, "Guild": 0})
		async for m in grab_bag:
			bag = m["Items"]
		if bag is None:
			embed = discord.Embed(title="__**Bag**__", description=f"{memberz} has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		for m in bag[0:10]:
			order += f"**{counter}:** {m}\n"
			counter += 1
		if len(bag) <= 0:
			embed = discord.Embed(title="__**Bag**__", description=f"{memberz} has `0` Items..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed = discord.Embed(title="__**Bag**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		
		pages = 1
		if len(bag) > 10:
			page = len(bag)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)
		if len(bag) <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_purchased"]
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

	@commands.command() # Buy Command
	async def buy(self, ctx, queue:int=None, *, memberz: discord.Member=None):
		if queue is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"You must Specify the Item Index &/or Member.\n`{self.bot.prefix}buy <Item Index>` *or* `{self.bot.prefix}buy <Item Index> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_4 = self.bot.db["Eco_purchased"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_5 = self.bot.db["Eco_limits"]
		recipent = None
		server = None
		sender = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		if not memberz is None:
			if memberz.id == ctx.author.id:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"You can't Purchase your Own Items..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			async for m in collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0}):
				recipent = m["Member"]
			if recipent is None:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"**{memberz}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
		shop = None
		
		async for m in collection_5.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
		if not memberz is None:
			if memberz.id == ctx.author.id:
				return
			collection_2 = self.bot.db["Eco_member_shop"]
			member_info = collection.find({"Guild": ctx.guild.id}, {"_id": 0})
			async for m in member_info:
				user = m["Member"]
				balance = m["Currency"]
				if user == ctx.author.id:
					buyer_balance = balance
				if user == memberz.id:
					seller_balance = balance
			grab_shop = collection_2.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0, "Guild": 0})
			async for m in grab_shop:
				shop = m["Items"]
				price = m["Price"]
			if shop is None:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"{memberz.display_name} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
			if shop == 0:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"{memberz.display_name} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
			item = shop[queue-1]
			total = price[queue-1]
			ending_balance = buyer_balance - price[queue-1]
			new_balance = seller_balance + price[queue-1]
			shop.pop(queue-1)
			price.pop(queue-1)
			if ending_balance <= 0:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"You have Insufficent Funds to make this Purchase.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			order = [f"{item}"]
			#order = [f"**{item}** *~Sold by {memberz}*"]
			grab_items = collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
			async for m in grab_items:
				bag = m["Items"]
				order += bag
			if len(order) > Bag_Limit:
				embed = discord.Embed(title="__**Bag Full**__", description=f"You already have **{Bag_Limit}** Items in your Bag.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": ending_balance}})
			await collection.update_one({"Guild": ctx.guild.id, "Member": memberz.id}, {"$set":{"Currency": new_balance}})
			await collection_2.update_one({"Member": memberz.id}, {"$set":{"Items": shop, "Price": price}})
			await collection_4.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": order}})
			embed = discord.Embed(title="__**Purchase Successful**__", description=f"You have Successfully Purchased **{item}** from **{memberz.user.mention}** for **{total}**.", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			embed_2 = discord.Embed(title="__***Purchase***__", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_author(name=f"{memberz}", icon_url=memberz.avatar_url_as(format=None, static_format="png"))
			embed_2.add_field(name="__**:satellite: Server:**__", value=f"**{ctx.guild}**", inline=False)
			embed_2.add_field(name="__**:newspaper: Item:**__", value=f"{item}", inline=False)
			embed_2.add_field(name="__**:money_with_wings: Price:**__", value=f"{total}", inline=False)
			embed_2.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		collection_2 = self.bot.db["Eco_guild_shop"]
		member_info = collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		shop = None
		grab_shop = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		async for m in grab_shop:
			shop = m["Items"]
			price = m["Price"]
		if shop is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"{ctx.guild} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"{ctx.guild} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		grab_bank = collection_3.find({"Guild": ctx.guild.id}, {"_id": 0})
		async for m in grab_bank:
			guild_balance = m["Currency"]
		item = shop[queue-1]
		total = price[queue-1]
		ending_balance = balance - price[queue-1]
		bank = guild_balance + price[queue-1]
		if ending_balance < 0:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"You have Insufficent Funds to make this Purchase.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		order = [f"{item}"]
		#order = [f"**{item}** *~Sold by {ctx.guild}*"]
		grab_items = collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
		async for m in grab_items:
			bag = m["Items"]
			order += bag
		if len(order) > Bag_Limit:
			embed = discord.Embed(title="__**Bag Full**__", description=f"You already have **{Bag_Limit}** Items in your Bag.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": ending_balance}})
		await collection_3.update_one({"Guild": ctx.guild.id}, {"$set":{"Currency": bank}})
		await collection_4.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": order}})
		embed = discord.Embed(title="__**Purchase Successful**__", description=f"You have Successfully Purchased ***{item}*** for **{price[queue-1]}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__***Purchase***__", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name="__**:newspaper: Item:**__", value=f"{item}", inline=False)
		embed_2.add_field(name="__**:money_with_wings: Price:**__", value=f"{total}", inline=False)
		embed_2.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Shop Command
	async def shop(self, ctx, *, memberz: discord.Member=None):
		collection = self.bot.db["Eco_member_shop"]
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if not memberz is None:
			async for m in collection_4.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0}):
				recipent = m["Member"]
			if recipent is None:
				embed = discord.Embed(title="__**Shop Error**__", description=f"**{memberz}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
		shop = None
		order = ""
		counter = 1
		if not memberz is None:
			grab_shop = collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0, "Guild": 0})
			async for m in grab_shop:
				shop = m["Items"]
				price = m["Price"]
			if shop is None:
				embed = discord.Embed(title="__**Shop**__", description=f"{memberz.display_name} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
			if len(shop) <= 0:
				embed = discord.Embed(title="__**Shop**__", description=f"{memberz.display_name} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
			for m in shop[0:10]:
				order += f"**{counter}:** {m} **({price[counter-1]})**\n"
				counter += 1
			embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			
			pages = 1
			if len(shop) > 10:
				page = len(shop)/10
				pages = int(page)+1
			message = await ctx.send(embed=embed)
			if len(shop) <= 10:
				await ctx.message.delete()
				return
			collection = self.bot.db["AM_shop"]
			log = {}
			log ["Guild_Name"] = ctx.guild.name
			log ["Guild"] = ctx.guild.id
			log ["Author"] = ctx.author.id
			log ["User"] = memberz.id
			log ["Channel"] = ctx.channel.id
			log ["Message"] = message.id
			log ["Warnings"] = len(shop)
			log ["Shop"] = shop
			log ["Price"] = price
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
			return
		grab_shop = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		shop = None
		async for m in grab_shop:
			shop = m["Items"]
			price = m["Price"]
		if shop is None:
			embed = discord.Embed(title="__**Shop**__", description=f"{ctx.guild} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Shop**__", description=f"{ctx.guild} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		for m in shop[0:10]:
			order += f"**{counter}:** {m} **({price[counter-1]})**\n"
			counter += 1
		embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		
		pages = 1
		if len(shop) > 10:
			page = len(shop)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)
		if len(shop) <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_shop"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Warnings"] = len(shop)
		log ["Shop"] = shop
		log ["Price"] = price
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

	@commands.command() # Balance Command
	async def balance(self, ctx, *, memberz: discord.Member=None):
		if memberz is None:
			memberz = ctx.author
		collection_2 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Balance Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection_2.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Balance Error**__", description=f"**{memberz}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		counter = "N/A"
		money = "N/A" 
		counter = 0
		if memberz is None:
			async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}).sort("Currency", pymongo.DESCENDING):
				member = m["Member"]
				money = m["Currency"]
				counter += 1
				if member == ctx.author.id:
					embed = discord.Embed(title="__**User Balance**__", description=f":money_with_wings: __**Balance:**__ {money}\n:classical_building: __**Rank in Server:**__ {counter}", timestamp=datetime.utcnow(), color=0xac5ece)
					embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
					await ctx.send(embed=embed)
					await ctx.message.delete()
					return
			embed = discord.Embed(title="__**User Balance**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}).sort("Currency", pymongo.DESCENDING):
			member = m["Member"]
			money = m["Currency"]
			counter += 1
			if member == memberz.id:
				embed = discord.Embed(title="__**User Balance**__", description=f":money_with_wings: __**Balance:**__ {money}\n:classical_building: __**Rank in Server:**__ {counter}", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
		embed = discord.Embed(title="__**User Balance**__", description=f"{memberz.display_name} has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
		return

	@commands.command() # Guild Balance Command
	async def gbalance(self, ctx):
		collection_2 = self.bot.db["Eco_guild_balance"]
		server = None

		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Balance Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		counter = "N/A"
		money = "N/A" 
		counter = 0
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}):
			guild = m["Guild"]
			money = m["Currency"]
			counter += 1
			if guild == ctx.guild.id:
				embed = discord.Embed(title="__**Server Balance**__", description=f"**{money}**", timestamp=datetime.utcnow(), color=0xac5ece)
				embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				await ctx.message.delete()
				return
		embed = discord.Embed(title="__**Server Balance**__", description=f"{ctx.guild} has not Registered.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
		return

	@commands.command() # Transfer Money Command
	async def transfer(self, ctx, amount: int=None, *, memberz: discord.Member=None):
		if amount is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"Specify an Amount to Transfer to the Mentioned Member.\n`{self.bot.prefix}transfer <Amount> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if memberz is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"Specify Member and Amount to Transfer to.\n`{self.bot.prefix}transfer <Amount> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if memberz.id == ctx.author.id:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You can't Transfer to Yourself..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		sender = None
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"**{memberz}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		grab_members = collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		sender_balance = 0
		receiver_balance = "N/A"
		async for m in grab_members:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == ctx.author.id:
				sender_balance = members_money
			if server_members == memberz.id:
				receiver_balance = members_money
		if receiver_balance == "N/A":
			embed = discord.Embed(title="__**Transfer Error**__", description=f"The Receiver must have an Active Account.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		sender_money = sender_balance - amount
		receiver_money = receiver_balance + amount
		if sender_money < 0:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You have Insufficent Funds to Transfer this Amount.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Member"] = ctx.author.id
		log ["Currency"] = sender_money
		old_log = {"Guild": ctx.guild.id, "Member": ctx.author.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Member"] = memberz.id
		log ["Currency"] = receiver_money
		old_log = {"Guild": ctx.guild.id, "Member": memberz.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title=f"__**Transfer Complete**__", description=f"*{memberz.display_name}* has Received your Transfer of **{amount}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Give Items Command
	async def give(self, ctx, amount: int=None, *, memberz: discord.Member=None):
		if amount is None:
			embed = discord.Embed(title="__**Gift Error**__", description=f"Specify an Item's Index to Give & Member to Send to.\n`{self.bot.prefix}give <Item Index> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if memberz is None:
			embed = discord.Embed(title="__**Gift Error**__", description=f"Specify a Member to Gift.\n`{self.bot.prefix}give <Item Index> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if memberz.id == ctx.author.id:
			embed = discord.Embed(title="__**Gift Error**__", description=f"You can't Gift Items to Yourself..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_5 = self.bot.db["Eco_limits"]
		sender = None
		recipent = None
		server = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Gift Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Gift Error**__", description=f"**{memberz}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_5.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
		grab_members = collection.find({"Guild": ctx.guild.id}, {"_id": 0})
		receiver_bag = "N/A"
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == ctx.author.id:
				sender_bag = members_items
				receiver_items = [f"{sender_bag[amount-1]}"]
			if server_members == memberz.id:
				receiver_bag = members_items
				if len(receiver_bag) > Bag_Limit:
					embed = discord.Embed(title="__**Bag Full**__", description=f"*{memberz.display_name}* already has **{Bag_Limit}** Items in their Bag.", timestamp=datetime.utcnow(), color=0xff0000)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
					await ctx.send(embed=embed)
					return
				receiver_items += members_items
		if receiver_bag == "N/A":
			embed = discord.Embed(title="__**Gift Error**__", description=f"The Receiver must have a Bag to Receive Gifts.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		item = sender_bag[amount-1]
		sender_bag.pop(amount-1)
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": sender_bag}})
		await collection.update_one({"Guild": ctx.guild.id, "Member": memberz.id}, {"$set":{"Items": receiver_items}})
		embed = discord.Embed(title=f"__**Gift Sent**__", description=f"*{memberz.display_name}* has Received *{item}*.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Daily Rewards Command
	@commands.cooldown(1, 86400, commands.BucketType.member)
	async def daily(self, ctx):
		collection_2 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Rewards Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_2.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Rewards Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		daily_rewards = random.randint(1, 100)
		member_info = collection_2.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": balance + daily_rewards}})
		embed = discord.Embed(title="__**Daily Rewards**__", description=f"You have Successfully Claimed {daily_rewards} from Daily Rewards.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@daily.error
	async def daily_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			h, remainder = divmod(error.retry_after, 3600)
			m, s = divmod(remainder, 60)
			embed = discord.Embed(title="__**Daily Rewards Error**__", description=f"You must wait **{int(h)}** hours & **{int(m)}** minutes to Claim the Daily Rewards again in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Drop Item Command
	async def drop(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"Specify an Item's Index to Drop.\n`{self.bot.prefix}drop <Item Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		recipent = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		sender_bag = None
		grab_members = collection.find({"Guild": ctx.guild.id}, {"_id": 0})
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == ctx.author.id:
				sender_bag = members_items
		if sender_bag is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"You have nothing in your Bag..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(sender_bag) <= 0:
			embed = discord.Embed(title="__**Drop Error**__", description=f"You have nothing in your Bag..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		item = sender_bag[amount-1]
		sender_bag.pop(amount-1)
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": sender_bag}})
		embed = discord.Embed(title=f"__**Dropped Item**__", description=f"You have Successfully Dropped *{item}*.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	
	@commands.command() # Selling Command
	async def selling (self, ctx, *, memberz: discord.Member=None):
		if memberz is None:
			memberz = ctx.author
		collection_2 = self.bot.db["Eco_member_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{memberz}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		shop = None
		order = ""
		counter = 1
		grab_shop = collection_2.find({"Guild": ctx.guild.id, "Member": memberz.id}, {"_id": 0, "Guild": 0})
		async for m in grab_shop:
			shop = m["Items"]
			price = m["Price"]
		if shop is None:
			embed = discord.Embed(title="__**Shop**__", description=f"{memberz.display_name} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		for m in shop[0:10]:
			order += f"**{counter}:** {m} **({price[counter-1]})**\n"
			counter += 1
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Shop**__", description=f"{memberz.display_name} has `0` Items in their Shop..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		
		pages = 1
		if len(shop) > 10:
			page = len(shop)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)
		if len(shop) <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_shop"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["User"] = memberz.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Warnings"] = len(shop)
		log ["Shop"] = shop
		log ["Price"] = price
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

	@commands.command() # Remove Item Command
	async def rsell(self, ctx, *, queue: int=None):
		if queue is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"Specify Item's Index to Remove from your Shop.\n`{self.bot.prefix}rsell <Item's Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["Eco_member_shop"]
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		items = []
		price =[]
		grab_snippets = collection_2.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
		async for m in grab_snippets:
			items += m["Items"]
			price += m["Price"]

		if items is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Remove Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		grab_items = collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
		add_item = items[queue-1]
		members_items = [add_item]
		async for m in grab_items:
			members_items += m["Items"]
		if len(members_items) > Bag_Limit:
			embed = discord.Embed(title="__**Inventory Full**__", description=f"You have **{Bag_Limit}** Items in your Inventory.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": members_items}})
		items.pop(queue-1)
		price.pop(int(queue-1))
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Removed**__", description=f"*{add_item}* has been Removed from your Shop.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Clear Shop Command
	async def csell(sell, ctx):
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["Eco_member_shop"]
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None
		shop = None

		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return


		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		grab_shop = collection_2.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
		async for m in grab_shop:
			shop = m["Items"]
		grab_items = collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
		async for m in grab_items:
			items = m["Items"]
		if shop is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Clear Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		new_items = shop + items
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": new_items}})
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": [], "Price": []}})
		embed = discord.Embed(title=f"__**Shop Cleared**__", description=f"Everything has been Cleared from your Shop.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Sell Item Command
	async def sell(self, ctx, price:int=None, *, item: int=None):
		if price is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"Specify a Price & Item to Add to your Shop.\n`{self.bot.prefix}sell <Price> <Item Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if item is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"Specify an Item's Index to Add to your Shop.\n`{self.bot.prefix}sell <Price> <Item Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["Eco_member_shop"]
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		grab_items = collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0})
		items = []
		async for m in grab_items:
			items += m["Items"]
		if items  is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"You have nothing in your Bag.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Sell Error**__", description=f"You have nothing in your Bag.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		item_name = items[item-1]
		items.pop(item-1)
		grab_shop = collection_2.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0, "Guild": 0})
		shop_items = [f"{item_name}"]
		price = [price]
		async for m in grab_shop:
			shop_items += m["Items"]
			price += m["Price"]
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": items}})
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": shop_items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Added**__", description=f"*{item_name}* has been to Added your Shop.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Deposit Money Command
	async def deposit(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"Specify an Amount to Deposit to your Savings Account.\n`{self.bot.prefix}deposit <Amount>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_2 =self.bot.db["Eco_bank"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		grab_members = collection.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		grab_bank = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		sender_balance = 0
		bank_balance = None
		async for m in grab_members:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == ctx.author.id:
				sender_balance = members_money
		async for m in grab_bank:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == ctx.author.id:
				bank_balance = members_money
		if bank_balance is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You must have an Active Savings Account.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		sender_money = sender_balance - amount
		bank_money = bank_balance + amount
		if sender_money < 0:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You don't have Enough Funds to Deposit this Amount.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": sender_money}})
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": bank_money}})
		embed = discord.Embed(title=f"__**Deposit Complete**__", description=f"You have Successfully Deposited **{amount}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Withdraw Money Command
	async def withdraw(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"Specify an Amount to Withdraw to your Savings Account.\n`{self.bot.prefix}withdraw <Amount>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_2 =self.bot.db["Eco_bank"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		grab_members = collection.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		grab_bank = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		sender_balance = 0
		bank_balance = None
		async for m in grab_members:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == ctx.author.id:
				sender_balance = members_money
		async for m in grab_bank:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == ctx.author.id:
				bank_balance = members_money
		if bank_balance is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You must have an Active Savings Account.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		sender_money = sender_balance + amount
		bank_money = bank_balance - amount
		if bank_money < 0:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You don't have Enough Funds to Withdraw this Amount.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": sender_money}})
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": bank_money}})
		embed = discord.Embed(title=f"__**Withdraw Complete**__", description=f"You have Successfully Withdrew **{amount}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Store Item Command
	async def store(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"Specify an Item's Index to Deposit.\n`{self.bot.prefix}store <Item Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_2 = self.bot.db["Eco_bank"]
		collection_4 = self.bot.db["Eco_purchased"]
		collection_5 = self.bot.db["Eco_limits"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None
		Box_Limit = 500

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_5.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Box_Limit = m["Box"]
		grab_members = collection_4.find({"Guild": ctx.guild.id}, {"_id": 0})
		grab_bag = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0})
		bank_bag = None
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == ctx.author.id:
				sender_bag = members_items
		async for m in grab_bag:
			bank_members = m["Member"]
			members_items = m["Items"]
			if bank_members == ctx.author.id:
				bank_bag = members_items
				bank_items = [f"{sender_bag[amount-1]}"]
				bank_items += members_items
		if bank_bag is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You must have a Security Box to Deposit Items.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(sender_bag) <= 0:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You have nothing in your Bag..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(bank_items) > Box_Limit:
			embed = discord.Embed(title="__**Security Box Full**__", description=f"You already have **{Box_Limit}** Items in your Storage Box.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		item = sender_bag[amount-1]
		sender_bag.pop(amount-1)
		await collection_4.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": sender_bag}})
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": bank_items}})
		embed = discord.Embed(title=f"__**Deposit Complete**__", description=f"You have Successfully Deposited *{item}*.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Take Item Command
	async def take(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"Specify an Item's Index to Withdraw.\n`{self.bot.prefix}take <Item Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_2 = self.bot.db["Eco_bank"]
		collection_5 = self.bot.db["Eco_limits"]
		collection_4 = self.bot.db["Eco_purchased"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		async for m in collection_5.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
		grab_members = collection_4.find({"Guild": ctx.guild.id}, {"_id": 0})
		grab_bag = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0})
		bank_bag = None
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == ctx.author.id:
				sender_bag = members_items
		async for m in grab_bag:
			bank_members = m["Member"]
			members_items = m["Items"]
			if bank_members == ctx.author.id:
				bank_bag = members_items
				sender_items = [f"{bank_bag[amount-1]}"]
				sender_items += sender_bag
		if bank_bag is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You must have a Security Box to Withdraw Items.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(bank_bag) <= 0:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You must have Items in your Security Box to Withdraw them.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(sender_items) > Bag_Limit:
			embed = discord.Embed(title="__**Bag Full**__", description=f"You already have **{Bag_Limit}** Items in your Bag.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		item = bank_bag[amount-1]
		bank_bag.pop(amount-1)
		await collection_4.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": sender_items}})
		await collection_2.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Items": bank_bag}})
		embed = discord.Embed(title=f"__**Withdraw Complete**__", description=f"You have Successfully Withdrew *{item}*.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Storage Command
	async def storage(self, ctx, *, memberz: discord.Member=None):
		collection_2 = self.bot.db["Eco_bank"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Storage Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Storage Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return

		counter = 0
		if memberz is None:
			memberz = ctx.author
		items = None
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}).sort("Currency", pymongo.DESCENDING):
			member = m["Member"]
			counter += 1
			if member == memberz.id:
				money = m["Currency"]
				items = m["Items"]
		if items is None:
			embed = discord.Embed(title="__**User Storage**__", description=f"{memberz.display_name} has not Rented a Security Box or Savings Account..", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return

		if len(items) <= 0 and money <= 0:
			embed = discord.Embed(title="__**User Storage**__", description=f"{memberz.display_name} has nothing in their Security Box or Savings Account..", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
			embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return

		counterz = 1
		order = ""
		for m in items[0:10]:
			order += f"**{counterz}:** {m}\n"
			counterz += 1

		embed = discord.Embed(title="__**User Storage**__", description=f"**Currency:** {money}\n__**Inventory**__\n{order}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_author(name=f"{memberz}", icon_url=str(memberz.avatar_url_as(format=None, static_format="png")))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))

		pages = 1
		if len(items) > 10:
			page = len(items)/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)
		if len(items) <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_bank"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["User"] = memberz.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Warnings"] = len(items)
		log ["Shop"] = items
		log ["Currency"] = money
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

	@commands.command() # Rent Storage Command
	async def rent(self, ctx):
		collection_2 = self.bot.db["Eco_bank"]
		collection = self.bot.db["Eco_guild_balance"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_5 = self.bot.db["Eco_limits"]
		recipent = None
		server = None
		Box_Limit = 500

		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Rent Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection_4.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0}):
			recipent = m["Member"]
			money = m["Currency"]
		if recipent is None:
			embed = discord.Embed(title="__**Rent Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Member"] = ctx.author.id
		log ["Currency"] = 0
		log ["Items"] = []
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}):
			member = m["Member"]
			if member == ctx.author.id:
				embed = discord.Embed(title="__**Rent Error**__", description=f"You already have a Security Box & Savings Account.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
		async for m in collection_5.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Box_Limit = m["Box"]
		amount = 1000000
		end_bal = money - amount
		if end_bal < 0:
			embed = discord.Embed(title="__**Rent Error**__", description=f"You don't have Enough Funds to Purchase a Storage Box & Savings Account.\n**Price:** *{amount}*", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection_2.insert_one(log)
		await collection_4.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": end_bal}})
		embed = discord.Embed(title="__**New Storage**__", description=f"You have Successfully Rented a Security Box *({Box_Limit} Slots)* & Savings Account.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()



	@commands.command() # Register Command
	@commands.has_permissions(kick_members=True)
	async def register(self, ctx):
		collection_2 = self.bot.db["Eco_guild_balance"]
		collection_4 = self.bot.db["Eco_limits"]
		collection = self.bot.db["Eco_guild_shop"]
		Guild_Start = 0
		async for m in collection_4.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Guild_Start = m["Server"]
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Currency"] = Guild_Start
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}):
			guild = m["Guild"]
			if guild == ctx.guild.id:
				embed = discord.Embed(title="__**Register Error**__", description=f"You already have Setup Currency Exchange.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
		await collection_2.insert_one(log)
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Items"] = []
		log ["Price"] = []
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Server Registered**__", description=f"You have Successfully Registered ***{ctx.guild}*** for Currency Exchange.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@register.error
	async def register_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Register this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Add Item Command
	@commands.has_permissions(kick_members=True)
	async def item(self, ctx, price:int=None, *, item: str=None):
		if price is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"Specify a Price & Item to Add to the Shop.\n`{self.bot.prefix}item <Price> <Item Name>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if item is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"Specify a Item to Add to the Shop.\n`{self.bot.prefix}item <Price> <Item Name>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		grab_items = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		items = [f"{item}"]
		price = [price]
		async for m in grab_items:
			items += m["Items"]
			price += m["Price"]
		await collection_2.update_one({"Guild": ctx.guild.id}, {"$set":{"Items": items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Added**__", description=f"*{item}* has been to Added the Shop.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@item.error
	async def item_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Add Items to the Shop in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Remove Item Command
	@commands.has_permissions(kick_members=True)
	async def ritem(self, ctx, *, queue: int=None):
		if queue is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"Specify Item's Index to Remove from the Shop.\n`{self.bot.prefix}ritem <Item's Index>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		items = []
		price =[]
		grab_snippets = collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0})
		async for m in grab_snippets:
			items += m["Items"]
			price += m["Price"]
		if items is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"There's nothing in {ctx.guild}'s Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Remove Error**__", description=f"There's nothing in {ctx.guild}'s Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		item = items[queue-1]
		items.pop(queue-1)
		price.pop(queue-1)
		await collection_2.update_one({"Guild": ctx.guild.id}, {"$set":{"Items": items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Removed**__", description=f"*{item}* has been Removed from the Shop.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@ritem.error
	async def ritem_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Remove Items from the Shop in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Shop Command
	@commands.has_permissions(kick_members=True)
	async def cshop(self, ctx):
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		items = None
		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0}):
			items = m["Items"]
		if server is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if items is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"There's nothing in {ctx.guild}'s Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Clear Error**__", description=f"There's nothing in {ctx.guild}'s Shop.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await collection_2.update_one({"Guild": ctx.guild.id}, {"$set":{"Items": [], "Price": []}})
		embed = discord.Embed(title=f"__**Shop Cleared**__", description=f"All Items has been Cleared from {ctx.guild}'s Shop.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@cshop.error
	async def cshop_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear the Shop in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Admin Withdraw Command
	@commands.has_permissions(kick_members=True)
	async def uwithdraw(self, ctx, queue: int=None, *, member: discord.Member=None):
		if queue is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"Specify an Amount & Member to Withdraw Funds from.\n`{self.bot.prefix}withdraw <Amount> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if member is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"Specify Member to Withdraw Funds from.\n`{self.bot.prefix}withdraw <Amount> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["logs"]
		server = None
		recipent = None
		mod_log = None
		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection.find({"Guild": ctx.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.guild.get_channel(Channelz)
		member_info = collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		ending_balance = balance - queue
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": ending_balance}})
		embed = discord.Embed(title="__**Withdraw**__", description=f"**{queue}** has been Withdrawed from ***{member}***.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if not mod_log is None:
			await mod_log.send(embed=embed)
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@uwithdraw.error
	async def uwithdraw_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Withdraw Funds from Members in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Admin Deposit Command
	@commands.has_permissions(kick_members=True)
	async def udeposit(self, ctx, queue: int=None, *, member: discord.Member=None):
		if queue is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"Specify an Amount & Member to Deposit Funds to.\n`{self.bot.prefix}deposit <Amount> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if member is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"Specify Member to Deposit Funds to.\n`{self.bot.prefix}deposit <Amount> <Mention Member>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["logs"]
		server = None
		recipent = None
		mod_log = None
		async for m in collection_3.find({"Guild": ctx.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{ctx.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection.find({"Guild": ctx.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		async for m in collection_2.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.guild.get_channel(Channelz)
		member_info = collection.find({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		ending_balance = balance + queue
		await collection.update_one({"Guild": ctx.guild.id, "Member": ctx.author.id}, {"$set":{"Currency": ending_balance}})
		embed = discord.Embed(title="__**Deposit**__", description=f"**{queue}** has Deposited to ***{member}*** .", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if not mod_log is None:
			await mod_log.send(embed=embed)
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@udeposit.error
	async def udeposit_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Deposit Funds to Members in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Bag Limit Command
	@commands.has_permissions(kick_members=True)
	async def lbag(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Limit Error**__", description=f"Specify an Amount for the Bag Limit.\n`{self.bot.prefix}lbag <Amount>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_limits"]
		Box_Limit = 500
		Guild_Start = 0
		User_Start = 0
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Box_Limit = m["Box"]
			Guild_Start = m["Server"]
			User_Start = m["User"]
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Bag"] = amount
		log ["Box"] = Box_Limit
		log ["Server"] = Guild_Start
		log ["User"] = User_Start
		old_log = {"Guild": ctx.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Bag Storage**__", description=f"You have Changed {ctx.guild}'s Bag Limit to **{amount}** Slots.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@lbag.error
	async def lbag_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the Bag Limit in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Box Limit Command
	@commands.has_permissions(kick_members=True)
	async def lbox(self, ctx, amount: int=None):

		if amount is None:
			embed = discord.Embed(title="__**Limit Error**__", description=f"Specify an Amount for the Box Limit.\n`{self.bot.prefix}lbox <Amount>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_limits"]
		Bag_Limit = 30
		Guild_Start = 0
		User_Start = 0
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
			Guild_Start = m["Server"]
			User_Start = m["User"]
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Bag"] = Bag_Limit
		log ["Box"] = amount
		log ["Server"] = Guild_Start
		log ["User"] = User_Start
		old_log = {"Guild": ctx.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Security Box Storage**__", description=f"You have Changed {ctx.guild}'s Security Box Limit to **{amount}** Slots.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@lbox.error
	async def lbox_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the Security Box Limit in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # User Start Command
	@commands.has_permissions(kick_members=True)
	async def ustart(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Limit Error**__", description=f"Specify an Amount for New Members to get upon Joining.\n`{self.bot.prefix}ustart <Amount>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_limits"]
		Bag_Limit = 30
		Box_Limit = 500
		Guild_Start = 0
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
			Box_Limit = m["Box"]
			Guild_Start =m["Server"]
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Bag"] = Bag_Limit
		log ["Box"] = Box_Limit
		log ["Server"] = Guild_Start
		log ["User"] = amount
		old_log = {"Guild": ctx.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**User Start Balance**__", description=f"You have Changed {ctx.guild}'s User Start Balance to **{amount}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@ustart.error
	async def ustart_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the User Start Balance in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Server Start Command
	@commands.has_permissions(kick_members=True)
	async def sstart(self, ctx, amount: int=None):
		if amount is None:
			embed = discord.Embed(title="__**Limit Error**__", description=f"Specify an Amount for Server to get upon Registering.\n`{self.bot.prefix}sstart <Amount>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Eco_limits"]
		Bag_Limit = 30
		User_Start = 0
		Box_Limit = 500
		async for m in collection.find({"Guild": ctx.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
			Box_Limit = m["Box"]
			User_Start= m["User"]
		log = {}
		log ["Guild"] = ctx.guild.id
		log ["Bag"] = Bag_Limit
		log ["Box"] = Box_Limit
		log ["Server"] = amount
		log ["User"] = User_Start
		old_log = {"Guild": ctx.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Server Start Balance**__", description=f"You have Changed {ctx.guild}'s Start Balance to **{amount}**.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@sstart.error
	async def sstart_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the Server's Start Balance in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		collection = self.bot.db["AM_shop"] # Paginate Shop
		menu = collection.find({})
		helps = []
		counter = 1
		member_user = None
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				try:
					checking = x["User"]
				except:
					pass
				Channel = x["Channel"]
				warnings = x["Warnings"]
				shop = x["Shop"]
				price = x["Price"]
				counter = x["Counter"]
				pages = x["Pages"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				try:
					member_user = guild.get_member(checking)
				except:
					pass
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
			for x in shop[min_items:max_items]:
				order += f"**{place}:** {x} **({price[place-1]})**\n"
				place += 1
			embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=guild.icon_url_as(format=None, static_format="png"))
			if not member_user is None:
				embed.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		collection = self.bot.db["AM_bank"] # Paginate Storage
		menu = collection.find({})
		helps = []
		counter = 1
		member_user = None
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				try:
					checking = x["User"]
				except:
					pass
				Channel = x["Channel"]
				warnings = x["Warnings"]
				shop = x["Shop"]
				counter = x["Counter"]
				pages = x["Pages"]
				money = x["Currency"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				try:
					member_user = guild.get_member(checking)
				except:
					pass
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
			for x in shop[min_items:max_items]:
				order += f"**{place}:** {x}\n"
				place += 1
			embed = discord.Embed(title="__**User Storage**__", description=f"**Currency:** {money}\n__**Inventory**__\n{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=ctx.guild.icon_url_as(format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		collection = self.bot.db["AM_purchased"] # Paginate Purchased
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
			embed = discord.Embed(title="__**Bag**__", description=f"{order}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_thumbnail(url=guild.icon_url_as(format=None, static_format="png"))
			embed.set_author(name=f"{member_user}", icon_url=str(member_user.avatar_url_as(format=None, static_format="png")))
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})			

def setup(bot):
	bot.add_cog(Economy(bot))