from collections import Counter

from rules import *
from players import *


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
