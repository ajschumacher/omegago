def adjacent_to(position):
    i, j = position
    adjacent_positions = ((i-1, j),
                          (i, j-1), (i, j+1),
                          (i+1, j))
    return adjacent_positions


def contiguous(position, played, result=None):
    if result is None:
        result = []
    if position in played:
        result.append(position)
        for adjacent in adjacent_to(position):
            if adjacent not in result:
                contiguous(adjacent, played, result)
    return frozenset(result)


def has_freedom(positions, blank):
    for position in positions:
        for adjacent in adjacent_to(position):
            if adjacent in blank:
                return True
    return False


def play(position, player, opponent, blank):
    if position not in blank:
        raise Exception('{} is not in {}'.format(position, blank))
    player = player.union(frozenset([position]))
    blank = blank.difference(frozenset([position]))
    for adjacent in adjacent_to(position):
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
                            last_player, last_opponent, last_blank))
