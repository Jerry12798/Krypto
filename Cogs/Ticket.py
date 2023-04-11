import discord
import asyncio
import time
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime
from Utils.Menus import Formatter, Pager



class Ticketer(commands.Cog, name="Ticketer", description="Ticket Commands"):
	def __init__(self,bot):
		self.bot = bot

	@commands.command() # Set Ticket Message
	@commands.has_permissions(administrator=True)
	async def tmessage(self, ctx, name: str=None, *, content: str=None):
		if name is None:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Create Name for Ticket.\n`{self.bot.prefix}tmessage <Ticket Name> <Ticket Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Attach Ticket Message.\n`{self.bot.prefix}tmessage <Ticket Name> <Ticket Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(content) > 950:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Please Keep Message under 950 Characters.\n`{self.bot.prefix}tmessage <Ticket Name> <Ticket Message>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Ticket_messages"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Ticket"] = name
		log ["Message"] = content
		embed = discord.Embed(title="__**Ticket Setup**__", description=f"Ticket Message has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		ticketz = []
		async for x in collection.find({"Guild": ctx.guild.id}, {"_id": 0, "Channel": 0}):
			ticketz += {x["Ticket"]}
		if name not in ticketz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Ticket Setup**__", description=f"Ticket Message has been changed to\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if name in ticketz:
			old_log = {"Guild": ctx.guild.id, "Ticket": name}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@tmessage.error
	async def tmessage_error(self, ctx, error):
		embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if isinstance(error, commands.CheckFailure):
			await ctx.send(embed=embed)

	@commands.command() # Set Ticket Category
	@commands.has_permissions(administrator=True)
	async def tcategory(self, ctx, *, category: discord.CategoryChannel=None):
		if category is None:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Mention Category to Send Tickets in.\n`{self.bot.prefix}tcategory <Mention Category>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return

		collection = self.bot.db["Ticket_category"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Category"] = category.id
		embed = discord.Embed(title="__**Ticket Setup**__", description=f"Tickets will now be sent to {category.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Ticket Setup**__", description=f"Tickets will no longer be sent to {category.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))

		category = None
		async for x in collection.find({"Guild": ctx.guild.id}, {"_id": 0, "Guild": 0}):
			category = {x["Category"]}
		if category is None:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
		else:
			old_log = {"Guild": ctx.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
	@tcategory.error
	async def tcategory_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Support Roles for Tickets
	@commands.has_permissions(administrator=True)
	async def trole(self, ctx, *, content: discord.Role=None):
		if content is None:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Mention a Role to Add to Ticket Support Roles.\n`{self.bot.prefix}trole <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Ticket_roles"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Role"] = content.id
		embed = discord.Embed(title="__**Ticket Setup**__", description=f"{content.mention} has been Added to Ticket Support Roles.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		rolez = []
		async for x in collection.find({"Guild": ctx.guild.id}, {"_id": 0, "Channel": 0}):
			rolez += {x["Role"]}
		if content.id not in rolez:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Ticket Setup**__", description=f"{content.mention} has been Removed from Ticket Support Roles.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if content.id in rolez:
			old_log = {"Guild": ctx.message.guild.id, "Role": content.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@trole.error
	async def trole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Send Ticket
	@commands.has_permissions(administrator=True)
	async def ticket(self, ctx, channel: discord.TextChannel=None, *, name: str=None):
		if channel is None:
			embed = discord.Embed(title="__**Ticket Error**__", description=f"Mention Channel to Toggle Ticket in.\n`{self.bot.prefix}ticket <Mention Channel> <Ticket Name>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Ticket_watchers"]
		collection_2 = self.bot.db["Ticket_messages"]

		embed = discord.Embed(title="__**Ticket**__", description=f"Ticket has been activated in {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Support Ticket**__", description=f"To Create a Ticket React with :envelope_with_arrow:", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))

		ticket_msg = None
		async for x in collection_2.find({"Guild": ctx.guild.id, "Ticket": name}, {"_id": 0, "Channel": 0}):
			ticket_msg = {x["Message"]}
		if not ticket_msg is None:
			embed_3 = discord.Embed(title="__**Support Ticket**__", description=f"{ticket_msg}", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.display_avatar.replace(format="png", static_format="png"))

		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id

		await ctx.send(embed=embed)
		msg = await channel.send(embed=embed_3)
		log ["Message"] = msg.id
		await msg.add_reaction("\U0001f4e9")
		await collection.insert_one(log)
		await ctx.message.delete()
		return
	@ticket.error
	async def ticket_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Ticketer(bot))