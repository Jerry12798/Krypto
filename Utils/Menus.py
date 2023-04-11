import discord
from datetime import datetime
from discord.ext import menus
from discord import ui



class Formatter(menus.ListPageSource):
	async def format_page(self, menu, entries):
		if menu.interaction.command.name == "eval":
			return f"```py\n{entries}```"
			
		if menu.interaction.command.name.endswith("leaderboard") or menu.interaction.command.name.startswith("leaderboard"):
			new_entries	 = ""
			if menu.interaction.command.name == "leaderboard_server" or menu.interaction.command.name == "leaderboard":
				for x in entries:
					new_entries += f"{x}"
				embed = discord.Embed(title="__**Server Leaderboard**__", description=f"{new_entries}", timestamp=datetime.now(), color=0xac5ece)
				try:
					embed.set_footer(text=f"{menu.interaction.user}", icon_url=menu.interaction.user.display_avatar.replace(format="png", static_format="png"))
				except:
					embed.set_footer(text=f"{menu.interaction.author}", icon_url=menu.interaction.author.display_avatar.replace(format="png", static_format="png"))

			if menu.interaction.command.name == "leaderboard_global" or menu.interaction.command.name == "gleaderboard":
				for x in entries:
					new_entries += f"{x}"
				embed = discord.Embed(title="__**Global Leaderboard**__", description=f"{new_entries}", timestamp=datetime.now(), color=0xac5ece)
				embed.set_thumbnail(url=menu.interaction.guild.icon.replace(format="png", static_format="png"))
				try:
					embed.set_footer(text=f"{menu.interaction.user}", icon_url=menu.interaction.user.display_avatar.replace(format="png", static_format="png"))
				except:
					embed.set_footer(text=f"{menu.interaction.author}", icon_url=menu.interaction.author.display_avatar.replace(format="png", static_format="png"))
					
			if menu.interaction.command.name == "leaderboard_votes" or menu.interaction.command.name == "vleaderboard":
				for x in entries:
					new_entries += f"{x}"
				embed = discord.Embed(title="__**Vote Leaderboard**__", description=f"{new_entries}", timestamp=datetime.now(), color=0xac5ece)
				try:
					embed.set_footer(text=f"{menu.interaction.user}", icon_url=menu.interaction.user.display_avatar.replace(format="png", static_format="png"))
				except:
					embed.set_footer(text=f"{menu.interaction.author}", icon_url=menu.interaction.author.display_avatar.replace(format="png", static_format="png"))
			return embed

		return entries

class DropDown(ui.Select):
	def __init__(self, menu, descriptions):
		self.menu = menu
		self.page_titles = descriptions
		options = []
		current = 0
		for x in range(self.menu._source.get_max_pages()):
			if self.page_titles is None:
				current += 1
				options.append(discord.SelectOption(label=f"Page {current}", value=current-1))
			else:
				title = self.page_titles[current]
				current += 1
				options.append(discord.SelectOption(label=f"Page {current}", description=f"{title}", value=current-1))
		super().__init__(placeholder=f"Select Page to View", min_values=1, max_values=1, options=options, row=0)

	async def callback(self, interaction:discord.Interaction):
		self.menu.current_interaction = interaction
		self.menu.current_page = int(self.values[0])
		await self.menu.show_page(int(self.values[0]))

class Pager(ui.View, menus.MenuPages):
	def __init__(self, source, dropdown=False, titles=False):
		super().__init__(timeout=60)
		self._source = source
		self.dropdown = dropdown
		self.descriptions = titles
		self.current_page = 0
		self.interaction = None
		self.message = None

	async def start(self, interaction):
		await self._source._prepare_once()
		self.interaction = interaction
		if self.dropdown is True:
			if self.descriptions is True:
				try:
					current = 0
					self.page_titles = []
					for x in range(self._source.get_max_pages()):
						page = await self._source.get_page(current)
						kwargs = await self._get_kwargs_from_page(page)
						title = kwargs['embed'].title.replace('*', '').replace('_', '')
						self.page_titles.append(title)
						current += 1
				except:
					self.page_titles = None
			else:
				self.page_titles = None
			self.add_item(DropDown(menu=self, descriptions=self.page_titles))
		initial_page = await self._source.get_page(0)
		kwargs = await self._get_kwargs_from_page(initial_page)
		title = kwargs['embed'].title.replace('*', '').replace('_', '')
		try:
			self.message = await interaction.followup.send(**kwargs)
		except:
			self.message = await interaction.channel.send(**kwargs)

	async def _get_kwargs_from_page(self, page):
		value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
		if isinstance(value, list):
			new_value = ""
			for s in value:
				new_value += s
			value = { 'content': new_value, 'embed': None }
		if isinstance(value, str):
			value = { 'content': value, 'embed': None }
		if isinstance(value, discord.Embed):
			value = { 'embed': value, 'content': None }
		if 'view' not in value:
			value.update({'view': self})
		return value

	async def interaction_check(self, interaction):
		try:
			return interaction.user == self.interaction.user
		except:
			return interaction.user == self.interaction.author

	async def show_page(self, page_number):
		page = await self._source.get_page(page_number)
		self.current_page = page_number
		kwargs = await self._get_kwargs_from_page(page)
		try:
			await self.current_interaction.response.edit_message(**kwargs)
		except:
			await self.message.edit(**kwargs)

	@ui.button(emoji='\U000023ee', style=discord.ButtonStyle.blurple, row=1)
	async def first_page(self, interaction, button):
		self.current_interaction = interaction
		await self.show_page(0)

	@ui.button(emoji='\U000023ea', style=discord.ButtonStyle.blurple, row=1)
	async def before_page(self, interaction, button):
		self.current_interaction = interaction
		await self.show_checked_page(self.current_page - 1)

	@ui.button(emoji='\U000023f9', style=discord.ButtonStyle.blurple, row=1)
	async def stop_page(self, interaction, button):
		self.stop()
		try:
			await self.message.delete_original_message()
		except:
			await self.message.delete()

	@ui.button(emoji='\U000023e9', style=discord.ButtonStyle.blurple, row=1)
	async def next_page(self, interaction, button):
		self.current_interaction = interaction
		await self.show_checked_page(self.current_page + 1)

	@ui.button(emoji='\U000023ed', style=discord.ButtonStyle.blurple, row=1)
	async def last_page(self, interaction, button):
		self.current_interaction = interaction
		await self.show_page(self._source.get_max_pages() - 1)