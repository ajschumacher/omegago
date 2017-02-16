import time
import random

from pprint import pprint as pp

from rules import *


def thompson(data):
    draws = [(random.betavariate(values[0], values[1]), choice)
             for choice, values in data.items()]
    return max(draws)[1]


def random_dist(l):
    # based on http://stackoverflow.com/questions/4265988/generate-random-numbers-with-a-given-numerical-distribution
    total = float(max(sum(value for item, value in l), 1))  # at least one
    r = random.uniform(0, 1)
    s = 0
    for item, value in l:
        try:
            s += value / total
        except ZeroDivisionError:
            print l, item, value, total
        if s >= r:
            return item
    return item  # Might occur because of floating point inaccuracies


def bounds(positions):
    row_min = min(position[0] for position in positions)
    row_max = max(position[0] for position in positions)
    col_min = min(position[1] for position in positions)
    col_max = max(position[1] for position in positions)
    return (row_min, row_max), (col_min, col_max)


def state_to_str(black, white, blank, played=(None, None), number=False):
    (row_min, row_max), (col_min, col_max) = bounds(
        black.union(white).union(blank))
    result = ''
    if number:
        result += '  ' + ' '.join(
            [str(j) for j in range(col_min, col_max + 1)]) + '\n'
    for i in range(row_min, row_max + 1):
        if number:
            result += str(i)
        for j in range(col_min, col_max + 1):
            if (i, j) == played:
                result += '-'
            else:
                result += ' '
            if (i, j) in black:
                result += '*'
            elif (i, j) in white:
                result += 'O'
            elif (i, j) in blank:
                result += ' '
            else:
                result += 'X'
        result += '\n'
    return result


def str_to_state(chars):
    lines = chars.rstrip('\n').split('\n')
    return lines_to_state(lines)


def lines_to_state(lines):
    black, white, blank = frozenset(), frozenset(), frozenset()
    for i in range(len(lines)):
        for j in range(len(lines[i]) / 2):
            cell = lines[i][1 + 2 * j]
            if cell == '*':
                black = black.union(frozenset([(i, j)]))
            elif cell == 'O':
                white = white.union(frozenset([(i, j)]))
            elif cell == ' ':
                blank = blank.union(frozenset([(i, j)]))
    return black, white, blank


def rectangular_start_state(shape):
    black, white = frozenset(), frozenset()
    blank = frozenset((i, j) for i in range(shape[0]) for j in range(shape[1]))
    return black, white, blank


def get_move():
    row, col = raw_input('row (space) col: ').split(' ')
    return int(row), int(col)


def human_mover(choices, player, opponent, blank):
    while True:
        position = get_move()
        if position not in choices:
            print 'not an option'
        else:
            return position


def random_mover(choices, player, opponent, blank):
    return random.choice(choices)


def biased_random_mover(choices, player, opponent, blank):
    choices = {choice: 0 for choice in choices}
    for choice in choices.keys():
        black, white, new_blank = play(choice, player, opponent, blank)
        outcome = len(black) - len(white)  # pretending we're black
        choices[choice] = outcome
    smallest = min(value for value in choices.values())
    choices = {choice: (value - smallest + 1) * len(blank)
               for choice, value in choices.items()}
    choice = random_dist(choices.items())
    return choice


def even_full_mover(choices, player, opponent, blank):
    results = []
    for choice in choices:
        black, white, new_blank = play(choice, player, opponent, blank)
        value = 0
        for _ in range(100):
            result = game(black, white, new_blank,
                          random_mover, random_mover,
                          player, opponent, blank)
            if result == 'black':
                value += 1
        results.append((value, choice))
    print sorted(results)
    return max(results)[1]


def fixed_full_mover(choices, player, opponent, blank):
    choices = {choice: 10 for choice in choices}
    for _ in range(400):
        choice = random_dist(choices.items())
        black, white, new_blank = play(choice, player, opponent, blank)
        result = game(black, white, new_blank,
                      biased_random_mover, biased_random_mover,
                      player, opponent, blank)
        choices[choice] += result
        least = min(value for value in choices.values())
        if least < 1:
            for item in choices.keys():
                choices[item] += abs(least) + 1
    print sum(value for item, value in choices.iteritems())
    print choices
    return max((value, item) for item, value in choices.iteritems())[1]


