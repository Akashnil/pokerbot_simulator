from action import *

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

	def reset(self):
		pass

import random

random.seed = 13

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
