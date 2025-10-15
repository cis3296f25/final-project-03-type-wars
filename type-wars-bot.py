# import os

# import discord
# from discord.ext import commands

# import logging
# from dotenv import load_dotenv

# load_dotenv()
# TOKEN = os.getenv('DISCORD_TOKEN')


# bot = commands.Bot(command_prefix = '/', intents = intents)

# @bot.event
# async def on_ready():
#     print("Ready, {bot.user.name}!")

# bot.run(TOKEN, log_handler = handler, log_level = logging.debug )

# client = discord.Client()

# @client.event
# async def on_ready():
#     print(f'{client.user} has connected to Discord!')

# client.run(TOKEN)

# client = discord.Client(intents=discord.Intents.default())
# client.run(os.environ.get('DISCORD_TOKEN'))

# class Client(discord.Client):
#     async def on_ready(self):
#         print(f'Logged on as {self.user}!')

#     async def on_message(self, message):
#         print(f'Message from {message.author}: {message.content}')

# intents = discord.Intents.default()
# intents.message_content = True

# client = Client(intents = intents)

# client.run(DISCORD_TOKEN)
# 
# async def on_message(self, message):
#          print(f'Message from {message.author}: {message.content}')



from dotenv import load_dotenv
from discord.ext import commands
import discord
import os
import logging

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename ='discord.log', encoding ='utf-8', mode ='w')

# Enabling intents (must do this for every intent needed)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user.name}!")

@bot.event
async def on_message(message):
         print(f'Message from {message.author}: {message.content}')

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

