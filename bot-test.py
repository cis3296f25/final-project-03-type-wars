from dotenv import load_dotenv
from discord.ext import commands
from discord import app_commands
import discord
import os
import logging

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Enabling intents (must do this for every intent needed)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

bot.remove_command("help")

GUILD_ID = 1420829218882719848

# Dictionary to store active RPS games
# Key: channel_id, Value: dict with game state
active_games = {}

class RPSButton(discord.ui.Button):
    def __init__(self, choice: str):
        super().__init__(label=choice.capitalize(), style=discord.ButtonStyle.primary)
        self.choice = choice
    
    async def callback(self, interaction: discord.Interaction):
        channel_id = interaction.channel_id
        
        if channel_id not in active_games:
            await interaction.response.send_message("This game is no longer active!", ephemeral=True)
            return
        
        game = active_games[channel_id]
        
        # Check if the user is one of the players
        if interaction.user.id not in [game['player1'].id, game['player2'].id]:
            await interaction.response.send_message("You're not in this game!", ephemeral=True)
            return
        
        # Store the player's choice
        if interaction.user.id == game['player1'].id:
            if 'choice1' in game:
                await interaction.response.send_message("You've already made your choice!", ephemeral=True)
                return
            game['choice1'] = self.choice
            await interaction.response.send_message(f"You chose {self.choice}!", ephemeral=True)
        elif interaction.user.id == game['player2'].id:
            if 'choice2' in game:
                await interaction.response.send_message("You've already made your choice!", ephemeral=True)
                return
            game['choice2'] = self.choice
            await interaction.response.send_message(f"You chose {self.choice}!", ephemeral=True)
        
        # Check if both players have chosen
        if 'choice1' in game and 'choice2' in game:
            await announce_winner(interaction.channel, game)
            # Disable all buttons
            for item in self.view.children:
                item.disabled = True
            await game['message'].edit(view=self.view)
            del active_games[channel_id]

class RPSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # 3 minute timeout
        self.add_item(RPSButton("rock"))
        self.add_item(RPSButton("paper"))
        self.add_item(RPSButton("scissors"))

@bot.event
async def on_ready():
    print(f"Logged on as {bot.user.name}!")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')
    
    if message.author == bot.user:
        return
    
    if "poo" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} -- don't say that!!")

    await bot.process_commands(message)

async def announce_winner(channel, game):
    """Determine and announce the winner of RPS game"""
    player1 = game['player1']
    player2 = game['player2']
    choice1 = game['choice1']
    choice2 = game['choice2']
    
    result_embed = discord.Embed(title="Rock Paper Scissors - Results!", color=discord.Color.blue())
    result_embed.add_field(name=player1.display_name, value=choice1.capitalize(), inline=True)
    result_embed.add_field(name=player2.display_name, value=choice2.capitalize(), inline=True)
    
    # Determine winner
    if choice1 == choice2:
        result_embed.add_field(name="Result", value="It's a tie! 🤝", inline=False)
    elif (choice1 == 'rock' and choice2 == 'scissors') or \
         (choice1 == 'paper' and choice2 == 'rock') or \
         (choice1 == 'scissors' and choice2 == 'paper'):
        result_embed.add_field(name="Winner", value=f"{player1.mention} wins! 🎉", inline=False)
    else:
        result_embed.add_field(name="Winner", value=f"{player2.mention} wins! 🎉", inline=False)
    
    await channel.send(embed=result_embed)

@bot.command(name="hello", description="say hello!", guild=discord.Object(id=GUILD_ID))
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!!")

@bot.tree.command(name="play", description="Play rock paper scissors with another user", guild=discord.Object(id=GUILD_ID))
async def play(interaction: discord.Interaction, opponent: discord.Member):
    """Start a game with another player"""
    
    if opponent == interaction.user:
        await interaction.response.send_message("You can't play against yourself!", ephemeral=True)
        return
    
    if opponent.bot:
        await interaction.response.send_message("You can't play against a bot!", ephemeral=True)
        return
    
    # Check if there's already an active game in this channel
    if interaction.channel_id in active_games:
        await interaction.response.send_message("There's already an active game in this channel! Please wait for it to finish.", ephemeral=True)
        return
    
    # Create view with buttons
    view = RPSView()
    
    # Send the message
    await interaction.response.send_message(
        f"{interaction.user.mention} has challenged {opponent.mention} to Rock Paper Scissors!\n\n"
        f"Both players, click your choice below:",
        view=view
    )
    
    # Get the message to store it
    message = await interaction.original_response()
    
    # Create new game
    active_games[interaction.channel_id] = {
        'player1': interaction.user,
        'player2': opponent,
        'message': message
    }

@bot.command(name="help", description="list out all commands", guild=discord.Object(id=GUILD_ID))
async def help(ctx):
    x = discord.Embed(title="Help", description="type-wars prefix is '/': ")
    
    x.add_field(name="/tw", value="Activate single-player 'Type Wars' game", inline=False)
    x.add_field(name="/tw @user", value="Activate multiplayer 'Type Wars' game", inline=False)
    x.add_field(name="/play @user", value="Challenge another user to Rock Paper Scissors", inline=False)

    await ctx.send(embed=x)

bot.run(token, log_handler=handler, log_level=logging.DEBUG)