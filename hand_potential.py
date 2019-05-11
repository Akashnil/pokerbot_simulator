from hand_strength import *

pots = {}

def num_rollouts(N):
	ret = 1
	for i in range(7 - N):
		ret *= (46+i)
	return ret

def canonical(situation):
	if len(situation) == 7:
		return canonical_situation(situation)
	hole, board = situation[:2], situation[2:]
	board = sorted([(x % 13, x // 13) for x in board])
	hole = sorted([(x % 13, x // 13) for x in hole])

	all_cards = board + hole
	idx = 0
	suit_map = {}
	for c in all_cards:
		s = c[1]
		if s not in suit_map:
			suit_map[s] = idx
			idx += 1
	all_cards = [(x[0], suit_map[x[1]]) for x in all_cards]

	board, hole = sorted(all_cards[:-2]), sorted(all_cards[-2:])

	suit_counts = [0]*4
	for x, y in board:
		suit_counts[y] += 1

	dead_suits = [s for s in range(4) if suit_counts[s] < len(board) - 2]

	known_cards = set(board)

	hole_ = []
	for x, y in hole:
		if y in dead_suits:
			for s in dead_suits:
				if (x, s) not in known_cards:
					hole_.append((x, s))
					known_cards.add((x, s))
					break
		else:
			hole_.append((x, y))
			known_cards.add((x, y))
	hole = sorted(hole_)

	return [x[0] + x[1] * 13 for x in hole + board]

# returns a list of (rank, count) which means this situation achieves the given rank or better 
# count times out of all the total_rollouts
def potential(situation):
	global num_curves
	global pots
	if len(situation) == 7:
		return [(hand_strength(situation), 1)]
	situation = canonical(situation)
	enc = encode(situation + [0], 52, 1000)
	if enc in pots:
		ret = []
		for i in range(pots[enc]):
			ec = encode(situation + [i+1], 52, 1000)
			count, rank = decode(pots[ec], 1<<40, 1000)
			ret.append((rank, count))
		return ret
	hole, board = situation[:2], situation[2:]
	all_points = []
	for cd in range(52):
		if cd in situation:
			continue
		cum_list = potential(situation + [cd])
		all_points.append(cum_list[0])
		all_points += [(cum_list[i][0], cum_list[i][1] - cum_list[i-1][1]) for i in range(1, len(cum_list))]
	all_points = sorted(all_points)
	ret = []
	current_rank = all_points[0][0]
	current_count = 0
	for rank, count in all_points:
		if rank != current_rank:
			ret.append((current_rank, current_count))
			current_rank = rank
		current_count += count
	ret.append((current_rank, current_count))
	if current_count != num_rollouts(len(situation)):
		print (ret)
		print (situation, current_count, num_rollouts(len(situation)))
		assert current_count == num_rollouts(len(situation))
	pots[enc] = len(ret)
	for i in range(len(ret)):
		ec = encode(situation + [i+1], 52, 1000)

		pots[ec] = encode([ret[i][1], ret[i][0]], 1<<40, 1000)
	return ret

import pickle
import random

def load_potential():
	try:
	    with open('potential_dict.pickle', 'rb') as handle:
	    	pots = pickle.load(handle)
	except FileNotFoundError:
		load_pct()
		for c0 in range(52):
			for c1 in range(c0+1, 52):
				pt = potential([c0, c1])
				pt = random.choice(pt)
				f_val = '{:.3f}'.format(pt[1] / num_rollouts(2))[1:]
				print ((c0, c1), f_val, pt)
		with open('potential_dict.pickle', 'wb') as handle:
		    pickle.dump(pots, handle, protocol=pickle.HIGHEST_PROTOCOL)

'''
import numpy
num_trials = 100
# Canonical situation test
for trials in range(num_trials):
	num_cards = numpy.random.randint(2, 8)
	if num_cards == 3 or num_cards == 4:
		num_cards = 5
	cards = numpy.random.choice(52, size=num_cards, replace=False)
	hole, board = cards[:2], cards[2:]
	pt = potential(cards)
	pt = random.choice(pt)
	f_val = '{:.3f}'.format(pt[1] / num_rollouts(num_cards))[1:]
	readable_hole = ' '.join([card_string(cd) for cd in hole])
	readable_hole = "{:<8}".format(readable_hole)
	readable_board = ' '.join([card_string(cd) for cd in board])
	readable_board = "{:<20}".format(readable_board)
	print(readable_hole, readable_board, f_val, pt)
'''