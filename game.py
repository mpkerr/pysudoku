from sudoku import Board, IllegalBoard, IllegalMove
from copy import copy
from math import log, ceil


class Game(object):
    def __init__(self, move, max_depth=10):
        self._move = move
        self._moves = []
        self._max_depth = max_depth
        self._depth = 0

    def pop(self):
        self._move = self._move.parent
        return self.board()

    def push(self, move):
        self._move = move
        self._depth = max(self._depth, self.depth())
        return self.board()

    def board(self):
        return self._move.board

    def depth(self):
        depth = 0
        move = self._move
        while move.parent:
            move = move.parent
            depth += 1
        return depth

    def play(self, board=None):
        board = board or self.board()

        if not board.terminal():
            if self.depth() >= self._max_depth:
                return board

            for markings in board.search():
                for move in map(lambda marking: Move(marking, board, self._move), markings):
                    self._moves.append(move)
                    if not move.valid:
                        continue

                    board = self.play(self.push(move))
                    if board.terminal():
                        return board

                    board = self.pop()

        return board

    def stats(self):
        moves = list(self.moves())
        return dict(
            complexity=ceil(log(moves[0].board.complexity())),
            depth=self.depth(),
            max_depth=self._depth,
            total_moves= len(self._moves) - 1,
            dead_ends=len(list(filter(lambda x: not x.valid, self._moves))),
            init=str(moves[0]),
            moves=list(map(str, moves[1:])),
            board=str(self.board()).split('\n'),
            terminal=self.board().terminal()
        )

    def moves(self):
        move = self._move
        moves = [move]
        while move.parent:
            move = move.parent
            moves.append(move)
        return reversed(moves)


class Move(object):
    def __init__(self, marking, board=None, parent=None):
        self.parent = parent
        self.marking = marking
        self.board = copy(board) if board else Board()

        try:
            for cell, value in marking:
                self.board(*cell).value = value
            self.board.reduce()
            self.valid = True
        except (IllegalBoard, IllegalMove):
            self.valid = False

    def __str__(self):
        return " ".join(map(lambda m: "{}={}".format("({},{})".format(*m[0]), m[1]), self.marking))



