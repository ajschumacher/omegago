def rectangular_start_state(shape):
    black, white = frozenset(), frozenset()
    blank = frozenset((i, j) for i in range(shape[0]) for j in range(shape[1]))
    return black, white, blank


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
