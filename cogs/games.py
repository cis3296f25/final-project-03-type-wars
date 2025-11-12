from discord.ext import commands
import discord

from games.rps import RockPaperScissors
from games.hangman import Hangman
from games.guessanumber import GuessANumber


class GameManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # channel_id -> game

    # ---- RPS command ----
    @discord.app_commands.command(name="rps", description="Play Rock Paper Scissors against another member!")
    async def rps(self, interaction: discord.Interaction, opponent: discord.Member):
        game = RockPaperScissors([interaction.user, opponent])
        self.active_games[interaction.channel_id] = game

        view = RPSView(game, self)
        await interaction.response.send_message(game.start(), view=view)

    # ---- Hangman command ----
    @discord.app_commands.command(name="hangman", description="Start a game of Hangman!")
    async def hangman(self, interaction: discord.Interaction):
        game = Hangman([interaction.user])
        self.active_games[interaction.channel_id] = game
        await interaction.response.send_message(game.start())

    # ---- Guess a Number command ----
    @discord.app_commands.command(name="gan", description="Guess a number between 1 and 10!")
    async def guess_a_number(self, interaction: discord.Interaction):
        game = GuessANumber([interaction.user])
        self.active_games[interaction.channel_id] = game
        await interaction.response.send_message(game.start())

    # ---- Cleanup helper ----
    def end_game(self, channel_id):
        if channel_id in self.active_games:
            del self.active_games[channel_id]

    # ---- Listener for text input (single-player text games) ----
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        if channel_id not in self.active_games:
            return

        game = self.active_games[channel_id]

        # Only handle text-based games (Hangman, GuessANumber, etc.)
        # Any game that uses apply_action for message content
        if hasattr(game, "apply_action"):
            result = game.apply_action(message.author, message.content.strip())
            if result:
                await message.channel.send(result)

            if game.is_over():
                self.end_game(channel_id)

# ---- RPS Button UI ----
class RPSView(discord.ui.View):
    def __init__(self, game, manager):
        super().__init__(timeout=30)
        self.game = game
        self.manager = manager
        for choice in game.choices:
            self.add_item(RPSButton(choice, game, manager))

class RPSButton(discord.ui.Button):
    def __init__(self, choice, game, manager):
        super().__init__(label=choice.capitalize(), style=discord.ButtonStyle.primary)
        self.choice = choice
        self.game = game
        self.manager = manager

    async def callback(self, interaction: discord.Interaction):
        player = interaction.user
        if player not in self.game.players:
            await interaction.response.send_message("You're not in this game!", ephemeral=True)
            return

        result = self.game.apply_action(player, self.choice)
        await interaction.response.send_message(result, ephemeral=True)

        if self.game.is_over():
            final = getattr(self.game, "resolve", lambda: "Game over!")()
            await interaction.message.channel.send(final)
            self.manager.end_game(interaction.message.channel.id)
            self.view.stop()

async def setup(bot):
    print("Loading GameManager cog...")
    await bot.add_cog(GameManager(bot))
