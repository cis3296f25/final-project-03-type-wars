# games/hangman.py
from .game import Game
from random_word import RandomWords
import random
import re

# First letter can be upper or lower; everything after must be lowercase a–z.
WORD_PATTERN = re.compile(r"^[A-Za-z][a-z]*$")


class Hangman(Game):
    def __init__(self, players):
        super().__init__(players)
        self.r = RandomWords()
        self.word = self._get_valid_word()
        self.guessed = set()
        self.lives = 6  # number of wrong guesses allowed

    # -------- Word selection --------
    def _get_valid_word(self):
        """
        Keep asking RandomWords for a word until we get one that:
        - is a string
        - has no spaces or punctuation
        - matches: first char A–Z or a–z, remaining chars a–z only
        """
        for _ in range(100):
            w = self.r.get_random_word()

            if not isinstance(w, str):
                continue

            w = w.strip()
            if not w:
                continue

            # Must match the pattern exactly
            if WORD_PATTERN.fullmatch(w):
                return w.lower()

        # If the API keeps giving garbage, fall back to a safe list
        fallback = ["python", "discord", "hangman", "bot", "programming"]
        return random.choice(fallback)

    # -------- Game interface methods --------
    def start(self):
        # Wrap the word display in backticks so underscores don't get eaten by Markdown
        return (
            "**Hangman Game Started!**\n\n"
            f"`{self.render()}`\n"
            f"Attempts left: {self.lives}\n"
            "Type a single letter to guess."
        )

    def get_valid_actions(self, player):
        # Any not-yet-guessed a–z letter is “valid”, but we still validate in apply_action.
        return [chr(c) for c in range(ord("a"), ord("z") + 1) if chr(c) not in self.guessed]

    def apply_action(self, player, action):
        letter = action.strip().lower()

        # Basic input validation
        if len(letter) != 1 or not letter.isalpha():
            return "Please guess a **single letter** (a–z)."

        if letter in self.guessed:
            return f"You already guessed **{letter}**.\n`{self.render()}`"

        self.guessed.add(letter)

        # Wrong guess
        if letter not in self.word:
            self.lives -= 1
            if self.lives <= 0:
                return f"❌ Wrong! No lives left. The word was **{self.word}**."
            return f"❌ Wrong! Attempts left: {self.lives}\n`{self.render()}`"

        # Correct guess
        if all(c in self.guessed for c in self.word):
            return f"🎉 Correct! You guessed the word: **{self.word}**"

        return f"✅ Good guess!\n`{self.render()}` (Attempts left: {self.lives})"

    def is_over(self):
        return self.lives <= 0 or all(c in self.guessed for c in self.word)

    def render(self):
        # Underscores for unguessed letters, letters revealed when guessed
        return " ".join(c if c in self.guessed else "_" for c in self.word)
