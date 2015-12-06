from sudoku import Board, IllegalBoard, V, N
from game import Game, Move
from random import choice, shuffle
from itertools import product


def random_board():
    def randrow(row):
        # randomize values of each cell across a row and choose a single combination
        values = [list(c.values) for c in row]
        for v in values:
            shuffle(v)
        return next(map(lambda x: list(zip([c.coord for c in row], x)),
                        filter(lambda x: len(x) == len(set(x)), product(*values))))

    while True:
        try:
            b = Board()
            for cell in b.rows[0]:
                cell.value = choice(list(cell.values))

            for row in b.rows[1:]:
                for c, v in randrow(row):
                    b(*c).value = v

            return b
        except IllegalBoard:
            pass


def board(marking):
    b = Board()
    for c, v in marking:
        b(*c).value = v
    return b


def create_board(difficulty, b=None):
    if b is None:
        b = random_board()

    def rank(b):
        from math import ceil, log
        return ceil(log(b.complexity()))

    while rank(b) < difficulty:
        # pick a value to erase
        value = choice(list(V))

        # pick a number of cells from which to erase this value
        count = choice(range(N))

        # pick random cells to erase
        cells = list(filter(lambda x: x.value == value, b))
        shuffle(cells)
        for cell in cells[:count]:
            cell.value = None

    return b


def game(marking):
    return Game(Move(marking))


def game_from_board(b):
    return game(b.marking)


def random_game(difficulty):
    return game_from_board(create_board(difficulty))
