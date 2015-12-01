from functools import reduce
from copy import copy

M = 3
N = M ** 2
V = range(1,N+1)

class IllegalMove(BaseException):
    pass

class IllegalBoard(BaseException):
    pass

class Unit(object):
    def __init__(self, values):
        self._values = values

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values

class Cell(Unit):
    def __init__(self, row, column, value=None, values=None):
        super(Cell,self).__init__(None if value else values or set(V))
        self._coord = (row, column)
        self._value = value
        self._block = None
        self._row = None
        self._column = None

    def __copy__(self):
        return Cell(self._coord[0], self._coord[1], self._value, copy(self._values))

    def __eq__(self, other):
        return self._value == other._value

    def __ne__(self, other):
        return self._value != other._value

    def validate_move(self, value):
        return not self.value and value in self.values

    @property
    def coord(self):
        return self._coord

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if not self.validate_move(value):
            raise IllegalMove()
        self._value = value
        self.values = None
        for x in [self.block, self.row, self.column]:
            x.update(value)

    @property
    def block(self):
        return self._block

    @block.setter
    def block(self, block):
        self._block = block

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, row):
        self._row = row

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, column):
        self._column = column

    def __str__(self):
        return "{}:{}".format("({},{})".format(*self._coord),self._value or self._values)

    def __repr__(self):
        return self.__str__()

class Group(Unit):
    def __init__(self, cells):
        super(Group,self).__init__(reduce(lambda x, y: x | y, filter(None, map(lambda x: x.values, cells)), set()))
        self._cells = cells

    @property
    def cells(self):
        return self._cells

    def update(self, value):
        self.values.remove(value)
        for c in filter(lambda x: x.values, self.cells):
            c.values &= self.values
            if c.values == set():
                raise IllegalBoard()

    def groups(self):
        """groups cells with the same open values"""
        groups = {}
        for c in filter(lambda x: x.values, self._cells):
            if tuple(c.values) in groups:
                groups[tuple(c.values)].append(c)
            else:
                groups[tuple(c.values)] = [c]
        return groups

class Block(Group):
    def __init__(self, cells):
        super(Block,self).__init__(cells)
        for c in cells:
            c.block = self

class Row(Group):
    def __init__(self, cells):
        super(Row,self).__init__(cells)
        for c in cells:
            c.row = self

class Column(Group):
    def __init__(self, cells):
        super(Column,self).__init__(cells)
        for c in cells:
            c.column = self

class Grid(object):
    def __init__(self, cells):
        self.cells = cells

    def __call__(self, i, j):
        return self.cells[i][j]

    def __iter__(self):
        return (x for y in self.cells for x in y)

class Board(Grid):
    def __init__(self, cells=None):
        super(Board,self).__init__(cells or [[Cell(i,j) for j in range(N)] for i in range(N)])

        def block(m, n):
            return [self.cells[i][j] for i in range(m*M,(m+1)*M) for j in range(n*M,(n+1)*M)]

        def row(m):
            return [self.cells[m][j] for j in range(N)]

        def column(n):
            return [self.cells[i][n] for i in range(N)]

        self.blocks = [Block(block(m, n)) for n in range(M) for m in range(M)]
        self.rows = [Row(row(i)) for i in range(N)]
        self.columns = [Column(column(j)) for j in range(N)]

        self._moves = []

    def __copy__(self):
        return Board([[copy(self.cells[i][j]) for j in range(N)] for i in range(N)])

    def open(self, n=None):
        for c in self:
            if not c.value and (n is None or len(c.values) == n):
                yield c

    def terminal(self):
        for cell in self:
            if not cell.value:
                return False
        return True

    def single_reduce(self):
        singles = []
        for single in self.open(1):
            single.value = next(iter(single.values))
            singles.append(single)
        return singles

    def block_reduce(self):
        """Apply the 'geometrical' argument. If this block
        contains M-1 complete rows or columns then the remaining
        values apply exclusively to the 'open' row or column
        """
        for b in self.blocks:
            rows = {row: 0 for row in set([c.coord[0] for c in b.cells])}
            cols = {col: 0 for col in set([c.coord[1] for c in b.cells])}
            for c in b.cells:
                row, column = c.coord
                if not c.value:
                    rows[row] += 1
                    cols[column] += 1
            rows = list(filter(lambda x: rows[x], rows))
            cols = list(filter(lambda x: cols[x], cols))

            if len(rows) == 1:
                for row in rows:
                    values = reduce(lambda x, y: x | y.values, filter(lambda x: x.coord[0] == row and x.values, b.cells), set())
                    for c in self.rows[row].cells:
                        if c.values and c.block is not b:
                            c.values -= values

            if len(cols) == 1:
                for col in cols:
                    values = reduce(lambda x, y: x | y.values, filter(lambda x: x.coord[1] == col and x.values, b.cells), set())
                    for c in self.columns[col].cells:
                        if c.values and c.block is not b:
                            c.values -= values

    @property
    def moves(self):
        return self._moves

    def __eq__(self, other):
        for i in range(N):
            for j in range(N):
                if self(i,j) != other(i,j):
                    return False
        return True

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return "\n".join([",".join(map(lambda x: str(x.value or 0),self.cells[i])) for i in range(N)])

class Move(object):
    def __init__(self, board, move):
        self.cell, self.value = move
        self.parent = board
        self.child = copy(board)
        self.child(*self.cell).value = self.value
        board.moves.append(self)

    def __str__(self):
        return "{}={}".format("({},{})".format(*self.cell),self.value)

class Game(object):
    def __init__(self, board):
        self._board = board

    def play(self, board=None):
        board = board or self._board

        while not board.terminal() and board.single_reduce():
            board.block_reduce()

        for cell in board.open(n=2):
            for value in cell.values:
                try:
                    move = Move(board, (cell.coord, value)) 
                    print(move)
                    print(move.child)
                    attempt = self.play(move.child)
                    if attempt.terminal():
                        return attempt
                except IllegalBoard:
                    continue

        return board

    @property
    def board(self):
        return self._board

    @staticmethod
    def move(board, cell, value):
        return Move(board, (cell, value)).child

easy = Board()
easy_marking = {
    (0,0): 9, (0,3): 1,
    (1,5): 8, (1,6): 5, (1,8): 6,
    (2,3): 5, (2,4): 9, (2,5): 2, (2,6): 3,
    (3,2): 1, (3,3): 3, (3,7): 6,
    (4,0): 4, (4,1): 2, (4,3): 7, (4,4): 8, (4,5): 6, (4,7): 1, (4,8): 5,
    (5,1): 7, (5,5): 1, (5,6): 4,
    (6,2): 6, (6,3): 8, (6,4): 2, (6,5): 4,
    (7,0): 1, (7,2): 5, (7,3): 9,
    (8,5): 5, (8,8): 3
}
for c,v in easy_marking.items():
    easy(*c).value = v

hard = Board()
hard_marking = {
    (0,5): 8, (0,8): 1,
    (1,1): 9, (1,2): 6, (1,6): 8, (1,8): 7,
    (2,4): 3, (2,5): 7, (2,7):6,
    (3,0): 6, (3,3): 2, (3,4): 1, (3,7): 3, (3,8): 4,
    (4,2): 3, (4,6): 1,
    (5,0): 5, (5,1): 1, (5,4): 4, (5,5): 3, (5,8): 9,
    (6,1): 3, (6,3): 5, (6,4): 2,
    (7,0): 2, (7,2): 4, (7,6): 9, (7,7): 5,
    (8,0): 1, (8,3): 8
}
for c,v in hard_marking.items():
    hard(*c).value = v

