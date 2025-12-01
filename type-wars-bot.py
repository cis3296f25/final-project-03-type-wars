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

#DictStorage
profiles = {}

if os.path.exists("profiles.json"):
    with open("profiles.json", "r") as f:
        profiles = json.load(f)

#save function for profiles to json file
def saveProfiles():
    with open("profiles.json", "w") as f:
        json.dump(profiles, f, indent=4)

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
    global users
    print(f"Logged on as {bot.user.name}!")
    try:
        with open("leaderboard.json", 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
        print("No win data file found. Starting with empty win data.")

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
            await add_win(ctx)

        else:
            await ctx.send(f"The correct word was **{word}**.")

@bot.command(name = "wins", description = "Check how many wins you have")
async def wins(ctx):

    id = str(ctx.author.id)

    if id not in users:
        await ctx.send("❓ You haven't played yet! Play some games to see your score! ")
    else:
        await ctx.send("🎖️  You have {} win(s) in TypeWars!".format(users[id]))


async def add_win(ctx):

    id = str(ctx.author.id)

    if id not in users:
        users[id] = 0

    users[id] += 1
    save_data()

async def save_data():
    global users
    with open("leaderboard.json", 'w') as f:
        json.dump(users, f, indent=2)

@bot.tree.command(name="hangman", description="Play a game of Hangman!")
async def hangman(interaction: discord.Interaction):
    r = RandomWords()
    word = r.get_random_word()
    if not word or not word.isalpha():
        await interaction.response.send_message("Couldn't get a valid word. Try again.")
        return

    word = word.lower()
    guessed_letters = []
    max_attempts = 6
    attempts_left = max_attempts

    def display_word():
        return " ".join([letter if letter in guessed_letters else "_" for letter in word])

    await interaction.response.send_message(
        f"**Hangman Game Started!**\n\n{display_word()}\nAttempts left: {attempts_left}"
    )

    def check_guess(m):
        return (
            m.author == interaction.user
            and m.channel == interaction.channel
            and len(m.content) == 1
            and m.content.isalpha()
        )

    while attempts_left > 0:
        try:
            guess_msg = await bot.wait_for("message", check=check_guess, timeout=30.0)
        except:
            await interaction.followup.send("⏰ Time’s up! Game over.")
            return

        guess = guess_msg.content.lower()

        if guess in guessed_letters:
            await interaction.followup.send(
                f"You already guessed **{guess}**!\n{display_word()}"
            )
            continue

        guessed_letters.append(guess)

        if guess in word:
            await interaction.followup.send(f"✅ Correct! {display_word()}")

            if all(letter in guessed_letters for letter in word):
                await interaction.followup.send(
                    f"🎉 Congrats {interaction.user.mention}! You guessed the word: **{word}**"
                )
                return

        else:
            attempts_left -= 1
            await interaction.followup.send(
                f"❌ Wrong guess! Attempts left: {attempts_left}\n{display_word()}"
            )

    await interaction.followup.send(f"💀 Game over! The word was **{word}**.")

#save function for profiles to json file
def saveProfiles():
    with open("profiles.json", "w") as f:
        json.dump(profiles, f, indent=4)


#Profile Feature
#ProfileManager
@bot.command(name="create", description="Create your profile", guild=GUILD_ID)
async def create(ctx):
    userID = str(ctx.author.id)
    #check if ID user exists already, if not say profile already exists and close func/command
    if userID in profiles:
        await ctx.send("User already has a profile")
    else:
        await ctx.send("Enter Username")
        response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
        #check the response and why it isn't working
        username = response.content
        #check to see if username already exists, print try again
        await ctx.send(f"Your username {username} is Saved")
       
        await ctx.send("Enter Bio")
        response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
        bio = response.content
        await ctx.send(f"Your Bio {bio} is Saved")
       
        await ctx.send("Enter Favorite Game")
        response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
        favgame = response.content
        await ctx.send(f"Your Favorite Game {favgame} is Saved")
       
        profiles[userID] = {"username": username, "bio": bio, "favgame": favgame}
        saveProfiles()
        await ctx.send("Profile Saved")


@bot.command(name="edit", description="Edit your profile", guild=GUILD_ID)
async def edit(ctx):
    #get ID
    userID = str(ctx.author.id)
    #check if profile exists
    if userID not in profiles:
        await ctx.send("User does not have a profile to edit")
    #ask user what they want to edit, parse it
    else:
        await ctx.send(f"What do you want to edit in your profile? Type: username, bio, OR fav game")
        response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
        #use if/else to call funcs
        choice = response.content.lower()
        if choice == "username":
            await EditUsername(ctx, userID)
        elif choice == "bio":
            await EditBio(ctx, userID)
        elif choice == "favgame":
            await EditFavGame(ctx, userID)
        else:
            await ctx.send("This is an invalid option")


async def EditUsername(ctx, userID):
    await ctx.send("Enter New Username")
    response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
    newUsername = response.content
    profiles[userID]["username"] = newUsername
    saveProfiles()
    await ctx.send("Your New Username {newUsername} is Saved")


async def EditBio(ctx, userID):
    await ctx.send("Enter New Bio")
    response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
    newBio = response.content
    profiles[userID]["bio"] = newBio
    saveProfiles()
    await ctx.send("Your New Bio {newBio} is Saved")


async def EditFavGame(ctx, userID):
    await ctx.send("Enter New Favorite Game")
    response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
    newGame = response.content
    profiles[userID]["favgame"] = newGame
    saveProfiles()
    await ctx.send("Your New Favorite Game {newGame} is Saved")


@bot.command(name="delete", description="Delete your entire profile", guild=GUILD_ID)
async def delete(ctx):
    userID = str(ctx.author.id)
    #check if user profile exists, try and use if/else from profile func


    if userID not in profiles:
            await ctx.send("User does not have a profile to delete")
    else:
        username = profiles[userID].get("username")
        await ctx.send(f"Are you sure you want to delete this, {username}, entire profile?  yes/no")
        response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)
        if response.content.lower() in ["yes", "y"]:
            del profiles[userID]
            saveProfiles()
            await ctx.send("This profile has been deleted")
        elif response.content.lower() in ["no", "n"]:
            await ctx.send(f"{username}’s profile was not deleted")


