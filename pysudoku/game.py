from copy import copy
from functools import reduce
from .sudoku import Board, IllegalBoard, IllegalMove


class Game(object):
    def __init__(self, move):
        self._root = move

    @property
    def root(self):
        return self._root

    @property
    def leaves(self):
        def leaves_(move):
            if not move.moves:
                yield move
            else:
                for m in move.moves:
                    yield from leaves_(m)

        yield from leaves_(self._root)

    @property
    def solutions(self):
        return list(filter(lambda x: x.board.terminal, self.leaves))

    @property
    def dead(self):
        return list(filter(lambda x: not x.valid, self.leaves))

    @staticmethod
    def depth(move):
        depth = 0
        while move.parent:
            depth += 1
            move = move.parent
        return depth

    @staticmethod
    def moves(move):
        moves = [move]
        while move.parent:
            move = move.parent
            moves.append(move)
        return reversed(moves)

    @staticmethod
    def stats(move):
        moves = list(Game.moves(move))
        return dict(
            complexity=reduce(lambda x, z: x + z[0] ** z[1],
                              [(y.board.stats['initial_complexity'] - y.board.stats['final_complexity'], i+1)
                               for i, y in enumerate(reversed(moves))], 0),
            depth=Game.depth(move),
            init=str(moves[0]),
            moves=list(map(str, moves[1:])),
            board=str(move.board).split('\n'),
            terminal=move.board.terminal,
            stats=[dict(board=moves[k].board.stats,
                        block=getattr(moves[k].board, 'block_stats', None),
                        row=getattr(moves[k].board, 'row_stats', None),
                        column=getattr(moves[k].board, 'column_stats', None),
                        invariants=moves[k].invariants)
                   for k in range(len(moves))],
        )

    def play(self, move=None):
        move = move or self._root

        if move.board.terminal:
            yield move
        else:
            for markings in move.board.search():
                for attempt in map(lambda marking: Move(marking, move.board, move), markings):
                    move.append(attempt)
                    if not move.valid:
                        continue

                    yield from self.play(attempt)


class Move(object):
    def __init__(self, marking, board=None, parent=None):
        self.parent = parent
        self.marking = marking
        self.moves = []
        self.board = copy(board) if board else Board()

        try:
            for cell, value in marking:
                self.board(*cell).value = value
            self.invariants = self.board.reduce()
            self.valid = True
        except (IllegalBoard, IllegalMove):
            self.valid = False

    def append(self, move):
        self.moves.append(move)

    def __str__(self):
        return " ".join(map(lambda m: "{}={}".format("({},{})".format(*m[0]), m[1]), self.marking))



