import time
import random

from rules import *
from game import *


def random_mover(choices, player, opponent, blank):
    return random.choice(choices)


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
        # To simulate for a fixed about of time:
        while time.time() < now + 6:  # seconds
            monte_carlo_tree_mover(choices, player, opponent, blank, tree)
            i += 1
        # To do a fixed number of simulations:
        # for _ in range(10):
        #     monte_carlo_tree_mover(choices, player, opponent, blank, tree)
        for choice, values in tree.items():
            print choice, values[0], values[1], values[0] / float(
                values[0] + values[1])
        print 'on', i, 'runs'
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
