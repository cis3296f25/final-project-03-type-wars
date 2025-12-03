import random
from .game import Game

RANKS = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]
SUITS = ["♠","♥","♦","♣"]

def new_deck():
    return [r + s for r in RANKS for s in SUITS]

def card_value(rank):
    if rank in ("J","Q","K"):
        return 10
    if rank == "A":
        return 11  # treat as 11 by default; adjust later
    return int(rank)

def hand_value(cards):
    # cards are like "A♠", "10♦", "J♣"
    total = 0
    aces = 0
    for c in cards:
        rank = c[:-1]
        v = card_value(rank)
        total += v
        if rank == "A":
            aces += 1
    # reduce aces from 11 -> 1 as needed
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

class Blackjack(Game):
    """
    Multiplayer blackjack vs dealer. Players join by starting the game via command.
    Turn order follows the players list. Bets are not implemented (no currency).
    Usage pattern:
      - instantiate with players (list of discord.Member)
      - call start() to get intro text
      - game manager must drive player actions via apply_action(player, action)
        where action is one of: "hit", "stand"
    """

    def __init__(self, players):
        super().__init__(players)
        self.deck = new_deck()
        random.shuffle(self.deck)
        self.hands = {p: [] for p in players}
        self.dealer = []
        self.current_turn = 0  # index into self.players
        self.stage = "dealing"  # dealing -> player_turns -> dealer -> finished
        self.results = None

        # deal
        for _ in range(2):
            for p in players:
                self.hands[p].append(self.deck.pop())
            self.dealer.append(self.deck.pop())
        # if any player has blackjack immediately we'll resolve on demand

# ===== BLACKJACK TESTING ===== #

    # def start(self):
    #     lines = []
    #     lines.append("Blackjack started! Players vs Dealer.")
    #     for p in self.players:
    #         lines.append(f"**{p.display_name}**: {', '.join(self.hands[p])}  ({hand_value(self.hands[p])})")
    #     lines.append(f"Dealer: {self.dealer[0]}, [hidden]")
    #     lines.append(self._turn_prompt())
    #     return "\n".join(lines)

    def start(self):
        lines = []
        lines.append("Blackjack started! Players vs Dealer.")
        for p in self.players:
            lines.append(f"**{p.display_name}**: {', '.join(self.hands[p])}  ({hand_value(self.hands[p])})")
        lines.append(f"Dealer: {self.dealer[0]}, [hidden]")

        # Ensure stage is set to player_turns so get_valid_actions works
        if self.stage == "dealing":
            self.stage = "player_turns"

        # If current_turn is beyond players (shouldn't happen), clamp it
        if self.current_turn >= len(self.players):
            self.current_turn = max(0, len(self.players) - 1)

        lines.append(self._turn_prompt())
        return "\n".join(lines)

    def _turn_prompt(self):
        if self.stage == "finished":
            return "Game finished."
        if not self.players:
            return "No players."
        # If current player busted or otherwise invalid, show next valid player
        idx = self.current_turn
        if idx < 0 or idx >= len(self.players):
            idx = 0
        return f"Turn: {self.players[idx].display_name}"
    
# ===== END BLACKJACK TESTING ===== #

    def get_valid_actions(self, player):
        # valid during their turn only
        if self.stage != "player_turns":
            # if still dealing, start player turns
            if self.stage == "dealing":
                self.stage = "player_turns"
            else:
                return []
        if self.players[self.current_turn] != player:
            return []
        hv = hand_value(self.hands[player])
        if hv >= 21:
            return []
        return ["hit", "stand"]

    def apply_action(self, player, action):
        action = action.lower().strip()
        # ensure we're in player turns
        if self.stage == "dealing":
            self.stage = "player_turns"

        if self.players[self.current_turn] != player:
            return "It's not your turn."

        if action not in ("hit","stand"):
            return "Invalid action. Use 'hit' or 'stand'."

        if action == "hit":
            card = self.deck.pop()
            self.hands[player].append(card)
            hv = hand_value(self.hands[player])
            if hv > 21:
                # player busted, advance turn
                msg = f"{player.display_name} draws {card} and busts with {hv}."
                self._advance_turn()
                # if that was last player, move to dealer stage
                if self.stage != "finished" and self.current_turn >= len(self.players):
                    self.stage = "dealer"
                    self._play_dealer()
                return msg
            if hv == 21:
                msg = f"{player.display_name} draws {card} and has 21."
                self._advance_turn()
                if self.stage != "finished" and self.current_turn >= len(self.players):
                    self.stage = "dealer"
                    self._play_dealer()
                return msg
            return f"{player.display_name} draws {card}. Hand: {', '.join(self.hands[player])} ({hv})"

        # stand
        self._advance_turn()
        if self.stage != "finished" and self.current_turn >= len(self.players):
            self.stage = "dealer"
            self._play_dealer()
        return f"{player.display_name} stands with {hand_value(self.hands[player])}."

    def _advance_turn(self):
        self.current_turn += 1

    def _play_dealer(self):
        # reveal dealer and hit until 17 or more (soft 17 stands)
        while hand_value(self.dealer) < 17:
            self.dealer.append(self.deck.pop())
        self._compute_results()
        self.stage = "finished"

    def _compute_results(self):
        dv = hand_value(self.dealer)
        outcomes = {}
        for p in self.players:
            pv = hand_value(self.hands[p])
            if pv > 21:
                outcomes[p] = ("lose", pv)
            elif dv > 21:
                outcomes[p] = ("win", pv)
            elif pv > dv:
                outcomes[p] = ("win", pv)
            elif pv == dv:
                outcomes[p] = ("push", pv)
            else:
                outcomes[p] = ("lose", pv)
        self.results = {"dealer_value": dv, "dealer_cards": list(self.dealer), "outcomes": outcomes}

    def is_over(self):
        return self.stage == "finished"

    def render(self):
        lines = []
        for p in self.players:
            lines.append(f"**{p.display_name}**: {', '.join(self.hands[p])} ({hand_value(self.hands[p])})")
        if self.stage == "finished" and self.results:
            dv = self.results["dealer_value"]
            dealer_cards = ", ".join(self.results["dealer_cards"])
            lines.append(f"Dealer: {dealer_cards} ({dv})")
            for p, (res, pv) in self.results["outcomes"].items():
                lines.append(f"{p.display_name}: {res.upper()} ({pv})")
        else:
            lines.append(f"Dealer: {self.dealer[0]}, [hidden]")
            lines.append(f"Turn: {self.players[self.current_turn].display_name}")
        return "\n".join(lines)