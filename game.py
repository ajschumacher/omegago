from collections import Counter

from rules import *
from board import *
from players import *


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
# lines = ('       ',
#          '       ',
#          '       ')
# lines = ('     ',
#          '     ')
# lines = ('   O *   ',
#          ' O   O * ',
#          '   O *   ')
# black, white, blank = lines_to_state(lines)


def main():
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


if __name__ == '__main__':
    main()
