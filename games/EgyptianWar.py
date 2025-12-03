import random
from collections import deque
from .game import Game

RANK_ORDER = {r: i for i, r in enumerate(["2","3","4","5","6","7","8","9","10","J","Q","K","A"], start=2)}
SUITS = ["♠","♥","♦","♣"]
RANKS = list(RANK_ORDER.keys())

def new_deck():
    return [r + s for r in RANKS for s in SUITS]

def rank_value(card):
    # card like "A♠" or "10♦"
    rank = card[:-1]
    return RANK_ORDER[rank]

class EgyptianWar(Game):
    """
    Multiplayer Egyptian War. Players flip cards in turn; highest wins the round.
    Ties cause a war among tied players (place up to 3 face-down and 1 face-up).
    Winner collects all table cards. Players eliminated when deck empty.
    """

    def __init__(self, players):
        super().__init__(players)
        deck = new_deck()
        random.shuffle(deck)
        # deal evenly
        self.decks = {p: deque() for p in players}
        for i, card in enumerate(deck):
            self.decks[players[i % len(players)]].append(card)
        self.players = list(players)
        self.table = []  # all cards on table
        self.round_plays = {}  # player -> last face-up card this round
        self.current_turn = 0
        self.stage = "playing"  # playing -> resolving -> finished
        self.war_contestants = None

    def start(self):
        lines = ["Egyptian War started! Flip to play."]
        for p in self.players:
            lines.append(f"**{p.display_name}**: {len(self.decks[p])} cards")
        lines.append(self._turn_prompt())
        return "\n".join(lines)

    def _turn_prompt(self):
        if self.stage == "finished":
            return "Game finished."
        if not self.players:
            return "No players."
        idx = min(max(0, self.current_turn), len(self.players) - 1)
        return f"Turn: {self.players[idx].display_name} — press Flip"

    def get_valid_actions(self, player):
        # only Flip when it's their turn and game playing
        if self.stage != "playing":
            return []
        if self.players[self.current_turn] != player:
            return []
        if not self.decks.get(player):
            return []
        return ["flip"]

    def apply_action(self, player, action):
        action = action.lower().strip()
        if action != "flip":
            return "Invalid action. Use 'flip'."
        if self.players[self.current_turn] != player:
            return "It's not your turn."

        if not self.decks[player]:
            # player has no cards
            self._advance_turn()
            return f"{player.display_name} has no cards and is skipped."

        # flip top card
        card = self.decks[player].popleft()
        self.table.append((player, card))
        self.round_plays[player] = card
        msg = f"{player.display_name} flips {card}."

        # advance turn
        self._advance_turn()

        # if all active players have flipped, resolve round
        if self._all_flipped():
            msg += "\n" + self._resolve_round()
            # cleanup round_plays
            self.round_plays.clear()
            # eliminate empty decks
            self._eliminate_empty_players()
            # check for game over
            if len(self.players) <= 1:
                self.stage = "finished"
                if self.players:
                    msg += f"\n{self.players[0].display_name} wins the game!"
                else:
                    msg += "\nNo players remain."
            else:
                # next round starts with winner or next player
                self.current_turn = self.current_turn % len(self.players)
        return msg

    def _advance_turn(self):
        # move to next player who still has cards
        if not self.players:
            return
        self.current_turn = (self.current_turn + 1) % len(self.players)
        # skip players with empty decks (they'll be removed soon)
        start = self.current_turn
        while self.players and not self.decks[self.players[self.current_turn]]:
            self.current_turn = (self.current_turn + 1) % len(self.players)
            if self.current_turn == start:
                break

    def _all_flipped(self):
        # consider only active players (those still in self.players)
        return all(p in self.round_plays or not self.decks[p] for p in self.players)

    def _resolve_round(self):
        # determine highest among face-up cards
        contenders = {p: rank_value(c) for p, c in self.round_plays.items()}
        if not contenders:
            return "No cards were played this round."
        max_val = max(contenders.values())
        tied = [p for p, v in contenders.items() if v == max_val]
        if len(tied) == 1:
            winner = tied[0]
            self._collect_table(winner)
            return f"{winner.display_name} wins the round and collects {len(self.table)} cards."
        # war among tied players
        return self._do_war(tied)

    def _do_war(self, tied_players):
        # Each tied player places up to 3 face-down and 1 face-up if possible
        war_msg = f"War between: {', '.join(p.display_name for p in tied_players)}."
        war_faceups = {}
        for p in tied_players:
            # place up to 3 face-down
            for _ in range(3):
                if self.decks[p]:
                    self.table.append((p, self.decks[p].popleft()))
                else:
                    break
            # place one face-up if possible
            if self.decks[p]:
                card = self.decks[p].popleft()
                self.table.append((p, card))
                war_faceups[p] = rank_value(card)
                war_msg += f" {p.display_name} shows {card}."
            else:
                war_msg += f" {p.display_name} cannot continue war and is eliminated."
        if not war_faceups:
            # no one could show a face-up card; choose a random tied player who still exists
            remaining = [p for p in self.players if self.decks[p]]
            if remaining:
                winner = remaining[0]
                self._collect_table(winner)
                return war_msg + f" {winner.display_name} collects the pile."
            else:
                return war_msg + " No winner this war."
        max_val = max(war_faceups.values())
        new_tied = [p for p, v in war_faceups.items() if v == max_val]
        if len(new_tied) == 1:
            winner = new_tied[0]
            self._collect_table(winner)
            return war_msg + f" {winner.display_name} wins the war and collects {len(self.table)} cards."
        # recursive war among new_tied
        return war_msg + " " + self._do_war(new_tied)

    def _collect_table(self, winner):
        # collect all table cards (player,card) and append card values to winner's deck
        cards = [card for _, card in self.table]
        random.shuffle(cards)  # optional shuffle before collecting
        for c in cards:
            self.decks[winner].append(c)
        self.table.clear()

    def _eliminate_empty_players(self):
        removed = []
        for p in list(self.players):
            if not self.decks[p]:
                removed.append(p)
                self.players.remove(p)
        # adjust current_turn if needed
        if self.players:
            self.current_turn = self.current_turn % len(self.players)
        return removed

    def is_over(self):
        return self.stage == "finished"

    def render(self):
        lines = []
        for p in self.players:
            lines.append(f"**{p.display_name}**: {len(self.decks[p])} cards")
        if self.table:
            table_cards = ", ".join(card for _, card in self.table[-12:])  # show last few
            lines.append(f"Table: {table_cards}")
        lines.append(self._turn_prompt())
        return "\n".join(lines)