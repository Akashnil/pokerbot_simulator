from hand_strength import *

pots = {}

def num_rollouts(situation):
	ret = 1
	for i in range(5 - len(situation[0])):
		ret *= (46+i)
	return ret

def canonical(situation):
	board, hole = situation
	if len(board) == 5:
		return canonical_situation(situation)
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

	return tuple([x[0] + x[1] * 13 for x in board]), tuple([x[0] + x[1] * 13 for x in hole])

num_curves = 0
curves_idx_dict = {}
idx_curves_dict = {}

# returns a list of (rank, count) which means this situation achieves the given rank or better 
# count times out of all the total_rollouts
def potential(situation):
	global num_curves
	global pots
	global curves_idx_dict
	global idx_curves_dict
	if len(situation[0]) == 5:
		return ((hand_strength(situation)[0], 1),)
	situation = canonical(situation)
	board, hole = situation
	if situation in pots:
		return idx_curves_dict[pots[situation]]
	all_points = []
	for cd in range(52):
		if cd in board:
			continue
		if cd in hole:
			continue
		board_ = list(board)
		board_.append(cd)
		cum_list = potential((board_, hole))
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
	if current_count != num_rollouts(situation):
		print (ret)
		print (situation, current_count, num_rollouts(situation))
		assert current_count == num_rollouts(situation)
	ret = tuple(ret)
	if ret in curves_idx_dict:
		pots[situation] = curves_idx_dict[ret]
	else:
		curves_idx_dict[ret] = num_curves
		idx_curves_dict[num_curves] = ret
		pots[situation] = num_curves
		num_curves += 1
	return ret

import pickle
import random

try:
    with open('potential_dict.pickle', 'rb') as handle:
    	pots = pickle.load(handle)
    #with open('curves_idx_dict.pickle', 'rb') as handle:
    #	curves_idx_dict = pickle.load(handle)
    with open('idx_curves_dict.pickle', 'rb') as handle:
    	idx_curves_dict = pickle.load(handle)
except FileNotFoundError:
	for c0 in range(52):
		for c1 in range(c0+1, 52):
			situ = ((), (c0, c1))
			pt = potential(situ)
			pt = random.choice(pt)
			f_val = '{:.3f}'.format(pt[1] / num_rollouts(situ))[1:]
			print ((c0, c1), f_val, pt)
	with open('potential_dict.pickle', 'wb') as handle:
	    pickle.dump(pots, handle, protocol=pickle.HIGHEST_PROTOCOL)
	#with open('curves_idx_dict.pickle', 'wb') as handle:
	#    pickle.dump(curves_idx_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
	with open('idx_curves_dict.pickle', 'wb') as handle:
	    pickle.dump(idx_curves_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

import numpy
num_trials = 500

# Canonical situation test
for trials in range(num_trials):
	num_cards = numpy.random.randint(2, 8)
	if num_cards == 3 or num_cards == 4:
		num_cards = 5
	cards = numpy.random.choice(52, size=num_cards, replace=False)
	board = cards[:-2]
	hole = cards[-2:]
	situation = canonical((board, hole))
	board, hole = situation
	pt = potential(situation)
	pt = random.choice(pt)
	f_val = '{:.3f}'.format(pt[1] / num_rollouts(situation))[1:]
	readable_hole = ' '.join([card_string(cd) for cd in hole])
	readable_hole = "{:<8}".format(readable_hole)
	readable_board = ' '.join([card_string(cd) for cd in board])
	readable_board = "{:<20}".format(readable_board)
	print(readable_hole, readable_board, f_val, pt)
