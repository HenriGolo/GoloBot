#!/usr/bin/python3

import discord
import time, datetime
import subprocess
import inspect
from os import environ

intents = discord.Intents.all()
bot = discord.Bot(intents=intents)
logs = open('logs/logs_dev.txt', 'a')

@bot.event
async def on_ready():
	currentTime = datetime.datetime.strptime(time.ctime(),"%c")
	for guild in bot.guilds:
		if guild.id == 664006363508244481:
			continue
		await guild.system_channel.send("Joyeux Noël :partying_face:")
		logs.write(f"\n{currentTime} Joyeux Noël souhaité dans {guild}\n")
	await bot.close()

# bot launch
bot.run(token=environ['token'])
logs.close()
