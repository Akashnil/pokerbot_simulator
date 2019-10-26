class GameRules:
	num_players = 4
	stack_size = 200 # in small blinds

import math
from player import *
from gamestate import *

class SequentialActionGame:
	game_rules = None
	game_state = None
	players = []

	def __init__(self, rules):
		self.game_rules = rules

	def register_players(self, players):
		self.players = players

	def reset_game_state(self):
		self.game_state = GameState(self.game_rules)
		for p in self.players:
			p.reset()

	def next_action(self, string = False):
		if self.game_state.is_terminal():
			net = self.game_state.net_winnings()
			for p in range(1, len(self.players)):
				self.players[p].inform_winning(net[p-1])
			return None
		acting_player = self.players[self.game_state.acting_player]
		action = acting_player.take_action(self.game_state)
		if string:
			return_string = action.readable_string(self.game_state)
		self.game_state.apply_action(action)
		return return_string if string else action

	def simulate_hand(self):
		self.reset_game_state()
		while True:
			p = self.game_state.acting_player
			act = self.next_action(False)
			if not act:
				return

rules = GameRules()

simulator = SequentialActionGame(rules)

players = [Dealer(), RandomPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]

simulator.register_players(players)

simulator.reset_game_state()

for i in range(1000000):
	simulator.simulate_hand()
	if i < 1000:
		print ('#' + '{:<4}'.format(str(i)) + simulator.game_state.results_string())

print ('stats: (count, mean, stdev)')

for p in range(1, 5):
	print ('p' + str(p) + ' statistics ' + str(players[p].stats()))