@bot.command(name="view", description="View your profile", guild=GUILD_ID)
async def view(ctx):
    userID = str(ctx.author.id)
    await ctx.send("Do you want to view your profile OR another user? type: mine OR (username)")
    response = await bot.wait_for("message", timeout=30, check=lambda msg: msg.author == ctx.author and msg.channel==ctx.channel)


    user = response.content.strip()
    if user.lower() == "mine":
        print("calling view profile")
        await ViewProfile(ctx, userID)
        return
    elif user != "mine":
        username = response.content.strip()
        print("calling view other prof")
        await ViewOtherProf(ctx, username)
        return
    #else:
        #await ctx.send("That is an invalid username")
    #call the funcs, use right arguements/parameters

async def ViewProfile(ctx, userID):
    print("in profile")
    if userID not in profiles:
        await ctx.send("You don't have a profile yet!")
        return
    profile = profiles[userID]


    embed = discord.Embed(title=f"{profile['username']}’s Profile")
    embed.add_field(name="Bio: ", value=profile["bio"], inline=False)
    embed.add_field(name="Favorite Game: ", value=profile["favgame"], inline=False)
    #embed.add_field(name = "Stats: ", value = profile["stats"])


    await ctx.send(embed=embed)


async def ViewOtherProf(ctx, username):
    #see how to see other users profile from username
    userID = None
    username = username.strip().replace("@", "")


    for IDs, profile in profiles.items():
        if profile["username"].lower() == username:
            userID = IDs
            break
    #if not in the profiles list, say user does not have a profile
    if userID is None:
        await ctx.send("This user does not have a profile")
    else:
        await ViewProfile(ctx, userID)


#CommandMenu
@bot.command(name="profile", description="View Commands to Manage Profiles", guild=GUILD_ID)
async def profile(ctx):
    userID = str(ctx.author.id)


    embed = discord.Embed(title="Profile Help Menu",  description="Commands to manage your profile")
    embed.add_field(name="/create", value="Create your profile", inline=False)
    embed.add_field(name="/edit", value="Edit your username, bio, or favorite game", inline=False)
    embed.add_field(name="/view", value="View our own profile or other users", inline=False)
    embed.add_field(name="/delete", value="Delete your profile", inline=False)


   
    await ctx.send(embed=embed)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

