# games/rps.py

from .base import Game

class RockPaperScissors(Game):
    def __init__(self, players):
        super().__init__(players)
        self.choices = ["rock", "paper", "scissors"]
        self.moves = {}

    def start(self):
        return "Rock Paper Scissors started! Each player, make your choice."

    def get_valid_actions(self, player):
        return self.choices

    def apply_action(self, player, action):
        self.moves[player] = action
        if len(self.moves) == len(self.players):
            return "All players have chosen."#self.resolve()
        return f"{player.display_name} has chosen. Waiting for others..."

    def resolve(self):
        p1, p2 = self.players
        c1, c2 = self.moves[p1], self.moves[p2]
        if c1 == c2:
            return f"Both chose {c1}. It's a draw!"
        if (c1 == "rock" and c2 == "scissors") or \
           (c1 == "scissors" and c2 == "paper") or \
           (c1 == "paper" and c2 == "rock"):
            return f"{p1.display_name} wins! {c1} beats {c2}."
        return f"{p2.display_name} wins! {c2} beats {c1}."

    def is_over(self):
        return len(self.moves) == len(self.players)

    def render(self):
        return f"Moves so far: {', '.join([p.display_name for p in self.moves])}"

# from .base import Game
# import random

# class RockPaperScissors(Game):
#     def __init__(self, players):
#         super().__init__(players)
#         self.choices = ["rock", "paper", "scissors"]

#     def start(self):
#         return "Game started! Choose rock, paper, or scissors."

#     def get_valid_actions(self, player):
#         return self.choices

#     def apply_action(self, player, action):
#         # store player’s choice
#         if not hasattr(self, "moves"):
#             self.moves = {}
#         self.moves[player] = action

#         if len(self.moves) == len(self.players):
#             return self.resolve()
#         return f"{player} has chosen. Waiting for others..."

#     def resolve(self):
#         p1, p2 = self.players
#         c1, c2 = self.moves[p1], self.moves[p2]
#         if c1 == c2:
#             return f"Both chose {c1}. It's a draw!"
#         if (c1 == "rock" and c2 == "scissors") or \
#            (c1 == "scissors" and c2 == "paper") or \
#            (c1 == "paper" and c2 == "rock"):
#             return f"{p1} wins! {c1} beats {c2}."
#         return f"{p2} wins! {c2} beats {c1}."

#     def render(self):
#         return f"Moves so far: {self.moves}"