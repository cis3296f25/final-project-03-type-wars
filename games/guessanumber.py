from .game import Game
import random

class GuessANumber(Game):
    def __init__(self, players):
        super().__init__(players)
        self.number = random.randint(1, 10)
        self.guesses = {}

    def start(self):
        return (
            "🎲 Guess A Number started! "
            "I'm thinking of a number between 1 and 10. "
            "Type your guess!"
        )

    def get_valid_actions(self, player):
        return [str(i) for i in range(1, 11)]

    def apply_action(self, player, action):
        try:
            guess = int(action)
        except ValueError:
            return f"{player.display_name}, please enter a number between 1 and 10."

        if guess < 1 or guess > 10:
            return f"{player.display_name}, your guess must be between 1 and 10."

        self.guesses[player] = guess

        if guess == self.number:
            return f"🎉 {player.display_name} guessed it! The number was {self.number}."
        else:
            return f"{player.display_name} guessed {guess}. Try again!"

    def is_over(self):
        return any(guess == self.number for guess in self.guesses.values())

    def render(self):
        if self.guesses:
            guesses_str = ", ".join(
                f"{p.display_name}: {g}" for p, g in self.guesses.items()
            )
            return f"Current guesses: {guesses_str}"
        return "No guesses yet."
