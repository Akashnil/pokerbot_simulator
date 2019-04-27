class GameRules:
	num_players = 4
	stack_size = 400 # in small blinds

class Action:
	enum = None # 'deal', 'fold', 'call', 'bet', 'open' open means flop / turn / river
	# Note: No need to distinguish between check and call, or between bet and raise
	# it is always clear from context
	street = None # If this is an open action, street will be 'flop', 'turn', or 'river'
	cards = None # If this is either deal action or open action: a sorted tuple of integers from 0 to 51.
	amount = None # If this is a bet action, a positive integer
	small_blind = False
	big_blind = False

	def readable_string(self, player_num, player_name = None):
		# convert this action into a string, player_num is either the player receiving cards or acting player
		player_string = 'player' + str(player_num)
		if player_name:
			player_string += '(' + player_name + ')'
		if small_blind:
			return player_string + ' POSTS SMALL BLIND'
		if big_blind:
			return player_string + ' POSTS BIG BLIND'
		if self.enum == 'deal':
			assert len(self.cards) == 2
			return player_string + ' DEALT ' + card_string(cards[0]) + card_string(cards[1])
		if self.enum == 'open':
			if self.street == 'flop':
				assert len(self.cards) == 3
				return 'FLOP ' + card_string(cards[0]) + card_string(cards[1]) + card_string(cards[2])
			if self.street == 'turn':
				assert len(self.cards) == 1
				return 'TURN ' + card_string(cards[0])
			if self.street == 'river':
				assert len(self.cards) == 1
				return 'RIVER ' + card_string(cards[0])
			assert False
		if self.enum == 'fold':
			return player_string + ' FOLDS'
		# We still don't distinguish check/call or bet/raise for readable strings yet.
		if self.enum == 'call':
			return player_string + ' CALLS'
		if self.enum == 'bet':
			return player_string + ' BETS ' + str(self.amount)

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

	def __init__(self, rules):
		self.actions = []
		self.acting_player = 0
		self.street = 0 # preflop = 0, flop = 1, turn = 2, river = 3, showdown = 4
		self.pot = 0
		self.max_bet = 0
		self.hole_cards = []
		self.open_cards = []
		self.player_states = []
		self.remaining = 0
		self.player_chips = []
		self.rules = rules

	def is_terminal(self):
		return self.remaining == 1 or self.street = 4

	def get_next_player(self):
		x = self.acting_player
		while True:
			x += 1
			x = ((x-1) % len(self.player_states)) + 1
			if x == self.leading_player:
				return 0
			if self.player_states[x]:
				return x

	def apply_action(self, action):
		self.actions.append(action)
		if action.enum == 'deal':
			self.hole_cards.append(action.cards)
			for cd in action.cards:
				self.all_cards.add(cd)
			self.player_states.append(True)
			self.player_chips.append(0)
			self.remaining += 1
			if len(self.hole_cards) == self.rules.num_players:
				self.acting_player = 1
				self.leading_player = 1
			return
		if action.enum == 'open':
			self.open_cards += list(action.cards)
			for cd in action.cards:
				self.all_cards.add(cd)
			self.acting_player = self.get_next_player()
			self.leading_player = self.acting_player
			return
		if action.enum == 'fold':
			self.player_states[acting_player] = False
			self.remaining -= 1
			if self.remaining == 1:
				return
			self.acting_player = self.get_next_player()
			if self.acting_player == 0:
				self.street += 1
			return
		if action.enum == 'call':
			extra = self.max_bet - self.player_chips[self.acting_player]
			self.player_chips[self.acting_player] = self.max_bet
			self.pot += extra
			self.acting_player = self.get_next_player()
			if self.acting_player == 0:
				self.street += 1

		if action.enum == 'bet':
			self.max_bet += action.amount
			self.leading_player = self.acting_player
			extra = self.max_bet - self.player_chips[self.acting_player]
			self.player_chips[self.acting_player] = self.max_bet
			self.pot += extra
			self.acting_player = self.get_next_player()

class Player:
	num_hands = 0
	mean_won = 0.
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

import random

class Dealer(Player):
	seed = 0

	def __init__(self, seed = 10):
		self.seed = seed
		random.seed(seed)

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
			c1 = self.draw_card()
			c2 = self.draw_card()
			action.cards = (c1, c2)
			return action
		if game.street == 1:
			action.enum = 'open'
			action.street = 'flop'
			c1 = self.draw_card()
			c2 = self.draw_card()
			c3 = self.draw_card()
			action.cards = (c1, c2, c3)
			return action
		if game.street == 2:
			action.enum = 'open'
			action.street = 'turn'
			c1 = self.draw_card()
			action.cards = (c1,)
			return action
		if game.street == 3:
			action.enum = 'open'
			action.street = 'river'
			c1 = self.draw_card()
			action.cards = (c1,)
			return action

class RandomPlayer(Player):
	# If the player can check, they will check with probability 3/4, bet with probability 1/4
	# If the player is facing a bet, they will fold 1/4 time, call 1/2 time, raise half pot 1/4 times.
	seed = 0

	def __init__(self, seed = 10):
		self.seed = seed
		random.seed(seed)

	def get_blind_action(self, game_state):
		if game_state.pot < 2:
			action = Action()
			action.enum = 'bet'
			action.amount = 1
			action.sb = game_state.pot == 0
			action.bb = not action.sb
			return action
		return None

	def take_action(self, game_state):
		blind = self.get_blind_action()
		if blind:
			return blind
		action = Action()
		acting_player = game_state.acting_player
		choice = random.randrange(4)
		if game_state.max_bet == game_state.player_chips[acting_player]:
			if choice < 1:
				action.enum = 'bet'
				action.amount = game_state.pot // 2
			else:
				action.enum = 'call'
			return action
		if choice < 1:
			action.enum = 'bet'
			action.amount = game_state.pot // 2
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

	def register_players(players):
		self.players = players

	def reset_game_state():
		self.game_state = GameState(self.game_rules)

	def next_action():
		if game_state.is_terminal():
			return None
		acting_player = players[game_state.acting_player]
		action = acting_player.take_action(game_state)
		game_state.apply_action(action)
		return action

rules = GameRules()

simulator = Simulator(rules)

players = [Dealer(), RandomPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()]

simulator.register_players(players)

simulator.reset_game_state()

for i in range(50):
	if simulator.game_state.is_terminal():
		'THE END'
		break