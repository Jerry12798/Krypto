import discord
import asyncio
import time
import pytz
import motor.motor_asyncio
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from Utils.Menus import Formatter, Pager
from Utils.Helpers import convert_seconds
from pytz import timezone



class Mod(commands.Cog, app_commands.Group, name="mod", description="Moderation Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="kick", description="Kick Specified Member") # Kick Command
	@app_commands.describe(member="Member to Kick", reason="Reason for Kicking")
	@app_commands.checks.has_permissions(kick_members=True)
	async def kick(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		embed = discord.Embed(title="__**Kicked**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Kick**__", description=f"{member.mention} has been kicked.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		await member.kick(reason=reason)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		#await ctx.message.delete()
	@kick.error
	async def kick_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Kick in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="ban", description="Ban Specified Member") # Ban Command
	@app_commands.describe(member="Member to Ban", reason="Reason for Banning")
	@app_commands.checks.has_permissions(ban_members=True)
	async def ban(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		embed = discord.Embed(title="__**Banned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Ban**__", description=f"{member.mention} has been banned.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await member.ban(reason=reason)
		await interaction.followup.send(embed=embed_2)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		#await ctx.message.delete()
	@ban.error
	async def ban_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Ban in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="ban_soft", description="Soft Ban Specified Member") # Soft Ban Command
	@app_commands.describe(member="Member to Soft Ban", reason="Reason for Soft Banning")
	@app_commands.checks.has_permissions(ban_members=True)
	async def ban_soft(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		embed = discord.Embed(title="__**Soft Banned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Soft Ban**__", description=f"{member.mention} has been soft banned.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await member.ban(reason=reason)
		await member.unban(reason=reason)
		await interaction.followup.send(embed=embed_2)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		#await ctx.message.delete()
	@ban_soft.error
	async def ban_soft_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Soft Ban in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="mute", description="Mute Specified Member") # Mute Command
	@app_commands.describe(member="Member to Mute", reason="Reason for Muting")
	@app_commands.checks.has_permissions(kick_members=True)
	async def mute(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		collection_2 = self.bot.db["Config_mute_role"]
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.add_roles(role)
		embed = discord.Embed(title="__**Muted**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Mute**__", description=f"{member.mention} has been muted.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		#await ctx.message.delete()
	@mute.error
	async def mute_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mute in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="mute_timed", description="Time Mute Specified Member") # Timed Mute Command
	@app_commands.describe(time="Amount of Time to Mute (d=days h=hours m=minutes s=seconds)", member="Member to Mute", reason="Reason for Muting")
	@app_commands.checks.has_permissions(kick_members=True)
	async def mute_timed(self, interaction:discord.Interaction, time:str, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Config_mute_role"]
		collection_3 = self.bot.db["AM_tmute"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
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
		log ["Guild_Name"] = str(interaction.guild)
		log ["Guild"] = interaction.guild.id
		log ["Channel"] = interaction.channel.id
		log ["Member"] = member.id
		log ["Author"] = interaction.user.id
		log ["Reason"] = reason
		log ["Role"] = role.id
		log ["Display_Time"] = fixer
		log ["Begin"] = current
		log ["End"] = date
		embed = discord.Embed(title="__**Muted**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed.add_field(name=":alarm_clock: Ends:", value=f"{fix}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Mute**__", description=f"{member.mention} has been Muted.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":alarm_clock: Ends:", value=f"{fix}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		if not mod_log is None:
			await mod_log.send(embed=embed_2)
		await collection_3.insert_one(log)
		#await ctx.message.delete()
	@mute_timed.error
	async def mute_timed_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mute in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="unmute", description="Unmute Specified Member") # Unmute Command
	@app_commands.describe(member="Member to Unmute", reason="Reason for Unmuting")
	@app_commands.checks.has_permissions(kick_members=True)
	async def unmute(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		mod_log =None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		collection_2 = self.bot.db["Config_mute_role"]
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.remove_roles(role)
		embed = discord.Embed(title="__**Unmuted**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Unmute**__", description=f"{member.mention} has been unmuted.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed_2)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		#await ctx.message.delete()
	@unmute.error
	async def unmute_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unmute in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	role_commands = app_commands.Group(name="role", description="Role Management & Moderation Commands")

	@role_commands.command(name="add", description="Add Role to Specified Member") # Add Role Command
	@app_commands.describe(role="Role to Add", member="Member to Add Role to")
	@app_commands.checks.has_permissions(manage_roles=True)
	async def add(self, interaction:discord.Interaction, role:discord.Role, member:discord.Member):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		embed = discord.Embed(title="__**Role Assigned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Role Assigned**__", description=f"You have been Assigned `{role}` in **{interaction.guild}**", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await member.add_roles(role)
		try:
			await member.send(embed=embed_4)
		except:
			pass
		await interaction.followup.send(embed=embed)
		if mod_log is None:
			#await ctx.message.delete()
			return	
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@add.error
	async def add_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Assign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@role_commands.command(name="remove", description="Remove Role from Specified Member") # Add Role Command
	@app_commands.describe(role="Role to Remove", member="Member to Remove Role From")
	@app_commands.checks.has_permissions(manage_roles=True)
	async def remove(self, interaction:discord.Interaction, role:discord.Role, member:discord.Member):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		embed = discord.Embed(title="__**Role Unassigned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Role Unassigned**__", description=f"You have been Unassigned `{role}` in **{interaction.guild}**", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await member.remove_roles(role)
		try:
			await member.send(embed=embed_4)
		except:
			pass
		await interaction.followup.send(embed=embed)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@remove.error
	async def remove_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unassign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@role_commands.command(name="remove_mass", description="Remove Role from Everyone") # Mass Remove Role Command
	@app_commands.describe(role="Role to Remove")
	@app_commands.checks.has_permissions(manage_roles=True)
	async def remove_mass(self, interaction:discord.Interaction, role:discord.Role):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)

		#embed_4 = discord.Embed(title="__**Role Unassigned**__", description=f"You have been Unassigned `{role}` in **{interaction.guild}**.", timestamp=datetime.now(), color=0xff0000)
		#embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		total = 0
		for i in interaction.guild.members:
			
			try:
				await i.remove_roles(role)
				total += 1
			except:
				pass

		embed = discord.Embed(title="__**Role Mass Unassigned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Members:", value=f"{total}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@remove_mass.error
	async def remove_mass_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unassign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@role_commands.command(name="add_mass", description="Add Role to Everyone") # Mass Add Role Command
	@app_commands.describe(role="Role to be Added")
	@app_commands.checks.has_permissions(manage_roles=True)
	async def add_mass(self, interaction:discord.Interaction, role:discord.Role):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)

		#embed_4 = discord.Embed(title="__**Role Assigned**__", description=f"You have been Assigned `{role}` in **{interaction.guild}**.", timestamp=datetime.now(), color=0xff0000)
		#embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		total = 0
		for i in interaction.guild.members:
			
			try:
				await i.add_roles(role)
				total += 1
			except:
				pass

		embed = discord.Embed(title="__**Role Mass Assigned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Members:", value=f"{total}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=interaction.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@add_mass.error
	async def add_mass_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Assign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
	
	@role_commands.command(name="menu", description="Create Rolemenu with Up to 10 Roles") # Rolemenu Command
	@app_commands.describe(menu="Rolemenu's Title/Name", role_1="Role to Be Added into Menu", role_2="Role to Be Added into Menu", role_3="Role to Be Added into Menu", role_4="Role to Be Added into Menu", role_5="Role to Be Added into Menu", role_6="Role to Be Added into Menu", role_7="Role to Be Added into Menu", role_8="Role to Be Added into Menu", role_9="Role to Be Added into Menu", role_10="Role to Be Added into Menu")
	@app_commands.checks.has_permissions(kick_members=True)
	async def menu(self, interaction:discord.Interaction, menu:str, role_1:discord.Role, role_2:discord.Role, role_3:discord.Role=None, role_4:discord.Role=None, role_5:discord.Role=None, role_6:discord.Role=None, role_7:discord.Role=None, role_8:discord.Role=None, role_9:discord.Role=None, role_10:discord.Role=None):
		reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		options = [role_1, role_2]
		if not role_3 is None:
			options.append(role_3)
		if not role_4 is None:
			options.append(role_4)
		if not role_5 is None:
			options.append(role_5)
		if not role_6 is None:
			options.append(role_6)
		if not role_7 is None:
			options.append(role_7)
		if not role_8 is None:
			options.append(role_8)
		if not role_9 is None:
			options.append(role_9)
		if not role_10 is None:
			options.append(role_10)
		description = []
		for x, option in enumerate(options):
			description += "\n{}: `{}`".format(reactions[x], option)
		embed = discord.Embed(title=f"**Rolemenu: {menu}**", description="".join(description), timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		react_message = await interaction.followup.send(embed=embed)
		for reaction in reactions[0:len(options)]:
			await react_message.add_reaction(reaction)
		roles = []
		for x in options:
			roles += {x.id}
		collection = self.bot.db["Mod_rolemenu"]
		menu = {}
		menu ["Guild_Name"] = interaction.guild.name
		menu ["Guild"] = interaction.guild.id
		menu ["Member"] = interaction.user.id
		menu ["Message"] = react_message.id
		menu ["Roles"] = roles
		await collection.insert_one(menu)
		#await ctx.message.delete()
	@menu.error
	async def menu_error(self, interaction, error):
		if isinstance(error, app_commands.BadArgument):
			embed = discord.Embed(title="__**Command Error**__", description="You must put Quotation Marks before & after Menu Name if it's more than one word.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to make a Rolemenu in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@role_commands.command(name="ping", description="Send Ping Message to Notify a Role") # Ping Role Command
	@app_commands.describe(role="Role to be Pinged", message="Message to Ping Role About")
	@app_commands.checks.has_permissions(manage_roles=True)
	async def ping(self, interaction:discord.Interaction, role:discord.Role, *, message:str):
		embed_3 = discord.Embed(title="__**Ping Notifications**__", description=f"{message}", timestamp=datetime.now(), color=0xac5ece)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(f"{role.mention}")
		await interaction.followup.send(embed=embed_3)
		#await ctx.message.delete()
	@ping.error
	async def ping_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mention Ping Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@role_commands.command(name="hire_message", description="Configure Role's Hire Messgae") # Set Message for Hire Role
	@app_commands.describe(role="Role to Configure", content="Message for Role")
	@app_commands.checks.has_permissions(administrator=True)
	async def hire_message(self, interaction:discord.Interaction, role:discord.Role, *, content:str):
		collection = self.bot.db["Config_hire"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Role"] = role.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Hire Role Message**__", description=f"{role.mention} Messsage has been set as\n{content}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		async for x in collection.find({}, {"_id": 0, "Role": role.id}):
			rolez = x["Role"]
		old_log = {"Role": role.id}
		await collection.delete_one(old_log)
		await collection.insert_one(log)
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()
	@hire_message.error
	async def hire_message_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	warnings = app_commands.Group(name="warnings", description="Warning Commands")

	@warnings.command(name="check", description="Check Warnings for You or Specified Member") # Warnings Command
	@app_commands.describe(member="Member to Check Warnings of")
	async def check(self, interaction:discord.Interaction, *, member:discord.Member=None,):
		
		if not member:
			member = interaction.user
		collection_2 = self.bot.db["Mod_warnings"]
		embeds = []
		warnings = 0
		check = 0
		grab_warnings = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasons = m["Reasons"]
		if warnings == 0:
			embed = discord.Embed(title="__**Warnings**__", description=f"{member.mention} has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		order = ""
		counter = 1
		for x in reasons:
			order += f"**{counter}:** {x}\n"
			counter += 1
			check += 1
			if check == 10:
				embed = discord.Embed(title="__**Warnings**__", description=f"{member.mention} has `{warnings}` Warnings.\n{order}", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
				check = 0
				order = ""
				embeds.append(embed)
		if check < 10 and check > 0:
			embed = discord.Embed(title="__**Warnings**__", description=f"{member.mention} has `{warnings}` Warnings.\n{order}", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)

		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(interaction)
		#await ctx.message.delete()

	@warnings.command(name="new", description="Warn Specified Member") # Warn Command
	@app_commands.describe(member="Member to Warn", reason="Reason for Warning")
	@app_commands.checks.has_permissions(kick_members=True)
	async def new(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Mod_warnings"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		warnings = 0
		reasonz = [f"{reason}"]
		grab_warnings = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasonz += m["Reasons"]
		warnings += 1
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Member"] = member.id
		log ["Warnings"] = warnings
		log ["Reasons"] = reasonz
		old_log = {"Guild": interaction.guild.id, "Member": member.id}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**Warning**__", description=f"{member.mention} has been warned", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{interaction.channel.mention}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warning**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{interaction.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed_2) 
		except:
			pass
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@new.error
	async def new_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Warn in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@warnings.command(name="remove", description="Removes Specified Warning from Specified Member") # Remove Warning Command
	@app_commands.describe(member="Member to Remove Warnings From", queue="Warning Queue to Remove", reason="Reason for Removing Warning")
	@app_commands.checks.has_permissions(kick_members=True)
	async def remove(self, interaction:discord.Interaction, member:discord.Member, queue:int, *, reason:str):
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Mod_warnings"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		warnings = 0
		reasonz = []
		grab_warnings = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasonz += m["Reasons"]
		warnings -= 1
		if warnings == -1:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"{member.mention} has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		reasonz.pop(queue-1)
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Member"] = member.id
		log ["Warnings"] = warnings
		log ["Reasons"] = reasonz
		old_log = {"Guild": interaction.guild.id, "Member": member.id}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**Warning Removed**__", description=f"{member.mention} now has `{warnings}` Warnings.", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{interaction.channel.mention}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warning Removed**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{interaction.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed_2)
		except:
			pass
		if mod_log is None:
			#await ctx.message.delete()
			return 
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@remove.error
	async def remove_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Remove Warnings in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@warnings.command(name="clear", description="Clear Warnings from Specified Member") # Clear Warning Command
	@app_commands.describe(member="Member to Clear Warnings of", reason="Reason for Clearing Warnings")
	@app_commands.checks.has_permissions(administrator=True)
	async def clear(self, interaction:discord.Interaction, member:discord.Member, *, reason:str):
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Mod_warnings"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		warnings = 0
		grab_warnings = collection_2.find({"Guild": interaction.guild.id, "Member": member.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
		if warnings == 0:
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"{member.mention} has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Member"] = member.id
		log ["Warnings"] = 0
		log ["Reasons"] = []
		old_log = {"Guild": interaction.guild.id, "Member": member.id}
		await collection_2.delete_one(old_log)
		await collection_2.insert_one(log)
		embed = discord.Embed(title=f"__**Warnings Cleared**__", description=f"{member.mention} now has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{interaction.channel.mention}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warnings Cleared**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{interaction.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{interaction.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed_2) 
		except:
			pass
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@clear.error
	async def clear_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear Warnings in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="clear_messages", description="Clears Specified Amount of Messages from Current Channel") # Clear Command
	@app_commands.describe(amount="Amount of Messages to Clear")
	@app_commands.checks.has_permissions(manage_messages=True)
	async def clear_messages(self, interaction:discord.Interaction, amount:int):
		#await ctx.message.delete()
		deleted = await interaction.channel.purge(limit=amount)
		embed = discord.Embed(title="__**Clear**__", description="Deleted {} message(s).".format(len(deleted)), timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.channel.send(embed=embed)
	@clear_messages.error
	async def clear_messages_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear Messages in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="hire", description="Gives Member Specified Role and Sends Role's Configured Message") # Hire Command
	@app_commands.describe(role="Role to Give", member="Member to Hire")
	@app_commands.checks.has_permissions(administrator=True)
	async def hire(self, interaction:discord.Interaction, role:discord.Role, member:discord.Member):
		collection = self.bot.db["logs"]
		collection_2 = self.bot.db["Config_hire"]
		mod_log = None
		async for m in collection.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = interaction.guild.get_channel(Channelz)
		role_message = None
		async for m in collection_2.find({"Role": role.id}, {"_id": 0, "Role": 0}):
			role_message = m["Message"]
		if role_message is None:
			embed_3 = discord.Embed(title="__**Hire Error**__", description=f"You must Create Hire Message for Role to Hire someone.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed_3)
			return
		embed = discord.Embed(title="__**New Hire**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
		embed.add_field(name=":alien: Position:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Hired**__", description=f"You have been Assigned `{role}` in **{interaction.guild}**", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_5 = discord.Embed(title="__**New Hire**__", description=f"{member.mention}, {role_message}", timestamp=datetime.now(), color=0xff0000)
		embed_5.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await member.add_roles(role)
		try:
			await member.send(embed=embed_4)
		except:
			pass
		await interaction.followup.send(embed=embed_5)
		if mod_log is None:
			#await ctx.message.delete()
			return
		await mod_log.send(embed=embed)
		#await ctx.message.delete()
	@hire.error
	async def hire_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Hire in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	giveaway = app_commands.Group(name="giveaway", description="Giveaway Commands")

	@giveaway.command(name="start", description="Start Giveaway in Specified Channel for Specified Amount of Time and Winners") # Giveaway Command
	@app_commands.describe(channel="Channel to Post Giveaway in", time="Amount of Time of Giveaway (d=days h=hours m=minutes s=seconds)", winners="Amount of Winners for Giveaway", prize="Item/Prize to be Given Away", description="Description/Overview of Giveaway")
	@app_commands.checks.has_permissions(administrator=True)
	async def start(self, interaction:discord.Interaction, channel:discord.TextChannel, time:str, winners:int, prize:str, *, description:str=None):
		fix, fix_str, current = convert_seconds(time)
		if description is None:
			description = ""
		collection = self.bot.db["Fun_giveaways"]
		collection_2 = self.bot.db["Fun_giveaways_entries"]
		collection_3 = self.bot.db["Fun_ended_giveaways"]
		log = {}
		log ["Guild_Name"] = str(interaction.guild)
		log ["Guild"] = interaction.guild.id
		log ["Winners"] = winners
		log ["Prize"] = prize
		log ["Description"] = description
		log ["Channel"] = channel.id
		log ["Begin"] = current
		log ["End"] = fix
		embed = discord.Embed(title="__**Giveaway Started**__", description=f"Giveaway Started in {channel.mention} for {prize}. There will be {winners} Winners.\n{description}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		embed = discord.Embed(title="__**Giveaway**__", description=f"__**{prize}**__\n{description}", timestamp=fix, color=0xac5ece)
		embed.set_footer(text=f"{winners} Winners", icon_url=interaction.guild.icon.replace(format="png", static_format="png"))
		message = await channel.send(embed=embed)
		await message.add_reaction("\U0001F389")
		log ["Message"] = message.id
		await collection.insert_one(log)
	@start.error
	async def start_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@giveaway.command(name="end", description="End Specified Giveaway") # End Giveaway Command
	@app_commands.describe(message="Giveaway Message ID to End")
	@app_commands.checks.has_permissions(administrator=True)
	async def end(self, interaction:discord.Interaction, message:str):
		collection = self.bot.db["Fun_giveaways_entries"]
		collection_2 = self.bot.db["Fun_giveaways"]
		collection_3 = self.bot.db["Fun_ended_giveaways"]
		async for m in collection_2.find({"Guild": interaction.guild.id, "Message": message}, {"_id": 0}):
			prize = m["Prize"]
			description = m["Description"]
			amount = m["Winners"]
			grab_channel = m["Channel"]
			message = m["Message"]
			end = m["End"]
			start = m["Begin"]
			channel = interaction.guild.get_channel(grab_channel)
			message = await channel.fetch_message(int(message))
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"Giveaway Ended in {channel.mention} for {prize}.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		entries = []
		async for m in collection.find({"Guild": interaction.guild.id, "Message": message.id}, {"_id": 0}):
			entries += {m["Member"]}
		order = f"__***{prize}***__\n{description}\n__***Winners***__\n"
		counter = 1
		win_list = ""
		while counter <= amount:
			winners = random.choice(entries)
			member = interaction.guild.get_member(winners)
			if counter + 1 >= amount:
				win_list += f"{member.mention}"
			if not counter + 1 >= amount:
				win_list += f"{member.mention}, "
			order += f"**{counter}:** {str(member.mention)}\n"
			counter +=1
		log = {}
		log ["Guild_Name"] = str(interaction.guild)
		log ["Guild"] = interaction.guild.id
		log ["Prize"] = prize
		log ["Description"] = description
		log ["Winners"] = amount
		log ["Channel"] = grab_channel
		log ["Members"] = entries
		log ["Message"] = message.id
		log ["End"] = end
		log ["Begin"] = start
		await collection_3.insert_one(log)
		old_log = {"Guild": interaction.guild.id, "Message": message.id}
		await collection.delete_one(old_log)
		await collection_2.delete_many(old_log)
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"{order}", timestamp=end, color=0xac5ece)
		embed.set_footer(text=f"{interaction.guild.name}", icon_url=interaction.guild.icon.replace(format="png", static_format="png"))
		await message.edit(embed=embed)
		await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
		#await ctx.message.delete()
	@end.error
	async def end_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@giveaway.command(name="reroll", description="Reroll Specified Giveaway") # Reroll Giveaway Command
	@app_commands.describe(message="Giveaway Message ID to Reroll", new_winners="Amount of Times to Reroll")
	@app_commands.checks.has_permissions(administrator=True)
	async def reroll(self, interaction:discord.Interaction, message:str, new_winners:int=None):
		collection = self.bot.db["Fun_ended_giveaways"]
		async for m in collection.find({"Guild": interaction.guild.id, "Message": message}, {"_id": 0}):
			prize = m["Prize"]
			description = m["Description"]
			amount = m["Winners"]
			if not new_winners is None:
				amount = new_winners
			grab_channel = m["Channel"]
			entries = m["Members"]
			message = m["Message"]
			end = m["End"]
			channel = interaction.guild.get_channel(grab_channel)
			message = await channel.fetch_message(int(message))
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"Giveaway Rerolled in {channel.mention} for {prize}.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		order = f"__***{prize}***__\n{description}\n__***New Winners***__\n"
		counter = 1
		win_list = ""
		while counter <= amount:
			winners = random.choice(entries)
			member = interaction.guild.get_member(winners)
			if counter + 1 >= amount:
				win_list += f"{member.mention}"
			if not counter + 1 >= amount:
				win_list += f"{member.mention}, "
			order += f"{str(member.mention)}\n"
			counter += 1
		old_log = {"Guild": interaction.guild.id, "Message": message.id}
		embed = discord.Embed(title="__**Giveaway Rerolled**__", description=f"{order}", timestamp=end, color=0xac5ece)
		embed.set_footer(text=f"{interaction.guild.name}", icon_url=interaction.guild.icon.replace(format="png", static_format="png"))
		await message.edit(embed=embed)
		await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
		#await ctx.message.delete()
	@reroll.error
	async def reroll_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="poll", description="Create Poll with Up to 10 Options/Questions") # Poll Command
	@app_commands.describe(question="Poll's Title/Question", answer_1="Poll Option/Answer", answer_2="Poll Option/Answer", answer_3="Poll Option/Answer", answer_4="Poll Option/Answer", answer_5="Poll Option/Answer", answer_6="Poll Option/Answer", answer_7="Poll Option/Answer", answer_8="Poll Option/Answer", answer_9="Poll Option/Answer", answer_10="Poll Option/Answer",)
	@app_commands.checks.has_permissions(kick_members=True)
	async def poll(self, interaction:discord.Interaction, question:str, answer_1:str, answer_2:str, answer_3:str=None, answer_4:str=None, answer_5:str=None, answer_6:str=None, answer_7:str=None, answer_8:str=None, answer_9:str=None, answer_10:str=None):
		if answer_3 is None and answer_1.upper() == "YES" and answer_2.upper() == "NO":
			reactions = ["\u2705", "\u274C"]
		else:
			reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		options = [answer_1, answer_2]
		if not answer_3 is None:
			options.append(answer_3)
		if not answer_4 is None:
			options.append(answer_4)
		if not answer_5 is None:
			options.append(answer_5)
		if not answer_6 is None:
			options.append(answer_6)
		if not answer_7 is None:
			options.append(answer_7)
		if not answer_8 is None:
			options.append(answer_8)
		if not answer_9 is None:
			options.append(answer_9)
		if not answer_10 is None:
			options.append(answer_10)
		description = []
		for x, option in enumerate(options):
			description += "\n{} {}".format(reactions[x], option)
		embed = discord.Embed(title=question, description="".join(description), timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		react_message = await interaction.followup.send(embed=embed)
		for reaction in reactions[0:len(options)]:
			await react_message.add_reaction(reaction)
		#await ctx.message.delete()
	@poll.error
	async def poll_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to make a Poll in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Mod(bot))