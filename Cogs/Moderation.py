import discord
import asyncio
import time
import pytz
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from Utils.Helpers import convert_seconds
from Utils.Menus import Formatter, Pager
from pytz import timezone



class Moderation(commands.Cog, name="Moderation", description="Moderation Commands"):
	def __init__(self,bot):
		self.bot = bot

	@commands.command() # Kick Command
	@commands.has_permissions(kick_members=True)
	async def kick(self, ctx, member: discord.Member=None, *, reason=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if not member:
			embed = discord.Embed(title="__**Kick Error**__", description=f"Specify a Member.\n`{self.bot.prefix}kick <Mention User> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Kick Error**__", description=f"Specify a Reason for Kicking Member.\n`{self.bot.prefix}kick <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Kicked**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Kick**__", description=f"{member.mention} has been kicked.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Kick in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Ban Error**__", description=f"Specify a Member.\n`{self.bot.prefix}ban <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Ban Error**__", description=f"Specify a Reason for Banning Member.\n`{self.bot.prefix}ban <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Banned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Ban**__", description=f"{member.mention} has been banned.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Ban in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Soft Ban Error**__", description=f"Specify a Member.\n`{self.bot.prefix}sban <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Soft Ban Error**__", description=f"Specify a Reason for Soft Banning Member.\n`{self.bot.prefix}sban <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Soft Banned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Soft Ban**__", description=f"{member.mention} has been soft banned.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Soft Ban in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Member.\n`{self.bot.prefix}mute <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Reason for Muting Member.\n`{self.bot.prefix}mute <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Config_mute_role"]
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.add_roles(role)
		embed = discord.Embed(title="__**Muted**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Mute**__", description=f"{member.mention} has been muted.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed_2)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@mute.error
	async def mute_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mute in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Timed Mute Command
	@commands.has_permissions(kick_members=True)
	async def tmute(self, ctx, time: str=None, member: discord.Member=None, *, reason=None):
		if time is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify an Amount of Time.\n*Days: d, Hours: h, Minutes: m, Seconds: s*\n`{self.bot.prefix}tmute <Amount of Time> <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if member is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Member.\n`{self.bot.prefix}tmute <Amount of Time> <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Mute Error**__", description=f"Specify a Reason for Muting Member.\n`{self.bot.prefix}tmute <Amount of Time> <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed = discord.Embed(title="__**Muted**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":alarm_clock: Ends:", value=f"{fix}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Mute**__", description=f"{member.mention} has been Muted.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":alarm_clock: Ends:", value=f"{fix}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed_2)
		if not mod_log is None:
			await mod_log.send(embed=embed_2)
		await collection_3.insert_one(log)
		await ctx.message.delete()
	@tmute.error
	async def tmute_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mute in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Unmute Error**__", description=f"Specify a Member.\n`{self.bot.prefix}unmute <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Unmute Error**__", description=f"Specify a Reason for Unmuting Member.\n`{self.bot.prefix}umute <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection_2 = self.bot.db["Config_mute_role"]
		async for m in collection_2.find({"Guild": member.guild.id}, {"_id": 0, "Guild": 0}):
			rolez = m["Role"]
			role = member.guild.get_role(rolez)
		await member.remove_roles(role)
		embed = discord.Embed(title="__**Unmuted**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			pass
		embed_2 = discord.Embed(title="__**Unmute**__", description=f"{member.mention} has been unmuted.", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":link: User ID:", value=f"{member.id}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed_2)
		if mod_log is None:
			await ctx.message.delete()
			return
		await mod_log.send(embed=embed_2)
		await ctx.message.delete()
	@unmute.error
	async def unmute_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unmute in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	#role_commands = commands.Group(name="role", description="Role Management & Moderation Commands")

	@commands.command() # Add Role Command
	@commands.has_permissions(manage_roles=True)
	async def arole(self, ctx, role: discord.Role=None, member: discord.Member=None):
		collection = self.bot.db["logs"]
		mod_log = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			mod_log = ctx.message.guild.get_channel(Channelz)
		if role is None:
			embed_2 = discord.Embed(title="__**Role Assign Error**__", description=f"Specify a User & Role to Assign them.\n`{self.bot.prefix}arole <Mention Role> <Mention User>`", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_2)
		elif member is None:
			embed_3 = discord.Embed(title="__**Role Assign Error**__", description=f"Specify a User to Assign to Role.\n`{self.bot.prefix}arole <Mention Role> <Mention User>`", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_3)
		else:
			embed = discord.Embed(title="__**Role Assigned**__", timestamp=datetime.now(), color=0xff0000)
			embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
			embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
			embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			embed_4 = discord.Embed(title="__**Role Assigned**__", description=f"You have been Assigned `{role}` in **{ctx.message.guild}**", timestamp=datetime.now(), color=0xff0000)
			embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Assign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed_2 = discord.Embed(title="__**Role Unassign Error**__", description=f"Specify a User & Role to Unassign them.\n`{self.bot.prefix}rrole <Mention Role> <Mention User>`", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_2)
		elif member is None:
			embed_3 = discord.Embed(title="__**Role Unassign Error**__", description=f"Specify a User to Unassign from Role.\n`{self.bot.prefix}rrole <Mention Role> <Mention User>`", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_3)
		else:
			embed = discord.Embed(title="__**Role Unassigned**__", timestamp=datetime.now(), color=0xff0000)
			embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
			embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
			embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			embed_4 = discord.Embed(title="__**Role Unassigned**__", description=f"You have been Unassigned `{role}` in **{ctx.message.guild}**", timestamp=datetime.now(), color=0xff0000)
			embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unassign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed_2 = discord.Embed(title="__**Role Unassign Error**__", description=f"Specify a Role to Mass Unassign.\n`{self.bot.prefix}mrrole <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_2)
			return

		#embed_4 = discord.Embed(title="__**Role Unassigned**__", description=f"You have been Unassigned `{role}` in **{ctx.message.guild}**.", timestamp=datetime.now(), color=0xff0000)
		#embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		total = 0
		for i in ctx.guild.members:
			
			try:
				await i.remove_roles(role)
				total += 1
			except:
				pass

		embed = discord.Embed(title="__**Role Mass Unassigned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Members:", value=f"{total}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=ctx.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@mrrole.error
	async def mrrole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Unassign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed_2 = discord.Embed(title="__**Role Assign Error**__", description=f"Specify a Role to Mass Assign.\n`{self.bot.prefix}marole <Mention Role>`", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_2)
			return

		#embed_4 = discord.Embed(title="__**Role Assigned**__", description=f"You have been Assigned `{role}` in **{ctx.message.guild}**.", timestamp=datetime.now(), color=0xff0000)
		#embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		total = 0
		for i in ctx.guild.members:
			
			try:
				await i.add_roles(role)
				total += 1
			except:
				pass

		embed = discord.Embed(title="__**Role Mass Assigned**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Members:", value=f"{total}", inline=False)
		embed.add_field(name=":alien: Role:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=ctx.guild.icon.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await mod_log.send(embed=embed)
		await ctx.message.delete()
	@marole.error
	async def marole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Assign Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command(pass_context=True) # Rolemenu Command
	@commands.has_permissions(kick_members=True)
	async def rolemenu(self, ctx, menu=None, *options: discord.Role):
		if len(options)<= 1:
			embed = discord.Embed(title="__**Rolemenu Error**__", description=f"You need a Menu Name and more than One Role to make a Rolemenu.\n`{self.bot.prefix}rolemenu <Create Name> <Mention Role 1> <Mention Role 2>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(options) > 10:
			embed = discord.Embed(title="__**Rolemenu Error**__", description=f"You cant't make a Rolemenu with more than 10 Roles.\n`{self.bot.prefix}rolemenu <Create Name> <Mention Role 1> <Mention Role 2>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		else:
			reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		description = []
		for x, option in enumerate(options):
			description += "\n{}: `{}`".format(reactions[x], option)
		embed = discord.Embed(title=f"**Rolemenu: {menu}**", description="".join(description), timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Command Error**__", description="You must put Quotation Marks before & after Menu Name if it's more than one word.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to make a Rolemenu in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Ping Role Command
	@commands.has_permissions(manage_roles=True)
	async def prole(self, ctx, role: discord.Role=None, *, message=None):
		if role is None:
			embed = discord.Embed(title="__**Ping Role Error**__", description=f"Specify a Role & Create a Message to Send them.\n`{self.bot.prefix}prole <Mention Role> <Create Message>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		elif message is None:
			embed_2 = discord.Embed(title="__**Ping Role Error**__", description=f"Create a Message to Notify **{role}** about.\n`{self.bot.prefix}prole <Mention Role> <Create Message>`", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_2)
			return
		embed_3 = discord.Embed(title="__**Ping Notifications**__", description=f"{message}", timestamp=datetime.now(), color=0xac5ece)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(f"{role.mention}")
		await ctx.send(embed=embed_3)
		await ctx.message.delete()
	@prole.error
	async def prole_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Mention Ping Roles in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Message for Hire Role
	@commands.has_permissions(administrator=True)
	async def hrole(self, ctx, role: discord.Role=None, *, content=None):
		if role is None:
			embed = discord.Embed(title="__**Hire Role Error**__", description=f"Mention a Role and Create a Message for it.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**Hire Role Error**__", description=f"Create a Message for the Mentioned Role.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_hire"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Role"] = role.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Hire Role Message**__", description=f"{role.mention} Messsage has been set as\n{content}", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	#warnings = commands.Group(name="warnings", description="Warning Commands")

	@commands.command() # Warnings Command
	async def warnings(self, ctx, *, member_user: discord.Member=None,):
		if not member_user:
			member_user = ctx.author
		collection_2 = self.bot.db["Mod_warnings"]
		embeds = []
		warnings = 0
		check = 0
		grab_warnings = collection_2.find({"Guild": ctx.message.guild.id, "Member": member_user.id}, {"_id": 0, "Guild": 0})
		async for m in grab_warnings:
			warnings = m["Warnings"]
			reasons = m["Reasons"]
		if warnings == 0:
			embed = discord.Embed(title="__**Warnings**__", description=f"{member_user.mention} has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		order = ""
		counter = 1
		for x in reasons:
			order += f"**{counter}:** {x}\n"
			counter += 1
			check += 1
			if check == 10:
				embed = discord.Embed(title="__**Warnings**__", description=f"{member_user.mention} has `{warnings}` Warnings.\n{order}", timestamp=datetime.now(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
				check = 0
				order = ""
				embeds.append(embed)
		if check < 10 and check > 0:
			embed = discord.Embed(title="__**Warnings**__", description=f"{member_user.mention} has `{warnings}` Warnings.\n{order}", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			embeds.append(embed)

		formatter = Formatter([i for i in embeds], per_page=1)
		menu = Pager(formatter)
		await menu.start(ctx)
		await ctx.message.delete()

	@commands.command() # Warn Command
	@commands.has_permissions(kick_members=True)
	async def warn(self, ctx, member_user: discord.Member=None, *, reason=None):
		if not member_user:
			embed = discord.Embed(title="__**Warning Error**__", description=f"Specify a Member.\n`{self.bot.prefix}warn <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Warning Error**__", description=f"Specify a Reason for Warning the Member.\n`{self.bot.prefix}warn <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed = discord.Embed(title=f"__**Warning**__", description=f"{member_user.mention} has been warned", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member_user.id}", inline=False)
		embed.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warning**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed_2.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Warn in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Remove Warning Command
	@commands.has_permissions(kick_members=True)
	async def rwarn(self, ctx, member_user: discord.Member=None, queue: int=1, *, reason: str=None):
		if not member_user:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"Specify a Member.\n`{self.bot.prefix}rwarn <Mention Member> <Warning Index> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if queue is None:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"Specify a Warnings Index to Remove.\n`{self.bot.prefix}rwarn <Mention Member> <Warning Index> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"Specify a Reason for Removing the Warning.\n`{self.bot.prefix}rwarn <Mention Member> <Warning Index> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Warning Remove Error**__", description=f"{member_user.mention} has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed = discord.Embed(title=f"__**Warning Removed**__", description=f"{member_user.mention} now has `{warnings}` Warnings.", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member_user.id}", inline=False)
		embed.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warning Removed**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.add_field(name=":no_entry_sign: Total Warnings:", value=f"{warnings}", inline=False)
		embed_2.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Remove Warnings in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Clear Warning Command
	@commands.has_permissions(administrator=True)
	async def cwarn(self, ctx, member_user: discord.Member=None, *, reason=None):
		if not member_user:
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"Specify a Member.\n`{self.bot.prefix}cwarn <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if reason is None:
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"Specify a Reason for Clearing Member's Warnings.\n`{self.bot.prefix}cwarn <Mention Member> <Reason>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Warning Clear Error**__", description=f"{member_user.mention} has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		embed = discord.Embed(title=f"__**Warnings Cleared**__", description=f"{member_user.mention} now has `0` Warnings.", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":link: User ID:", value=f"{member_user.id}", inline=False)
		embed.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		embed_2 = discord.Embed(title=f"__**Warnings Cleared**__", timestamp=datetime.now(), color=0xff0000)
		embed_2.add_field(name=":satellite: Server:", value=f"**{ctx.guild}**", inline=False)
		embed_2.add_field(name=":tv: Channel:", value=f"{ctx.channel.mention}", inline=False)
		embed_2.add_field(name=":newspaper: Reason:", value=f"{reason}", inline=False)
		embed_2.set_thumbnail(url=member_user.display_avatar.replace(format="png", static_format="png"))
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear Warnings in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command(pass_context=True) # Clear Command
	@commands.has_permissions(manage_messages=True)
	async def clear(self, ctx, amount: int=None):
		if not amount:
			embed = discord.Embed(title="__**Clear Error**__", description=f"Specify an Amount of Messages to Delete.\n`{self.bot.prefix}clear <Number of Messages>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		await ctx.message.delete()
		deleted = await ctx.channel.purge(limit=amount)
		embed = discord.Embed(title="__**Clear**__", description="Deleted {} message(s).".format(len(deleted)), timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.channel.send(embed=embed)
	@clear.error
	async def clear_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Clear Messages in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Hire Command
	@commands.has_permissions(administrator=True)
	async def hire(self, ctx, role: discord.Role=None, member: discord.Member=None):
		if role is None:
			embed_2 = discord.Embed(title="__**Hire Error**__", description=f"Specify a User & Role to Assign them.\n`{self.bot.prefix}hire <Mention Role> <Mention User>`", timestamp=datetime.now(), color=0xff0000)
			embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_2)
			return
		if member is None:
			embed_3 = discord.Embed(title="__**Hire Error**__", description=f"Specify a User to Hire.\n`{self.bot.prefix}hire <Mention Role> <Mention User>`", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed_3 = discord.Embed(title="__**Hire Error**__", description=f"You must Create Hire Message for Role to Hire someone.\n`{self.bot.prefix}hrole <Mention Role> <Create Message>`", timestamp=datetime.now(), color=0xff0000)
			embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed_3)
			return
		embed = discord.Embed(title="__**New Hire**__", timestamp=datetime.now(), color=0xff0000)
		embed.add_field(name=":busts_in_silhouette: Member:", value=f"{member.mention}", inline=False)
		embed.add_field(name=":alien: Position:", value=f"`{role}`", inline=False)
		embed.set_thumbnail(url=member.display_avatar.replace(format="png", static_format="png"))
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_4 = discord.Embed(title="__**Hired**__", description=f"You have been Assigned `{role}` in **{ctx.message.guild}**", timestamp=datetime.now(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_5 = discord.Embed(title="__**New Hire**__", description=f"{member.mention}, {role_message}", timestamp=datetime.now(), color=0xff0000)
		embed_5.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Hire in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	#giveaway = commands.Group(name="giveaway", description="Giveaway Commands")

	@commands.command() # Giveaway Command
	@commands.has_permissions(administrator=True)
	async def giveaway(self, ctx, channel: discord.TextChannel=None, time: str=None, winners: int=None, prize: str=None, *, description: str=None):
		if channel is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Channel to Announce Giveaway in.\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if time is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Specify an Amount of Time to End the Giveaway in.\n*Days: d, Hours: h, Minutes: m, Seconds: s*\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if winners is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Specify an Amount of Winners.\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if prize is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Prize for the Giveaway.\n*Must do Quotes Before & After Prize that Contains 2 Words or More*\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		fix, fix_str, current = convert_seconds(time)
		if description is None:
			description = ""
		collection = self.bot.db["Fun_giveaways"]
		collection_2 = self.bot.db["Fun_giveaways_entries"]
		collection_3 = self.bot.db["Fun_ended_giveaways"]
		log = {}
		log ["Guild_Name"] = str(ctx.guild)
		log ["Guild"] = ctx.guild.id
		log ["Winners"] = winners
		log ["Prize"] = prize
		log ["Description"] = description
		log ["Channel"] = channel.id
		log ["Begin"] = current
		log ["End"] = fix
		embed = discord.Embed(title="__**Giveaway Started**__", description=f"Giveaway Started in {channel.mention} for {prize}. There will be {winners} Winners.\n{description}", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		embed = discord.Embed(title="__**Giveaway**__", description=f"__**{prize}**__\n{description}", timestamp=fix, color=0xac5ece)
		embed.set_footer(text=f"{winners} Winners", icon_url=ctx.guild.icon.replace(format="png", static_format="png"))
		message = await channel.send(embed=embed)
		await message.add_reaction("\U0001F389")
		log ["Message"] = message.id
		await collection.insert_one(log)
	@giveaway.error
	async def giveaway_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # End Giveaway Command
	@commands.has_permissions(administrator=True)
	async def gend(self, ctx, messagez: int=None):
		if messagez is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Giveaway Message ID to End.\n`{self.bot.prefix}gend <Giveaway Message ID>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Fun_giveaways_entries"]
		collection_2 = self.bot.db["Fun_giveaways"]
		collection_3 = self.bot.db["Fun_ended_giveaways"]
		async for m in collection_2.find({"Guild": ctx.guild.id, "Message": messagez}, {"_id": 0}):
			prize = m["Prize"]
			description = m["Description"]
			amount = m["Winners"]
			grab_channel = m["Channel"]
			messagez = m["Message"]
			end = m["End"]
			start = m["Begin"]
			channel = ctx.guild.get_channel(grab_channel)
			message = await channel.fetch_message(messagez)
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"Giveaway Ended in {channel.mention} for {prize}.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		entries = []
		async for m in collection.find({"Guild": ctx.guild.id, "Message": messagez}, {"_id": 0}):
			entries += {m["Member"]}
		order = f"__***{prize}***__\n{description}\n__***Winners***__\n"
		counter = 1
		win_list = ""
		while counter <= amount:
			winners = random.choice(entries)
			member = ctx.guild.get_member(winners)
			if counter + 1 >= amount:
				win_list += f"{member.mention}"
			if not counter + 1 >= amount:
				win_list += f"{member.mention}, "
			order += f"**{counter}:** {str(member.mention)}\n"
			counter +=1
		log = {}
		log ["Guild_Name"] = str(ctx.guild)
		log ["Guild"] = ctx.guild.id
		log ["Prize"] = prize
		log ["Description"] = description
		log ["Winners"] = amount
		log ["Channel"] = grab_channel
		log ["Members"] = entries
		log ["Message"] = messagez
		log ["End"] = end
		log ["Begin"] = start
		await collection_3.insert_one(log)
		old_log = {"Guild": ctx.guild.id, "Message": messagez}
		await collection.delete_one(old_log)
		await collection_2.delete_many(old_log)
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"{order}", timestamp=end, color=0xac5ece)
		embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.replace(format="png", static_format="png"))
		await message.edit(embed=embed)
		await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
		await ctx.message.delete()
	@gend.error
	async def gend_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Reroll Giveaway Command
	@commands.has_permissions(administrator=True)
	async def reroll(self, ctx, messagez: int=None, new_winners: int=None):
		if messagez is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Giveaway Message ID to Reroll.\n`{self.bot.prefix}reroll <Giveaway Message ID> <Amount to Reroll>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Fun_ended_giveaways"]
		async for m in collection.find({"Guild": ctx.guild.id, "Message": messagez}, {"_id": 0}):
			prize = m["Prize"]
			description = m["Description"]
			amount = m["Winners"]
			if not new_winners is None:
				amount = new_winners
			grab_channel = m["Channel"]
			entries = m["Members"]
			messagez = m["Message"]
			end = m["End"]
			channel = ctx.guild.get_channel(grab_channel)
			message = await channel.fetch_message(messagez)
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"Giveaway Rerolled in {channel.mention} for {prize}.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		order = f"__***{prize}***__\n{description}\n__***New Winners***__\n"
		counter = 1
		win_list = ""
		while counter <= amount:
			winners = random.choice(entries)
			member = ctx.guild.get_member(winners)
			if counter + 1 >= amount:
				win_list += f"{member.mention}"
			if not counter + 1 >= amount:
				win_list += f"{member.mention}, "
			order += f"{str(member.mention)}\n"
			counter += 1
		old_log = {"Guild": ctx.guild.id, "Message": messagez}
		embed = discord.Embed(title="__**Giveaway Rerolled**__", description=f"{order}", timestamp=end, color=0xac5ece)
		embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon.replace(format="png", static_format="png"))
		await message.edit(embed=embed)
		await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
		await ctx.message.delete()
	@reroll.error
	async def reroll_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command(pass_context=True) # Poll Command
	@commands.has_permissions(kick_members=True)
	async def poll(self, ctx, question=None, *options: str):
		if len(options)<= 1:
			embed = discord.Embed(title="__**Poll Error**__", description=f"You need a Question and more than One Choice to make a Poll.\n`{self.bot.prefix}poll <Create Name> <Choice 1> <Choice 2>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(options) > 10:
			embed = discord.Embed(title="__**Poll Error**__", description=f"You can't make a Poll with more than 10 Questions.\n*Seperate Poll Names & Answers that Contain Spaces with Quotation Marks.*\n`{Bot_Prefix}poll <Create Name> <Answer 1> <Answer 2>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(options) == 2 and options[0].upper() == "YES" and options[1].upper() == "NO":
			reactions = ["\u2705", "\u274C"]
		else:
			reactions = ["\u0031\u20E3", "\u0032\u20E3", "\u0033\u20E3", "\u0034\u20E3", "\u0035\u20E3", "\u0036\u20E3", "\u0037\u20E3", "\u0038\u20E3", "\u0039\u20E3", "\U0001F51F"]
		description = []
		for x, option in enumerate(options):
			description += "\n{} {}".format(reactions[x], option)
		embed = discord.Embed(title=question, description="".join(description), timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		react_message = await ctx.send(embed=embed)
		for reaction in reactions[0:len(options)]:
			await react_message.add_reaction(reaction)
		await ctx.message.delete()
	@poll.error
	async def poll_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to make a Poll in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Moderation(bot))