import os

import discord
from discord.ext import commands

import logging
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename = 'discord.log', encoding = 'utf-8', mode ='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '/', intents = intents)

@bot.event
async def on_ready():
    print("Ready, {bot.user.name}!")

bot.run(TOKEN, log_handler = handler, log_level = logging.debug )

# client = discord.Client()

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

# client.run(TOKEN)