import discord
import asyncio
import json
import time
import pymongo
import motor.motor_asyncio
import pytz
import random
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from Utils.Menus import Formatter, Pager
from pytz import timezone

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

User_Start = config['User_Start']
Guild_Start = config['Guild_Start']
Bag_Limit = config['Bag_Limit']
Box_Limit = config['Box_Limit']



class Economy(commands.Cog, app_commands.Group, name="economy", description="Economy & Setup Commands"):
	def __init__(self, bot):
		super().__init__()
		self.bot = bot
		self.bot.user_start = User_Start
		self.bot.guild_start = Guild_Start
		self.bot.bag_limit = Bag_Limit
		self.bot.box_limit = Box_Limit
		
	@app_commands.command(name="apply", description="Register to Use Currency Exchange") # Apply Command
	async def apply(self, interaction:discord.Interaction):
		collection_2 = self.bot.db["Eco_member_balance"]
		collection = self.bot.db ["Eco_guild_balance"]
		collection_3 = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_limits"]
		collection_5 = self.bot.db["Eco_member_shop"]
		check = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			check = m["Guild"]
		if check is None:
			embed = discord.Embed(title="__**Apply Error**__", description=f"**{interaction.guild}** has not Registered with {self.bot.user.mention} to use Currency Exchange.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		User_Start = 0
		async for m in collection_4.find({"Guild": interaction.guild.id}, {"_id": 0}):
			User_Start = m["User"]
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Member"] = interaction.user.id
		log ["Currency"] = User_Start
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}):
			member = m["Member"]
			if member == interaction.user.id:
				embed = discord.Embed(title="__**Apply Error**__", description=f"You already have an Account.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		await collection_2.insert_one(log)
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Member"] = interaction.user.id
		log ["Items"] = []
		await collection_3.insert_one(log)
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Member"] = interaction.user.id
		log ["Items"] = []
		log ["Price"] = []
		await collection_5.insert_one(log)
		embed = discord.Embed(title="__**Account Created**__", description="You have Successfully Created an Account.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="shop", description="Display Server's or Specified Member's Shop") # Shop Command
	@app_commands.describe(member="Member to Check Shop of")
	async def shop(self, interaction:discord.Interaction, *, member: discord.Member=None):
		collection = self.bot.db["Eco_member_shop"]
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None
		item_count = 0
		embeds = []

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if not member is None:
			async for m in collection_4.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
				recipent = m["Member"]
			if recipent is None:
				embed = discord.Embed(title="__**Shop Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		shop = None
		order = ""
		counter = 1
		if not member is None:
			grab_shop = collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
			async for m in grab_shop:
				shop = m["Items"]
				price = m["Price"]
			if shop is None:
				embed = discord.Embed(title="__**Shop**__", description=f"{member.display_name} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
				return
			if len(shop) <= 0:
				embed = discord.Embed(title="__**Shop**__", description=f"{member.display_name} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
				return
			for m in shop:
				order += f"**{counter}:** {m} **({price[counter-1]})**\n"
				counter += 1
				item_count += 1
				if item_count == 10:
					embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
					embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
					embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					embeds.append(embed)
					item_count = 0
					order = ""

			if item_count < 10 and item_count > 0:
				embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)
			
			formatter = Formatter([i for i in embeds], per_page=1)
			menu = Pager(formatter)
			await menu.start(interaction)
			#await ctx.message.delete()
			return
		grab_shop = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		shop = None
		async for m in grab_shop:
			shop = m["Items"]
			price = m["Price"]
		if shop is None:
			embed = discord.Embed(title="__**Shop**__", description=f"{interaction.guild} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Shop**__", description=f"{interaction.guild} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		for m in shop:
			order += f"**{counter}:** {m} **({price[counter-1]})**\n"
			counter += 1
			item_count += 1
			if item_count == 10:
				embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)
				item_count = 0
				order = ""

		if item_count < 10 and item_count > 0:
			embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)
		
		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="bag", description="Check Your or Mentioned Member's bage") # Bag Command
	@app_commands.describe(member="Member to Check Bag of")
	async def bag(self, interaction:discord.Interaction, member: discord.Member=None):
		if member is None:
			member = interaction.user
		collection_2 = self.bot.db["Eco_purchased"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection = self.bot.db["Eco_member_balance"]
		sender = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Bag Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Bag Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		bag = None
		order = ""
		embeds = []
		counter = 1
		item_count = 0
		grab_bag = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
		async for m in grab_bag:
			bag = m["Items"]
		if bag is None:
			embed = discord.Embed(title="__**Bag**__", description=f"{member} has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		for m in bag:
			order += f"**{counter}:** {m}\n"
			counter += 1
			item_count += 1
			if item_count == 10:
				embed = discord.Embed(title="__**Bag**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)
				item_count = 0
				order = ""
		if len(bag) <= 0:
			embed = discord.Embed(title="__**Bag**__", description=f"{member} has `0` Items..", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if item_count < 10 and item_count > 0:
			embed = discord.Embed(title="__**Bag**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)
		
		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="buy", description="Buy Item From Server or Mentioned Member's Shop") # Buy Command
	@app_commands.describe(item="Item's Queue You Want to Purchase", member="Member to Buy From")
	async def buy(self, interaction:discord.Interaction, item:int, *, member: discord.Member=None):
		collection = self.bot.db["Eco_member_balance"]
		collection_4 = self.bot.db["Eco_purchased"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_5 = self.bot.db["Eco_limits"]
		recipent = None
		server = None
		sender = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		if not member is None:
			if member.id == interaction.user.id:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"You can't Purchase your Own Items..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			async for m in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
				recipent = m["Member"]
			if recipent is None:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		shop = None
		
		async for m in collection_5.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
		if not member is None:
			if member.id == interaction.user.id:
				return
			collection_2 = self.bot.db["Eco_member_shop"]
			member_info = collection.find({"Guild": interaction.guild.id}, {"_id": 0})
			async for m in member_info:
				user = m["Member"]
				balance = m["Currency"]
				if user == interaction.user.id:
					buyer_balance = balance
				if user == member.id:
					seller_balance = balance
			grab_shop = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
			async for m in grab_shop:
				shop = m["Items"]
				price = m["Price"]
			if shop is None:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"{member.display_name} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
				return
			if shop == 0:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"{member.display_name} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
				return
			item = shop[item-1]
			total = price[item-1]
			ending_balance = buyer_balance - price[item-1]
			new_balance = seller_balance + price[item-1]
			shop.pop(item-1)
			price.pop(item-1)
			if ending_balance <= 0:
				embed = discord.Embed(title="__**Purchase Error**__", description=f"You have Insufficent Funds to make this Purchase.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			order = [f"{item}"]
			#order = [f"**{item}** *~Sold by {member}*"]
			grab_items = collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
			async for m in grab_items:
				bag = m["Items"]
				order += bag
			if len(order) > Bag_Limit:
				embed = discord.Embed(title="__**Bag Full**__", description=f"You already have **{Bag_Limit}** Items in your Bag.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
			await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": ending_balance}})
			await collection.update_one({"Guild": interaction.guild.id, "Member": member.id}, {"$set":{"Currency": new_balance}})
			await collection_2.update_one({"Member": member.id}, {"$set":{"Items": shop, "Price": price}})
			await collection_4.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": order}})
			embed = discord.Embed(title="__**Purchase Successful**__", description=f"You have Successfully Purchased **{item}** from **{member.user.mention}** for **{total}**.", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embed_2 = discord.Embed(title="__***Purchase***__", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_author(name=f"{member}", icon_url=member.display_avatar.replace(format="png", static_format="png"))
			embed_2.add_field(name="__**:satellite: Server:**__", value=f"**{interaction.guild}**", inline=False)
			embed_2.add_field(name="__**:newspaper: Item:**__", value=f"{item}", inline=False)
			embed_2.add_field(name="__**:money_with_wings: Price:**__", value=f"{total}", inline=False)
			embed_2.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		collection_2 = self.bot.db["Eco_guild_shop"]
		member_info = collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		shop = None
		grab_shop = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for m in grab_shop:
			shop = m["Items"]
			price = m["Price"]
		if shop is None:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"{interaction.guild} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"{interaction.guild} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		grab_bank = collection_3.find({"Guild": interaction.guild.id}, {"_id": 0})
		async for m in grab_bank:
			guild_balance = m["Currency"]
		item = shop[item-1]
		total = price[item-1]
		ending_balance = balance - price[item-1]
		bank = guild_balance + price[item-1]
		if ending_balance < 0:
			embed = discord.Embed(title="__**Purchase Error**__", description=f"You have Insufficent Funds to make this Purchase.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		order = [f"{item}"]
		#order = [f"**{item}** *~Sold by {interaction.guild}*"]
		grab_items = collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_items:
			bag = m["Items"]
			order += bag
		if len(order) > Bag_Limit:
			embed = discord.Embed(title="__**Bag Full**__", description=f"You already have **{Bag_Limit}** Items in your Bag.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": ending_balance}})
		await collection_3.update_one({"Guild": interaction.guild.id}, {"$set":{"Currency": bank}})
		await collection_4.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": order}})
		embed = discord.Embed(title="__**Purchase Successful**__", description=f"You have Successfully Purchased ***{item}*** for **{price[item-1]}**.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__***Purchase***__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name="__**:newspaper: Item:**__", value=f"{item}", inline=False)
		embed_2.add_field(name="__**:money_with_wings: Price:**__", value=f"{total}", inline=False)
		embed_2.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="balance", description="Check Your or Specified Member's Balance") # Balance Command
	@app_commands.describe(member="Member to Check Balance of")
	async def balance(self, interaction:discord.Interaction, *, member: discord.Member=None):
		if member is None:
			member = interaction.user
		collection_2 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Balance Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Balance Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		counter = "N/A"
		money = "N/A" 
		counter = 0
		if member is None:
			async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}).sort("Currency", pymongo.DESCENDING):
				current_member = m["Member"]
				money = m["Currency"]
				counter += 1
				if current_member == interaction.user.id:
					embed = discord.Embed(title="__**User Balance**__", description=f":money_with_wings: __**Balance:**__ {money}\n:classical_building: __**Rank in Server:**__ {counter}", timestamp=datetime.now(), color=0xac5ece)
					embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					await interaction.followup.send(embed=embed)
					#await ctx.message.delete()
					return
			embed = discord.Embed(title="__**User Balance**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}).sort("Currency", pymongo.DESCENDING):
			current_member = m["Member"]
			money = m["Currency"]
			counter += 1
			if current_member == member.id:
				embed = discord.Embed(title="__**User Balance**__", description=f":money_with_wings: __**Balance:**__ {money}\n:classical_building: __**Rank in Server:**__ {counter}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
				return
		embed = discord.Embed(title="__**User Balance**__", description=f"{member.display_name} has not Applied for an Account..", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
		return

	@app_commands.command(name="balance_server", description="Check Server's Balance") # Guild Balance Command
	async def balance_server(self, interaction:discord.Interaction):
		collection_2 = self.bot.db["Eco_guild_balance"]
		server = None

		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Balance Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		counter = "N/A"
		money = "N/A" 
		counter = 0
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}):
			guild = m["Guild"]
			money = m["Currency"]
			counter += 1
			if guild == interaction.guild.id:
				embed = discord.Embed(title="__**Server Balance**__", description=f"**{money}**", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				#await ctx.message.delete()
				return
		embed = discord.Embed(title="__**Server Balance**__", description=f"{interaction.guild} has not Registered.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
		return

	@app_commands.command(name="daily", description="Receive Daily Currency Drop") # Daily Rewards Command
	@app_commands.checks.cooldown(1, 86400, key=lambda i: (i.guild_id, i.user.id))
	async def daily(self, interaction:discord.Interaction):
		collection_2 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Rewards Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_2.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Rewards Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		daily_rewards = random.randint(1, 100)
		member_info = collection_2.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": balance + daily_rewards}})
		embed = discord.Embed(title="__**Daily Rewards**__", description=f"You have Successfully Claimed {daily_rewards} from Daily Rewards.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@daily.error
	async def daily_error(self, interaction, error):
		if isinstance(error, app_commands.CommandOnCooldown):
			h, remainder = divmod(error.retry_after, 3600)
			m, s = divmod(remainder, 60)
			embed = discord.Embed(title="__**Daily Rewards Error**__", description=f"You must wait **{int(h)}** hours & **{int(m)}** minutes to Claim the Daily Rewards again in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	security = app_commands.Group(name="security", description="Safety Deposit Box & Savings Account Commands")

	@security.command(name="rent", description="Rent Storage (Safety Deposit Box & Savings Account)") # Rent Storage Command
	async def rent(self, interaction:discord.Interaction):
		collection_2 = self.bot.db["Eco_bank"]
		collection = self.bot.db["Eco_guild_balance"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_5 = self.bot.db["Eco_limits"]
		recipent = None
		server = None
		Box_Limit = 500

		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Rent Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
			money = m["Currency"]
		if recipent is None:
			embed = discord.Embed(title="__**Rent Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Member"] = interaction.user.id
		log ["Currency"] = 0
		log ["Items"] = []
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}):
			member = m["Member"]
			if member == interaction.user.id:
				embed = discord.Embed(title="__**Rent Error**__", description=f"You already have a Security Box & Savings Account.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		async for m in collection_5.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Box_Limit = m["Box"]
		amount = 1000000
		end_bal = money - amount
		if end_bal < 0:
			embed = discord.Embed(title="__**Rent Error**__", description=f"You don't have Enough Funds to Purchase a Storage Box & Savings Account.\n**Price:** *{amount}*", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection_2.insert_one(log)
		await collection_4.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": end_bal}})
		embed = discord.Embed(title="__**New Storage**__", description=f"You have Successfully Rented a Security Box *({Box_Limit} Slots)* & Savings Account.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@security.command(name="storage", description="Check Storage of Your or Specified Member's Safety Deposit Box") # Storage Command
	@app_commands.describe(member="Member to Check Storage of")
	async def storage(self, interaction:discord.Interaction, *, member: discord.Member=None):
		collection_2 = self.bot.db["Eco_bank"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Storage Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if member is None:
			member = interaction.user
		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Storage Error**__", description=f"{member.mention} has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		counter = 0
		
		items = None
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}).sort("Currency", pymongo.DESCENDING):
			current_member = m["Member"]
			counter += 1
			if current_member == member.id:
				money = m["Currency"]
				items = m["Items"]
		if items is None:
			embed = discord.Embed(title="__**User Storage**__", description=f"{member.display_name} has not Rented a Security Box or Savings Account..", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return

		if len(items) <= 0 and money <= 0:
			embed = discord.Embed(title="__**User Storage**__", description=f"{member.display_name} has nothing in their Security Box or Savings Account..", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return

		counterz = 1
		order = ""
		embeds = []
		item_count = 0
		for m in items:
			order += f"**{counterz}:** {m}\n"
			counterz += 1
			item_count += 1
			if item_count == 10:
				embed = discord.Embed(title="__**User Storage**__", description=f"**Currency:** {money}\n__**Inventory**__\n{order}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)
				item_count = 0
				order = ""

		if item_count < 10 and item_count > 0:
			embed = discord.Embed(title="__**User Storage**__", description=f"**Currency:** {money}\n__**Inventory**__\n{order}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)

		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@security.command(name="withdraw", description="Withdraw Currency from Savings Account") # Withdraw Money Command
	@app_commands.describe(amount="Amount to Withdraw")
	async def withdraw(self, interaction:discord.Interaction, amount: int):
		collection = self.bot.db["Eco_member_balance"]
		collection_2 =self.bot.db["Eco_bank"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		grab_members = collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		grab_bank = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		sender_balance = 0
		bank_balance = None
		async for m in grab_members:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == interaction.user.id:
				sender_balance = members_money
		async for m in grab_bank:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == interaction.user.id:
				bank_balance = members_money
		if bank_balance is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You must have an Active Savings Account.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		sender_money = sender_balance + amount
		bank_money = bank_balance - amount
		if bank_money < 0:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You don't have Enough Funds to Withdraw this Amount.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": sender_money}})
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": bank_money}})
		embed = discord.Embed(title=f"__**Withdraw Complete**__", description=f"You have Successfully Withdrew **{amount}**.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@security.command(name="deposit", description="Deposit Currency into Savings Account") # Deposit Money Command
	@app_commands.describe(amount="Amount to Deposit")
	async def deposit(self, interaction:discord.Interaction, amount: int):
		collection = self.bot.db["Eco_member_balance"]
		collection_2 =self.bot.db["Eco_bank"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		grab_members = collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		grab_bank = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		sender_balance = 0
		bank_balance = None
		async for m in grab_members:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == interaction.user.id:
				sender_balance = members_money
		async for m in grab_bank:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == interaction.user.id:
				bank_balance = members_money
		if bank_balance is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You must have an Active Savings Account.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		sender_money = sender_balance - amount
		bank_money = bank_balance + amount
		if sender_money < 0:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You don't have Enough Funds to Deposit this Amount.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": sender_money}})
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": bank_money}})
		embed = discord.Embed(title=f"__**Deposit Complete**__", description=f"You have Successfully Deposited **{amount}**.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@security.command(name="take", description="Take Item from Safety Deposit Box") # Take Item Command
	@app_commands.describe(item="Item Index to Take")
	async def take(self, interaction:discord.Interaction, item: int):
		collection = self.bot.db["Eco_member_balance"]
		collection_2 = self.bot.db["Eco_bank"]
		collection_5 = self.bot.db["Eco_limits"]
		collection_4 = self.bot.db["Eco_purchased"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_5.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
		grab_members = collection_4.find({"Guild": interaction.guild.id}, {"_id": 0})
		grab_bag = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0})
		bank_bag = None
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == interaction.user.id:
				sender_bag = members_items
		async for m in grab_bag:
			bank_members = m["Member"]
			members_items = m["Items"]
			if bank_members == interaction.user.id:
				bank_bag = members_items
				sender_items = [f"{bank_bag[item-1]}"]
				sender_items += sender_bag
		if bank_bag is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You must have a Security Box to Withdraw Items.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(bank_bag) <= 0:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"You must have Items in your Security Box to Withdraw them.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(sender_items) > Bag_Limit:
			embed = discord.Embed(title="__**Bag Full**__", description=f"You already have **{Bag_Limit}** Items in your Bag.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		item = bank_bag[item-1]
		bank_bag.pop(item-1)
		await collection_4.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": sender_items}})
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": bank_bag}})
		embed = discord.Embed(title=f"__**Withdraw Complete**__", description=f"You have Successfully Withdrew *{item}*.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@security.command(name="store", description="Store Item in Safety Deposit Box") # Store Item Command
	@app_commands.describe(item="Item Index to Store")
	async def store(self, interaction:discord.Interaction, item: int):
		collection = self.bot.db["Eco_member_balance"]
		collection_2 = self.bot.db["Eco_bank"]
		collection_4 = self.bot.db["Eco_purchased"]
		collection_5 = self.bot.db["Eco_limits"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		recipent = None
		server = None
		Box_Limit = 500

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_5.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Box_Limit = m["Box"]
		grab_members = collection_4.find({"Guild": interaction.guild.id}, {"_id": 0})
		grab_bag = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0})
		bank_bag = None
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == interaction.user.id:
				sender_bag = members_items
		async for m in grab_bag:
			bank_members = m["Member"]
			members_items = m["Items"]
			if bank_members == interaction.user.id:
				bank_bag = members_items
				bank_items = [f"{sender_bag[item-1]}"]
				bank_items += members_items
		if bank_bag is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You must have a Security Box to Deposit Items.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(sender_bag) <= 0:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"You have nothing in your Bag..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(bank_items) > Box_Limit:
			embed = discord.Embed(title="__**Security Box Full**__", description=f"You already have **{Box_Limit}** Items in your Storage Box.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		item = sender_bag[item-1]
		sender_bag.pop(item-1)
		await collection_4.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": sender_bag}})
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": bank_items}})
		embed = discord.Embed(title=f"__**Deposit Complete**__", description=f"You have Successfully Deposited *{item}*.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	manage = app_commands.Group(name="manage", description="Shop Configuration & Item/Currency Management Commands")

	@manage.command(name="selling", description="Display Items Member is Selling") # Selling Command
	@app_commands.describe(member="Member to Check Items of")
	async def selling (self, interaction:discord.Interaction, *, member: discord.Member=None):
		if member is None:
			member = interaction.user
		collection_2 = self.bot.db["Eco_member_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		shop = None
		order = ""
		embeds = []
		counter = 1
		item_count = 0
		grab_shop = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
		async for m in grab_shop:
			shop = m["Items"]
			price = m["Price"]
		if shop is None:
			embed = discord.Embed(title="__**Shop**__", description=f"{member.display_name} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		for m in shop:
			order += f"**{counter}:** {m} **({price[counter-1]})**\n"
			counter += 1
			item_count += 1
			if item_count == 10:
				embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
				embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				embeds.append(embed)
				item_count = 0
				order = ""
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Shop**__", description=f"{member.display_name} has `0` Items in their Shop..", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		if item_count < 10 and item_count > 0:
			embed = discord.Embed(title="__**Shop**__", description=f"{order}", timestamp=datetime.now(), color=0xac5ece)
			embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
			embed.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)
		
		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@manage.command(name="sell", description="List Item for Sell") # Sell Item Command
	@app_commands.describe(price="Amount to List item for", item="Item Index to List")
	async def sell(self, interaction:discord.Interaction, price:int, *, item: int):
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["Eco_member_shop"]
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		grab_items = collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0})
		items = []
		async for m in grab_items:
			items += m["Items"]
		if items  is None:
			embed = discord.Embed(title="__**Sell Error**__", description=f"You have nothing in your Bag.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Sell Error**__", description=f"You have nothing in your Bag.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		item_name = items[item-1]
		items.pop(item-1)
		grab_shop = collection_2.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
		shop_items = [f"{item_name}"]
		price = [price]
		async for m in grab_shop:
			shop_items += m["Items"]
			price += m["Price"]
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": items}})
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": shop_items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Added**__", description=f"*{item_name}* has been to Added your Shop.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@manage.command(name="remove", description="Remove Item from Your Shop") # Remove Item Command
	@app_commands.describe(item="Item Index to Remove")
	async def remove(self, interaction:discord.Interaction, *, item: int):
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["Eco_member_shop"]
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		items = []
		price =[]
		grab_snippets = collection_2.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_snippets:
			items += m["Items"]
			price += m["Price"]

		if items is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Remove Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		grab_items = collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
		add_item = items[item-1]
		members_items = [add_item]
		async for m in grab_items:
			members_items += m["Items"]
		if len(members_items) > Bag_Limit:
			embed = discord.Embed(title="__**Inventory Full**__", description=f"You have **{Bag_Limit}** Items in your Inventory.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": members_items}})
		items.pop(item-1)
		price.pop(int(item-1))
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Removed**__", description=f"*{add_item}* has been Removed from your Shop.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@manage.command(name="clear", description="Clear All Items from Your Shop") # Clear Shop Command
	async def clear(self, interaction:discord.Interaction):
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["Eco_member_shop"]
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		recipent = None
		server = None
		shop = None

		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return


		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		grab_shop = collection_2.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_shop:
			shop = m["Items"]
		grab_items = collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_items:
			items = m["Items"]
		if shop is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(shop) <= 0:
			embed = discord.Embed(title="__**Clear Error**__", description=f"You have nothing in your Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		new_items = shop + items
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": new_items}})
		await collection_2.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": [], "Price": []}})
		embed = discord.Embed(title=f"__**Shop Cleared**__", description=f"Everything has been Cleared from your Shop.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@manage.command(name="transfer", description="Transfer Currency to Specified Member") # Transfer Money Command
	@app_commands.describe(amount="Amount to Transfer", member="Member to Transfer to")
	async def transfer(self, interaction:discord.Interaction, amount: int, *, member: discord.Member):
		if member.id == interaction.user.id:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You can't Transfer to Yourself..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		sender = None
		recipent = None
		server = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		grab_members = collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		sender_balance = 0
		receiver_balance = "N/A"
		async for m in grab_members:
			server_members = m["Member"]
			members_money = m["Currency"]
			if server_members == interaction.user.id:
				sender_balance = members_money
			if server_members == member.id:
				receiver_balance = members_money
		if receiver_balance == "N/A":
			embed = discord.Embed(title="__**Transfer Error**__", description=f"The Receiver must have an Active Account.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		sender_money = sender_balance - amount
		receiver_money = receiver_balance + amount
		if sender_money < 0:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You have Insufficent Funds to Transfer this Amount.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Member"] = interaction.user.id
		log ["Currency"] = sender_money
		old_log = {"Guild": interaction.guild.id, "Member": interaction.user.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Member"] = member.id
		log ["Currency"] = receiver_money
		old_log = {"Guild": interaction.guild.id, "Member": member.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title=f"__**Transfer Complete**__", description=f"*{member.display_name}* has Received your Transfer of **{amount}**.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@manage.command(name="give", description="Give Item to Specified Member") # Give Items Command
	@app_commands.describe(item="Item Index to Give Away", member="Member to Give item to")
	async def give(self, interaction:discord.Interaction, item: int, *, member: discord.Member):
		if member.id == interaction.user.id:
			embed = discord.Embed(title="__**Gift Error**__", description=f"You can't Gift Items to Yourself..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_5 = self.bot.db["Eco_limits"]
		sender = None
		recipent = None
		server = None
		Bag_Limit = 30

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Gift Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			sender = m["Member"]
		if sender is None:
			embed = discord.Embed(title="__**Transfer Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Gift Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_5.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
		grab_members = collection.find({"Guild": interaction.guild.id}, {"_id": 0})
		receiver_bag = "N/A"
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == interaction.user.id:
				sender_bag = members_items
				receiver_items = [f"{sender_bag[item-1]}"]
			if server_members == member.id:
				receiver_bag = members_items
				if len(receiver_bag) > Bag_Limit:
					embed = discord.Embed(title="__**Bag Full**__", description=f"*{member.display_name}* already has **{Bag_Limit}** Items in their Bag.", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					await interaction.followup.send(embed=embed)
					return
				receiver_items += members_items
		if receiver_bag == "N/A":
			embed = discord.Embed(title="__**Gift Error**__", description=f"The Receiver must have a Bag to Receive Gifts.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		item = sender_bag[item-1]
		sender_bag.pop(item-1)
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": sender_bag}})
		await collection.update_one({"Guild": interaction.guild.id, "Member": member.id}, {"$set":{"Items": receiver_items}})
		embed = discord.Embed(title=f"__**Gift Sent**__", description=f"*{member.display_name}* has Received *{item}*.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@manage.command(name="drop", description="Drop Specified Item") # Drop Item Command
	@app_commands.describe(item="Item Index to Drop")
	async def drop(self, interaction:discord.Interaction, item:int):
		collection = self.bot.db["Eco_purchased"]
		collection_4 = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		recipent = None

		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		async for m in collection_4.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"You have not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		sender_bag = None
		grab_members = collection.find({"Guild": interaction.guild.id}, {"_id": 0})
		async for m in grab_members:
			server_members = m["Member"]
			members_items = m["Items"]
			if server_members == interaction.user.id:
				sender_bag = members_items
		if sender_bag is None:
			embed = discord.Embed(title="__**Drop Error**__", description=f"You have nothing in your Bag..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(sender_bag) <= 0:
			embed = discord.Embed(title="__**Drop Error**__", description=f"You have nothing in your Bag..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		item = sender_bag[item-1]
		sender_bag.pop(item-1)
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Items": sender_bag}})
		embed = discord.Embed(title=f"__**Dropped Item**__", description=f"You have Successfully Dropped *{item}*.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()


	admin_eco = app_commands.Group(name="admin", description="Economy Admin & Setup Commands")


	@admin_eco.command(name="register", description="Register Server to Use Currency Exchange") # Register Command
	@app_commands.checks.has_permissions(kick_members=True)
	async def register(self, interaction:discord.Interaction):
		collection_2 = self.bot.db["Eco_guild_balance"]
		collection_4 = self.bot.db["Eco_limits"]
		collection = self.bot.db["Eco_guild_shop"]
		Guild_Start = 0
		async for m in collection_4.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Guild_Start = m["Server"]
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Currency"] = Guild_Start
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}):
			guild = m["Guild"]
			if guild == interaction.guild.id:
				embed = discord.Embed(title="__**Register Error**__", description=f"You already have Setup Currency Exchange.", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				await interaction.followup.send(embed=embed)
				return
		await collection_2.insert_one(log)
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Items"] = []
		log ["Price"] = []
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Server Registered**__", description=f"You have Successfully Registered ***{interaction.guild}*** for Currency Exchange.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@register.error
	async def register_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Register this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="withdraw", description="Withdraw Currency from Specified Member") # Admin Withdraw Command
	@app_commands.describe(amount="Amount to Withdraw", member="Member to Withdraw From")
	@app_commands.checks.has_permissions(kick_members=True)
	async def withdraw(self, interaction:discord.Interaction, amount: int, *, member: discord.Member):
		collection = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["logs"]
		server = None
		recipent = None
		mod_log = None
		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Withdraw Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		member_info = collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		ending_balance = balance - amount
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": ending_balance}})
		embed = discord.Embed(title="__**Withdraw**__", description=f"**{amount}** has been Withdrawed from ***{member}***.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if not mod_log is None:
			await mod_log.send(embed=embed)
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@withdraw.error
	async def withdraw_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Withdraw Funds from Members in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="deposit", description="Deposit Currency to Specified Member") # Admin Deposit Command
	@app_commands.describe(amount="Amount to Deposit", member="Member to Deposit to")
	@app_commands.checks.has_permissions(kick_members=True)
	async def deposit(self, interaction:discord.Interaction, amount: int, *, member: discord.Member):
		collection = self.bot.db["Eco_member_balance"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		collection_2 = self.bot.db["logs"]
		server = None
		recipent = None
		mod_log = None
		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0}):
			recipent = m["Member"]
		if recipent is None:
			embed = discord.Embed(title="__**Deposit Error**__", description=f"**{member}** has not Applied for an Account..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		member_info = collection.find({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"_id": 0})
		async for m in member_info:
			balance = m["Currency"]
		ending_balance = balance + amount
		await collection.update_one({"Guild": interaction.guild.id, "Member": interaction.user.id}, {"$set":{"Currency": ending_balance}})
		embed = discord.Embed(title="__**Deposit**__", description=f"**{amount}** has Deposited to ***{member}*** .", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if not mod_log is None:
			await mod_log.send(embed=embed)
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@deposit.error
	async def deposit_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Deposit Funds to Members in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="add", description="Create Item for Server Shop") # Add Item Command
	@app_commands.describe(price="Price of Item", item="Name of Item")
	@app_commands.checks.has_permissions(kick_members=True)
	async def add(self, interaction:discord.Interaction, price:int, *, item: str):
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Shop Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		grab_items = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		items = [f"{item}"]
		price = [price]
		async for m in grab_items:
			items += m["Items"]
			price += m["Price"]
		await collection_2.update_one({"Guild": interaction.guild.id}, {"$set":{"Items": items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Added**__", description=f"*{item}* has been to Added the Shop.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@add.error
	async def add_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Add Items to the Shop in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="remove", description="Remove Item from Server Shop") # Remove Item Command
	@app_commands.describe(item="Item Index to Remove")
	@app_commands.checks.has_permissions(kick_members=True)
	async def remove(self, interaction:discord.Interaction, *, item: int):
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		if server is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		items = []
		price =[]
		grab_snippets = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for m in grab_snippets:
			items += m["Items"]
			price += m["Price"]
		if items is None:
			embed = discord.Embed(title="__**Remove Error**__", description=f"There's nothing in {interaction.guild}'s Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Remove Error**__", description=f"There's nothing in {interaction.guild}'s Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		item_name = items[item-1]
		items.pop(item-1)
		price.pop(item-1)
		await collection_2.update_one({"Guild": interaction.guild.id}, {"$set":{"Items": items, "Price": price}})
		embed = discord.Embed(title=f"__**Item Removed**__", description=f"*{item_name}* has been Removed from the Shop.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@remove.error
	async def remove_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Remove Items from the Shop in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="clear", description="Removes All Items from Server's Shop") # Clear Shop Command
	@app_commands.checks.has_permissions(kick_members=True)
	async def clear(self, interaction:discord.Interaction):
		collection_2 = self.bot.db["Eco_guild_shop"]
		collection_3 = self.bot.db["Eco_guild_balance"]
		server = None
		items = None
		async for m in collection_3.find({"Guild": interaction.guild.id}, {"_id": 0}):
			server = m["Guild"]
		async for m in collection_2.find({"Guild": interaction.guild.id}, {"_id": 0}):
			items = m["Items"]
		if server is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"**{interaction.guild}** hasn't Registered with {self.bot.user.mention} to use Currency Exchange..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if items is None:
			embed = discord.Embed(title="__**Clear Error**__", description=f"There's nothing in {interaction.guild}'s Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(items) <= 0:
			embed = discord.Embed(title="__**Clear Error**__", description=f"There's nothing in {interaction.guild}'s Shop.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		await collection_2.update_one({"Guild": interaction.guild.id}, {"$set":{"Items": [], "Price": []}})
		embed = discord.Embed(title=f"__**Shop Cleared**__", description=f"All Items has been Cleared from {interaction.guild}'s Shop.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@clear.error
	async def clear_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear the Shop in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="limit_bag", description="Set Server Bag Limit") # Bag Limit Command
	@app_commands.describe(amount="Amount of Items Allowed in Bag")
	@app_commands.checks.has_permissions(kick_members=True)
	async def limit_bag(self, interaction:discord.Interaction, amount: int):
		collection = self.bot.db["Eco_limits"]
		Box_Limit = 500
		Guild_Start = 0
		User_Start = 0
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Box_Limit = m["Box"]
			Guild_Start = m["Server"]
			User_Start = m["User"]
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Bag"] = amount
		log ["Box"] = Box_Limit
		log ["Server"] = Guild_Start
		log ["User"] = User_Start
		old_log = {"Guild": interaction.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Bag Storage**__", description=f"You have Changed {interaction.guild}'s Bag Limit to **{amount}** Slots.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@limit_bag.error
	async def limit_bag_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the Bag Limit in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="limit_box", description="Set Server Safety Box Limit") # Box Limit Command
	@app_commands.describe(amount="Amount of Items Allowed in Safety Deposit Box")
	@app_commands.checks.has_permissions(kick_members=True)
	async def limit_box(self, interaction:discord.Interaction, amount: int):
		collection = self.bot.db["Eco_limits"]
		Bag_Limit = 30
		Guild_Start = 0
		User_Start = 0
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
			Guild_Start = m["Server"]
			User_Start = m["User"]
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Bag"] = Bag_Limit
		log ["Box"] = amount
		log ["Server"] = Guild_Start
		log ["User"] = User_Start
		old_log = {"Guild": interaction.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Security Box Storage**__", description=f"You have Changed {interaction.guild}'s Security Box Limit to **{amount}** Slots.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@limit_box.error
	async def limit_box_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the Security Box Limit in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="limit_user_start", description="Set Amount of Currency for New Currency Exchange Members to Receive") # User Start Command
	@app_commands.describe(amount="Amount of Currency to Receive")
	@app_commands.checks.has_permissions(kick_members=True)
	async def limit_user_start(self, interaction:discord.Interaction, amount: int):
		collection = self.bot.db["Eco_limits"]
		Bag_Limit = 30
		Box_Limit = 500
		Guild_Start = 0
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
			Box_Limit = m["Box"]
			Guild_Start =m["Server"]
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Bag"] = Bag_Limit
		log ["Box"] = Box_Limit
		log ["Server"] = Guild_Start
		log ["User"] = amount
		old_log = {"Guild": interaction.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**User Start Balance**__", description=f"You have Changed {interaction.guild}'s User Start Balance to **{amount}**.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@limit_user_start.error
	async def limit_user_start_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the User Start Balance in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@admin_eco.command(name="limit_server_start", description="Set Amount of Currency for Server to Begin with") # Server Start Command
	@app_commands.describe(amount="Amount to Begin with")
	@app_commands.checks.has_permissions(kick_members=True)
	async def limit_server_start(self, interaction:discord.Interaction, amount: int):
		collection = self.bot.db["Eco_limits"]
		Bag_Limit = 30
		User_Start = 0
		Box_Limit = 500
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0}):
			Bag_Limit = m["Bag"]
			Box_Limit = m["Box"]
			User_Start= m["User"]
		log = {}
		log ["Guild"] = interaction.guild.id
		log ["Bag"] = Bag_Limit
		log ["Box"] = Box_Limit
		log ["Server"] = amount
		log ["User"] = User_Start
		old_log = {"Guild": interaction.guild.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Server Start Balance**__", description=f"You have Changed {interaction.guild}'s Start Balance to **{amount}**.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@limit_server_start.error
	async def limit_server_start_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Set the Server's Start Balance in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Economy(bot))