def fixed_trunc_mover(choices, player, opponent, blank):
    choices = {choice: 10 for choice in choices}
    for _ in range(400):
        choice = random_dist(choices.items())
        black, white, new_blank = play(choice, player, opponent, blank)
        result = game(black, white, new_blank,
                      biased_random_mover, biased_random_mover,
                      player, opponent, blank, max_steps=4)
        choices[choice] += result
        least = min(value for value in choices.values())
        if least < 1:
            for item in choices.keys():
                choices[item] += abs(least)
    print sum(value for item, value in choices.iteritems())
    print choices
    return max((value, item) for item, value in choices.iteritems())[1]


def even_trunc_mover(choices, player, opponent, blank):
    results = []
    for choice in choices:
        black, white, new_blank = play(choice, player, opponent, blank)
        value = 0
        for _ in range(100):
            result = game(black, white, new_blank,
                          random_mover, random_mover,
                          player, opponent, blank, max_steps=4)
            if result == 'black':
                value += 1
        results.append((value, choice))
    print sorted(results)
    return max(results)[1]


def monte_carlo_tree_mover(choices, player, opponent, blank, tree=None):
    # tree is like {choice: [wins, losses, tree]}
    if tree is None:
        tree = {}
        now, i = time.time(), 0
        while time.time() < now + 6:
            monte_carlo_tree_mover(choices, player, opponent, blank, tree)
            i += 1
        # for _ in range(10):
        #     monte_carlo_tree_mover(choices, player, opponent, blank, tree)
        pp(tree)
        print 'on', i, 'runs'
        # for choice, values in tree.items():
        #     print choice, values[0], values[1], values[0] / float(
        #         values[0] + values[1])
        rates = [(values[0] / float(values[0] + values[1]), choice)
                 for choice, values in tree.items()]
        return max(rates)[1]
    else:
        if len(choices) == 0:  # game over
            return True  # our loss is win of caller
        if len(tree) < len(choices):  # Never tried some moves.
            choice = [choice for choice in choices if choice not in tree][0]
            new_player, new_opponent, new_blank = play(
                choice, player, opponent, blank)
            result = game(new_opponent, new_player, new_blank,
                          random_mover, random_mover,
                          opponent, player, blank)
            win = not result > 0  # opponent loses
            if win:
                tree[choice] = [2, 1, {}]
            else:
                tree[choice] = [1, 2, {}]
        else:
            choice = thompson(tree)
            new_player, new_opponent, new_blank = play(
                choice, player, opponent, blank)
            new_choices = allowed(new_opponent, new_player, new_blank,
                                  opponent, player, blank)
            win = monte_carlo_tree_mover(new_choices,
                                         new_opponent, new_player, new_blank,
                                         tree=tree[choice][2])
            if win:
                tree[choice][0] += 1
            else:
                tree[choice][1] += 1
        return not win


def game(black, white, blank,
         black_mover, white_mover,
         last_black=None, last_white=None, last_blank=None,
         first='black', show=False, pause=False,
         max_steps=500):
    steps = 0
    if show:
        print state_to_str(black, white, blank, number=True)
    while True:
        if max_steps < steps:
            if show:
                print 'taking forever; calling it based on pieces'
            return len(black) - len(white)
        if first == 'white':
            first = 'black'
        else:
            choices = allowed(black, white, blank,
                              last_black, last_white, last_blank)
            if not choices:
                if show:
                    print 'white wins!'
                return len(black) - len(white)
            position = black_mover(choices, black, white, blank)
            last_black, last_white, last_blank = black, white, blank
            black, white, blank = play(position, black, white, blank)
        if show:
            print state_to_str(black, white, blank,
                               played=position, number=True)
        choices = allowed(white, black, blank,
                          last_white, last_black, last_blank)
        if not choices:
            if show:
                print 'black wins!'
            return len(black) - len(white)
        if pause:
            raw_input()
        position = white_mover(choices, white, black, blank)
        last_black, last_white, last_blank = black, white, blank
        white, black, blank = play(position, white, black, blank)
        steps += 1
        if show:
            print state_to_str(black, white, blank,
                               played=position, number=True)


from collections import Counter

# lines = ('       ',
#          '       ',
#          '       ')
# lines = ('     ',
#          '     ')
# lines = ('   O *   ',
#          ' O   O * ',
#          '   O *   ')
# black, white, blank = lines_to_state(lines)
black, white, blank = rectangular_start_state((5, 5))
# black, white = frozenset(), frozenset()
# blank = frozenset([(1, 1), (2, 1), (1, 2), (4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)])
results = [game(black, white, blank,
                monte_carlo_tree_mover, human_mover,
                show=True)
           for _ in range(1)]
print Counter(results)
wins = ['black' if result > 0 else 'white' for result in results]
print Counter(wins)
