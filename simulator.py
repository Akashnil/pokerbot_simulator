from hand_rankings import *

class GameRules:
	num_players = 4
	stack_size = 200 # in small blinds

class Action:
	enum = None # 'deal', 'fold', 'call', 'bet', 'open' open means flop / turn / river
	# Note: No need to distinguish between check and call, or between bet and raise
	# it is always clear from context
	street = None # If this is an open action, street will be 'flop', 'turn', or 'river'
	cards = None # If this is either deal action or open action: a sorted tuple of integers from 0 to 51.
	amount = 0 # If this is a bet action, a positive integer
	small_blind = False
	big_blind = False

	def action_string(self, game_state):
		call_string = 'CALL ' + str(game_state.remaining_price())
		call_string = '{:<10}'.format(call_string)
		bet_string = 'BET ' + str(self.amount) if self.enum == 'bet' else ''
		bet_string = '{:<9}'.format(bet_string)
		price_string = 'PRICE ' + str(game_state.price + self.amount)
		price_string = '{:<12}'.format(price_string)
		pot_string = 'POT ' + str(game_state.pot + game_state.remaining_price() + self.amount)
		pot_string = '{:<10}'.format(pot_string)
		return call_string + bet_string + price_string + pot_string

	def readable_string(self, game_state, player_name = None):
		# convert this action into a string, player_num is either the player receiving cards or acting player
		if not self.enum == 'deal':
			player_id = game_state.acting_player
		else:
			player_id = len(game_state.hole_cards) + 1
		player_string = 'p' + str(player_id)
		if player_name:
			player_string += '(' + player_name + ')'
		if self.small_blind:
			return player_string + ' POSTS SB'
		if self.big_blind:
			return player_string + ' POSTS BB'
		if self.enum == 'deal':
			assert len(self.cards) == 2
			return player_string + ' DEALT ' + card_string(self.cards[0]) + card_string(self.cards[1])
		if self.enum == 'open':
			if self.street == 'flop':
				assert len(self.cards) == 3
				return 'FLOP ' + card_string(self.cards[0]) + card_string(self.cards[1]) + card_string(self.cards[2])
			if self.street == 'turn':
				assert len(self.cards) == 1
				return 'TURN ' + card_string(self.cards[0])
			if self.street == 'river':
				assert len(self.cards) == 1
				return 'RIVER ' + card_string(self.cards[0])
			assert False
		if self.enum == 'fold':
			return player_string + ' FOLDS'
		# We still don't distinguish check/call or bet/raise for readable strings yet.

		return player_string + ' ' + self.action_string(game_state)

class GameState:
	actions = []
	acting_player = 0
	player_states = [] # list of booleans: True if player is still in the hand, False if folded
	player_chips = [] # list of amounts that each player has added to the pot
	leading_player = 1 # the player who has the betting lead, where the street will end
	street = 0
	pot = 0
	hole_cards = []
	open_cards = []
	all_cards = set()
	rules = None
	remaining = 0
	winners = None

	def __init__(self, rules):
		self.actions = []
		self.acting_player = 0
		self.street = 0 # preflop = 0, flop = 1, turn = 2, river = 3, showdown = 4
		self.pot = 0
		self.price = 0
		self.hole_cards = []
		self.open_cards = []
		self.all_cards = set()
		self.player_states = []
		self.remaining = rules.num_players
		self.winners = None
		self.player_chips = []
		self.rules = rules

	def all_string(self):
		return ' '.join([self.acting_player, self.leading_player, self.street, self.open_cards, self.all_cards, self.remaining])

	def pot_string(self):
		return 'PRICE ' + '{:<4}'.format(str(self.price)) + 'POT ' + '{:<4}'.format(str(self.pot))

	def is_terminal(self):
		return self.remaining == 1 or self.street == 4

	def find_current_winners(self):
		if self.remaining == 1:
			for i in range(len(self.player_states)):
				if self.player_states[i]:
					self.winners = [i+1]
					return [i+1]
		best_hand = (100,)
		current_winners = []
		for i in range(len(self.player_states)):
			if self.player_states[i]:
				val = hand_value(list(self.hole_cards[i]) + self.open_cards)
				if val == best_hand:
					current_winners.append(i+1)
				if val < best_hand:
					best_hand = val
					current_winners = [i+1]
		self.winners = current_winners
		return current_winners

	def net_winnings(self):
		if not self.winners:
			self.find_current_winners()
		winning = self.pot / len(self.winners) # In rare cases net winning may be fractional
		if int(winning) == winning:
			winning = int(winning)
		net = [-x for x in self.player_chips]
		for x in self.winners:
			net[x-1] += winning
		return net

	def results_string(self):
		net = self.net_winnings()
		return 'p' + str(self.winners) + ' WINS ' + str(self.pot) + ' NET PROFIT ' + str(net)

	def get_next_player(self):
		x = self.acting_player
		while True:
			x = (x % len(self.player_states)) + 1
			if x == self.leading_player:
				return 0
			if self.player_states[x-1]:
				return x

	def remaining_price(self):
		return self.price - self.player_chips[self.acting_player-1]

	def apply_action(self, action):
		self.actions.append(action)
		if action.enum == 'deal':
			self.hole_cards.append(action.cards)
			for cd in action.cards:
				self.all_cards.add(cd)
			self.player_states.append(True)
			self.player_chips.append(0)
			if len(self.hole_cards) == self.rules.num_players:
				self.acting_player = 1
				self.leading_player = 1
			return
		if action.enum == 'open':
			self.open_cards += list(action.cards)
			for cd in action.cards:
				self.all_cards.add(cd)
			self.leading_player = len(self.player_states)
			self.acting_player = self.get_next_player()
			self.leading_player = self.acting_player
			return
		if action.enum == 'fold':
			self.player_states[self.acting_player-1] = False
			self.remaining -= 1
			if self.remaining == 1:
				return
			self.acting_player = self.get_next_player()
			if self.acting_player == 0:
				self.street += 1
			return
		if action.enum == 'call':
			extra = self.price - self.player_chips[self.acting_player-1]
			self.player_chips[self.acting_player-1] = self.price
			self.pot += extra
			self.acting_player = self.get_next_player()
			if self.acting_player == 0:
				self.street += 1

		if action.enum == 'bet':
			self.price += action.amount
			self.leading_player = self.acting_player
			extra = self.price - self.player_chips[self.acting_player-1]
			self.player_chips[self.acting_player-1] = self.price
			self.pot += extra
			self.acting_player = self.get_next_player()

