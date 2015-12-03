from functools import reduce
from itertools import product
from copy import copy

M = 3
N = M ** 2
V = range(1,N+1)

class IllegalMove(BaseException):
    def __init__(self, cell, value ):
        self._cell = cell
        self._value = value

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
            raise IllegalMove(self.coord, value)
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
            if len(c.values) == 0:
                raise IllegalBoard()

    def open(self, n=None):
        for c in self._cells:
            if not c.value and (n is None or len(c.values) == n):
                yield c

    def combinations(self, n=None):
        cells = list(self.open(n))
        return list(map(lambda x: list(zip([c.coord for c in cells], x)),
                        filter(lambda x: len(x) == len(set(x)), product(*[c.values for c in cells]))))

class Block(Group):
    def __init__(self, cells):
        super(Block,self).__init__(cells)
        for c in cells:
            c.block = self

    def reduce(self):
        vals = set()

        rowvals = {v: set() for v in self.values}
        colvals = {v: set() for v in self.values}

        for cell in filter(lambda c: c.values, self.cells):
            for value in cell.values:
                rowvals[value].add(cell.coord[0])
                colvals[value].add(cell.coord[1])

        for v in filter(lambda v: len(rowvals[v]) == 1, rowvals):
            row = rowvals[v].pop()
            for cell in self.cells:
                if cell.coord[0] == row:
                    for c in cell.row.cells:
                        if c.block is not self and c.values and v in c.values:
                            c.values.remove(v)
                            vals.add(v)

        for v in filter(lambda v: len(colvals[v]) == 1, colvals):
            col = colvals[v].pop()
            for cell in self.cells:
                if cell.coord[1] == col:
                    for c in cell.column.cells:
                        if c.block is not self and c.values and v in c.values:
                            c.values.remove(v)
                            vals.add(v)

        return vals

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

    def __copy__(self):
        return Board([[copy(self.cells[i][j]) for j in range(N)] for i in range(N)])

    def search(self):
        blocks = sorted([block.combinations() for block in self.blocks], key=len)
        rows = sorted([row.combinations() for row in self.rows], key=len)
        columns = sorted([column.combinations() for column in self.columns], key=len)
        return sorted(list(map(lambda x: next(iter(x)), filter(None,[blocks, rows, columns]))), key=len)

    def open(self, n=None):
        for c in self:
            if not c.value and (n is None or len(c.values) == n):
                yield c

    def terminal(self):
        for cell in self:
            if not cell.value:
                return False
        return True

    def reduce(self):
        while True:
            for cell in self.open(1):
                cell.value = next(iter(cell.values))

            if not reduce(lambda x, y: x or y, [block.reduce() for block in self.blocks], False):
                break

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
        return " ".join(map(lambda m: "{}={}".format("({},{})".format(*m[0]),m[1]), self.marking))

class Game(object):
    def __init__(self, move, max_depth=10):
        self._move = move
        self._max_depth = max_depth

    def pop(self):
        self._move = self._move.parent
        return self.board()

    def push(self, move):
        self._move = move
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
                for move in list(map(lambda marking: Move(marking, board, self._move), markings)):
                    if not move.valid:
                        continue

                    board = self.play(self.push(move))
                    if board.terminal():
                        return board

                    board = self.pop()

        return board

def game(marking):
    return Game(Move(marking))

def board(marking):
    board = Board()
    for c,v in marking:
        board(*c).value = v
    return board

