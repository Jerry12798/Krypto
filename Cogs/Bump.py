import discord
import asyncio
import time
import motor.motor_asyncio
import pytz
from discord.ext import commands
from datetime import datetime
from pytz import timezone
from Utils.Helpers import server_stats



class Bump(commands.Cog, name="Bump", description="Server Bump & Setup Commands"):
	def __init__(self,bot):
		self.bot = bot
	async def cog_load(self):
		pass
	async def cog_unload(self):
		pass

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
		creation_date = ctx.guild.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		if server_invite is None:
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must Set Server's Invite before you can Bump.\n`{self.bot.prefix}sinvite <Invite Link>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if server_description is None:
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must Set Server's Description before you can Bump.\n`{self.bot.prefix}sdescription <Create Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(description=f":crown: __**Owner:**__ {ctx.guild.owner}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.now(), color=0xac5ece)
		embed.set_author(name=f"{ctx.message.guild}", icon_url=str(ctx.message.guild.icon.replace(format="png", static_format="png")))
		embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
		embed.add_field(name=f":busts_in_silhouette: Members [{ctx.guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
		embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(ctx.guild.roles)}`\n__**Categories:**__ `{len(ctx.guild.categories)}`\n__**Channels:**__ `{len(ctx.guild.channels)}`\n__**Verification:**__ {ctx.guild.verification_level}\n__**Content Filter:**__ {ctx.guild.explicit_content_filter}", inline=False)
		if not len(ctx.guild.emojis) == 0:
			embed.add_field(name=f":100: Emotes [{len(ctx.guild.emojis)}]", value=" ".join(map(lambda o: str(o), ctx.guild.emojis[0:9])), inline=False)
		if not server_banner is None:
			embed.set_image(url=f"{server_banner}")		
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Bump**__", description=f"Your Ad has been Successfully Bumped in `{len(guilds)}` Servers.", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description="You do not have Required Permissions to Bump this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
		if isinstance(error, commands.CommandOnCooldown):
			m, s = divmod(error.retry_after, 60)
			h, m = divmod(m, 60)
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must wait **{int(m)}** minutes to Bump this Server again.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
		creation_date = ctx.guild.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		if server_invite is None:
			embed = discord.Embed(title="__**Preview Error**__", description=f"You must Set Server's Invite before you can Preview it.\n`{self.bot.prefix}sinvite <Invite Link>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if server_description is None:
			embed = discord.Embed(title="__**Preview Error**__", description=f"You must Set Server's Description before you can Preview it.\n`{self.bot.prefix}sdescription <Create Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(description=f":crown: __**Owner:**__ {ctx.guild.owner}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.now(), color=0xac5ece)
		embed.set_author(name=f"{ctx.message.guild}", icon_url=str(ctx.message.guild.icon.replace(format="png", static_format="png")))
		embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
		embed.add_field(name=f":busts_in_silhouette: Members [{ctx.guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
		embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(ctx.guild.roles)}`\n__**Categories:**__ `{len(ctx.guild.categories)}`\n__**Channels:**__ `{len(ctx.guild.channels)}`\n__**Verification:**__ {ctx.guild.verification_level}\n__**Content Filter:**__ {ctx.guild.explicit_content_filter}", inline=False)
		if not len(ctx.guild.emojis) == 0:
			embed.add_field(name=f":100: Emotes [{len(ctx.guild.emojis)}]", value=" ".join(map(lambda o: str(o), ctx.guild.emojis[0:9])), inline=False)
		if not server_banner is None:
			embed.set_image(url=f"{server_banner}")		
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()

	@commands.command() # Set Bump Message
	@commands.has_permissions(administrator=True)
	async def sdescription(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Attach Server Description.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if "https://discord.gg/" in ctx.message.content.lower():
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please No Invites inside Your Description.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if len(content) > 950:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please Keep Description under 950 Characters.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_description"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Description has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Description has been changed to\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@sdescription.error
	async def sdescription_error(self, ctx, error):
		embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if isinstance(error, commands.CheckFailure):
			await ctx.send(embed=embed)

	@commands.command() # Set Bump Invite
	@commands.has_permissions(administrator=True)
	async def sinvite(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Attach Server Invite.\n`{self.bot.prefix}sinvite <Invite Link>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		if not content.startswith("https://discord.gg/"):
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please Enter a Valid Invite.\n`{self.bot.prefix}sinvite <Invite Link>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_invite"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Invite has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Invite has been changed to\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Bump Banner
	@commands.has_permissions(administrator=True)
	async def sbanner(self, ctx, *, content: str=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Attach Banner URL.\n`{self.bot.prefix}sbanner <Banner URL>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_banner"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Message"] = content
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Banner has been set as\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Banner has been changed to\n{content}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
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
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Bump Channel
	@commands.has_permissions(administrator=True)
	async def bumpset(self, ctx, *, content: discord.TextChannel=None):
		if content is None:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Mention a Channel to Receive Bumps in.\n`{self.bot.prefix}bumpset <Mention Channel>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_channels"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = ctx.message.guild.id
		log ["Channel"] = content.id
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Your Server will Receive Bumps in {content.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Bump Setup**__", description=f"This Channel will now Receive Bumps.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await content.send(embed=embed_3)
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Your Server will no longer Receive Bumps.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": ctx.message.guild.id}
			await collection.delete_one(old_log)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@bumpset.error
	async def bumpset_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Bump(bot))