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
