from discord.ext import commands
import discord
import logging

from games.rps import RockPaperScissors
from games.hangman import Hangman
from games.guessanumber import GuessANumber
from games.blackjack import Blackjack
from games.EgyptianWar import EgyptianWar
from games.typewars import TypeWars

class GameManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # channel_id -> game

    # ---- TW comand ----
    @discord.app_commands.command(name="tw", description="Play TypeWars!")
    async def tw(self, interaction: discord.Interaction, opponent: discord.Member = None):
        players = [interaction.user] if not opponent else [interaction.user, opponent]
        game = TypeWars(players)
        self.active_games[interaction.channel_id] = game
        await interaction.response.send_message(game.start())

    # ---- TypeWars comand ----
    @discord.app_commands.command(name="typewars", description="Play TypeWars!")
    async def typewars(self, interaction: discord.Interaction, opponent: discord.Member = None):
        players = [interaction.user] if not opponent else [interaction.user, opponent]
        game = TypeWars(players)
        self.active_games[interaction.channel_id] = game
        await interaction.response.send_message(game.start())
    
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

    # ---- Blackjack command ----
    @discord.app_commands.command(name="blackjack", description="Play Blackjack with one or more members!!")
    async def blackjack(self, interaction: discord.Interaction, opponent: discord.Member = None):
        """
        Start a blackjack game.
        Usage:
          /blackjack                -> solo game vs dealer
          /blackjack @player1 ...   -> multiplayer game vs dealer
        """
        # Build player list
        if opponent:
            players = [interaction.user, opponent]
        else:
            players = [interaction.user]

        game = Blackjack(players)
        self.active_games[interaction.channel_id] = game

        # create a simple view with Hit/Stand buttons
        view = BlackjackView(game, self)
        await interaction.response.send_message(game.start(), view=view)

    @discord.app_commands.command(name="egyptian", description="Play Egyptian War with one or more members!")
    async def egyptian(self, interaction: discord.Interaction, opponent: discord.Member = None):
        await interaction.response.defer(thinking=False)
        try:
            if opponent:
                players = [interaction.user, opponent]
            else:
                players = [interaction.user]
            game = EgyptianWar(players)
            self.active_games[interaction.channel_id] = game
            view = EgyptianView(game, self)
            await interaction.followup.send(game.start(), view=view)
        except Exception:
            logging.exception("Failed to start Egyptian War")
            await interaction.followup.send("Failed to start game.", ephemeral=True)

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
                profiles_cog = self.bot.get_cog("Profiles")
                if profiles_cog and hasattr(game, "winner") and game.winner:
                    mode = getattr(game, "mode", "single" if len(game.players) == 1 else "multi")
                    duration = getattr(game, "duration", None)
                    word = getattr(game, "word", None)

                    await profiles_cog.record_typewars_result(
                        winner=game.winner,
                        mode=mode,
                        duration=duration,
                        word=word,
                    )

                self.end_game(channel_id)


        # if hasattr(game, "apply_action"):
        #     result = game.apply_action(message.author, message.content.strip())
        #     if result:
        #         await message.channel.send(result)

        #     if game.is_over():
        #         # If this is TypeWars and we have a winner, record their win
        #         if isinstance(game, TypeWars) and getattr(game, "winner", None) is not None:
        #             profiles_cog = self.bot.get_cog("Profiles")
        #             if profiles_cog:
        #                 # record win in leaderboard + profile
        #                 await profiles_cog.add_win(game.winner)

        #         self.end_game(channel_id)


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

# ---- Blackjack UI ---- 
class BlackjackView(discord.ui.View):
    def __init__(self, game, manager, timeout=120):
        super().__init__(timeout=timeout)
        self.game = game
        self.manager = manager
        # two buttons shared; view enforces per-player turn
        self.add_item(BlackjackButton("Hit", style=discord.ButtonStyle.primary, action="hit"))
        self.add_item(BlackjackButton("Stand", style=discord.ButtonStyle.secondary, action="stand"))

    async def on_timeout(self):
        # when view times out, remove active game if still present
        cid = None
        for k,v in list(self.manager.active_games.items()):
            if v is self.game:
                cid = k
                break
        if cid:
            self.manager.end_game(cid)
            try:
                # best-effort notification (ignore if message deleted)
                await self.message.channel.send("Blackjack timed out, game ended.")
            except Exception:
                pass

class BlackjackButton(discord.ui.Button):
    def __init__(self, label, style, action):
        super().__init__(label=label, style=style)
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        player = interaction.user
        # ensure there is a game registered for the channel
        channel_id = interaction.message.channel.id
        game = self.view.game
        manager = self.view.manager

        # validate it's the right player's turn
        valid_actions = game.get_valid_actions(player)
        if not valid_actions:
            await interaction.response.send_message("It's not your turn or no actions are available.", ephemeral=True)
            return
        if self.action not in valid_actions:
            await interaction.response.send_message("Action not allowed right now.", ephemeral=True)
            return

        result = game.apply_action(player, self.action)
        # ephemeral acknowledgement for the actor
        await interaction.response.send_message(result, ephemeral=True)

        # update the public game state every action
        try:
            await interaction.message.edit(content=game.render(), view=self.view)
        except Exception:
            # message may be deleted; ignore editing errors
            pass

        # if game finished, announce results and cleanup
        if game.is_over():
            try:
                await interaction.message.channel.send(game.render())
            except Exception:
                pass
            manager.end_game(channel_id)
            self.view.stop()

# ===== EGYPTIAN WAR ===== #

# in GameManager cog


class EgyptianView(discord.ui.View):
    def __init__(self, game, manager, timeout=120):
        super().__init__(timeout=timeout)
        self.game = game
        self.manager = manager
        self.add_item(FlipButton())

    async def on_timeout(self):
        cid = None
        for k, v in list(self.manager.active_games.items()):
            if v is self.game:
                cid = k
                break
        if cid:
            self.manager.end_game(cid)
            try:
                await self.message.channel.send("Egyptian War timed out, game ended.")
            except Exception:
                pass

class FlipButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Flip", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        player = interaction.user
        game = self.view.game
        manager = self.view.manager
        valid = game.get_valid_actions(player)
        if "flip" not in valid:
            await interaction.response.send_message("It's not your turn or you cannot flip.", ephemeral=True)
            return
        result = game.apply_action(player, "flip")
        await interaction.response.send_message(result, ephemeral=True)
        try:
            await interaction.message.edit(content=game.render(), view=self.view)
        except Exception:
            pass
        if game.is_over():
            try:
                await interaction.message.channel.send(game.render())
            except Exception:
                pass
            manager.end_game(interaction.message.channel.id)
            self.view.stop()

# ===== END EGYPTIAN WAR ====== #

async def setup(bot):
    print("Loading GameManager cog...")
    await bot.add_cog(GameManager(bot))
