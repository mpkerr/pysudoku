from sudoku import Board, IllegalBoard, IllegalMove
from copy import copy
from functools import reduce
import operator


class Game(object):
    def __init__(self, move, max_depth=10):
        self._move = move
        self._max_depth = max_depth
        self._depth = 0

    def push(self, move):
        self._move = move
        self._depth = max(self._depth, self.depth)
        return self.board

    def pop(self):
        self._move = self._move.parent
        return self.board

    @property
    def move(self):
        return self._move

    @property
    def board(self):
        return self._move.board

    @property
    def stats(self):
        moves = list(self.moves)
        return dict(
            depth=self.depth,
            max_depth=self._depth,
            dead=self.dead,
            init=str(moves[0]),
            moves=list(map(str, moves[1:])),
            board=str(self.board).split('\n'),
            terminal=self.board.terminal(),
            stats=[dict(board=moves[k].board.stats,
                        block=moves[k].board.block_stats,
                        row=moves[k].board.row_stats,
                        column=moves[k].board.column_stats)
                   for k in range(len(moves))],
        )

    @property
    def dead(self):
        def _dead(move):
            if not move.valid:
                return 1
            return reduce(operator.add, map(_dead, move.moves), 0)

        return _dead(self.root)

    @property
    def root(self):
        move = self._move
        while move.parent:
            move = move.parent
        return move

    @property
    def moves(self):
        move = self._move
        moves = [move]
        while move.parent:
            move = move.parent
            moves.append(move)
        return reversed(moves)

    @property
    def depth(self):
        depth = 0
        move = self._move
        while move.parent:
            move = move.parent
            depth += 1
        return depth

    def play(self, board=None):
        board = board or self.board

        if not board.terminal():
            if self.depth >= self._max_depth:
                return board

            for markings in board.search():
                for move in map(lambda marking: Move(marking, board, self._move), markings):
                    self.move.append(move)
                    if not move.valid:
                        continue

                    board = self.play(self.push(move))
                    if board.terminal():
                        return board

                    board = self.pop()

        return board


class Move(object):
    def __init__(self, marking, board=None, parent=None):
        self.parent = parent
        self.marking = marking
        self.moves = []
        self.board = copy(board) if board else Board()

        try:
            for cell, value in marking:
                self.board(*cell).value = value
            self.board.reduce()
            self.valid = True
        except (IllegalBoard, IllegalMove):
            self.valid = False

    def append(self, move):
        self.moves.append(move)

    def __str__(self):
        return " ".join(map(lambda m: "{}={}".format("({},{})".format(*m[0]), m[1]), self.marking))



