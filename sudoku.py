from copy import deepcopy as copy

N = 9
M = 3
V = range(1,N+1)

class IllegalMove:
    pass

class Unit(object):
    def __init__(self):
        self._values = set(V)

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values

class Group(Unit):
    def __init__(self, cells):
        super(Group,self).__init__()
        self._cells = cells

    @property
    def cells(self):
        return self._cells

    def update(self, value):
        self.values.remove(value)
        for c in filter(lambda x: x.values, self.cells):
            c.values &= self.values

class Cell(Unit):
    def __init__(self, row, column):
        super(Cell,self).__init__()
        self._coord = (row, column)
        self._value = None
        self._block = None
        self._row = None
        self._column = None

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def validate_move(self, value):
        return value in self.block.values & self.column.values & self.row.values

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
        return "{}:{}".format("({},{})".format(*self._coord),self._value)

    def __repr__(self):
        return self.__str__()

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

class Board(Grid):
    def __init__(self, cells):
        super(Board,self).__init__(cells)

        def block(m, n):
            return [self.cells[i][j] for i in range(m*M,(m+1)*M) for j in range(n*M,(n+1)*M)]

        def row(m):
            return [self.cells[m][j] for j in range(N)]

        def column(n):
            return [self.cells[i][n] for i in range(N)]

        self.blocks = [[Block(block(m, n)) for n in range(M)] for m in range(M)]
        self.rows = [Row(row(i)) for i in range(N)]
        self.columns = [Column(column(j)) for j in range(N)]

        self._moves = []

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

class Move(object):
    def __init__(self, board, move):
        self.cell, self.value = move
        self.parent = board
        self.child = copy(board)
        self.child(*self.cell).value = self.value
        board.moves().append(self)

class Game(object):
    def __init__(self, board):
        self._root = board
        self._cursor = None

    def move(self, cell, value):
        move = Move(self._cursor or self._root, (cell, value))
        self._cursor = move.parent

board = Board(cells=[[Cell(i,j) for j in range(N)] for i in range(N)])

marking = {(0,1):1, (2,3):7, (4,4):3, (5,6):5}

for c,v in marking.items():
    board(*c).value = v

