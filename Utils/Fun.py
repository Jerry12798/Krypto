import akinator
import discord
from akinator.async_aki import Akinator
from datetime import datetime



async def play_aki(self, interaction):
	def check(m):
		if m.author.id == interaction.user.id and m.channel.id == interaction.channel.id:
			return m
	async def go_back(previous_state):
		try:
			state = await self.bot.aki.back()
		except akinator.CantGoBackAnyFurther:
			embed = discord.Embed(title="__**Akinator Error**__", description=f"I can't go back any further!", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			interaction_to_edit = await interaction.original_message()
			await interaction_to_edit.edit(embed=embed)
			state = previous_state

		return state
	async def ask_questions(state):
		while self.bot.aki.progression <= 80:
			embed = discord.Embed(title=f"__**Akinator | Question {self.bot.aki.step+1}**__", description=f"**{state}**\n\nYes **(Y)** / No **(N)** / IDK **(I)** / Probably **(P)** / Probably Not **(PN)**\n[Back **(B)**]", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			try:
				interaction_to_edit = await interaction.original_message()
				await interaction_to_edit.edit(embed=embed)
			except:
				await interaction.followup.send(embed=embed)

			answer = await self.bot.wait_for('message', check=check)
			
			if answer.content.lower() == "back" or answer.content.lower() == "b":
				state = await go_back(previous_state=state)
			else:
				try:
					state = await self.bot.aki.answer(answer.content.lower())
				except akinator.AkiTimedOut:
					await self.bot.aki.close()
					self.bot.playing_aki.remove(interaction.user.id)
					return
				except akinator.AkiNoQuestions:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Akinator has No More Questions!", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					interaction_to_edit = await interaction.original_message()
					await interaction_to_edit.edit(embed=embed)
					await self.bot.aki.close()
					self.bot.playing_aki.remove(interaction.user.id)
					return
				except akinator.AkiServerDown:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Akinator is currently down!", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					interaction_to_edit = await interaction.original_message()
					await interaction_to_edit.edit(embed=embed)
					await self.bot.aki.close()
					self.bot.playing_aki.remove(interaction.user.id)
					return
				except akinator.AkiTechnicalError:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Akinator has faced a technical error!", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					interaction_to_edit = await interaction.original_message()
					await interaction_to_edit.edit(embed=embed)
					await self.bot.aki.close()
					self.bot.playing_aki.remove(interaction.user.id)
					return
				except akinator.InvalidAnswerError:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Invalid Answer\n\nYes **(Y)** / No **(N)** / IDK **(I)** / Probably **(P)** / Probably Not **(PN)**\n[Back **(B)**]", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
					interaction_to_edit = await interaction.original_message()
					await interaction_to_edit.edit(embed=embed)

					answer = await self.bot.wait_for('message', check=check)
					
					if answer.content.lower() == "back" or answer.content.lower() == "b":
						state = await go_back(previous_state=state)
					else:
						try:
							state = await self.bot.aki.answer(answer.content.lower())
						except akinator.AkiTimedOut:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(interaction.user.id)
							return
						except akinator.AkiNoQuestions:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(interaction.user.id)
							return
						except akinator.AkiServerDown:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(interaction.user.id)
							return
						except akinator.AkiTechnicalError:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(interaction.user.id)
							return
						except akinator.InvalidAnswerError:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(interaction.user.id)
							return
					try:
						await answer.delete()	
					except:
						pass
			try:
				await answer.delete()	
			except:
				pass
			await self.bot.aki.win()
	
	if interaction.user.id in self.bot.playing_aki:
		embed = discord.Embed(title="__**Akinator Error**__", description=f"You already have an active game going.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		interaction_to_edit = await interaction.original_message()
		await interaction_to_edit.edit(embed=embed)
		return

	state = await self.bot.aki.start_game()

	self.bot.playing_aki.append(interaction.user.id)
	
	await ask_questions(state=state)

	embed = discord.Embed(title="__**Akinator**__", description=f"**Is this your character?**\n{self.bot.aki.first_guess['name']}\n{self.bot.aki.first_guess['description']}\n\nYes **(Y)** or No **(N)**\n[Back **(B)**]", timestamp=datetime.now(), color=0xac5ece)
	embed.set_image(url=self.bot.aki.first_guess['absolute_picture_path'])
	embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
	interaction_to_edit = await interaction.original_message()
	await interaction_to_edit.edit(embed=embed)

	await self.bot.aki.close()
	self.bot.playing_aki.remove(interaction.user.id)

	answer = await self.bot.wait_for('message', check=check)

	if answer.content.lower() == "yes" or answer.content.lower().lower() == "y":
		embed = discord.Embed(title="__**Akinator**__", description=f"I love playing with you!", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		interaction_to_edit = await interaction.original_message()
		await interaction_to_edit.edit(embed=embed)
	if answer.content.lower() == "no" or answer.content.lower().lower() == "n":
		embed = discord.Embed(title="__**Akinator**__", description=f"Oof.. hopefully I'll have better luck next time.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		interaction_to_edit = await interaction.original_message()
		await interaction_to_edit.edit(embed=embed)
	try:
		await answer.delete()	
	except:
		pass

async def play_ctx_aki(self, ctx):
	def check(m):
		if m.author.id == ctx.author.id and m.channel.id == ctx.channel.id:
			return m
	async def go_back(previous_state):
		try:
			state = await self.bot.aki.back()
		except akinator.CantGoBackAnyFurther:
			embed = discord.Embed(title="__**Akinator Error**__", description=f"I can't go back any further!", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)
			state = previous_state

		return state
	async def ask_questions(state):
		while self.bot.aki.progression <= 80:
			embed = discord.Embed(title=f"__**Akinator | Question {self.bot.aki.step+1}**__", description=f"**{state}**\n\nYes **(Y)** / No **(N)** / IDK **(I)** / Probably **(P)** / Probably Not **(PN)**\n[Back **(B)**]", timestamp=datetime.now(), color=0xac5ece)
			embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
			await ctx.send(embed=embed)

			answer = await self.bot.wait_for('message', check=check)
			
			if answer.content.lower() == "back" or answer.content.lower() == "b":
				state = await go_back(previous_state=state)
			else:
				try:
					state = await self.bot.aki.answer(answer.content.lower())
				except akinator.AkiTimedOut:
					await self.bot.aki.close()
					self.bot.playing_aki.remove(ctx.author.id)
					return
				except akinator.AkiNoQuestions:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Akinator has No More Questions!", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
					await ctx.send(embed=embed)

					await self.bot.aki.close()
					self.bot.playing_aki.remove(ctx.author.id)
					return
				except akinator.AkiServerDown:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Akinator is currently down!", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
					await ctx.send(embed=embed)

					await self.bot.aki.close()
					self.bot.playing_aki.remove(ctx.author.id)
					return
				except akinator.AkiTechnicalError:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Akinator has faced a technical error!", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
					await ctx.send(embed=embed)

					await self.bot.aki.close()
					self.bot.playing_aki.remove(ctx.author.id)
					return
				except akinator.InvalidAnswerError:
					embed = discord.Embed(title="__**Akinator Error**__", description=f"Invalid Answer\n\nYes **(Y)** / No **(N)** / IDK **(I)** / Probably **(P)** / Probably Not **(PN)**\n[Back **(B)**]", timestamp=datetime.now(), color=0xff0000)
					embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
					await ctx.send(embed=embed)

					answer = await self.bot.wait_for('message', check=check)
					
					if answer.content.lower() == "back" or answer.content.lower() == "b":
						state = await go_back(previous_state=state)
					else:
						try:
							state = await self.bot.aki.answer(answer.content.lower())
						except akinator.AkiTimedOut:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(ctx.author.id)
							return
						except akinator.AkiNoQuestions:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(ctx.author.id)
							return
						except akinator.AkiServerDown:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(ctx.author.id)
							return
						except akinator.AkiTechnicalError:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(ctx.author.id)
							return
						except akinator.InvalidAnswerError:
							await self.bot.aki.close()
							self.bot.playing_aki.remove(ctx.author.id)
							return
				
			await self.bot.aki.win()
	
	if ctx.author.id in self.bot.playing_aki:
		embed = discord.Embed(title="__**Akinator Error**__", description=f"You already have an active game going.", timestamp=datetime.now(), color=0xff0000)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
		return

	state = await self.bot.aki.start_game()

	self.bot.playing_aki.append(ctx.author.id)
	
	await ask_questions(state=state)

	embed = discord.Embed(title="__**Akinator**__", description=f"**Is this your character?**\n{self.bot.aki.first_guess['name']}\n{self.bot.aki.first_guess['description']}\n\nYes **(Y)** or No **(N)**\n[Back **(B)**]", timestamp=datetime.now(), color=0xac5ece)
	embed.set_image(url=self.bot.aki.first_guess['absolute_picture_path'])
	embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
	await ctx.send(embed=embed)

	await self.bot.aki.close()
	self.bot.playing_aki.remove(ctx.author.id)

	answer = await self.bot.wait_for('message', check=check)

	if answer.content.lower() == "yes" or answer.content.lower().lower() == "y":
		embed = discord.Embed(title="__**Akinator**__", description=f"I love playing with you!", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)
	if answer.content.lower() == "no" or answer.content.lower().lower() == "n":
		embed = discord.Embed(title="__**Akinator**__", description=f"Oof.. hopefully I'll have better luck next time.", timestamp=datetime.now(), color=0xac5ece)
		embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.display_avatar.replace(format="png", static_format="png"))
		await ctx.send(embed=embed)