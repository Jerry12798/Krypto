import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from Utils.Menus import Formatter, Pager



class Ticket(commands.Cog, app_commands.Group, name="ticket", description="Ticket Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="panel_message", description="Creates Panel Message with Specified Name") # Set Ticket Message
	@app_commands.describe(name="Create Ticket Panel Name", content="Create Ticket Panel Message")
	@app_commands.checks.has_permissions(administrator=True)
	async def panel_message(self, interaction: discord.Interaction, name: str, *, content: str):
		if len(content) > 950:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Please Keep Message under 950 Characters.\n`{self.bot.prefix}tmessage <Ticket Name> <Ticket Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Ticket_messages"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Ticket"] = name
		log ["Message"] = content
		embed = discord.Embed(title="__**Ticket Setup**__", description=f"Ticket Message has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		ticketz = []
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Channel": 0}):
			ticketz += {x["Ticket"]}
		if name not in ticketz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Ticket Setup**__", description=f"Ticket Message has been changed to\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if name in ticketz:
			old_log = {"Guild": interaction.guild.id, "Ticket": name}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
	@panel_message.error
	async def panel_message_error(self, interaction, error):
		embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if isinstance(error, app_commands.CheckFailure):
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="category", description="Sets Category to Receive New Tickets in") # Set Ticket Category
	@app_commands.describe(category="Mention Category to Receive Tickets in")
	@app_commands.checks.has_permissions(administrator=True)
	async def category(self, interaction: discord.Interaction, *, category: discord.CategoryChannel):
		collection = self.bot.db["Ticket_category"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Category"] = category.id
		embed = discord.Embed(title="__**Ticket Setup**__", description=f"Tickets will now be sent to {category.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Ticket Setup**__", description=f"Tickets will no longer be sent to {category.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))

		category = None
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			category = {x["Category"]}
		if category is None:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
		else:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
	@category.error
	async def category_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="support_role", description="Sets Support Roles to be Added into Tickets") # Set Support Roles for Tickets
	@app_commands.describe(role="Mention Role to Add to Support Tickets")
	@app_commands.checks.has_permissions(administrator=True)
	async def support_role(self, interaction: discord.Interaction, *, role: discord.Role):
		collection = self.bot.db["Ticket_roles"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Role"] = role.id
		embed = discord.Embed(title="__**Ticket Setup**__", description=f"{role.mention} has been Added to Ticket Support Roles.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		rolez = []
		async for x in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Channel": 0}):
			rolez += {x["Role"]}
		if role.id not in rolez:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Ticket Setup**__", description=f"{role.mention} has been Removed from Ticket Support Roles.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if role.id in rolez:
			old_log = {"Guild": interaction.guild.id, "Role": role.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
	@support_role.error
	async def support_role_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="create", description="Creates Ticket in Specified Channel") # Send Ticket
	@app_commands.describe(channel="Channel to Send Ticket Creator in", name="Ticket Panel Name to Send")
	@app_commands.checks.has_permissions(administrator=True)
	async def create(self, interaction: discord.Interaction, channel: discord.TextChannel, *, name: str=None):
		collection = self.bot.db["Ticket_watchers"]
		collection_2 = self.bot.db["Ticket_messages"]

		embed = discord.Embed(title="__**Ticket**__", description=f"Ticket has been activated in {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Support Ticket**__", description=f"To Create a Ticket React with :envelope_with_arrow:", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))

		ticket_msg = None
		async for x in collection_2.find({"Guild": interaction.guild.id, "Ticket": name}, {"_id": 0, "Channel": 0}):
			ticket_msg = {x["Message"]}
		if not ticket_msg is None:
			embed_3 = discord.Embed(title="__**Support Ticket**__", description=f"{ticket_msg}", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))

		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id

		await interaction.followup.send(embed=embed)
		msg = await channel.send(embed=embed_3)
		log ["Message"] = msg.id
		await msg.add_reaction("\U0001f4e9")
		await collection.insert_one(log)
	@create.error
	async def create_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Ticket(bot))