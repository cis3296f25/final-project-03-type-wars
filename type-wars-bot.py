from dotenv import load_dotenv
from discord.ext import commands
from random_word import RandomWords
from tournament import setup as setup_tournament
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
setup_tournament(bot)
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





@bot.command(name="win", description="Report that you won your match")
async def win(ctx):
    ok, result = tournaments.report(ctx.guild.id, ctx.author.name)
    if not ok:
        await ctx.send(result)
        return
    if isinstance(result, str):
        await ctx.send(result)
        return
    matches = result
    text = "**Next Round Matches:**\n"
    for m in matches:
        if m.player2:
            text += f"🔹 {m.player1} vs {m.player2}\n"
        else:
            text += f"🔸 {m.player1} gets a bye\n"
    await ctx.send(text)



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

bot.run(token, log_handler=handler, log_level=logging.DEBUG)

