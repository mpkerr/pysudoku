from sudoku import Board
from random import choice, shuffle
from itertools import product


def random_board():
    def randrow(row):
        # randomize values of each cell across a row and choose a single combination
        values = [list(c.values) for c in row]
        for v in values:
            shuffle(v)
        return next(map(lambda x: list(zip([c.coord for c in row], x)), filter(lambda x: len(x) == len(set(x)), product(*values))))

    board = Board()
    for cell in board.rows[0]:
        cell.value = choice(list(cell.values))

    for row in board.rows[1:]:
        for c, v in randrow(row):
            board(*c).value = v

    return board