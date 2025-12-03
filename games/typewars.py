# # games/typewars.py
# from .game import Game
# from random_word import RandomWords
# import time


# class TypeWars(Game):
#     def __init__(self, players):
#         super().__init__(players)
#         self.r = RandomWords()
#         self.word = self._get_word()
#         self.start_time = None
#         self.winner = None

#     # ---- Helpers ----
#     def _get_word(self):
#         try:
#             w = self.r.get_random_word()
#             if w and w.isalpha():
#                 return w.lower()
#         except Exception:
#             pass
#         # fallback
#         return "typing"

#     # ---- Required Interface ----
#     def start(self):
#         self.start_time = time.time()
#         if len(self.players) == 1:
#             mode = f"{self.players[0].mention}, type the word as fast as you can!"
#         else:
#             mode = (
#                 f"{self.players[0].mention} vs {self.players[1].mention}!\n"
#                 f"First to type the word wins!"
#             )

#         return (
#             f"⌨ **TYPE WARS!** ⌨\n"
#             f"{mode}\n\n"
#             f"Type this word: **{self.word}**"
#         )

#     def get_valid_actions(self, player):
#         # Any message content is acceptable — GameManager passes all text
#         return ["any"]

#     def apply_action(self, player, action):
#         # player typed something
#         msg = action.strip().lower()

#         if msg != self.word:
#             # Wrong → ignore silently
#             return None

#         # Correct
#         if not self.winner:
#             self.winner = player
#             time_taken = round(time.time() - self.start_time, 2)
#             return (
#                 f"🏆 {player.mention} wins Type Wars!\n"
#                 f"⏱ Time: **{time_taken} seconds**"
#             )

#         return None  # Game already ended

#     def is_over(self):
#         return self.winner is not None

#     def render(self):
#         if self.winner:
#             return f"Winner: {self.winner.mention} (word was **{self.word}**)"
#         return f"Type this word: **{self.word}**"

# games/typewars.py
from .game import Game
from random_word import RandomWords
import time


class TypeWars(Game):
    def __init__(self, players):
        super().__init__(players)
        self.r = RandomWords()
        self.word = self._get_word()
        self.start_time = None
        self.winner = None
        self.duration = None  # <-- add this
        self.mode = "single" if len(players) == 1 else "multi"  # <-- add this

    def _get_word(self):
        # your filtered word logic here
        w = self.r.get_random_word()
        if not w:
            return "typing"
        return w.lower()

    def start(self):
        self.start_time = time.time()  # <-- start timing here

        if len(self.players) == 1:
            mode = f"{self.players[0].mention}, type the word as fast as you can!"
        else:
            mode = (
                f"{self.players[0].mention} vs {self.players[1].mention}!\n"
                f"First to type the word wins!"
            )

        return (
            "⌨ **TYPE WARS!** ⌨\n"
            f"{mode}\n\n"
            f"Type this word: **{self.word}**"
        )

    def get_valid_actions(self, player):
        return ["any"]

    def apply_action(self, player, action):
        msg = action.strip().lower()

        if msg != self.word:
            return None  # ignore wrong guesses

        # First correct winner
        if not self.winner:
            self.winner = player
            if self.start_time is not None:
                self.duration = round(time.time() - self.start_time, 2)
            else:
                self.duration = None

            if self.duration is not None:
                return (
                    f"🏆 {player.mention} wins Type Wars!\n"
                    f"⏱ Time: **{self.duration} seconds**"
                )
            else:
                return f"🏆 {player.mention} wins Type Wars!"

        return None

    def is_over(self):
        return self.winner is not None

    def render(self):
        if self.winner:
            return f"Winner: {self.winner.mention} (word was **{self.word}**)"
        return f"Type this word: **{self.word}**"
