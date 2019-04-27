class GameRules:
	num_players = 3
	stack_size = 400 # in small blinds

class Action:
	enum = None # 'deal', 'fold', 'call', 'bet', 'open' open means flop / turn / river
	# Note: No need to distinguish between check and call, or between bet and raise
	# it is always clear from context
	street = None # If this is an open action, street will be 'flop', 'turn', or 'river'
	cards = None # If this is either deal action or open action: a sorted tuple of integers from 0 to 51.
	amount = None # If this is a bet action, a positive integer

	def readable_string(player_num, player_name = None, small_blind = False, big_blind = False, all_in = False):
		# convert this action into a string, player_num is either the player receiving cards or acting player
		player_string = 'player' + str(player_num)
		if player_name:
			player_string += '(' + player_name + ')'
		if small_blind:
			return player_string + ' POSTS SMALL BLIND'
		if big_blind:
			return player_string + ' POSTS BIG BLIND'
		if enum == 'deal':
			assert len(cards) == 2
			return player_string + ' DEALT ' + card_string(cards[0]) + card_string(cards[1])
		if enum == 'open':
			if street == 'flop':
				assert len(cards) == 3
				return 'FLOP ' + card_string(cards[0]) + card_string(cards[1]) + card_string(cards[2])
			if street == 'turn':
				assert len(cards) == 1
				return 'TURN ' + card_string(cards[0])
			if street == 'river':
				assert len(cards) == 1
				return 'RIVER ' + card_string(cards[0])
			assert False
		if enum == 'fold':
			return player_string + ' FOLDS'
		# We still don't distinguish check/call or bet/raise for readable strings yet.
		if enum == 'call':
			return player_string + ' CALLS'
		if enum == 'bet':
			if all_in:
				return player_string + ' ALLIN ' + str(amount)
			return player_string + ' BETS ' + str(amount)

class GameState:
	actions = []
	string = ''
	# dealer is player 0, small blind is player 1, big blind is player 2
	def acting_player():
		pass

	def partial_state(idx):
		# copy self, then remove information about other players' hole cards
		pass


class SequentialActionGame:
	game_rules = None
