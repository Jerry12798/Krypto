import aiohttp
import asyncio
import discord
import re
import zlib
import heapq
import io
import os
import lxml.etree as etree
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from difflib import SequenceMatcher

RTFM_PAGE_TYPES = {
	'latest': 'https://discordpy.readthedocs.io/en/latest',
	'stable': 'https://discordpy.readthedocs.io/en/stable',
	'python': 'https://docs.python.org/3',
}


_word_regex = re.compile(r'\W', re.IGNORECASE)

def partial_ratio(a, b):
	short, long = (a, b) if len(a) <= len(b) else (b, a)
	m = SequenceMatcher(None, short, long)
	blocks = m.get_matching_blocks()
	scores = []
	for i, j, n in blocks:
		start = max(j - i, 0)
		end = start + len(short)
		o = SequenceMatcher(None, short, long[start:end])
		r = o.ratio()
		if 100 * r > 99:
			return 100
		scores.append(r)
	return int(round(100 * max(scores)))

def quick_ratio(a, b):
	m = SequenceMatcher(None, a, b)
	return int(round(100 * m.quick_ratio()))

def finder(text, collection, *, key=None, lazy=True):
	suggestions = []
	text = str(text)
	pat = '.*?'.join(map(re.escape, text))
	regex = re.compile(pat, flags=re.IGNORECASE)
	for item in collection:
		to_search = key(item) if key else item
		r = regex.search(to_search)
		if r:
			suggestions.append((len(r.group()), r.start(), item))

	def sort_key(tup):
		if key:
			return tup[0], tup[1], key(tup[2])
		return tup

	if lazy:
		return (z for _, _, z in sorted(suggestions, key=sort_key))
	else:
		return [z for _, _, z in sorted(suggestions, key=sort_key)]

def _extraction_generator(query, choices, scorer=quick_ratio, score_cutoff=0):
	try:
		for key, value in choices.items():
			score = scorer(query, key)
			if score >= score_cutoff:
				yield (key, score, value)
	except AttributeError:
		for choice in choices:
			score = scorer(query, choice)
			if score >= score_cutoff:
				yield (choice, score)

def extract(query, choices, *, scorer=quick_ratio, score_cutoff=0, limit=10):
	it = _extraction_generator(query, choices, scorer, score_cutoff)
	key = lambda t: t[1]
	if limit is not None:
		return heapq.nlargest(limit, it, key=key)
	return sorted(it, key=key, reverse=True)

def extract_matches(query, choices, *, scorer=quick_ratio, score_cutoff=0):
	matches = extract(query, choices, scorer=scorer, score_cutoff=score_cutoff, limit=None)
	if len(matches) == 0:
		return []
	top_score = matches[0][1]
	to_return = []
	index = 0
	while True:
		try:
			match = matches[index]
		except IndexError:
			break
		else:
			index += 1
		if match[1] != top_score:
			break
		to_return.append(match)
	return to_return

class SphinxObjectFileReader:
	BUFSIZE = 16 * 1024
	def __init__(self, buffer):
		self.stream = io.BytesIO(buffer)

	def readline(self):
		return self.stream.readline().decode('utf-8')

	def skipline(self):
		self.stream.readline()

	def read_compressed_chunks(self):
		decompressor = zlib.decompressobj()
		while True:
			chunk = self.stream.read(self.BUFSIZE)
			if len(chunk) == 0:
				break
			yield decompressor.decompress(chunk)
		yield decompressor.flush()

	def read_compressed_lines(self):
		buf = b''
		for chunk in self.read_compressed_chunks():
			buf += chunk
			pos = buf.find(b'\n')
			while pos != -1:
				yield buf[:pos].decode('utf-8')
				buf = buf[pos + 1:]
				pos = buf.find(b'\n')




def parse_object_inv(self, stream, url):
	result = {}
	inv_version = stream.readline().rstrip()
	if inv_version != '# Sphinx inventory version 2':
		raise RuntimeError('Invalid objects.inv file version.')
	projname = stream.readline().rstrip()[11:]
	version = stream.readline().rstrip()[11:]
	line = stream.readline()
	if 'zlib' not in line:
		raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')
	entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
	for line in stream.read_compressed_lines():
		match = entry_regex.match(line.rstrip())
		if not match:
			continue
		name, directive, prio, location, dispname = match.groups()
		domain, _, subdirective = directive.partition(':')
		if directive == 'py:module' and name in result:
			continue
		if directive == 'std:doc':
			subdirective = 'label'
		if location.endswith('$'):
			location = location[:-1] + name
		key = name if dispname == '-' else dispname
		prefix = f'{subdirective}:' if domain == 'std' else ''
		if projname == 'discord.py':
			key = key.replace('discord.ext.commands.', '').replace('discord.', '')
		result[f'{prefix}{key}'] = os.path.join(url, location)
	return result

