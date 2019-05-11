from hand_rankings import *
pct = {}

def encode(lst, N, last = None):
	if last == None:
		last = N
	ret = 0
	for x in range(len(lst)-1):
		ret = ret * (N+1)
		ret += lst[x]+1
	ret = ret * (last+1)
	ret += lst[-1]+1
	return ret

def decode(val, N, last = None):
	if last == None:
		last = N
	ret = []
	ret.append((val % (last+1)) - 1)
	val //= (last+1)
	while val != 0:
		ret.append((val % (N+1)) - 1)
		val //= (N+1)
	return ret[::-1]

def remaining_combos(N):
	return ((52-N) * (51-N)) // 2

# situation is a pair (board, hole). board is a tuple of cards 0, 3, 4, 5 long.
# hole is a pair of starting cards. returns the same cards by reordering and changing the suits.
def canonical_situation(situation):
	hole, board = situation[:2], situation[2:]
	if len(board) == 0:
		if hole[0] // 13 == hole[1] // 13:
			hole = hole[0] % 13, hole[1] % 13
			if hole[0] > hole[1]:
				hole = hole[1], hole[0]
		else:
			hole = hole[0] % 13, hole[1] % 13
			if hole[0] > hole[1]:
				hole = hole[1], hole[0]
			hole = hole[0], hole[1] + 13
	suit_counts = [0]*4
	for x in board:
		suit_counts[x // 13] += 1

	flushable_suit = -1
	for s in range(4):
		if suit_counts[s] >= 3:
			flushable_suit = s

	flushable_board = sorted([x % 13 for x in board if x // 13 == flushable_suit])
	board = sorted([x % 13 for x in board if x // 13 != flushable_suit])
	flushable_hole = sorted([x % 13 for x in hole if x // 13 == flushable_suit])
	hole = sorted([x % 13 for x in hole if x // 13 != flushable_suit])
	seen = set()
	for i in range(len(board)):
		board[i] += 13 * (i % 4)
		while board[i] in seen:
			board[i] += 13
			board[i] = (board[i] % 52)
		seen.add(board[i])
	for i in range(len(hole)):
		while hole[i] in seen:
			hole[i] += 13
		seen.add(hole[i])
	board = board + [x + 13*3 for x in flushable_board]
	hole = hole + [x + 13*3 for x in flushable_hole]

	return hole + board

# for a given board, calculate the relative hand value of every holding, eg. percentage of holdings that beats it.
def pct_calc(board):
	# print (board)
	board = list(board)
	blockers = set(board)
	hand_values = []
	val_dict = {}
	pct_dict = {}
	for c0 in range(52):
		if c0 in blockers:
			continue
		for c1 in range(c0+1, 52):
			if c1 in blockers:
				continue
			all_cards = board[:] + [c0, c1]
			val = hand_value(all_cards)
			hand_values.append((val, (c0, c1)))
			val_dict[(c0, c1)] = val
			# print ((c0, c1), val)
	total_combos = len(hand_values)
	hand_values = sorted(hand_values)
	rank = 0
	count = 0
	best = (-1, )
	for value, hole in hand_values:
		if best < value:
			best = value
			rank = count
		better_blocks = 0
		total_blocks = 0
		for x in range(52):
			if x == hole[0] or x == hole[1] or x in blockers:
				continue
			if x < hole[0]:
				if val_dict[(x, hole[0])] < value:
					better_blocks += 1
				if val_dict[(x, hole[1])] < value:
					better_blocks += 1
			elif x < hole[1]:
				if val_dict[(hole[0], x)] < value:
					better_blocks += 1
				if val_dict[(x, hole[1])] < value:
					better_blocks += 1
			else:
				if val_dict[(hole[0], x)] < value:
					better_blocks += 1
				if val_dict[(hole[1], x)] < value:
					better_blocks += 1
			total_blocks += 2
		situation = canonical_situation(list(hole) + board)
		if total_combos - total_blocks - 1 != remaining_combos(len(situation)):
			print (remaining_combos(len(situation)), total_combos - total_blocks - 1)
			assert False
		situ = encode(situation, 52)
		if situ not in pct:
			if len(pct) % 100000 == 0:
				print (len(pct) // 100000)
			pct[situ] = rank - better_blocks
		# hole_String = ' '.join([card_string(x) for x in situation[1]])
		# print (hole_String, rel_val)
		count += 1

# Given a set of ranks on the board, return the next set of possibilities for the rank
def next_board(board):
	if len(board) == 0:
		return [0]
	elif len(board) < 5:
		ret = board[:]
		ret.append(ret[-1])
		if len(ret) == 5 and ret[0] == ret[-1]:
			return next_board(ret)
		return ret
	else:
		for i in range(4, -1, -1):
			if board[i] != 12:
				ret = board[:i]
				ret.append(board[i] + 1)
				return ret
		return None

import pickle

def load_pct():
	try:
		# situation_dict is saved
	    with open('situation_dict.pickle', 'rb') as handle:
	    	pct = pickle.load(handle)
	except FileNotFoundError:
		board = []
		count = 0

		while board != None:
			uniques = list(set(board))
			repeats = [board[i] for i in range(1, len(board)) if board[i] == board[i-1]]
			for flush_idx in range(1<<len(uniques)):
				bin_mask = bin(flush_idx)[2:].zfill(len(uniques))
				if bin_mask.count('1') in [1, 2]:
					continue
				non_flush = [uniques[i] for i in range(len(uniques)) if bin_mask[i] == '0'] + repeats
				non_flush = sorted(non_flush)
				flush = [uniques[i] for i in range(len(uniques)) if bin_mask[i] == '1']
				if len(flush) == 0:
					board_ = [non_flush[i] + 13 * (i % 4) for i in range(len(non_flush))]
				else:
					board_ = [non_flush[i] + 13 * (i % 3) for i in range(len(non_flush))] + [x + 13 * 3 for x in flush]
				board_ = sorted(board_)
				# print (' '.join([card_string(x) for x in board_]))
				pct_calc(board_)
				count += 1
				# print (count, 49882)
			board = next_board(board)
		# dictionary done
		with open('situation_dict.pickle', 'wb') as handle:
		    pickle.dump(pct, handle, protocol=pickle.HIGHEST_PROTOCOL)

def hand_strength(situation):
	return pct[encode(canonical_situation(situation), 52)]

'''
import numpy
num_trials = 500

# Canonical situation test
for trials in range(num_trials):
	num_cards = numpy.random.randint(2, 7)
	if num_cards == 3 or num_cards == 4:
		num_cards = 7
	cards = numpy.random.choice(52, size=num_cards, replace=False)
	board = cards[2:]
	hole = cards[:2]
	strength = hand_strength(cards)
	tot = remaining_combos(len(cards))
	f_val = '{:.3f}'.format(strength / tot)[1:]
	readable_hole = ' '.join([card_string(cd) for cd in hole])
	readable_hole = "{:<8}".format(readable_hole)
	readable_board = ' '.join([card_string(cd) for cd in board])
	readable_board = "{:<20}".format(readable_board)
	strength = "{:<5}".format(str(strength))
	print(readable_hole, readable_board, f_val, strength, tot)
'''