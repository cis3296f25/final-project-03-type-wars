from dotenv import load_dotenv
from discord.ext import commands
from random_word import RandomWords
import discord
import os
import logging
import json
import time

#DictStorage
profiles = {}

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





@bot.command(name="typewars", description="Challenge someone to a typing duel!")
async def typewars(ctx):
    from random_word import RandomWords
    import time

    await ctx.send("Do you want to play against someone? (yes/no)")

    def check_reply(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        reply = await bot.wait_for("message", check=check_reply, timeout=15.0)
    except:
        await ctx.send("You didn’t respond in time. Game cancelled.")
        return

    if reply.content.lower() in ["yes", "y"]:
        await ctx.send("Tag the user you want to challenge (e.g., @username):")

        try:
            challenge_msg = await bot.wait_for("message", check=check_reply, timeout=15.0)
        except:
            await ctx.send("You didn’t tag anyone in time. Game cancelled.")
            return

        # Extract mentioned user
        if not challenge_msg.mentions:
            await ctx.send("You didn’t tag a valid user. Game cancelled.")
            return

        opponent = challenge_msg.mentions[0]
        await ctx.send(f"{opponent.mention}, you’ve been challenged to a typing duel by {ctx.author.mention}! Type `accept` to play or `decline` to skip.")

        def check_opponent(m):
            return m.author == opponent and m.channel == ctx.channel and m.content.lower() in ["accept", "decline"]

        try:
            response = await bot.wait_for("message", check=check_opponent, timeout=15.0)
        except:
            await ctx.send(f"{opponent.mention} didn’t respond. Game cancelled.")
            return

        if response.content.lower() == "decline":
            await ctx.send("Challenge declined. Maybe next time!")
            return

        await ctx.send("Challenge accepted! Get ready...")

        r = RandomWords()
        word = r.get_random_word()

        await ctx.send(f"Type this word as fast as you can: **{word}**")

        start_time = time.time()

        def check_winner(m):
            return m.channel == ctx.channel and m.content.strip().lower() == word.lower() and m.author in [ctx.author, opponent]

        try:
            winner_msg = await bot.wait_for("message", check=check_winner, timeout=10.0)
        except:
            await ctx.send("No one typed the word in time! No winner this round.")
            return

        end_time = time.time()
        speed = round(end_time - start_time, 2)
        await ctx.send(f"🏆 {winner_msg.author.mention} wins! They typed it in **{speed} seconds!**")

    else:
        # Single-player version
        r = RandomWords()
        word = r.get_random_word()
        await ctx.send(f"Type this word as fast as you can: **{word}**")

        start_time = time.time()

        def check_single(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await bot.wait_for("message", check=check_single, timeout=10.0)
        except:
            await ctx.send("⏰ Time’s up! You didn’t type in time.")
            return

        end_time = time.time()

        if msg.content.strip().lower() == word.lower():
            speed = round(end_time - start_time, 2)
            await ctx.send(f"Nice job {ctx.author.mention}! You typed it correctly in **{speed} seconds!**")
        else:
            await ctx.send(f"The correct word was **{word}**.")
bot.run(token, log_handler=handler, log_level=logging.DEBUG)


#ProfileManager
@bot.command(name="Create")
async def CreateProf(ctx, userID):
	await ctx.send("Enter Username")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	username = response.context
    #check to see if username already exists, print try again
	print(f"Your username {username} is Saved")
	
	await ctx.send("Enter Bio")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	bio = response.context
	print(f"Your Bio {bio} is Saved")
	
	await ctx.send("Enter Favorite Game")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	favGame = response.context
	print(f"Your Favorite Game {favGame} is Saved")
	
	profiles[userID] = {"username": username, "bio": bio, "fav game": favGame}
	print("Profile Saved")

async def EditUsername(ctx, userID):
	await ctx.send("Enter New Username")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	newUsername = response.context
	profiles[userID]["username"] = newUsername
	print("Your New Username {newUsername} is Saved")

async def EditBio(ctx, userID):
	await ctx.send("Enter New Bio")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	newBio = response.context
	profiles[userID]["bio"] = newBio
	print("Your New Bio {newBio} is Saved")

async def EditFavGame(ctx, userID):
	await ctx.send("Enter New Favorite Game")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	newGame = response.context
	profiles[userID]["fav game"] = newGame
	print("Your New Favorite Game {newGame} is Saved")

@bot.command(name="Delete")
async def DeleteProf(ctx, userID):
	username = profiles[userID].get("username")
	await ctx.send(f"Are you sure you want to delete this, {username}, entire profile?  yes/no")
	response = await bot.wait_for("message", check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
	if response.content.lower() in ["yes", "y"]:
		del profiles[userID]
		print("This profile has been deleted")
	elif response.content.ower() in ["no", "n"]:
		print(f"{username}’s profile was not deleted")

@bot.command(name="View")
async def ViewProf(ctx, userID):
	profile = profiles[userID]
	embed = discord.Embed(title=f"{profile['username']}’s Profile")
	#might have to add description above
	embed.add_field(name = "Bio: ", value = profile["bio"])
	embed.add_field(name = "Favorite Game: ", value = profile["fav game"])
	embed.add_field(name = "Stats: ", value = profile["stats"])

async def ViewOtherProf(username):
    #see how to see other users profile from username
	for IDs, profile in profiles.items():
		if profile["username"].lower() == username.lower():
			userID = IDs
			break
	ViewProf(userID)

async def parse(input):
	parts = input.strip().split()
	command = parts[0][1]
	if len(parts) > 1:
		attribute = parts[1]
	else:
		attribute = None
	return command, attribute


#CommandMenu
@bot.command(name="Profile")
async def profileMenu(ctx, interaction: discord.Interaction):
	userID = str(interaction.user.id)

	embed = discord.Embed(title="Profile Help Menu",  description="Commands to manage your profile")
	embed.add_field(name="/Create", value="Create your profile", inline=False)
	embed.add_field(name="/Edit Username", value="Edit your username", inline=False)
	embed.add_field(name="/Edit Bio", value="Edit your bio", inline=False)
	embed.add_field(name="/Edit FavGame", value="Edit your favorite game", inline=False)
	embed.add_field(name="/View", value="View our own profile", inline=False)
	embed.add_field(name="/View [username]", value="View others profiles using their username", inline=False)
	embed.add_field(name="/Delete", value="Delete your profile", inline=False)

    
	await interaction.response.send_message(embed=embed)
	try:
		msg = await bot.wait_for("message",check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel, timeout=30)
	except:
		await interaction.followup.send("Time has ran out", ephemeral=True)
		return
	response = msg.content.lower().strip()
	command, attribute = parse(response)

	if command == "create":
		if userID in profiles:
			print("User already has a profile")
		else:
			await CreateProf(userID)
	elif command == "view":
		if userID not in profiles:
			print("This user does not have a profile")
		else:
			await ViewProf(userID)
	elif command == "view" and attribute is not None:
		if userID not in profiles:
			print("This user does not have a profile")
		else:
			await ViewOtherProf(attribute)
	elif command == "delete":
		if userID not in profiles:
			print("User does not have a profile")
		else:
			await DeleteProf(userID)
	elif command == "edit" and attribute == "username":
		if userID not in profiles:
			print("User does not have a profile")
		else:
			await EditUsername(userID)
	elif command == "edit" and attribute == "bio":
		if userID not in profiles:
			print("User does not have a profile")
		else:
			await EditBio(userID)
	elif command == "edit" and attribute == "FavGame":
		if userID not in profiles:
			print("User does not have a profile")
		else:
			await EditFavGame(userID)
