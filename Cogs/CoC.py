import discord
import asyncio
import coc
import json
import time
import motor.motor_asyncio
import pymongo
from discord.ext import commands
from datetime import datetime

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

CoC_Email = config['CoC_Email']
CoC_Pass = config['CoC_Pass']
CoC_Key_Name = config['CoC_Key_Name']
CoC_Client = coc.EventsClient(key_names=CoC_Key_Name)



class CoC(commands.Cog, name="CoC"):
	def __init__(self,bot):
		self.bot = bot
		self.bot.coc = self.bot.loop.create_task(CoC_Client.login(CoC_Email, CoC_Pass))
	def cog_unload(self):
		self.bot.coc.cancel()
		coc.close()
		
	@commands.command() # Player Information Command
	async def pinfo(self, ctx, *, player: str=None):
		if player is None:
			embed = discord.Embed(title="__**Player Information Error**__", description=f"Specify Player's Tag to get Information about.\n`{self.bot.prefix}pinfo <Player Tag>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			playerz = await self.bot.coc.get_player(player)
		except:
			embed = discord.Embed(title="__**Player Information Error**__", description=f"Player with Tag `{player}` could not be found.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		#print(playerz.clan)

		order_5 = "" 
		for m in playerz.labels:
			order_5 += f"*{m.name}*, "

		amount = 3
		embed = discord.Embed(title=f"__***Player Information***__ *(1/{amount})*", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name="__**General**__", value=f"**:bust_in_silhouette: Name:** {playerz.name}\n**:name_badge: Tag:** {player}\n**:classical_building: Townhall:** {playerz.town_hall}\n**:construction_site: Builder Hall:** {playerz.builder_hall}\n**:space_invader:  EXP:** {playerz.exp_level}\n**:globe_with_meridians: League:** {playerz.league}\n**:alien: Clan Role:** {playerz.role}\n[Click to View](<{playerz.share_link}>)", inline=False)
		embed.add_field(name="__**Stats**__", value=f"**:crossed_swords: Attack Wins:** {playerz.attack_wins}\n**:shield: Defense Wins:** {playerz.defense_wins}\n**:small_red_triangle: Versus Wins:** {playerz.versus_attack_wins}\n**:outbox_tray: Donations:** {playerz.donations}\n**:inbox_tray: Received Donations:** {playerz.received}\n**:star: War Stars:** {playerz.war_stars}\n**:beginner: League Rank:** {playerz.league_rank}", inline=False)
		embed.add_field(name="__**Trophies**__", value=f"**:reminder_ribbon: Labels:** {order_5}\n**:trophy: Trophies:** {playerz.trophies}\n**:skull_crossbones: Versus Trophies:** {playerz.versus_trophies}\n**:chart_with_upwards_trend: Best Trophies:** {playerz.best_trophies}\n**:fleur_de_lis: Best Versus Trophies:** {playerz.best_versus_trophies}", inline=False)
		embed.add_field(name="__**Clan**__", value=f"**:crown: Name:** {playerz.clan}\n**:busts_in_silhouette: Tag**: {playerz.clan.tag}\n**:calendar: Current Clan Rank:** {playerz.clan_rank}\n**:bar_chart: Previous Clan Rank:** {playerz.clan_previous_rank}", inline=False)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		message = await ctx.send(embed=embed)

		collection = self.bot.db["AM_player"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Player"] = player
		log ["Counter"] = 1
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

	@commands.command() # Clan Information Command
	async def clan(self, ctx, *, clan: str=None):
		if clan is None:
			embed = discord.Embed(title="__**Clan Information Error**__", description=f"Specify Clan's Tag to get Information about.\n`{self.bot.prefix}pinfo <Player Tag>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			clanz = await self.bot.coc.get_clan(clan)
		except:
			embed = discord.Embed(title="__**Clan Information Error**__", description=f"Clan with Tag `{clan}` could not be found.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		order_5 = "" 
		for m in clanz.labels:
			order_5 += f"*{m.name}*, "
		members = ""
		for m in clanz.members:
			members += f"{m.name}, "

		embed = discord.Embed(title="__**General Information**__ *(1/2)*", description=f"{clanz.description}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name="__**General**__", value=f"**:crown: Name:** {clanz.name}\n**:busts_in_silhouette: Members:** {clanz.member_count}\n**:name_badge: Tag:** {clan}\n**:calendar: Rank:** {clanz.rank}\n**:bar_chart: Previous Rank:** {clanz.previous_rank}\n**:fleur_de_lis: Type:** {clanz.type}\n**:pencil: Requirements:** {clanz.required_trophies}\n**:chart_with_upwards_trend: Public War Log:** {clanz.public_war_log}\n**:notepad_spiral: War Frequency:** {clanz.war_frequency}\n[Click to View](<{clanz.share_link}>)", inline=False)
		embed.add_field(name="__**Stats**__", value=f"**:reminder_ribbon: Labels:** {order_5}\n**:small_red_triangle: Wins:** {clanz.war_wins}\n**:small_red_triangle_down: Losses:** {clanz.war_losses}\n**:shield: Ties:** {clanz.war_ties}\n**:trophy: Points:** {clanz.points}\n**:skull_crossbones: Versus Points:** {clanz.versus_points}", inline=False)
		#embed.set_thumbnail(url=clanz.badge)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		message = await ctx.send(embed=embed)

		collection = self.bot.db["AM_clan"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Clan"] = clan
		log ["Counter"] = 1
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



	@commands.Cog.listener() # Paginate Player Information Event
	async def on_raw_reaction_add(self, payload):
		if payload.user_id == self.bot.user.id:
			return
	
		collection = self.bot.db["AM_player"]
		menu = collection.find({})
		helps = []
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				counter = x["Counter"]
				player = x["Player"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)

		if payload.message_id in helps:
			if not payload.user_id == author:
				return

			playerz = await self.bot.coc.get_player(player)

			order = "" 
			for m in playerz.troops:
				order += f"**{m.name}** *{m.level}*, "

			order_2 = "" 
			for m in playerz.heroes:
				order_2 += f"**{m.name}** *{m.level}*, "

			order_3 = "" 
			for m in playerz.achievements:
				order_3 += f"**{m.name}**, "

			order_4 = "" 
			for m in playerz.spells:
				order_4 += f"**{m.name}** *{m.level}*, "

			order_5 = "" 
			for m in playerz.labels:
				order_5 += f"*{m.name}*, "

			amount = 3
			embed = discord.Embed(title=f"__***Player Information***__ *(1/{amount})*", timestamp=datetime.utcnow(), color=0xff0000)
			embed.add_field(name="__**General**__", value=f"**:bust_in_silhouette: Name:** {playerz.name}\n**:name_badge: Tag:** {player}\n**:classical_building: Townhall:** {playerz.town_hall}\n**:construction_site: Builder Hall:** {playerz.builder_hall}\n**:space_invader:  EXP:** {playerz.exp_level}\n**:globe_with_meridians: League:** {playerz.league}\n**:alien: Clan Role:** {playerz.role}\n[Click to View](<{playerz.share_link}>)", inline=False)
			embed.add_field(name="__**Stats**__", value=f"**:crossed_swords: Attack Wins:** {playerz.attack_wins}\n**:shield: Defense Wins:** {playerz.defense_wins}\n**:small_red_triangle: Versus Wins:** {playerz.versus_attack_wins}\n**:outbox_tray: Donations:** {playerz.donations}\n**:inbox_tray: Received Donations:** {playerz.received}\n**:star: War Stars:** {playerz.war_stars}\n**:beginner: League Rank:** {playerz.league_rank}", inline=False)
			embed.add_field(name="__**Trophies**__", value=f"**:reminder_ribbon: Labels:** {order_5}\n**:trophy: Trophies:** {playerz.trophies}\n**:skull_crossbones: Versus Trophies:** {playerz.versus_trophies}\n**:chart_with_upwards_trend: Best Trophies:** {playerz.best_trophies}\n**:fleur_de_lis: Best Versus Trophies:** {playerz.best_versus_trophies}", inline=False)
			embed.add_field(name="__**Clan**__", value=f"**:crown: Name:** {playerz.clan}\n**:busts_in_silhouette: Tag**: {playerz.clan.tag}\n**:calendar: Current Clan Rank:** {playerz.clan_rank}\n**:bar_chart: Previous Clan Rank:** {playerz.clan_previous_rank}", inline=False)
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

			embed_2 = discord.Embed(title=f"__***Detailed Information***__ *(2/{amount})*", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.add_field(name="__**:crossed_swords: Troops**__", value=f"{order}", inline=False)
			embed_2.add_field(name="__**:skull_crossbones: Heroes**__", value=f"{order_2}", inline=False)
			embed_2.add_field(name="__**:crystal_ball: Spells**__", value=f"{order_4}", inline=False)
			embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

			embed_3 = discord.Embed(title=f"__***:trophy: Achievements***__ *(3/{amount})*", description=f"{order_3}", timestamp=datetime.utcnow(), color=0xff0000)
			embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

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
				counter = 3
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > 3:
				counter = 3

			if counter == 1:
				await message.edit(embed=embed)

			if counter == 2:
				await message.edit(embed=embed_2)

			if counter == 3:
				await message.edit(embed=embed_3)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})



		collection_2 = self.bot.db["AM_clan"]
		menu = collection_2.find({})
		helps = []
		async for x in menu:
			helps += {x["Message"]}
			if x["Message"] == payload.message_id:
				author = x["Author"]
				Channel = x["Channel"]
				counter = x["Counter"]
				clan = x["Clan"]
				guild = self.bot.get_guild(payload.guild_id)
				member = guild.get_member(payload.user_id)
				channel = guild.get_channel(Channel)
				message = await channel.fetch_message(payload.message_id)

		if payload.message_id in helps:
			if not payload.user_id == author:
				return

			clanz = await self.bot.coc.get_clan(clan)

			amount = 2
			order_5 = "" 
			for m in clanz.labels:
				order_5 += f"*{m.name}*, "

			members = ""
			for m in clanz.members:
				members += f"{m.name}, "

			embed = discord.Embed(title=f"__**General Information**__ *(1/{amount})*", description=f"{clanz.description}", timestamp=datetime.utcnow(), color=0xff0000)
			embed.add_field(name="__**General**__", value=f"**:crown: Name:** {clanz.name}\n**:busts_in_silhouette: Members:** {clanz.member_count}\n**:name_badge: Tag:** {clan}\n**:calendar: Rank:** {clanz.rank}\n**:bar_chart: Previous Rank:** {clanz.previous_rank}\n**:fleur_de_lis: Type:** {clanz.type}\n**:pencil: Requirements:** {clanz.required_trophies}\n**:chart_with_upwards_trend: Public War Log:** {clanz.public_war_log}\n**:notepad_spiral: War Frequency:** {clanz.war_frequency}\n[Click to View](<{clanz.share_link}>)", inline=False)
			embed.add_field(name="__**Stats**__", value=f"**:reminder_ribbon: Labels:** {order_5}\n**:small_red_triangle: Wins:** {clanz.war_wins}\n**:small_red_triangle_down: Losses:** {clanz.war_losses}\n**:shield: Ties:** {clanz.war_ties}\n**:trophy: Points:** {clanz.points}\n**:skull_crossbones: Versus Points:** {clanz.versus_points}", inline=False)
			#embed.set_thumbnail(url=clanz.badge)
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

			embed_2 = discord.Embed(title=f"__**Clan Members**__ *(2/{amount})*", description=f"{members}", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))

			"""embed_3 = discord.Embed(title="__**War Information**__", description=f"{clanz.description}", timestamp=datetime.utcnow(), color=0xff0000)
			embed_3.add_field(name="__**Stats**__", value=f"**EXP Earned:** {clanz.exp_earned}\n**War Stars:** {clanz.stars}\n**Max Stars:** {clanz.max_stars}\n**Attacks Used:** {clanz.attacks_used}\n**Destruction:** {clanz.destruction}", inline=False)
			embed_3.add_field(name="__**Attacks**__", value=f"{clanz.attacks}", inline=False)
			embed_3.add_field(name="__**Defenses**__", value=f"{clanz.defenses}", inline=False)
			embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))"""

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
				counter = 2
				for x in message.reactions:
					if x.emoji == "\U000023ed":
						reaction = x

			if counter < 1:
				counter = 1

			if counter > 2:
				counter = 2

			if counter == 1:
				await message.edit(embed=embed)

			if counter == 2:
				await message.edit(embed=embed_2)

			#if counter == 3:
				#await message.edit(embed=embed_3)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

def setup(bot):
	bot.add_cog(CoC(bot))