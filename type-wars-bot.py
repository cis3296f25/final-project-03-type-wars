from dotenv import load_dotenv
from discord.ext import commands
from random_word import RandomWords
import discord
import os
import logging
import json
import time

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename ='discord.log', encoding ='utf-8', mode ='w')

# Enabling intents (must do this for every intent needed)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot.remove_command("help")

# Code for a multi-page help menu...in progress
# help_menu = json.load(open("help.json"))

# def createHelpEmbed(pageNum=0, inline=False):
#     pageTitle = list(help_menu)[pageNum]
#     embed=discord.embed(color=0x0080ff, title=pageTitle)
#     for key, val in help_menu[pageTitle].items():
#         embed.set_footer(text=f"Page {pageNum+1} of {len(list(help_menu))}")
#     return embed

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
    # await ctx.send(embed=createHelpEmbed)
    embed = discord.Embed(title = "Help", description= "Type-Wars uses the '/' prefix: ")
    
    embed.add_field(name = "/tw", value = "Activate single-player 'Type Wars' game")
    embed.add_field(name = "/tw @user", value = "Activate multiplayer 'Type Wars' game")



    await ctx.send(embed = embed)


@bot.command(name="typewars", description="Test your typing speed!", guild=GUILD_ID)
async def typewars(ctx):
	from random_word import RandomWords
	import time
	
	r = RandomWords()
	word = r.get_random_word()
	
	await ctx.send(f" Type this word as fast as you can **{word}**")

	start_time = time.time()

	def check(m):
		return m.author == ctx.author and m.channel == ctx.channel

	try:
		msg= await bot.wait_for("message", check=check, timeout=10.0)
	except:
		await ctx.seed("Times up! Didnt type in time")
		return

	end_time=time.time()

	if msg.content.strip().lower() == word.lower():
		speed = round(end_time - start_time, 2)
		await ctx.send(f" Nice job{ctx.author.mention}! You typed it correct in **{speed} seconds**!")
	else: 
		await ctx.send(f"The correct word was **{word}**.")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

