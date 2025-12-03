class Game:
    def __init__(self, players):
        self.players = players  # list of discord.Member
        self.state = None       # game-specific state object
        self.current_turn = 0   # index into players

    def start(self):
        """Initialize game state and return opening message/embed."""
        raise NotImplementedError

    def get_valid_actions(self, player):
        """Return list of valid actions for the given player."""
        raise NotImplementedError

    def apply_action(self, player, action):
        """Update state based on action. Return result message/embed."""
        raise NotImplementedError

    def is_over(self):
        """Return True if game has ended."""
        raise NotImplementedError

    def render(self):
        """Return a string/embed representing the current state."""
        raise NotImplementedError