import random


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


def adjacents(position):
    i, j = position
    return ((i, j+1), (i, j-1), (i+1, j), (i-1, j))


def contiguous(position, played, result=None):
    if result is None:
        result = []
    if position in played:
        result.append(position)
        for adjacent in adjacents(position):
            if adjacent not in result:
                contiguous(adjacent, played, result)
    return frozenset(result)


def has_freedom(positions, blank):
    for position in positions:
        for adjacent in adjacents(position):
            if adjacent in blank:
                return True
    return False


def get_move():
    row, col = raw_input('row (space) col: ').split(' ')
    return int(row), int(col)


def play(position, player, opponent, blank):
    if position not in blank:
        raise Exception('{} is not in {}'.format(position, blank))
    player = player.union(frozenset([position]))
    blank = blank.difference(frozenset([position]))
    for adjacent in adjacents(position):
        group = contiguous(adjacent, opponent)
        if not has_freedom(group, blank):
            opponent = opponent.difference(group)
            blank = blank.union(group)
    group = contiguous(position, player)
    if not has_freedom(group, blank):
        player = player.difference(group)
        blank = blank.union(group)
    return player, opponent, blank


def suicide(position, player, opponent, blank):
    player, opponent, blank = play(position, player, opponent, blank)
    if position not in player:
        return True
    return False


def ko(position,
       player, opponent, blank,
       last_player, last_opponent, last_blank):
    player, opponent, blank = play(position, player, opponent, blank)
    same_player = player == last_player
    same_opponent = opponent == last_opponent
    same_blank = blank == last_blank
    if same_player and same_opponent and same_blank:
        return True
    return False


def allowed(player, opponent, blank,
            last_player, last_opponent, last_blank):
    return tuple(position for position in blank
                 if not suicide(position, player, opponent, blank)
                 and not ko(position,
                            player, opponent, blank,
                            last_player, last_opponent,  last_blank))


def human_mover(choices, player, opponent, blank):
    while True:
        position = get_move()
        if position not in choices:
            print 'not an option'
        else:
            return position


def random_mover(choices, player, opponent, blank):
    return random.choice(choices)


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
    for _ in range(1000):
        choice = random_dist(choices.items())
        black, white, new_blank = play(choice, player, opponent, blank)
        result = game(black, white, new_blank,
                      random_mover, random_mover,
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
    for _ in range(1000):
        choice = random_dist(choices.items())
        black, white, new_blank = play(choice, player, opponent, blank)
        result = game(black, white, new_blank,
                      random_mover, random_mover,
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
black, white, blank = rectangular_start_state((4, 4))
# black, white = frozenset(), frozenset()
# blank = frozenset([(1, 1), (2, 1), (1, 2), (4, 4), (4, 5), (4, 6), (5, 4), (5, 5), (5, 6), (6, 4), (6, 5), (6, 6)])
print Counter(game(black, white, blank,
                   fixed_full_mover, human_mover,
                   show=True)
              for _ in range(1))

# while True:
#     print state_to_str(black, white, blank)
#     print 'for black'
#     while True:
#         position = get_move()
#         if position not in blank:
#             print 'not an option'
#         else:
#             black, white, blank = play(position, black, white, blank)
#             break
#     print state_to_str(black, white, blank)
#     print 'for white'
#     while True:
#         position = get_move()
#         if position not in blank:
#             print 'not an option'
#         else:
#             white, black, blank = play(position, white, black, blank)
#             break


# black = ((0, 2), (1, 0), (2, 1))
# white = ((0, 1), (1, 2), (2, 0))
# # shape = (3, 3)
# blank = ((0, 0), (1, 1), (2, 2))
# print state_to_str(black, white, blank)

# lines = ('   O * ',
#          ' *   O ',
#          ' O *   ')
# black, white, blank = lines_to_state(lines)
# print black
# print white
# print blank

# lines = (' O O * ',
#          ' * * * ',
#          ' O *   ')
# black, white, blank = lines_to_state(lines)
# print state_to_str(black, white, blank)
# print 'black', black
# print 'white', white
# print 'blank', blank
# print contiguous((0, 0), white)
# print contiguous((0, 0), black)
# print contiguous((1, 0), white)
# print contiguous((1, 0), black)

# print

# print has_freedom(contiguous((0, 0), white), blank)
# print has_freedom(contiguous((1, 0), black), blank)


# def array_to_str(array):
#     return '\n'.join(' ' + ' '.join(row) for row in array)


# def str_to_array(chars):
#     return [line[i+1:i+2] for line in chars.split('\n')
#             for i in range(0, len(line), 2)]




# def get(pos, array):
#     try:
#         cell = array[pos[0]][pos[1]]
#     except IndexError:
#         return False


# def has_freedom(pos, array, color=None, checked=None):
#     if pos in checked:
#         return False
#     try:
#         cell = array[pos]
#     except IndexError:
#         return False
#     if cell == ' ':
#         return True
#     if color is None:
#         color = cell
#     if cell != color:
#         return False
#     if checked is None:
#         checked = [pos]
#     else:
#         checked.append(pos)
#     if has_freedom((pos[0]))
#     print checked


# def contiguous(position, array, color=None, positions=None):
#     try:
#         cell = array[position]
#     except IndexError:
#         return []
#     return positions

# array = np.array([[' ', 'O', '*'],
#                   ['*', ' ', 'O'],
#                   ['O', '*', ' ']])
# print array_to_str(array)
# print str_to_array(chars)

# first: array (base Py or numpy, numeric or ASCII)
# second: black, white, shape
# third: black, white, blank