async def build_rtfm_lookup_table(self):
	cache = {}
	for key, page in RTFM_PAGE_TYPES.items():
		cache[key] = {}
		async with self.bot.session.get(page + '/objects.inv') as resp:
			if resp.status != 200:
				raise RuntimeError('Cannot build rtfm lookup table, try again later.')
			stream = SphinxObjectFileReader(await resp.read())
			cache[key] = parse_object_inv(self, stream, page)
	self._rtfm_cache = cache

async def do_rtfm(self, interaction, key, obj):
	if obj is None and key == 'latest':
		e = discord.Embed(title="__**Discord.py Documentation Lookup**__", description=f'[Click to View the Discord.py Documentation](<https://discordpy.readthedocs.io/en/latest>)\nYou may also search for a Reference Point in the Documentation.\n`{Bot_Prefix}rtd <Reference Query>`', colour=discord.Colour.blurple(),  timestamp=datetime.now(), color=0xac5ece)
		try:
			e.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=e)
			return
		except:
			e.set_footer(text=f"{interaction.author}", icon_url=interaction.author.display_avatar.replace(format="png", static_format="png"))
			await interaction.send(embed=e)
			await interaction.message.delete()
			return
	if obj is None and key == 'stable':
		e = discord.Embed(title="__**Discord.py Documentation Lookup**__", description=f'[Click to View the Discord.py Documentation](<https://discordpy.readthedocs.io/en/stable>)\nYou may also search for a Reference Point in the Documentation.\n`{Bot_Prefix}rtd <Reference Query>`', colour=discord.Colour.blurple(),  timestamp=datetime.now(), color=0xac5ece)
		try:
			e.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=e)
			return
		except:
			e.set_footer(text=f"{interaction.author}", icon_url=interaction.author.display_avatar.replace(format="png", static_format="png"))
			await interaction.send(embed=e)
			await interaction.message.delete()
			return
	if obj is None and key == 'python':
		e = discord.Embed(title="__**Python Documentation Lookup**__", description=f'[Click to View the Python Documentation](<https://docs.python.org/3>)\nYou may also search for a Reference Point in the Documentation.\n`{Bot_Prefix}rtd py <Reference Query>`', colour=discord.Colour.blurple(),  timestamp=datetime.now(), color=0xac5ece)
		try:
			e.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			await interaction.followup.send(embed=e)
			return
		except:
			e.set_footer(text=f"{interaction.author}", icon_url=interaction.author.display_avatar.replace(format="png", static_format="png"))
			await interaction.send(embed=e)
			await interaction.message.delete()
			return
	if not hasattr(self, '_rtfm_cache'):
		await build_rtfm_lookup_table(self)
	obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)
	if key.startswith('latest'):
		q = obj.lower()
		for name in dir(discord.abc.Messageable):
			if name[0] == '_':
				continue
			if q == name:
				obj = f'abc.Messageable.{name}'
				break
	cache = list(self._rtfm_cache[key].items())

	def transform(tup):
		return tup[0]

	matches = finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]
	e = discord.Embed(colour=discord.Colour.blurple(),  timestamp=datetime.now(), color=0xac5ece)
	if key == 'latest' or key == 'stable':
		e.title = "__**Discord.py Documentation Lookup**__"
	if key == 'python':
		e.title = "__**Python Documentation Lookup**__"
	if len(matches) == 0:
		try:
			embed = discord.Embed(title="__**Lookup Error**__", description=f"Could not find any Results..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
			return await interaction.followup.send(embed=embed)
		except:
			embed = discord.Embed(title="__**Lookup Error**__", description=f"Could not find any Results..", timestamp=datetime.now(), color=0xff0000)
			embed.set_footer(text=f"{interaction.author}", icon_url=interaction.author.display_avatar.replace(format="png", static_format="png"))
			return await interaction.send(embed=embed)
	e.description = '\n'.join(f'[`{key}`]({url})' for key, url in matches)
	try:
		e.set_footer(text=f"{interaction.user}", icon_url=interaction.user.display_avatar.replace(format="png", static_format="png"))
		await interaction.followup.send(embed=e)
	except:
		e.set_footer(text=f"{interaction.author}", icon_url=interaction.author.display_avatar.replace(format="png", static_format="png"))
		await interaction.send(embed=e)
		await interaction.message.delete()

async def refresh_faq_cache(self):
	self.faq_entries = {}
	base_url = 'https://discordpy.readthedocs.io/en/latest/faq.html'
	async with self.bot.session.get(base_url) as resp:
		text = await resp.text(encoding='utf-8')
		root = etree.fromstring(text, etree.HTMLParser())
		nodes = root.findall(".//div[@id='questions']/ul[@class='simple']/li/ul//a")
		for node in nodes:
			self.faq_entries[''.join(node.itertext()).strip()] = base_url + node.get('href').strip()