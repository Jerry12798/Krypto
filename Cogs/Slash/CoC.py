import discord
import asyncio
import coc
import json
import time
import traceback
import motor.motor_asyncio
import pymongo
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from Utils.Menus import Formatter, Pager

with open('Config.json', 'r') as configuration:
	config = json.load(configuration)

CoC_Email = config['CoC_Email']
CoC_Pass = config['CoC_Pass']
CoC_Key_Name = config['CoC_Key_Name']



class CoC(commands.Cog, app_commands.Group, name="coc", description="Clash of Clans Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot
		if not hasattr(self.bot, 'coc_client'):
			self.bot.coc_client = coc.EventsClient(key_names=CoC_Key_Name)
			self.bot.coc = self.bot.loop.create_task(self.bot.coc_client.login(CoC_Email, CoC_Pass))
	async def cog_unload(self):
		if hasattr(self.bot, 'coc'):
			self.bot.coc.cancel()
			self.bot.coc_client.close()
		
	@app_commands.command(name="player", description="Display Information on Clash of Clans Player") # Player Information Command
	@app_commands.describe(player="Player Tag to Lookup")
	async def pinfo(self, interaction:discord.Interaction, *, player:str):
		try:
			playerz = await self.bot.coc_client.get_player(player)
		except Exception as e:
			embed = discord.Embed(title="__**Player Information Error**__", description=f"Player with Tag `{player}` could not be found.\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return

		order = "" 
		for m in playerz.troops:
			order += f"**{m.name}** *{m.level}*, "
		try:
			league_rank = playerz.league_rank
		except:
			league_rank = 'N/A'
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

		current = 1
		amount = 3
		embeds = []
		embed = discord.Embed(title=f"__***Player Information***__ *({current}/{amount})*", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name="__**General**__", value=f"**:bust_in_silhouette: Name:** {playerz.name}\n**:name_badge: Tag:** {player}\n**:classical_building: Townhall:** {playerz.town_hall}\n**:construction_site: Builder Hall:** {playerz.builder_hall}\n**:space_invader:  EXP:** {playerz.exp_level}\n**:globe_with_meridians: League:** {playerz.league}\n**:alien: Clan Role:** {playerz.role}\n[Click to View](<{playerz.share_link}>)", inline=False)
		embed.add_field(name="__**Stats**__", value=f"**:crossed_swords: Attack Wins:** {playerz.attack_wins}\n**:shield: Defense Wins:** {playerz.defense_wins}\n**:small_red_triangle: Versus Wins:** {playerz.versus_attack_wins}\n**:outbox_tray: Donations:** {playerz.donations}\n**:inbox_tray: Received Donations:** {playerz.received}\n**:star: War Stars:** {playerz.war_stars}\n**:beginner: League Rank:** {league_rank}", inline=False)
		embed.add_field(name="__**Trophies**__", value=f"**:reminder_ribbon: Labels:** {order_5}\n**:trophy: Trophies:** {playerz.trophies}\n**:skull_crossbones: Versus Trophies:** {playerz.versus_trophies}\n**:chart_with_upwards_trend: Best Trophies:** {playerz.best_trophies}\n**:fleur_de_lis: Best Versus Trophies:** {playerz.best_versus_trophies}", inline=False)
		embed.add_field(name="__**Clan**__", value=f"**:crown: Name:** {playerz.clan}\n**:busts_in_silhouette: Tag**: {playerz.clan.tag}\n**:calendar: Current Clan Rank:** {playerz.clan_rank}\n**:bar_chart: Previous Clan Rank:** {playerz.clan_previous_rank}", inline=False)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embeds.append(embed)

		current += 1

		embed = discord.Embed(title=f"__***Detailed Information***__ *({current}/{amount})*", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name="__**:crossed_swords: Troops**__", value=f"{order}", inline=False)
		embed.add_field(name="__**:skull_crossbones: Heroes**__", value=f"{order_2}", inline=False)
		embed.add_field(name="__**:crystal_ball: Spells**__", value=f"{order_4}", inline=False)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embeds.append(embed)

		current += 1

		embed = discord.Embed(title=f"__***:trophy: Achievements***__ *({current}/{amount})*", description=f"{order_3}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embeds.append(embed)

		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)

	@app_commands.command(name="clan", description="Display Information on Clash of Clans Clan") # Clan Information Command
	@app_commands.describe(clan="Clan Tag to Lookup")
	async def clan(self, interaction:discord.Interaction, *, clan:str):
		try:
			clanz = await self.bot.coc_client.get_clan(clan)
		except Exception as e:
			embed = discord.Embed(title="__**Clan Information Error**__", description=f"Clan with Tag `{clan}` could not be found.\n__**Traceback**__```py\n{traceback.format_exc()}```", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		order_5 = "" 
		for m in clanz.labels:
			order_5 += f"*{m.name}*, "
		members = ""
		for m in clanz.members:
			members += f"{m.name}, "
		try:
			rank = clanz.rank
		except:
			rank = 'N/A'
		try:
			previous_rank = clanz.previous_rank
		except:
			previous_rank = 'N/A'
		try:
			badge = clanz.badge.url
		except:
			badge = None

		current = 1
		amount = 2
		embeds = []
		embed = discord.Embed(title=f"__**General Information**__ *({current}/{amount})*", description=f"{clanz.description}", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name="__**General**__", value=f"**:crown: Name:** {clanz.name}\n**:busts_in_silhouette: Members:** {clanz.member_count}\n**:name_badge: Tag:** {clan}\n**:calendar: Rank:** {rank}\n**:bar_chart: Previous Rank:** {previous_rank}\n**:fleur_de_lis: Type:** {clanz.type}\n**:pencil: Requirements:** {clanz.required_trophies}\n**:chart_with_upwards_trend: Public War Log:** {clanz.public_war_log}\n**:notepad_spiral: War Frequency:** {clanz.war_frequency}\n[Click to View](<{clanz.share_link}>)", inline=False)
		embed.add_field(name="__**Stats**__", value=f"**:reminder_ribbon: Labels:** {order_5}\n**:small_red_triangle: Wins:** {clanz.war_wins}\n**:small_red_triangle_down: Losses:** {clanz.war_losses}\n**:shield: Ties:** {clanz.war_ties}\n**:trophy: Points:** {clanz.points}\n**:skull_crossbones: Versus Points:** {clanz.versus_points}", inline=False)
		if not badge is None:
			embed.set_thumbnail(url=badge)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embeds.append(embed)

		current += 1

		embed = discord.Embed(title=f"__**Clan Members**__ *({current}/{amount})*", description=f"{members}", timestamp=datetime.now(), color=0xff0000)
		if not badge is None:
			embed.set_thumbnail(url=badge)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embeds.append(embed)

		current +=1

		"""embed = discord.Embed(title="__**War Information**__", description=f"{clanz.description}", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name="__**Stats**__", value=f"**EXP Earned:** {clanz.exp_earned}\n**War Stars:** {clanz.stars}\n**Max Stars:** {clanz.max_stars}\n**Attacks Used:** {clanz.attacks_used}\n**Destruction:** {clanz.destruction}", inline=False)
		embed.add_field(name="__**Attacks**__", value=f"{clanz.attacks}", inline=False)
		embed.add_field(name="__**Defenses**__", value=f"{clanz.defenses}", inline=False)
		if not badge is None:
			embed.set_thumbnail(url=badge)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embeds.append(embed)"""

		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)

async def setup(bot):
	await bot.add_cog(CoC(bot))