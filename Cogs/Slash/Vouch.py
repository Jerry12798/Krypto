import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from Utils.Menus import Formatter, Pager



class Vouch(commands.Cog, app_commands.Group, name="vouch", description="Vouching Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="check", description="Check Your or Specified Member's Vouches") # Vouches Command
	@app_commands.describe(member="Member to Check Vouches for")
	async def check(self, interaction:discord.Interaction, member:discord.Member=None):
		if member is None:
			member = interaction.user
		collection_2 = self.bot.db["Eco_member_vouches"]
		collection_3 = self.bot.db["Eco_profile_banner"]
		collection_4 = self.bot.db["Eco_profile_link"]

		profile_banner = None
		grab_banner = collection_3.find({"Member": member.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			profile_banner = x["Message"]
		profile_link = "-"
		grab_banner = collection_4.find({"Member": member.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			profile_link = x["Message"]

		bag = None
		order = ""
		counter = 1
		check = 0
		embeds = []
		grab_bag = collection_2.find({"Member": member.id}, {"_id": 0})
		async for m in grab_bag:
			bag = m["Items"]
		if bag is None:
			embed = discord.Embed(title=f"**{member}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** 0\n**Positive:** 0\n**Negative:** 0\n__**Shop Link**__\n{profile_link}\n{member} has no Vouches..\nBe sure to use a Middleman", timestamp=datetime.now(), color=0xff0000)
			embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.display_avatar.replace(format="png", static_format="png")))
			if not profile_banner is None:
				embed.set_image(url=f"{profile_banner}")
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		for m in bag:
			order += f"**{counter}:** {m}\n"
			counter += 1
			check += 1
			if check == 10:
				embed = discord.Embed(title=f"**{member}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** {len(bag)}\n**Positive:** {len(bag)}\n**Negative:** 0\n__**Shop Link**__\n{profile_link}", timestamp=datetime.now(), color=0xac5ece)
				embed.add_field(name="__**Vouches**__", value=f"{order}", inline=False)
				embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
				embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.display_avatar.replace(format="png", static_format="png")))
				if not profile_banner is None:
					embed.set_image(url=f"{profile_banner}")
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				check = 0
				order = ""
				embeds.append(embed)
		if len(bag) <= 0:
			embed = discord.Embed(title=f"**{member}'s Vouches**", description=f"__**Vouch Information**__\n**Total:** 0\n**Positive:** 0\n**Negative:** 0\n__**Shop Link**__\n{profile_link}\n{member} has no Vouches..\nBe sure to use a Middleman", timestamp=datetime.now(), color=0xff0000)
			embed.add_field(name="__**Vouches**__", value=f"{order}", inline=False)
			embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed.set_author(name=f"{self.bot.user.name} Vouch", icon_url=str(self.bot.user.display_avatar.replace(format="png", static_format="png")))
			if not profile_banner is None:
				embed.set_image(url=f"{profile_banner}")
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		
		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@app_commands.command(name="new", description="Vouch for Specified Member") # Vouch Command
	@app_commands.describe(member="Member to Vouch for", reason="Reason for Vouching")
	async def new(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		if member.id == interaction.user.id:
			embed = discord.Embed(title="__**Vouch Error**__", description=f"You can't Vouch for yourself.\n`{self.bot.prefix}vouch <Mention Member> <Vouch Details>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection_2 = self.bot.db["Eco_pending_vouch"]
		collection = self.bot.db["Eco_total_vouches"]
		total = 0
		grab_total = collection.find({}, {"_id": 0, "Guild": 0})
		async for m in grab_total:
			total = m["Total_Vouches"]
		total += 1
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		embed_2 = discord.Embed(title=f"__**Incoming Vouch**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_author(name=f"{member}", icon_url=str(member.display_avatar.replace(format="png", static_format="png")))
		embed_2.add_field(name="Server:", value=f"**{interaction.guild}**", inline=False)
		embed_2.add_field(name="Vouch ID:", value=f"**{total}**", inline=False)
		embed_2.add_field(name="Details:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		message = await mod_log.send(embed=embed_2)
		counter = {}
		counter ["Total_Vouches"] = total
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = message.id
		log ["Member"] = member.id
		log ["Buyer"] = interaction.user.id
		log ["Vouch_ID"] = total
		log ["Vouch"] = reason
		old_counter = {}
		await collection_2.insert_one(log)
		await collection.delete_one(old_counter)
		await collection.insert_one(counter)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Submitted**\n**Vouch ID:** `{total}`\n*You MUST Clearly State Items Received & Amount if Applicable. If you have not use the Revouch Command below.*\n`{Bot_Prefix}revouch <Vouch ID> <Vouch Details>`", timestamp=datetime.now(), color=0xff0000)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		message = await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="redo", description="Revouch for Specified Vouch") # Revouch Command
	@app_commands.describe(vouch="Vouch ID to Fix", reason="Reason for Vouch/Revouch")
	async def redo(self, interaction:discord.Interaction, vouch:int, *, reason:str):
		collection_2 = self.bot.db["Eco_pending_vouch"]
		grab_member = collection_2.find({"Vouch_ID": vouch}, {"_id": 0})
		async for x in grab_member:
			grab_buyer = x["Buyer"]
			member_user_id = x["Member"]
			grab_message = x["Message"]
		if not grab_buyer == interaction.user.id:
			embed = discord.Embed(title="__**Revouch Error**__", description=f"You can only Revouch for your Vouches.\n`{self.bot.prefix}revouch <Vouch ID> <Vouch Details>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		member_user = interaction.guild.get_member(member_user_id)
		mod_log = self.bot.get_channel(self.bot.vouch_queue)
		message = await mod_log.fetch_message(grab_message)
		embed_2 = discord.Embed(title=f"__**Incoming Vouch**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_author(name=f"{member_user}", icon_url=str(member_user.display_avatar.replace(format="png", static_format="png")))
		embed_2.add_field(name="Server:", value=f"**{interaction.guild}**", inline=False)
		embed_2.add_field(name="Vouch ID:", value=f"**{vouch}**", inline=False)
		embed_2.add_field(name="Details:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await message.edit(embed=embed_2)
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Member"] = member_user.id
		log ["Message"] = message.id
		log ["Buyer"] = interaction.user.id
		log ["Vouch_ID"] = vouch
		log ["Vouch"] = reason
		old_log = {"Vouch_ID": vouch}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**{self.bot.user.name} Vouch**__", description=f"**Vouch Resubmitted**\n**Vouch ID:** `{vouch}`\n*{reason}*", timestamp=datetime.now(), color=0xff0000)
		embed.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	setup = app_commands.Group(name="set", description="Vouch Profile Setup Commands")

	@setup.command(name="banner", description="Set Banner for Vouch Profile") # Set Profile Banner
	@app_commands.describe(banner="Banner URL to Display on Vouch Profile")
	async def banner(self, interaction:discord.Interaction, *, banner: str):
		if not banner.startswith("https://"):
			embed = discord.Embed(title="__**Setup Error**__", description=f"Please Enter a Valid URL.\n`{self.bot.prefix}vbanner <Banner URL>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Eco_profile_banner"]
		log = {}
		log ["Member"] = interaction.user.id
		log ["Message"] = banner
		embed = discord.Embed(title="__**Profile Setup**__", description=f"Your Banner has been set as\n{banner}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Member"]}
		if interaction.user.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Profile Setup**__", description=f"Your Banner has been changed to\n{banner}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.user.id in guildz:
			old_log = {"Member": interaction.user.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return

	@setup.command(name="profile_url", description="Set Custom URL to Display on Vouch Profile") # Set Profile Link
	@app_commands.describe(url="URL to Display on Vouch Profile")
	async def profile_url(self, interaction:discord.Interaction, *, url:str):
		if not url.startswith("https://"):
			embed = discord.Embed(title="__**Setup Error**__", description=f"Please Enter a Valid URL.\n`{self.bot.prefix}vlink <URL>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Eco_profile_link"]
		log = {}
		log ["Member"] = interaction.user.id
		log ["Message"] = url
		embed = discord.Embed(title="__**Profile Setup**__", description=f"Your Profile Link has been set as\n{url}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Member"]}
		if interaction.user.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Profile Setup**__", description=f"Your Profile Link has been changed to\n{url}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.user.id in guildz:
			old_log = {"Member": interaction.user.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return

async def setup(bot):
	await bot.add_cog(Vouch(bot))