import discord
import easy_pil
import io
import numpy
from captcha.audio import AudioCaptcha
from captcha.image import ImageCaptcha
from easy_pil import Editor, Canvas, load_image_async, Font
from Utils.Helpers import create_random_string



async def create_ascii_art(file, scale=.1, gray_scale=.1, width_correction=7/4):
	chars = numpy.asarray(list(' .,:;irsXA253hMHGS#9B&@'))
	img = await load_image_async(str(file))
	img_size = ( round(img.size[0]*scale*width_correction), round(img.size[1]*scale) )
	img = numpy.sum( numpy.asarray( img.resize(img_size) ), axis=2)
	img -= img.min()
	img = (1.0 - img/img.max())**gray_scale*(chars.size-1)
	result = "\n".join( ("".join(r) for r in chars[img.astype(int)]) )
	
	return result

async def create_captcha(param):
	image = ImageCaptcha(width=280, height=80) #fonts=['public/css/fonts/Clip.ttf'])
	image_object = image.generate(param)
	file = discord.File(fp=image_object, filename="CAPTCHA.png")
	files = [file]
	if not param.isnumeric():
		audio = AudioCaptcha(voicedir='public/sounds/characters')
		audio_object = audio.generate(param)
		audio_file = discord.File(fp=io.BytesIO(audio_object), filename="CAPTCHA.wav")
		files = [file, audio_file]
	if param.isnumeric():
		audio = AudioCaptcha()
		audio_object = audio.generate(param)
		audio_file = discord.File(fp=io.BytesIO(audio_object), filename="CAPTCHA.wav")
		files = [file, audio_file]

	return files

async def make_rank_card(exp, lvl, rank, member, global_rank=False):
	next_level_xp = (lvl+1)**4
	current_level_xp = lvl**4
	xp_need = next_level_xp - current_level_xp
	xp_have = exp - current_level_xp
	percentage = (xp_have/xp_need)*100

	""" Rank Card Creation """

	# Grab Assets
	background = Editor("public/images/assets/Background.jpg").resize((900, 300))
	pfp = await load_image_async(str(member.display_avatar.url))
	avatar = Editor(pfp).resize((250, 250)).circle_image()

	# Grab Font(s)
	clip_large = Font("public/css/fonts/Clip.ttf").poppins(size=50)
	clip = Font("public/css/fonts/Clip.ttf").poppins(size=40)
	clip_small = Font("public/css/fonts/Clip.ttf").poppins(size=30)

	# Add Avatar to Background
	background.paste(avatar.image, (10, 25))

	# Level Percentage
	background.rectangle((240, 220), width=650, height=40, fill="white", radius=20)
	background.bar((240, 220), max_width=650, height=40, percentage=percentage, fill="#0cf569", radius=20)
	background.text((625, 265), f"{exp} / {(lvl+1)**4} XP", font=clip_small, color="#0cf569")

	# Spacer (Below Rank Information)
	background.rectangle((465, 75), width=420, height=2, fill="#0cf569")

	# User & Rank Information
	background.text((260, 175), str(member), font=clip, color="#22c9c7")
	background.text((480, 30), f"Rank: {rank}  Level: {lvl}", font=clip, color="#22c9c7")

	if global_rank is True: # Add Global Rank Information
		background.text((280, 55), "Global", font=clip_large, color="#0cf569")

	# Convert into Discord File
	file = discord.File(fp=background.image_bytes, filename="Rank-Card.png")

	return file

async def make_welcome_card(member, position="N/A"):

	""" Welcome Card Creation """

	# Grab Assets
	background = Editor("public/images/assets/Background.jpg").resize((900, 300))
	pfp = await load_image_async(str(member.display_avatar.url))
	avatar = Editor(pfp).resize((200, 200)).circle_image()

	# Grab Font(s)
	clip_large = Font("public/css/fonts/Clip.ttf").poppins(size=50)
	clip = Font("public/css/fonts/Clip.ttf").poppins(size=40)
	clip_small = Font("public/css/fonts/Clip.ttf").poppins(size=30)

	# Add Avatar to Background
	background.paste(avatar.image, (350, 10))

	# Member Info
	if len(str(member)) < 15:
		background.text((90, 220), f"{str(member)} just joined the server", font=clip, color="#22c9c7")
	if len(str(member)) >= 15:
		background.text((10, 220), f"{str(member)} just joined the server", font=clip, color="#22c9c7")
	background.text((350, 275), f"Member #{position}", font=clip_small, color="#0cf569")

	# Convert into Discord File
	file = discord.File(fp=background.image_bytes, filename="Welcome-Card.png")

	return file