import discord
import asyncio
import time
import motor.motor_asyncio
import pytz
from discord.ext import commands, tasks
from datetime import datetime
from pytz import timezone
from Utils.Helpers import server_stats



class Bump(commands.Cog, name="Bump"):
	def __init__(self,bot):
		self.bot = bot
		self.AutoBump.start()
	def cog_unload(self):
		self.AutoBump.cancel()
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)

	@commands.command() # Bump
	@commands.has_permissions()
	@commands.cooldown(1, 3600, commands.BucketType.guild)
	async def bump(self, ctx):
		bot_count = 0
		for b in ctx.guild.members:
			if b.bot:
				bot_count += 1
		online, idle, offline, dnd = server_stats(ctx.guild)
		collection = self.bot.db["Bump_guild_channels"]
		collection_2 = self.bot.db["Bump_guild_banner"]
		collection_3 = self.bot.db["Bump_guild_description"]
		collection_4 = self.bot.db["Bump_guild_invite"]
		grab_channels = collection.find({}, {"_id": 0})
		bump_channels = []
		guilds = []
		async for x in grab_channels:
			bump_channels += {x["Channel"]}
			guilds += {x["Guild"]}
		server_banner = None
		server_description = None
		server_invite = None
		grab_banner = collection_2.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			server_banner = x["Message"]
		grab_description = collection_3.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_description:
			server_description = x["Message"]
		grab_invite = collection_4.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_invite:
			server_invite = x["Message"]
		fmt = "%I:%M%p %B %d, %Y %Z"
		creation_date = ctx.guild.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime(fmt)
		if server_invite is None:
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must Set Server's Invite before you can Bump.\n`{self.bot.prefix}sinvite <Invite Link>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if server_description is None:
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must Set Server's Description before you can Bump.\n`{self.bot.prefix}sdescription <Create Description>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(description=f":crown: __**Owner:**__ {ctx.guild.owner}\n:earth_americas: __**Region:**__ {ctx.guild.region}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_author(name=f"{ctx.message.guild}", icon_url=str(ctx.message.guild.icon_url_as(format=None, static_format="png")))
		embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
		embed.add_field(name=f":busts_in_silhouette: Members [{ctx.guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
		embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(ctx.guild.roles)}`\n__**Categories:**__ `{len(ctx.guild.categories)}`\n__**Channels:**__ `{len(ctx.guild.channels)}`\n__**Verification:**__ {ctx.guild.verification_level}\n__**Content Filter:**__ {ctx.guild.explicit_content_filter}", inline=False)
		if not len(ctx.guild.emojis) == 0:
			embed.add_field(name=f":100: Emotes [{len(ctx.guild.emojis)}]", value=" ".join(map(lambda o: str(o), ctx.guild.emojis[0:9])), inline=False)
		if not server_banner is None:
			embed.set_image(url=f"{server_banner}")		
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_2 = discord.Embed(title="__**Bump**__", description=f"Your Ad has been Successfully Bumped in `{len(guilds)}` Servers.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		for x in bump_channels:
			try:
				bump_feed = self.bot.get_channel(x)
				await bump_feed.send(embed=embed)
			except:
				print(f"Server {x} has Altered their Bump Channel.")
		await ctx.send(embed=embed_2)
		await ctx.message.delete()
	@bump.error
	async def bump_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Bump this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
		if isinstance(error, commands.CommandOnCooldown):
			m, s = divmod(error.retry_after, 60)
			h, m = divmod(m, 60)
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must wait **{int(m)}** minutes to Bump this Server again.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Bump Preview
	async def spreview(self, ctx):
		bot_count = 0
		for b in ctx.guild.members:
			if b.bot:
				bot_count += 1
		online, idle, offline, dnd = server_stats(ctx.guild)
		collection_2 = self.bot.db["Bump_guild_banner"]
		collection_3 = self.bot.db["Bump_guild_description"]
		collection_4 = self.bot.db["Bump_guild_invite"]
		server_banner = None
		server_description = None
		server_invite = None
		grab_banner = collection_2.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			server_banner = x["Message"]
		grab_description = collection_3.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_description:
			server_description = x["Message"]
		grab_invite = collection_4.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_invite:
			server_invite = x["Message"]
		fmt = "%I:%M%p %B %d, %Y %Z"
		creation_date = ctx.guild.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime(fmt)
		if server_invite is None:
			embed = discord.Embed(title="__**Preview Error**__", description=f"You must Set Server's Invite before you can Preview it.\n`{self.bot.prefix}sinvite <Invite Link>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if server_description is None:
			embed = discord.Embed(title="__**Preview Error**__", description=f"You must Set Server's Description before you can Preview it.\n`{self.bot.prefix}sdescription <Create Description>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(description=f":crown: __**Owner:**__ {ctx.guild.owner}\n:earth_americas: __**Region:**__ {ctx.guild.region}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_author(name=f"{ctx.message.guild}", icon_url=str(ctx.message.guild.icon_url_as(format=None, static_format="png")))
		embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
		embed.add_field(name=f":busts_in_silhouette: Members [{ctx.guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
		embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(ctx.guild.roles)}`\n__**Categories:**__ `{len(ctx.guild.categories)}`\n__**Channels:**__ `{len(ctx.guild.channels)}`\n__**Verification:**__ {ctx.guild.verification_level}\n__**Content Filter:**__ {ctx.guild.explicit_content_filter}", inline=False)
		if not len(ctx.guild.emojis) == 0:
			embed.add_field(name=f":100: Emotes [{len(ctx.guild.emojis)}]", value=" ".join(map(lambda o: str(o), ctx.guild.emojis[0:9])), inline=False)
		if not server_banner is None:
			embed.set_image(url=f"{server_banner}")		
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Set Bump Channel
	@commands.has_permissions(administrator=True)
	async def bumpset(self, ctx, *, content: discord.TextChannel=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Mention a Channel to Receive Bumps in.\n`{self.bot.prefix}bumpset <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_channels"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Channel"] = content.id
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Your Server will Receive Bumps in {content.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Bump Setup**__", description=f"This Channel will now Receive Bumps.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await content.send(embed=embed_3)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Your Server will no longer Receive Bumps.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@bumpset.error
	async def bumpset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Bump Banner
	@commands.has_permissions(administrator=True)
	async def sbanner(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Attach Banner URL.\n`{self.bot.prefix}sbanner <Banner URL>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_banner"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Banner has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Banner has been changed to\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@sbanner.error
	async def sbanner_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Bump Invite
	@commands.has_permissions(administrator=True)
	async def sinvite(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Attach Server Invite.\n`{self.bot.prefix}sinvite <Invite Link>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if not content.startswith("https://discord.gg/"):
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please Enter a Valid Invite.\n`{self.bot.prefix}sinvite <Invite Link>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_invite"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Invite has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Invite has been changed to\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@sinvite.error
	async def sinvite_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Bump Message
	@commands.has_permissions(administrator=True)
	async def sdescription(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Attach Server Description.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if "https://discord.gg/" in ctx.message.content.lower():
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please No Invites inside Your Description.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(content) > 950:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please Keep Description under 950 Characters.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_description"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Description has been set as\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Description has been changed to\n{content}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@sdescription.error
	async def sdescription_error(self, ctx, error):
		embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if isinstance(error, commands.CheckFailure):
			await ctx.send(embed=embed)

	@commands.command() # Set AutoBump Servers
	@is_owner()
	async def autobump(self, ctx, Guild: int=None, *, Owner: int=None):
		if Guild is None:
			embed = discord.Embed(title="__**Auto-Bump Error**__", description=f"Mention the Server's ID & Owner's User ID that's Receiving Auto-Bump.\n`{self.bot.prefix}autobump <Server ID> <User ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if Owner is None:
			embed = discord.Embed(title="__**Auto-Bump Error**__", description=f"Mention the Owner's User ID of the Guild who is Receiving Auto-Bump.\n`{self.bot.prefix}autobump <Server ID> <User ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_autobump"]
		Guild = self.bot.get_guild(Guild)
		Owner = Guild.get_member(Owner)
		log = {}
		log ["Guild_Name"] = str(Guild)
		log ["Owner"] = str(Owner)
		log ["Guild"] = Guild.id
		log ["Owner_ID"] = Owner.id
		log ["Members"] = Guild.member_count
		guildz = None
		async for x in collection.find({"Guild": Guild.id}, {"_id": 0, "Guild_Name": 0}):
			guildz = x["Guild"]
		if not guildz is None:
			old_log = {"Guild": Guild.id}
			await collection.delete_one(old_log)
			embed = discord.Embed(title="__**Auto-Bump Setup**__", description=f"Auto-Bump has been Disabled for **{Guild}**.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		await collection.insert_one(log)
		embed = discord.Embed(title="__**Auto-Bump Setup**__", description=f"Auto-Bump has been Enabled for *{Owner}* in **{Guild}**.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		embed = discord.Embed(title="__**Auto-Bump**__", description=f"Congratulations, Auto-Bump has been Enabled for {self.bot.user.mention} in {Guild}.\n*(Please Wait for Bump Cycle. You can still use {Bot_Prefix}bump)*", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await Owner.send(embed=embed)
		except:
			embed = discord.Embed(title="__**Auto-Bump**__", description=f"User has DM's Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		await ctx.message.delete()
	@autobump.error
	async def autobump_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



	@tasks.loop(hours=1)
	async def AutoBump(self):
		collection = self.bot.db["Bump_autobump"]
		async for x in collection.find({}, {"_id": 0}):
			try:
				guild = discord.utils.get(self.bot.guilds,id=int(x["Guild"]))
			except Exception as e:
				print(e)
				continue
			if guild is None:
				continue
			bot_count = 0
			for b in guild.members:
				if b.bot:
					bot_count += 1
			online, idle, offline, dnd = server_stats(guild)
			collection = self.bot.db["Bump_guild_channels"]
			collection_2 = self.bot.db["Bump_guild_banner"]
			collection_3 = self.bot.db["Bump_guild_description"]
			collection_4 = self.bot.db["Bump_guild_invite"]
			grab_channels = collection.find({}, {"_id": 0})
			bump_channels = []
			guilds = []
			async for x in grab_channels:
				bump_channels += {x["Channel"]}
				guilds += {x["Guild"]}
			server_banner = None
			server_description = None
			server_invite = None
			grab_banner = collection_2.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
			async for x in grab_banner:
				server_banner = x["Message"]
			grab_description = collection_3.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
			async for x in grab_description:
				server_description = x["Message"]
			grab_invite = collection_4.find({"Guild": guild.id}, {"_id": 0, "Guild": 0})
			async for x in grab_invite:
				server_invite = x["Message"]
			fmt = "%I:%M%p %B %d, %Y %Z"
			creation_date = guild.created_at
			az = creation_date.astimezone(timezone("US/Eastern"))
			correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
			create_date = correct_zone.strftime(fmt)
			if server_invite is None:
				print(f"Server {guild} has Not Setup an Invite to Bump.")
				return
			if server_description is None:
				print(f"Server {guild} has Not Setup a Description to Bump.")
				return
			embed = discord.Embed(description=f":crown: __**Owner:**__ {guild.owner}\n:earth_americas: __**Region:**__ {guild.region}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_author(name=f"{guild}", icon_url=str(guild.icon_url_as(format=None, static_format="png")))
			embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
			embed.add_field(name=f":busts_in_silhouette: Members [{guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
			embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(guild.roles)}`\n__**Categories:**__ `{len(guild.categories)}`\n__**Channels:**__ `{len(guild.channels)}`\n__**Verification:**__ {guild.verification_level}\n__**Content Filter:**__ {guild.explicit_content_filter}", inline=False)
			if not len(guild.emojis) == 0:
				embed.add_field(name=f":100: Emotes [{len(guild.emojis)}]", value=" ".join(map(lambda o: str(o), guild.emojis[0:9])), inline=False)
			if not server_banner is None:
				embed.set_image(url=f"{server_banner}")		
			embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			for x in bump_channels:
				try:
					bump_feed = self.bot.get_channel(x)
					await bump_feed.send(embed=embed)		
				except:
					print(f"Server {x} has Altered their Bump Channel.")
			print(f"[Auto Bump] {guild.name} has been Bumped.")
			await asyncio.sleep(180)

	@AutoBump.before_loop
	async def before_AutoBump(self):
		await self.bot.wait_until_ready()

def setup(bot):
	bot.add_cog(Bump(bot))