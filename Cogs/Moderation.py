import discord
import asyncio
import time
import pytz
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from pytz import timezone



class Moderation(commands.Cog, name="Moderation"):
	def __init__(self,bot):
		self.bot = bot
	@commands.command(pass_context=True) # Rolemenu Command
	@commands.has_permissions(kick_members=True)
	async def rolemenu(self, ctx, menu=None, *options: discord.Role):
		if len(options)<= 1:
			embed = discord.Embed(title="__**Rolemenu Error**__", description=f"You need a Menu Name and more than One Role to make a Rolemenu.\n`{self.bot.prefix}rolemenu <Create Name> <Mention Role 1> <Mention Role 2>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(options) > 10:
			embed = discord.Embed(title="__**Rolemenu Error**__", description=f"You cant't make a Rolemenu with more than 10 Roles.\n`{self.bot.prefix}rolemenu <Create Name> <Mention Role 1> <Mention Role 2>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		else:
			reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		description = []
		for x, option in enumerate(options):
			description += "\n{}: `{}`".format(reactions[x], option)
		embed = discord.Embed(title=f"**Rolemenu: {menu}**", description="".join(description), timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		react_message = await ctx.send(embed=embed)
		for reaction in reactions[0:len(options)]:
			await react_message.add_reaction(reaction)
		roles = []
		for x in options:
			roles += {x.id}
		collection = self.bot.db["Mod_rolemenu"]
		menu = {}
		menu ["Guild_Name"] = ctx.guild.name
		menu ["Guild"] = ctx.guild.id
		menu ["Member"] = ctx.author.id
		menu ["Message"] = react_message.id
		menu ["Roles"] = roles
		await collection.insert_one(menu)
		await ctx.message.delete()
	@rolemenu.error
	async def rolemenu_error(self, ctx, error):
		if isinstance(error, commands.BadArgument):
			embed = discord.Embed(title="__**Command Error**__", description="You must put Quotation Marks before & after Menu Name if it's more than one word.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to make a Rolemenu in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command(pass_context=True) # Poll Command
	@commands.has_permissions(kick_members=True)
	async def poll(self, ctx, question=None, *options: str):
		if len(options)<= 1:
			embed = discord.Embed(title="__**Poll Error**__", description=f"You need a Question and more than One Choice to make a Poll.\n`{self.bot.prefix}poll <Create Name> <Choice 1> <Choice 2>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(options) > 10:
			embed = discord.Embed(title="__**Poll Error**__", description=f"You can't make a Poll with more than 10 Questions.\n*Seperate Poll Names & Answers that Contain Spaces with Quotation Marks.*\n`{Bot_Prefix}poll <Create Name> <Answer 1> <Answer 2>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(options) == 2 and options[0].upper() == "YES" and options[1].upper() == "NO":
			reactions = ["\u2705", "\u274C"]
		else:
			reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		description = []
		for x, option in enumerate(options):
			description += "\n{} {}".format(reactions[x], option)
		embed = discord.Embed(title=question, description="".join(description), timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		react_message = await ctx.send(embed=embed)
		for reaction in reactions[0:len(options)]:
			await react_message.add_reaction(reaction)
		await ctx.message.delete()
	@poll.error
	async def poll_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to make a Poll in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Add Role Command
	@commands.has_permissions(manage_roles=True)
	async def arole(self, ctx, role: discord.Role=None, member: discord.Member=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if role is None:
			embed_2 = discord.Embed(title="__**Role Assign Error**__", description=f"Specify a User & Role to Assign them.\n`{self.bot.prefix}arole <Mention Role> <Mention User>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
		elif member is None:
			embed_3 = discord.Embed(title="__**Role Assign Error**__", description=f"Specify a User to Assign to Role.\n`{self.bot.prefix}arole <Mention Role> <Mention User>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_3)
		else:
			embed = discord.Embed(title="__**Role Assigned**__", timestamp=datetime.utcnow(), color=0xff0000)
			embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
			embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
			embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			embed_4 = discord.Embed(title="__**Role Assigned**__", description=f"You have been Assigned `{role}` in **{ctx.message.guild}**", timestamp=datetime.utcnow(), color=0xff0000)
			embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await member.add_roles(role)
			try:
				await member.send(embed=embed_4)
			except:
				pass
			await ctx.send(embed=embed)
			if mod_log is None:
				await ctx.message.delete()
				return	
			await mod_log.send(embed=embed)
			await ctx.message.delete()
	@arole.error
	async def arole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Assign Roles in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Remove Role Command
	@commands.has_permissions(manage_roles=True)
	async def rrole(self, ctx, role: discord.Role=None, member: discord.Member=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if role is None:
			embed_2 = discord.Embed(title="__**Role Unassign Error**__", description=f"Specify a User & Role to Unassign them.\n`{self.bot.prefix}rrole <Mention Role> <Mention User>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
		elif member is None:
			embed_3 = discord.Embed(title="__**Role Unassign Error**__", description=f"Specify a User to Unassign from Role.\n`{self.bot.prefix}rrole <Mention Role> <Mention User>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_3)
		else:
			embed = discord.Embed(title="__**Role Unassigned**__", timestamp=datetime.utcnow(), color=0xff0000)
			embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
			embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
			embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			embed_4 = discord.Embed(title="__**Role Unassigned**__", description=f"You have been Unassigned `{role}` in **{ctx.message.guild}**", timestamp=datetime.utcnow(), color=0xff0000)
			embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await member.remove_roles(role)
			try:
				await member.send(embed=embed_4)
			except:
				pass
			await ctx.send(embed=embed)
			if mod_log is None:
				await ctx.message.delete()
				return
			await mod_log.send(embed=embed)
			await ctx.message.delete()
	@rrole.error
	async def rrole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unassign Roles in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Mass Remove Role Command
	@commands.has_permissions(manage_roles=True)
	async def mrrole(self, ctx, role: discord.Role=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if role is None:
			embed_2 = discord.Embed(title="__**Role Unassign Error**__", description=f"Specify a Role to Mass Unassign.\n`{self.bot.prefix}mrrole <Mention Role>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			return

		#embed_4 = discord.Embed(title="__**Role Unassigned**__", description=f"You have been Unassigned `{role}` in **{ctx.message.guild}**.", timestamp=datetime.utcnow(), color=0xff0000)
		#embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		total = 0
		for i in ctx.guild.members:
			
			try:
				await i.remove_roles(role)
				total += 1
			except:
				pass

		embed = discord.Embed(title="__**Role Mass Unassigned**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Members:", value=f"{total}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@mrrole.error
	async def mrrole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unassign Roles in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Mass Add Role Command
	@commands.has_permissions(manage_roles=True)
	async def marole(self, ctx, role: discord.Role=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if role is None:
			embed_2 = discord.Embed(title="__**Role Assign Error**__", description=f"Specify a Role to Mass Assign.\n`{self.bot.prefix}marole <Mention Role>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			return

		#embed_4 = discord.Embed(title="__**Role Assigned**__", description=f"You have been Assigned `{role}` in **{ctx.message.guild}**.", timestamp=datetime.utcnow(), color=0xff0000)
		#embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		total = 0
		for i in ctx.guild.members:
			
			try:
				await i.add_roles(role)
				total += 1
			except:
				pass

		embed = discord.Embed(title="__**Role Mass Assigned**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Members:", value=f"{total}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=ctx.guild.icon_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@marole.error
	async def marole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Assign Roles in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Ping Role Command
	@commands.has_permissions(manage_roles=True)
	async def prole(self, ctx, role: discord.Role=None, *, message=None):
		if role is None:
			embed = discord.Embed(title="__**Ping Role Error**__", description=f"Specify a Role & Create a Message to Send them.\n`{self.bot.prefix}prole <Mention Role> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		elif message is None:
			embed_2 = discord.Embed(title="__**Ping Role Error**__", description=f"Create a Message to Notify **{role}** about.\n`{self.bot.prefix}prole <Mention Role> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			return
		embed_3 = discord.Embed(title="__**Ping Notifications**__", description=f"{message}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(f"{role.mention}")
		await ctx.send(embed=embed_3)
		await ctx.message.delete()
	@prole.error
	async def prole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mention Ping Roles in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Message for Hire Role
	@commands.has_permissions(administrator=True)
	async def hrole(self, ctx, role: discord.Role=None, *, content=None):
		if role is None:
			embed = discord.Embed(title="__**Hire Role Error**__", description=f"Mention a Role and Create a Message for it.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**Hire Role Error**__", description=f"Create a Message for the Mentioned Role.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_hire"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Role"] = role.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Hire Role Message**__", description=f"{role.mention} Messsage has been set as\n{content}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		async for x in collection.find({}, {"_id": 0, "Role": role.id}):
			rolez = x["Role"]
		old_log = {"Role": role.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@hrole.error
	async def hrole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Hire Command
	@commands.has_permissions(administrator=True)
	async def hire(self, ctx, role: discord.Role=None, member: discord.Member=None):
		if role is None:
			embed_2 = discord.Embed(title="__**Hire Error**__", description=f"Specify a User & Role to Assign them.\n`{self.bot.prefix}hire <Mention Role> <Mention User>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
			return
		if member is None:
			embed_3 = discord.Embed(title="__**Hire Error**__", description=f"Specify a User to Hire.\n`{self.bot.prefix}hire <Mention Role> <Mention User>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_3)
			return
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Config_hire"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		role_message = None
		async for m in collection_2.find({"Role": role.id}, {"_id": 0, "Role": 0}):
			role_message = m["Message"]
		if role_message is None:
			embed_3 = discord.Embed(title="__**Hire Error**__", description=f"You must Create Hire Message for Role to Hire someone.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_3)
			return
		embed = discord.Embed(title="__**New Hire**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
		embed.add_field(name=":alien: Position:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Hired**__", description=f"You have been Assigned `{role}` in **{ctx.message.guild}**", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_5 = discord.Embed(title="__**New Hire**__", description=f"{member.mention}, {role_message}", timestamp=datetime.utcnow(), color=0xff0000)
		embed_5.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await member.add_roles(role)
		try:
			await member.send(embed=embed_4)
		except:
			pass
		await ctx.send(embed=embed_5)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@hire.error
	async def hire_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Hire in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Kick Command
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member=None, *, reason=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member:
			embed = discord.Embed(title="__**Kick Error**__", description=f"Specify a Member.\n`{self.bot.prefix}kick <Mention User> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Kick Error**__", description=f"Specify a Reason for Kicking Member.\n`{self.bot.prefix}kick <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Kicked**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Kick**__", description=f"{member.mention} has been kicked.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		await member.kick(reason=reason)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@kick.error
	async def kick_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Kick in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Ban Command
	@commands.has_permissions(ban_members=True)
	async def ban(self, ctx, member: discord.Member=None, *, reason=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member:
			embed = discord.Embed(title="__**Ban Error**__", description=f"Specify a Member.\n`{self.bot.prefix}ban <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Ban Error**__", description=f"Specify a Reason for Banning Member.\n`{self.bot.prefix}ban <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Banned**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Ban**__", description=f"{member.mention} has been banned.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await member.ban(reason=reason)
		await ctx.send(embed=embed_2)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@ban.error
	async def ban_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Ban in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Soft Ban Command
	@commands.has_permissions(ban_members=True)
	async def sban(self, ctx, member: discord.Member=None, *, reason=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member:
			embed = discord.Embed(title="__**Soft Ban Error**__", description=f"Specify a Member.\n`{self.bot.prefix}sban <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Soft Ban Error**__", description=f"Specify a Reason for Soft Banning Member.\n`{self.bot.prefix}sban <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Soft Banned**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Soft Ban**__", description=f"{member.mention} has been soft banned.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await member.ban(reason=reason)
		await member.unban(reason=reason)
		await ctx.send(embed=embed_2)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@sban.error
	async def sban_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Soft Ban in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Mute Command
	@commands.has_permissions(kick_members=True)
	async def mute(self, ctx, member: discord.Member=None, *, reason=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Member.\n`{self.bot.prefix}mute <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Reason for Muting Member.\n`{self.bot.prefix}mute <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Config_mute_role"]
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.add_roles(role)
		embed = discord.Embed(title="__**Muted**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Mute**__", description=f"{member.mention} has been muted.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mute in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Timed Mute Command
	@commands.has_permissions(kick_members=True)
	async def tmute(self, ctx, time: str=None, member: discord.Member=None, *, reason=None):
		if time is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify an Amount of Time.\n*Days: d, Hours: h, Minutes: m, Seconds: s*\n`{self.bot.prefix}tmute <Amount of Time> <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if member is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Member.\n`{self.bot.prefix}tmute <Amount of Time> <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Reason for Muting Member.\n`{self.bot.prefix}tmute <Amount of Time> <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Config_mute_role"]
		collection_3 = self.bot.db["AM_tmute"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		future = time.lower()
		current = datetime.now()
		current = current.astimezone(timezone("US/Eastern"))
		d = 0
		h = 0
		m = 0
		s = 0
		for x in future:
			if x == "d":
				fix = future.split('d')
				d = int(fix[0])
				future = fix[1]
			if x == "h":
				fix = future.split('h')
				h = int(fix[0])
				future = fix[1]
			if x == "m":
				fix = future.split('m')
				m = int(fix[0])
				future = fix[1]
			if x == "s":
				fix = future.split('s')
				s = int(fix[0])
				future = fix[1]

		string = ""
		if d != 0:
			string += f"{d} days"
		if h != 0:
			if d == 0:
				string += f"{h} hours"
			if d != 0:
				if m != 0 or s != 0:
					string += f", {h} hours"
				if m == 0 and s == 0:
					string += f", and {h} hours"
		if m != 0:
			if h == 0 and d == 0:
				string += f"{m} minutes"
			if h != 0 or d != 0:
				if s != 0:
					string += f", {m} minutes"
				if s == 0:
					string += f", and {m} minutes"
		if s != 0:
			if m == 0 and h == 0 and d == 0:
				string += f"{s} seconds"
			if m != 0 or h != 0 or d != 0:
					string += f", and {s} seconds"

		amount = timedelta(days=d, hours=h, minutes=m, seconds=s)
		date = current + amount
		fmt = "%I:%M%p %B %d, %Y %Z"
		fix = date.strftime(fmt)
		fixer = current.strftime(fmt)
		
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.add_roles(role)
		log = {}
		log ["Guild_Name"] = str(ctx.guild)
		log ["Guild"] = ctx.guild.id
		log ["Channel"] = ctx.channel.id
		log ["Member"] = member.id
		log ["Author"] = ctx.author.id
		log ["Reason"] = reason
		log ["Role"] = role.id
		log ["Display_Time"] = fixer
		log ["Begin"] = current
		log ["End"] = date
		embed = discord.Embed(title="__**Muted**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":alarm_clock: Ends:", value=f"{fix}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Mute**__", description=f"{member.mention} has been Muted.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":alarm_clock: Ends:", value=f"{fix}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		if not mod_log is None:
			await mod_log.send(embed=embed_2)
		await collection_3.insert_one(log)
		await ctx.message.delete()
	@tmute.error
	async def tmute_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mute in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Unmute Command
	@commands.has_permissions(kick_members=True)
	async def unmute(self, ctx, member: discord.Member=None, *, reason=None):
		collection = self.bot.db["logs"]
		mod_log =None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member:
			embed = discord.Embed(title="__**Unmute Error**__", description=f"Specify a Member.\n`{self.bot.prefix}unmute <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Unmute Error**__", description=f"Specify a Reason for Unmuting Member.\n`{self.bot.prefix}umute <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Config_mute_role"]
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.remove_roles(role)
		embed = discord.Embed(title="__**Unmuted**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Unmute**__", description=f"{member.mention} has been unmuted.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@unmute.error
	async def unmute_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unmute in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Warn Command
	@commands.has_permissions(kick_members=True)
	async def warn(self, ctx, member_user: discord.Member=None, *, reason=None):
		if not member_user:
			embed = discord.Embed(title="__**Warning Error**__", description=f"Specify a Member.\n`{self.bot.prefix}warn <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Warning Error**__", description=f"Specify a Reason for Warning the Member.\n`{self.bot.prefix}warn <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Mod_warnings"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		warnings = 0
		reasonz = [f"{reason}"]
		grab_warnings = collection_2.find({"Guild": ctx.message.guild.id, "Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasonz += m["Reasons"]
		warnings += 1
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Member"] = member_user.id
		log ["Warnings"] = warnings
		log ["Reasons"] = reasonz
		old_log = {"Guild": ctx.message.guild.id, "Member": member_user.id}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**Warning**__", description=f"{member_user.mention} has been warned", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member_user.id}", inline=False)
		embed.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warning**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed_2.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member_user.send(embed=embed_2) 
		except:
			pass
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@warn.error
	async def warn_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Warn in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Remove Warning Command
	@commands.has_permissions(kick_members=True)
	async def rwarn(self, ctx, member_user: discord.Member=None, queue: int=1, *, reason: str=None):
		if not member_user:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"Specify a Member.\n`{self.bot.prefix}rwarn <Mention Member> <Warning Index> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if queue is None:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"Specify a Warnings Index to Remove.\n`{self.bot.prefix}rwarn <Mention Member> <Warning Index> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"Specify a Reason for Removing the Warning.\n`{self.bot.prefix}rwarn <Mention Member> <Warning Index> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Mod_warnings"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		warnings = 0
		reasonz = []
		grab_warnings = collection_2.find({"Guild": ctx.message.guild.id, "Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasonz += m["Reasons"]
		warnings -= 1
		if warnings == -1:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"{member_user.mention} has `0` Warnings.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		reasonz.pop(queue-1)
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Member"] = member_user.id
		log ["Warnings"] = warnings
		log ["Reasons"] = reasonz
		old_log = {"Guild": ctx.message.guild.id, "Member": member_user.id}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**Warning Removed**__", description=f"{member_user.mention} now has `{warnings}` Warnings.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member_user.id}", inline=False)
		embed.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warning Removed**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed_2.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member_user.send(embed=embed_2)
		except:
			pass
		if mod_log is None:
			await ctx.message.delete()
			return 
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@rwarn.error
	async def rwarn_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Remove Warnings in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Warning Command
	@commands.has_permissions(administrator=True)
	async def cwarn(self, ctx, member_user: discord.Member=None, *, reason=None):
		if not member_user:
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"Specify a Member.\n`{self.bot.prefix}cwarn <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"Specify a Reason for Clearing Member's Warnings.\n`{self.bot.prefix}cwarn <Mention Member> <Reason>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Mod_warnings"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		warnings = 0
		grab_warnings = collection_2.find({"Guild": ctx.message.guild.id, "Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
		if warnings == 0:
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"{member_user.mention} has `0` Warnings.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Member"] = member_user.id
		log ["Warnings"] = 0
		log ["Reasons"] = []
		old_log = {"Guild": ctx.message.guild.id, "Member": member_user.id}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**Warnings Cleared**__", description=f"{member_user.mention} now has `0` Warnings.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member_user.id}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warnings Cleared**__", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member_user.avatar_url_as(format=None, static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member_user.send(embed=embed_2) 
		except:
			pass
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@cwarn.error
	async def cwarn_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear Warnings in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Warnings Command
	#@commands.has_permissions(kick_members=True)
	async def warnings(self, ctx, *, member_user: discord.Member=None,):
		if not member_user:
			member_user = ctx.author
		collection_2 = self.bot.db["Mod_warnings"]
		warnings = 0
		grab_warnings = collection_2.find({"Guild": ctx.message.guild.id, "Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasons = m["Reasons"]
		if warnings == 0:
			embed = discord.Embed(title="__**Warnings**__", description=f"{member_user.mention} has `0` Warnings.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		order = ""
		counter = 1
		for x in reasons[0:10]:
			order += f"**{counter}:** {x}\n"
			counter += 1
		embed = discord.Embed(title="__**Warnings**__", description=f"{member_user.mention} has `{warnings}` Warnings.\n{order}", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))

		pages = 1
		if warnings > 10:
			page = warnings/10
			pages = int(page)+1
		message = await ctx.send(embed=embed)
		if warnings <= 10:
			await ctx.message.delete()
			return
		collection = self.bot.db["AM_warnings"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.guild.id
		log ["Author"] = ctx.author.id
		log ["User"] = member_user.id
		log ["Channel"] = ctx.channel.id
		log ["Message"] = message.id
		log ["Reasons"] = reasons
		log ["Warnings"] = warnings
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
	"""@warnings.error
	async def warnings_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Check Warnings in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)"""

	@commands.command(pass_context=True) # Clear Command
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, amount: int=None):
		if not amount:
			embed = discord.Embed(title="__**Clear Error**__", description=f"Specify an Amount of Messages to Delete.\n`{self.bot.prefix}clear <Number of Messages>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await ctx.message.delete()
		deleted = await ctx.channel.purge(limit=amount)
		embed = discord.Embed(title="__**Clear**__", description="Deleted {} message(s).".format(len(deleted)), timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.channel.send(embed=embed)
	@clear.error
	async def clear_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear Messages in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

			

	@commands.Cog.listener()
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		collection = self.bot.db["AM_warnings"] # Paginate Warnings
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
			embed = discord.Embed(title="__**Warnings**__", description=f"{member_user.mention} has `{warnings}` Warnings.\n{order}", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{member}", icon_url=member.avatar_url_as(format=None, static_format="png"))
			await message.edit(embed=embed)

			try:
				await reaction.remove(member)
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})
				return
			except:
				await collection.update_one({"Message": payload.message_id}, {"$set":{"Counter": counter}})

		# Rolemenu Event (Add Role on Reaction)
		reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		reaction = payload.emoji
		guild = self.bot.get_guild(int(payload.guild_id))
		member = guild.get_member(int(payload.user_id))
		embed = discord.Embed(title="__**Role Assigned**__", description=f"You have a new role in **{guild}**", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		
		collection = self.bot.db["Mod_rolemenu"]
		grab_menu = {"Message": payload.message_id}
		menu = collection.find(grab_menu)
		roles = None
		async for x in menu:
			roles = x["Roles"]
		if roles is None:
			return
		counter = 0
		for x in reactions:
			if str(payload.emoji) == x:
				rolez = guild.get_role(roles[counter])
				await member.add_roles(rolez)
				try:
					await member.send(embed=embed)
				except:
					pass
				counter +=1

	@commands.Cog.listener() # Rolemenu Event (Remove Role on Reaction)
	async def on_raw_reaction_remove(self, payload):
		await self.bot.wait_until_ready()
		reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		guild = self.bot.get_guild(int(payload.guild_id))
		member = guild.get_member(int(payload.user_id))
		embed = discord.Embed(title="__**Role Unassigned**__", description=f"You have lost role in **{guild}**", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		
		collection = self.bot.db["Mod_rolemenu"]
		grab_menu = {"Message": payload.message_id}
		menu = collection.find(grab_menu)
		roles = None
		async for x in menu:
			roles = x["Roles"]
		if roles is None:
			return
		counter = 0
		for x in reactions:
			if str(payload.emoji) == x:
				rolez = guild.get_role(roles[counter])
				await member.remove_roles(rolez)
				try:
					await member.send(embed=embed)
				except:
					pass
				counter += 1

def setup(bot):
	bot.add_cog(Moderation(bot))