import math

class Player:
	num_hands = 0
	mean = 0.
	variance_sum = 0.

	def take_action(self, game_state):
		# returns a member of Action class
		pass

	def inform_winning(self, amount):
		self.num_hands += 1
		delta = amount - self.mean
		self.mean += delta / self.num_hands
		delta_ = amount - self.mean
		self.variance_sum += delta * delta_

	def stats(self):
		return self.num_hands, self.mean, math.sqrt(self.variance_sum / self.num_hands)

import random

random.seed = 5

class Dealer(Player):

	def draw_card(self, game_state):
		while True:
			x = random.randrange(52)
			if x not in game_state.all_cards:
				break
		game_state.all_cards.add(x)
		return x

	def take_action(self, game_state):
		action = Action()
		if game_state.street == 0:
			action.enum = 'deal'
			c1 = self.draw_card(game_state)
			c2 = self.draw_card(game_state)
			action.cards = (c1, c2)
			return action
		if game_state.street == 1:
			action.enum = 'open'
			action.street = 'flop'
			c1 = self.draw_card(game_state)
			c2 = self.draw_card(game_state)
			c3 = self.draw_card(game_state)
			action.cards = (c1, c2, c3)
			return action
		if game_state.street == 2:
			action.enum = 'open'
			action.street = 'turn'
			c1 = self.draw_card(game_state)
			action.cards = (c1,)
			return action
		if game_state.street == 3:
			action.enum = 'open'
			action.street = 'river'
			c1 = self.draw_card(game_state)
			action.cards = (c1,)
			return action

class RandomPlayer(Player):
	# If the player can check, they will check with probability 3/4, bet with probability 1/4
	# If the player is facing a bet, they will fold 1/4 time, call 1/2 time, raise half pot 1/4 times.

	def get_blind_action(self, game_state):
		if game_state.pot < 2:
			action = Action()
			action.enum = 'bet'
			action.amount = 1
			action.small_blind = game_state.pot == 0
			action.big_blind = not action.small_blind
			return action
		return None

	def take_action(self, game_state):
		blind = self.get_blind_action(game_state)
		if blind:
			return blind
		action = Action()
		acting_player = game_state.acting_player
		choice = random.randrange(4)
		if game_state.price == game_state.player_chips[acting_player-1]:
			if choice < 1 and game_state.price < game_state.rules.stack_size:
				action.enum = 'bet'
				action.amount = game_state.pot // 2
				if action.amount < 2:
					action.amount = 2
				if action.amount + game_state.price > game_state.rules.stack_size:
					action.amount = game_state.rules.stack_size - game_state.price
			else:
				action.enum = 'call'
			return action
		if choice < 1 and game_state.price < game_state.rules.stack_size:
			action.enum = 'bet'
			action.amount = game_state.pot // 2
			if action.amount < 2:
				action.amount = 2
			if action.amount + game_state.price > game_state.rules.stack_size:
				action.amount = game_state.rules.stack_size - game_state.price
		elif choice < 3:
			action.enum = 'call'
		else:
			action.enum = 'fold'
		return action

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

rules = GameRules()

simulator = SequentialActionGame(rules)

players = [Dealer(), RandomPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]

simulator.register_players(players)

simulator.reset_game_state()

for i in range(1000000):
	simulator.reset_game_state()
	while True:
		p = simulator.game_state.acting_player
		act = simulator.next_action(True)
		if not act:
			if i < 1000:
				print ('#' + '{:<4}'.format(str(i)) + simulator.game_state.results_string())
			break
		else:
			# print (act)
			continue

print ('stats: (count, mean, stdev)')

for p in range(1, 5):
	print ('p' + str(p) + ' statistics ' + str(players[p].stats()))

