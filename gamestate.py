from hand_rankings import *

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
		winning = self.pot / (len(self.winners) + 0.) # In rare cases net winning may be fractional
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
