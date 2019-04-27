suit_letter = {0:'s', 1:'h', 2:'d', 3:'c'}
rank_letter = {0:'A', 1:'K', 2:'Q', 3:'J', 4:'T', 5:'9', 6:'8', 7:'7', 8:'6', 9:'5', 10:'4', 11:'3', 12:'2'}

def hand_value(cards):
	'''
	input is list of cards (usually 7) from 0 to 51. Output is a number R followed by an ordered list of 5 cards.
	R is 0 if straight flush, 1 if quads, 2 if full house, 3 if flush, 4 if straight, 5 if 3 of a kind, 6 if 2 pair,
	7 if pair, 8 if high card. The 5 cards that follow only have rank, no suit.
	The tuple can be compared lexicographically to determine which one wins.
	'''
	cards = sorted(cards)
	num_cards = len(cards) # should be 7, but not assumed so, could be less or more
	def find_straight(cds):
		r = 1
		for i in range(1, num_cards):
			if cds[i] == cds[i-1]+1 and cds[i] % 13 != 0:
				r += 1
				if r == 4 and cds[i] % 13 == 12 and cds[i] - 12 in cds:
					return (cds[i]-3) % 13 # This is the wheel, the largest (worst) straight, with value 9
				if r == 5:
					return (cds[i]-4) % 13 # The rank of the straight, value from 0 to 8
			else:
				r = 1
		return None

	sflush = find_straight(cards)
	if sflush:
		return 0, tuple([sflush+i for i in range(5)])

	ranks = [cd % 13 for cd in cards]
	ranks = sorted(ranks)
	
	# print (ranks)
	groups = []
	r = 1
	for i in range(1, num_cards+1):
		if i < num_cards and ranks[i] == ranks[i-1]:
			r += 1
		else:
			groups.append((-r, ranks[i-1]))
			r = 1
	groups = sorted(groups)
	# print (groups)
	best_group = groups[0]
	assert best_group[0] >= -4 and best_group[0] <= -1
	if best_group[0] == -4:
		# quads: find the kicker
		kickers = [rnk  for rnk in ranks if rnk != best_group[1]]
		return 1, tuple([best_group[1]]*4 + kickers[:1])

	if len(groups) == 1:
		second_group = None
	else:
		second_group = groups[1]
	if best_group[0] == -3 and second_group and second_group[0] <= -2:
		return 2, tuple([best_group[1]]*3 + [second_group[1]]*2)

	for i in range(num_cards-4):
		if cards[i] // 13 == cards[i+4] // 13:
			# found the flush
			return 3, tuple([x % 13 for x in cards[i:i+5]])

	straight = find_straight(ranks)
	if straight:
		return 4, tuple([straight+i for i in range(5)])

	if best_group[0] == -3:
		kickers = [rnk for rnk in ranks if rnk != best_group[1]]
		return 5, tuple([best_group[1]]*3 + kickers[:2])

	if best_group[0] == -2 and second_group and second_group[0] == -2:
		kickers = [rnk for rnk in ranks if rnk != best_group[1] and rnk != second_group[1]]
		return 6, tuple([best_group[1]]*2 + [second_group[1]]*2 + kickers[:1])

	if best_group[0] == -2:
		kickers = [rnk for rnk in ranks if rnk != best_group[1]]
		return 7, tuple([best_group[1]]*2 + kickers[:3])

	return 8, tuple(ranks[:5])

def card_string(num):
	# num is an integer from 0 to 51, returns human readable card, eg. 0 is As (ace of spades), 14 is Kh, 30 is Td, 51 is 2c
	suit = num // 13
	rank = num % 13
	return rank_letter[rank] + suit_letter[suit]

'''
#Testing code below

import numpy

num_trials = 25
# Here we are testing the hand rankings of num_trials random collections of cards. Half the trials have 7 cards,
# other half have a random  number of cards from 2 to 6.

for trials in range(num_trials):
	if numpy.random.randint(2) == 0:
		num_cards = 7
	else:
		num_cards = numpy.random.randint(2, 7)
	cards = numpy.random.choice(52, size=num_cards, replace=False)
	value = hand_value(cards)
	readable_cards = ' '.join([card_string(cd) for cd in cards])
	readable_cards = "{:<25}".format(readable_cards)
	print(readable_cards, value[0], value[1])

'''