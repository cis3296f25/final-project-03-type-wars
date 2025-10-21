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

bot = commands.Bot(command_prefix='/', intents=intents)

bot.remove_command("help")

GUILD_ID = discord.Object(id=1420829218882719848)

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user.name}!")

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    
    if message.author == bot.user:
        return
    
    if "poo" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} -- don't say that!!")

    await bot.process_commands(message)
       
@bot.command(name = "hello", description= "say hello!", guild = GUILD_ID)
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!!")


@bot.command(name = "help", description = "list out all commands", guild = GUILD_ID)
async def help(ctx):
    x = discord.Embed(title = "Help", description= "type-wars prefix is '/': ")
    
    x.add_field(name = "/tw", value = "Activate single-player 'Type Wars' game")
    x.add_field(name = "/tw @user", value = "Activate multiplayer 'Type Wars' game")

    await ctx.send(embed = x)


bot.run(token, log_handler=handler, log_level=logging.DEBUG)

