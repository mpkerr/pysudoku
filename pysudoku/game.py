from sudoku import Board, IllegalBoard, IllegalMove
from copy import copy


class Game(object):
    def __init__(self, move):
        self._root = move

    @property
    def root(self):
        return self._root

    @property
    def leafs(self):
        leafs = []

        def leafs_(move):
            if not move.moves:
                leafs.append(move)
            else:
                for m in move.moves:
                    leafs_(m)

        leafs_(self._root)
        return leafs

    @property
    def solutions(self):
        return list(filter(lambda x: x.board.terminal, self.leafs))

    @property
    def dead(self):
        return list(filter(lambda x: not x.valid, self.leafs))

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
        return list(reversed(moves))

    @property
    def stats(self):
        def stats_(move):
            moves = list(Game.moves(move))
            return dict(
                depth=Game.depth(move),
                init=str(moves[0]),
                moves=list(map(str, moves[1:])),
                board=str(move.board).split('\n'),
                terminal=move.board.terminal,
                stats=[dict(board=moves[k].board.stats,
                            block=getattr(moves[k].board, 'block_stats', None),
                            row=getattr(moves[k].board, 'row_stats', None),
                            column=getattr(moves[k].board, 'column_stats', None))
                       for k in range(len(moves))],
            )
        return list(map(stats_, self.solutions))

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
            self.board.reduce()
            self.valid = True
        except (IllegalBoard, IllegalMove):
            self.valid = False

    def append(self, move):
        self.moves.append(move)

    def __str__(self):
        return " ".join(map(lambda m: "{}={}".format("({},{})".format(*m[0]), m[1]), self.marking))



