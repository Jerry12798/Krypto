import discord
import asyncio
import json
import time
import motor.motor_asyncio
import pymongo
from discord.ext import commands
from datetime import datetime



class Support(commands.Cog, name="Support"):
	def __init__(self, bot):
		self.bot = bot
	def is_owner():
		def predicate(ctx):
			return ctx.message.author.id in ctx.bot.owners
		return commands.check(predicate)

	@commands.command() # Direct Message Command
	@is_owner()
	async def reply(self, ctx, member: discord.User=None, *, content:str=None):
		if member is None:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"You need to Mention a Ticket ID & Create Message to Send.\n`{self.bot.prefix}reply <Ticket ID> <Create Reply Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		if content is None:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"Write a Message to DM with {self.bot.user.mention}.\n`{self.bot.prefix}reply <Ticket ID> <Create Reply Message>`", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title=f"__**{self.bot.user.name} Support**__", timestamp=datetime.utcnow(), color=0xac5ece)
		embed.add_field(name="Ticket:", value=f"{member.id}", inline=False)
		embed.add_field(name="Message:", value=f"{content}", inline=False)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		try:
			await member.send(embed=embed)
		except:
			embed = discord.Embed(title="__**DM Reply Error**__", description=f"User has DM's Disabled.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Support Ticket**__", description=f"Your Message was Successfully Sent.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
	@reply.error
	async def reply_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Reply Error**__", description=f"You are not Authorized to Send Messages with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Logout Command
	@is_owner()
	async def logout(self, ctx):
		embed = discord.Embed(title="__**Logging Out...**__", description=f"Goodnight...", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		self.mongo_client.close()
		await ctx.send(embed=embed)
		await ctx.message.delete()
		await self.bot.close()
	@logout.error
	async def logout_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Logout Error**__", description=f"You are not Authorized to Logout {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Load Cog Command
	@is_owner()
	async def load(self, ctx, *, extension_name : str=None):
		if extension_name is None:
			embed = discord.Embed(title="__**Load Error**__", description=f"Mention the Cog you want to Load.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			self.bot.load_extension(extension_name)
		except Exception as e:
			exc = '**{}:** *{}*'.format(type(e).__name__, e)
			embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback:**__\n{exc}", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Loaded**__", description=f"{extension_name} has been Loaded.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@load.error
	async def load_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Load Error**__", description=f"You are not Authorized to Load Cogs with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Unload Cog Command
	@is_owner()
	async def unload(self, ctx, *, extension_name : str=None):
		if extension_name is None:
			embed = discord.Embed(title="__**Unload Error**__", description=f"Mention the Cog you want to Unload.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			self.bot.unload_extension(extension_name)
		except Exception as e:
			exc = '**{}:** *{}*'.format(type(e).__name__, e)
			embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback:**__\n{exc}", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Unloaded**__", description=f"{extension_name} has been Unloaded.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@unload.error
	async def unload_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Unload Error**__", description=f"You are not Authorized to Unload Cogs with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Reload Cog Command
	@is_owner()
	async def reload(self, ctx, *, extension_name : str=None):
		if extension_name is None:
			embed = discord.Embed(title="__**Reload Error**__", description=f"Mention the Cog you want to Reload.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			self.bot.unload_extension(extension_name)
		except Exception as e:
			exc = '**{}:** *{}*'.format(type(e).__name__, e)
			embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback:**__\n{exc}", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		try:
			self.bot.load_extension(extension_name)
		except Exception as e:
			exc = '**{}:** *{}*'.format(type(e).__name__, e)
			embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback:**__\n{exc}", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			return
		embed = discord.Embed(title="__**Cog Reloaded**__", description=f"{extension_name} has been Reloaded.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@reload.error
	async def reload_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Reload Error**__", description=f"You are not Authorized to Reload Cogs with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)

	@commands.command() # Restart All Cogs Command
	@is_owner()
	async def restart(self, ctx):
		for extension in extensions:
			try:
				self.bot.unload_extension(extension)
			except Exception as e:
				exc = '**{}:** *{}*'.format(type(e).__name__, e)
				embed = discord.Embed(title="__**Unload Error**__", description=f"There was an error trying to unload *{extension_name}*\n__**Traceback:**__\n{exc}", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			try:
				self.bot.load_extension(extension)
			except Exception as e:
				exc = '**{}:** *{}*'.format(type(e).__name__, e)
				embed = discord.Embed(title="__**Load Error**__", description=f"There was an error trying to load *{extension_name}*\n__**Traceback:**__\n{exc}", timestamp=datetime.utcnow(), color=0xff0000)
				embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
				await ctx.send(embed=embed)
				return
			embed = discord.Embed(title="__**Cog Reloaded**__", description=f"{extension} has been Reloaded.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)
			await asyncio.sleep(1)
		embed = discord.Embed(title="__**Cogs Restarted**__", description=f"All Cogs have been Reloaded.", timestamp=datetime.utcnow(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
		await ctx.send(embed=embed)
		await ctx.message.delete()
	@restart.error
	async def restart_error(self, ctx, error):
		if isinstance(error, commands.CheckFailure):
			embed = discord.Embed(title="__**Restart Error**__", description=f"You are not Authorized to Restart Cogs with {self.bot.user.mention}.", timestamp=datetime.utcnow(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar_url_as(format=None, static_format="png"))
			await ctx.send(embed=embed)



def setup(bot):
	bot.add_cog(Support(bot))