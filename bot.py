from dotenv import load_dotenv
from discord.ext import commands
import discord
import os
import logging

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Load cogs
initial_extensions = ["cogs.games"]

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user.name}!")

if __name__ == "__main__":
    for ext in initial_extensions:
        bot.load_extension(ext)

    bot.run(token, log_handler=handler, log_level=logging.DEBUG)