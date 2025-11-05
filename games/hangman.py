# games/hangman.py
from .base import Game
import random

WORDS = ["python", "discord", "hangman", "bot", "programming"]

class Hangman(Game):
    def __init__(self, players):
        super().__init__(players)
        self.word = random.choice(WORDS)
        self.guessed = set()
        self.lives = 6

    def start(self):
        return f"Hangman started! Word: {self.render()} (lives: {self.lives})\nType a single letter to guess."

    def get_valid_actions(self, player):
        # Any single alphabetic character not already guessed
        return [c for c in "abcdefghijklmnopqrstuvwxyz" if c not in self.guessed]

    def apply_action(self, player, action):
        letter = action.lower()
        if not letter.isalpha() or len(letter) != 1:
            return "Please guess a single letter."

        if letter in self.guessed:
            return f"You already guessed '{letter}'."

        self.guessed.add(letter)

        if letter not in self.word:
            self.lives -= 1
            if self.lives <= 0:
                return f"❌ Wrong! No lives left. The word was **{self.word}**."
            return f"❌ Wrong! Lives left: {self.lives}\n{self.render()}"

        # Correct guess
        if all(c in self.guessed for c in self.word):
            return f"🎉 Correct! The word was **{self.word}**. You win!"
        return f"✅ Good guess!\n{self.render()} (lives: {self.lives})"

    def is_over(self):
        return self.lives <= 0 or all(c in self.guessed for c in self.word)

    def render(self):
        return " ".join(c if c in self.guessed else "_" for c in self.word)