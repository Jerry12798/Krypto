import discord
import asyncio
import time
import motor.motor_asyncio
import pytz
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
from pytz import timezone
from Utils.Helpers import server_stats



class Bumpset(commands.Cog, app_commands.Group, name="bumpset", description="Server Bump & Setup Commands"):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot
	async def cog_load(self):
		pass
	async def cog_unload(self):
		pass

	@app_commands.command(name="bump", description="Bump the Server") # Bump
	@app_commands.checks.cooldown(1, 3600, key=lambda i: (i.guild_id))
	async def bump(self, interaction:discord.Interaction):
		bot_count = 0
		for b in interaction.guild.members:
			if b.bot:
				bot_count += 1
		online, idle, offline, dnd = server_stats(interaction.guild)
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
		grab_banner = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			server_banner = x["Message"]
		grab_description = collection_3.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_description:
			server_description = x["Message"]
		grab_invite = collection_4.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_invite:
			server_invite = x["Message"]
		creation_date = interaction.guild.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		if server_invite is None:
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must Set Server's Invite before you can Bump.\n`{self.bot.prefix}sinvite <Invite Link>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if server_description is None:
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must Set Server's Description before you can Bump.\n`{self.bot.prefix}sdescription <Create Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		embed = discord.Embed(description=f":crown: __**Owner:**__ {interaction.guild.owner}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.now(), color=0xac5ece)
		embed.set_author(name=f"{interaction.guild}", icon_url=str(interaction.guild.icon.replace(format="png", static_format="png")))
		embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
		embed.add_field(name=f":busts_in_silhouette: Members [{interaction.guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
		embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(interaction.guild.roles)}`\n__**Categories:**__ `{len(interaction.guild.categories)}`\n__**Channels:**__ `{len(interaction.guild.channels)}`\n__**Verification:**__ {interaction.guild.verification_level}\n__**Content Filter:**__ {interaction.guild.explicit_content_filter}", inline=False)
		if not len(interaction.guild.emojis) == 0:
			embed.add_field(name=f":100: Emotes [{len(interaction.guild.emojis)}]", value=" ".join(map(lambda o: str(o), interaction.guild.emojis[0:9])), inline=False)
		if not server_banner is None:
			embed.set_image(url=f"{server_banner}")		
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_2 = discord.Embed(title="__**Bump**__", description=f"Your Ad has been Successfully Bumped in `{len(guilds)}` Servers.", timestamp=datetime.now(), color=0xac5ece)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		for x in bump_channels:
			try:
				bump_feed = self.bot.get_channel(x)
				await bump_feed.send(embed=embed)
			except:
				print(f"Server {x} has Altered their Bump Channel.")
		await interaction.followup.send(embed=embed_2)
		#await ctx.message.delete()
	@bump.error
	async def bump_error(self, interaction, error):
		if isinstance(error, app_commands.CommandOnCooldown):
			m, s = divmod(error.retry_after, 60)
			h, m = divmod(m, 60)
			embed = discord.Embed(title="__**Bump Error**__", description=f"You must wait **{int(m)}** minutes to Bump this Server again.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="preview", description="Display Preview of Server Bump") # Bump Preview
	async def preview(self, interaction:discord.Interaction):
		bot_count = 0
		for b in interaction.guild.members:
			if b.bot:
				bot_count += 1
		online, idle, offline, dnd = server_stats(interaction.guild)
		collection_2 = self.bot.db["Bump_guild_banner"]
		collection_3 = self.bot.db["Bump_guild_description"]
		collection_4 = self.bot.db["Bump_guild_invite"]
		server_banner = None
		server_description = None
		server_invite = None
		grab_banner = collection_2.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_banner:
			server_banner = x["Message"]
		grab_description = collection_3.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_description:
			server_description = x["Message"]
		grab_invite = collection_4.find({"Guild": interaction.guild.id}, {"_id": 0, "Guild": 0})
		async for x in grab_invite:
			server_invite = x["Message"]
		creation_date = interaction.guild.created_at
		az = creation_date.astimezone(timezone("US/Eastern"))
		correct_zone = az.replace(tzinfo=pytz.utc).astimezone(timezone("US/Eastern"))
		create_date = correct_zone.strftime("%B %d, %Y %I:%M%p %Z")
		if server_invite is None:
			embed = discord.Embed(title="__**Preview Error**__", description=f"You must Set Server's Invite before you can Preview it.\n`{self.bot.prefix}sinvite <Invite Link>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if server_description is None:
			embed = discord.Embed(title="__**Preview Error**__", description=f"You must Set Server's Description before you can Preview it.\n`{self.bot.prefix}sdescription <Create Description>`", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		embed = discord.Embed(description=f":crown: __**Owner:**__ {interaction.guild.owner}\n:calendar: __**Created:**__ {create_date}",timestamp=datetime.now(), color=0xac5ece)
		embed.set_author(name=f"{interaction.guild}", icon_url=str(interaction.guild.icon.replace(format="png", static_format="png")))
		embed.add_field(name=":clipboard: Description:", value=f"{server_description}\n\n[Click to Join]({server_invite})", inline=False)
		embed.add_field(name=f":busts_in_silhouette: Members [{interaction.guild.member_count}]", value=f":computer: **Online:** `{online}`\n:white_circle: **Offline:** `{offline}`\n:zzz: **Away:** `{idle}`\n:red_circle: **Do Not Disturb:** `{dnd}`", inline=False)
		embed.add_field(name=":globe_with_meridians: Misc", value=f"__**Bots:**__ `{bot_count}`\n__**Roles:**__ `{len(interaction.guild.roles)}`\n__**Categories:**__ `{len(interaction.guild.categories)}`\n__**Channels:**__ `{len(interaction.guild.channels)}`\n__**Verification:**__ {interaction.guild.verification_level}\n__**Content Filter:**__ {interaction.guild.explicit_content_filter}", inline=False)
		if not len(interaction.guild.emojis) == 0:
			embed.add_field(name=f":100: Emotes [{len(interaction.guild.emojis)}]", value=" ".join(map(lambda o: str(o), interaction.guild.emojis[0:9])), inline=False)
		if not server_banner is None:
			embed.set_image(url=f"{server_banner}")		
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=embed)
		#await ctx.message.delete()

	@app_commands.command(name="description", description="Set Server's Bump Advertisement Message") # Set Bump Message
	@app_commands.describe(message="Advertisement Message to be Displayed")
	@app_commands.checks.has_permissions(administrator=True)
	async def description(self, interaction:discord.Interaction, *, message:str):
		if "https://discord.gg/" in message.lower():
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please No Invites inside Your Description.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		if len(message) > 950:
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please Keep Description under 950 Characters.\n`{self.bot.prefix}sdescription <Server Description>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_description"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = message
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Description has been set as\n{message}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Description has been changed to\n{message}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@description.error
	async def description_error(self, interaction, error):
		embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if isinstance(error, app_commands.CheckFailure):
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="invite", description="Set Server's Bump Invite URL") # Set Bump Invite
	@app_commands.describe(invite="Server's Invite to Add")
	@app_commands.checks.has_permissions(administrator=True)
	async def invite(self, interaction:discord.Interaction, *, invite:str):
		if not invite.startswith("https://discord.gg/"):
			embed = discord.Embed(title="__**Bumpset Error**__", description=f"Please Enter a Valid Invite.\n`{self.bot.prefix}sinvite <Invite Link>`.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)
			return
		collection = self.bot.db["Bump_guild_invite"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = invite
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Invite has been set as\n{invite}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Invite has been changed to\n{invite}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@invite.error
	async def invite_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="banner", description="Set Server's Banner URL") # Set Bump Banner
	@app_commands.describe(url="Banner URL to Add")
	@app_commands.checks.has_permissions(administrator=True)
	async def banner(self, interaction:discord.Interaction, *, url: str):
		collection = self.bot.db["Bump_guild_banner"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Message"] = url
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Server Banner has been set as\n{url}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Server Banner has been changed to\n{url}.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await collection.insert_one(log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@banner.error
	async def banner_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

	@app_commands.command(name="feed", description="Set Channel to Receive Bump Feed in") # Set Bump Channel
	@app_commands.describe(channel="Channel to Receive Feed in")
	@app_commands.checks.has_permissions(administrator=True)
	async def feed(self, interaction:discord.Interaction, *, channel:discord.TextChannel):
		collection = self.bot.db["Bump_guild_channels"]
		log = {}
		log ["Guild_Name"] = interaction.guild.name
		log ["Guild"] = interaction.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Bump Setup**__", description=f"Your Server will Receive Bumps in {channel.mention}.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		embed_3 = discord.Embed(title="__**Bump Setup**__", description=f"This Channel will now Receive Bumps.", timestamp=datetime.now(), color=0xff0000)
		embed_3.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if interaction.guild.id not in guildz:
			await collection.insert_one(log)
			await channel.send(embed=embed_3)
			await interaction.followup.send(embed=embed)
			#await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Bump Setup**__", description=f"Your Server will no longer Receive Bumps.", timestamp=datetime.now(), color=0xff0000)
		embed_2.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		if interaction.guild.id in guildz:
			old_log = {"Guild": interaction.guild.id}
			await collection.delete_one(old_log)
			await interaction.followup.send(embed=embed_2)
			#await ctx.message.delete()
			return
	@feed.error
	async def feed_error(self, interaction, error):
		if isinstance(error, app_commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=embed)

async def setup(bot):
	await bot.add_cog(Bumpset(bot))