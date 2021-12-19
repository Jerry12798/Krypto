import time
import pytz
import random
import string
from datetime import datetime, timedelta
from pytz import timezone



def server_stats(guild):
	online = 0
	offline = 0
	idle = 0
	dnd = 0

	for m in guild.members:
		if str(m.status) == "online":
				online += 1
		elif str(m.status) == "offline":
				offline += 1
		elif str(m.status) == "idle":
				idle += 1
		elif str(m.status) == "dnd":
				dnd += 1
	return online, idle, offline, dnd

def convert_seconds(time):
	future = time.lower()
	current = datetime.now()
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
	return fix

def create_random_string(length):
	letters = string.ascii_lowercase
	result = "".join(random.choice(letters) for i in range(length))
	return result

def create_random_digits(length):
	digits = string.digits
	result = "".join(random.choice(digits) for i in range(length))
	return result