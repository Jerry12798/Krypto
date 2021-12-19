import discord
import time
import random
import asyncio
import motor.motor_asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from Utils.Helpers import convert_seconds




class Entertainment(commands.Cog, name="Entertainment"):
	def __init__(self,bot):
		self.bot = bot
		
	@commands.command() # Words of Wisdom (8-Ball) Command
	async def wisdom(self, ctx, *,  message=None):
		if message is None:
			embed = discord.Embed(title="__**Words of Wisdom Error**__", description=f"Ask a Question to Gain Foresight about.\n`{self.bot.prefix}wisdom <Your Question>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
		wisdom_quotes = ["Yes", "No", "Maybe", "Ask Again Later", "Sometimes Answers can only be Found by the Questioner.", "Fate may Predict the Future but Free Will Creates Opportunity to Change it.", "Knowledge should be Shared... but Should we Share it, if the Information may Negatively Effect the Receivers Perspective of the Future?", "Some Answers are better being left Unkown."]
		embed_2 = discord.Embed(title="__**Words of Wisdom**__", description=f":question: __**Q:**__ {message}\n:crystal_ball: __**A:**__ {random.choice(wisdom_quotes)}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Dice Roll Command
	async def dice(self, ctx, sides:int=None):
		if sides is None:
			embed = discord.Embed(title="__**Dice Roll**__", description=f":game_die: __**Dice Sides:**__ `6`\n:question: __**Number:**__ `{random.randint(1,6)}`", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Dice Roll**__", description=f":game_die: __**Dice Sides:**__ `{sides}`\n:question: __**Number:**__ `{random.randint(1,sides)}`", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Coin Flip Command
	async def flip(self, ctx, side=None):
		sides = ["Heads", "Tails"]
		if side is None:
			embed = discord.Embed(title="__**Coin Flip**__", description=f":moyai: __**Side:**__ {random.choice(sides)}", timestamp=datetime.utcnow(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await ctx.message.delete()
			return
		embed_2 = discord.Embed(title="__**Coin Flip**__", description=f":pencil: __**Your Choice:**__ {side}\n:moyai: __**Side:**__ {random.choice(sides)}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Rock, Paper, Scissors Command
	async def rps(self, ctx, *, choice=None):
		choices = ["Rock", "Paper", "Scissors"]
		bot_choice = random.choice(choices)
		if choice is None:
			embed = discord.Embed(title="__**Rock, Paper, Scissors Error**__", description=f"You must Include your Choice.\n`{self.bot.prefix}rps <Your Choice>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed_2 = discord.Embed(title="__**Rock, Paper, Scissors**__", description=f":robot: __**{self.bot.user.name}'s Choice:**__ {bot_choice}\n:pencil: __**Your Choice:**__ {choice}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed_2)
		await ctx.message.delete()

	@commands.command() # Phone Call Command
	async def phone(self, ctx, *, content:str=None):
		if content is None:
			embed = discord.Embed(title="__**Phone Error**__", description=f"Write a Message to make a Call.\n`{self.bot.prefix}phone <Create Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		external_links = ["https", ".com", ".net", ".org", ".tv"]
		for x in external_links:
			if x in content.lower():
				embed = discord.Embed(title="__**Phone Error**__", description=f"Please Do Not Send Links.", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
		if "discord.gg" in content.lower():
			embed = discord.Embed(title="__**Phone Error**__", description=f"Please Do Not Send Invites.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		collection = self.bot.db["Config_phone"]
		servers = None
		async for m in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			Channelz = m["Channel"]
			servers = ctx.message.guild.get_channel(Channelz)
		if servers is None:
			embed = discord.Embed(title="__**Phone Error**__", description=f"You must Setup a Line to Use the Phone.\n`{self.bot.prefix}psetup <Mention Channel>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		linez = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			linez += {x["Guild"]}
		lines = len(linez)-1
		embed = discord.Embed(title="__**Incoming Call**__", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="Caller's Message:", value=f"{content}", inline=False)
		embed.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild is servers.guild:
			embed_2 = discord.Embed(title="__**Message Sent**__", timestamp=datetime.utcnow(), color=0xac5ece)
			embed_2.add_field(name="Receiving Servers:", value=f"Message received in {lines} servers.", inline=False)
			embed_2.set_footer(text=f"{self.bot.user}", icon_url=self.bot.user.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed_2)
		grab_channelz = collection.find({}, {"_id": 0, "Guild": 0})
		channelz = []
		async for x in grab_channelz:
			channelz += {x["Channel"]}
		for x in channelz:
			try:
				lines = self.bot.get_channel(x)
				if lines.guild is not ctx.message.guild: 
					await lines.send(embed=embed)
			except:
				print(f"Server {x} has Altered their Phone Line Channel.")
		await ctx.message.delete()

	@commands.command() # Giveaway Command
	@commands.has_permissions(administrator=True)
	async def giveaway(self, ctx, channel: discord.TextChannel=None, time: str=None, winners: int=None, prize: str=None, *, description: str=None):
		if channel is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Channel to Announce Giveaway in.\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if time is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Specify an Amount of Time to End the Giveaway in.\n*Days: d, Hours: h, Minutes: m, Seconds: s*\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if winners is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Specify an Amount of Winners.\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if prize is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Prize for the Giveaway.\n*Must do Quotes Before & After Prize that Contains 2 Words or More*\n`{self.bot.prefix}giveaway <Mention Channel> <Amount of Time> <Amount of Winners> <Prize> <Prize Description>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		fix = convert_seconds(time)
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
		log ["End"] = date
		embed = discord.Embed(title="__**Giveaway Started**__", description=f"Giveaway Started in {channel.mention} for {prize}. There will be {winners} Winners.\n{description}", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		embed = discord.Embed(title="__**Giveaway**__", description=f"__**{prize}**__\n{description}", timestamp=date, color=0xac5ece)
		embed.set_footer(text=f"{winners} Winners", icon_url=ctx.guild.icon_url_as(format=None, static_format="png"))
		message = await channel.send(embed=embed)
		await message.add_reaction("\U0001F389")
		log ["Message"] = message.id
		await collection.insert_one(log)
	@giveaway.error
	async def giveaway_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # End Giveaway Command
	@commands.has_permissions(administrator=True)
	async def gend(self, ctx, messagez: int=None):
		if messagez is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Giveaway Message ID to End.\n`{self.bot.prefix}gend <Giveaway Message ID>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"Giveaway Ended in {channel.mention} for {prize}.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url_as(format=None, static_format="png"))
		await message.edit(embed=embed)
		await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
		await ctx.message.delete()
	@gend.error
	async def gend_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Reroll Giveaway Command
	@commands.has_permissions(administrator=True)
	async def reroll(self, ctx, messagez: int=None, new_winners: int=None):
		if messagez is None:
			embed = discord.Embed(title="__**Giveaway Error**__", description=f"Mention a Giveaway Message ID to Reroll.\n`{self.bot.prefix}reroll <Giveaway Message ID> <Amount to Reroll>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed = discord.Embed(title="__**Giveaway Ended**__", description=f"Giveaway Rerolled in {channel.mention} for {prize}.", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
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
		embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url_as(format=None, static_format="png"))
		await message.edit(embed=embed)
		await channel.send(f"Congratulations {win_list}! You won the **{prize}**!")
		await ctx.message.delete()
	@reroll.error
	async def reroll_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Set Phone Call Channel
	@commands.has_permissions(administrator=True)
	async def psetup(self, ctx, *, channel: discord.TextChannel=None):
		if channel is None:
			embed = discord.Embed(title="__**Phone Setup Error**__", description=f"Mention Channel to Receive Phone Calls in.\n`{self.bot.prefix}psetup <Mention Channel>`.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
		collection = self.bot.db["Config_phone"]
		log = {}
		log ["Guild_Name"] = ctx.guild.name
		log ["Guild"] = channel.guild.id
		log ["Channel"] = channel.id
		embed = discord.Embed(title="__**Phone Setup**__", description=f"Phone Calls will be directed to {channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_3 = discord.Embed(title="__**Phone Setup**__", description=f"This channel will now receive Phone Calls.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_3.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		guildz = []
		async for x in collection.find({}, {"_id": 0, "Channel": 0}):
			guildz += {x["Guild"]}
		if ctx.message.guild.id not in guildz:
			await collection.insert_one(log)
			await ctx.send(embed=embed)
			await channel.send(embed=embed_3)
			await ctx.message.delete()
			return
		async for x in collection.find({"Guild": ctx.message.guild.id}, {"_id": 0, "Guild": 0}):
			grab_old_channel = x["Channel"]
			old_channel = ctx.message.guild.get_channel(grab_old_channel)
		embed_2 = discord.Embed(title="__**Phone Setup**__", description=f"Phone Calls will no longer be Received in {old_channel.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_2.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		embed_4 = discord.Embed(title="__**Phone Setup**__", description=f"This Channel will no longer Receive Phone Calls.", timestamp=datetime.utcnow(), color=0xff0000)
		embed_4.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		if ctx.message.guild.id in guildz:
			old_log = {"Guild": channel.guild.id}
			await collection.delete_one(old_log)
			await old_channel.send(embed=embed_4)
			await ctx.send(embed=embed_2)
			await ctx.message.delete()
			return
	@psetup.error
	async def psetup_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Permission Error**__", description=f"You do not have Required Permissions to Configure {self.bot.user.mention} in this Server.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)


		
	@commands.Cog.listener() # Get Vote Event
	async def on_raw_reaction_add(self, payload):
		await self.bot.wait_until_ready()
		if self.bot.user.id == payload.user_id:
			return
		collection = self.bot.db["Fun_giveaways"]
		collection_2 = self.bot.db["Fun_giveaways_entries"]
		message = 0
		async for x in collection.find({"Message": payload.message_id}, {"_id": 0}):
			message = x["Message"]
		if payload.message_id == message:
			if payload.user_id != self.bot.user.id:
				if str(payload.emoji) == "\U0001F389":
					log = {}
					log ["Guild"] = payload.guild_id
					log ["Message"] = payload.message_id
					log ["Member"] = payload.user_id
					collection_2.insert_one(log)

def setup(bot):
	bot.add_cog(Entertainment(bot))