from discord.ext import commands
import discord

from games.rps import RockPaperScissors
from games.hangman import Hangman

class GameManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # channel_id -> game

    @commands.command(name="rps")
    async def rps(self, ctx, opponent: discord.Member):
        # Create game
        game = RockPaperScissors([ctx.author, opponent])
        self.active_games[ctx.channel.id] = game

        # Send intro message with buttons
        view = RPSView(game, self)
        await ctx.send(game.start(), view=view)

    def end_game(self, channel_id):
        if channel_id in self.active_games:
            del self.active_games[channel_id]
    
    @commands.command(name="hangman")
    async def hangman(self, ctx):
        game = Hangman([ctx.author])
        self.active_games[ctx.channel.id] = game
        await ctx.send(game.start())
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        channel_id = message.channel.id
        if channel_id in self.active_games:
            game = self.active_games[channel_id]

            # Only handle Hangman guesses for now
            if isinstance(game, Hangman):
                result = game.apply_action(message.author, message.content.strip())
                await message.channel.send(result)

                if game.is_over():
                    self.end_game(channel_id)

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

##### CALLBACK VERSIONS #####

async def callback(self, interaction: discord.Interaction):
    player = interaction.user
    if player not in self.game.players:
        await interaction.response.send_message("You're not in this game!", ephemeral=True)
        return

    result = self.game.apply_action(player, self.choice)
    await interaction.response.send_message(result, ephemeral=True)

    if self.game.is_over():
        final = self.game.resolve()
        await interaction.message.channel.send(final)
        self.manager.end_game(interaction.message.channel.id)
        self.view.stop()

    # async def callback(self, interaction: discord.Interaction):
    #     player = interaction.user
    #     if player not in self.game.players:
    #         await interaction.response.send_message("You're not in this game!", ephemeral=True)
    #         return

    #     result = self.game.apply_action(player, self.choice)
    #     await interaction.response.send_message(result, ephemeral=True)

    #     if self.game.is_over():
    #         final = self.game.resolve()
    #         await interaction.message.channel.send(final)
    #         self.manager.end_game(interaction.message.channel.id)
    #         self.view.stop()

##### END #####

async def setup(bot):
    await bot.add_cog(GameManager(bot))