from functools import reduce
from itertools import product, combinations, chain
from copy import copy
from collections import namedtuple, Counter
import operator
import math

M = 3
N = M ** 2
V = range(1, N+1)


class IllegalMove(BaseException):
    def __init__(self, cell, value):
        self._cell = cell
        self._value = value


class IllegalBoard(BaseException):
    pass


class Unit(object):
    """A Unit has a set of available values"""
    def __init__(self, values):
        self._values = values

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, values):
        self._values = values


class Cell(Unit):
    """A Cell represents an entry in a sudoku grid. A Cell belongs
    to three groups: a block, a row, and a column"""
    Coord = namedtuple('Coord', ['row', 'column'])

    def __init__(self, row, column, value=None, values=None):
        super(Cell, self).__init__(None if value else values or set(V))
        self._coord = Cell.Coord(row, column)
        self._value = value
        self._block = None
        self._row = None
        self._column = None

    def __copy__(self):
        return Cell(self._coord[0], self._coord[1], self._value, copy(self._values))

    def __eq__(self, other):
        return self._coord == other._coord and self._value == other._value

    def __ne__(self, other):
        return self._coord != other._coord or self._value != other._value

    @property
    def coord(self):
        return self._coord

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value:
            if not self.value and value not in self.values:
                raise IllegalMove(self.coord, value)
            self._value = value
            self.values = None
            for group in self.groups:
                group.values.remove(value)
                for cell in filter(lambda c: c.values and value in c.values, group.cells):
                    cell.values.remove(value)
                    if len(cell.values) == 0:
                        raise IllegalBoard()
        elif value != self._value:
            for group in self.groups:
                group.values.add(self.value)
            self.values = set([self._value])
            self._value = None
            for group in self.groups:
                for cell in filter(lambda c: c.values, group.cells):
                    cell.values |= cell.block.values & cell.row.values & cell.column.values

    @property
    def groups(self):
        return [self.block, self.row, self.column]

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
        return "{}:{}".format("({},{})".format(*self._coord), self._value or self._values)

    def __repr__(self):
        return self.__str__()


class Group(Unit):
    """A Group represents a collection of cells. Either a Block, a Row, or a Column"""
    def __init__(self, cells):
        super(Group, self).__init__(reduce(lambda x, y: x | y, filter(None, map(lambda x: x.values, cells)), set()))
        self._cells = cells
        self._stats = Counter(reduce=0)

    def __iter__(self):
        return iter(self._cells)

    @property
    def cells(self):
        return self._cells

    @property
    def stats(self):
        return self._stats

    def open(self, n=None):
        for c in self._cells:
            if not c.value and (n is None or len(c.values) == n):
                yield c

    def combinations(self, n=None):
        cells = list(self.open(n))
        return list(map(lambda x: list(zip([c.coord for c in cells], x)),
                        filter(lambda x: len(x) == len(set(x)), product(*[c.values for c in cells]))))

    def reduce(self):
        """Apply n-ary exclusion to reduce the possible values available
        to cells in this group"""
        vals = set()

        for count in range(2, M+1):
            pairs = list(self.open(count))
            if len(pairs) >= count:
                for pairwise in combinations(pairs, count):
                    if reduce(operator.eq, map(lambda x: x.values, pairwise)):
                        for c in self.cells:
                            if c not in pairwise and c.values and c.values & pairwise[0].values:
                                vals |= c.values - pairwise[0].values
                                c.values -= pairwise[0].values
                                self._stats[count] += 1

        if vals:
            self._stats['reduce'] += 1

        return vals


class Block(Group):
    """A Block is a MxM group of adjacent cells"""
    def __init__(self, cells):
        super(Block, self).__init__(cells)
        for c in cells:
            c.block = self

    def reduce(self):
        """Apply hidden-value elimination to reduce the possible
        values available to cells in this block"""
        vals = super(Block, self).reduce()

        rowvals = {v: set() for v in self.values}
        colvals = {v: set() for v in self.values}

        for cell in filter(lambda c: c.values, self.cells):
            for value in cell.values:
                rowvals[value].add(cell.coord[0])
                colvals[value].add(cell.coord[1])

        def apply(valdict, axis):
            for v in filter(lambda v: len(valdict[v]) == 1, valdict):
                k = valdict[v].pop()
                for cell in self.cells:
                    if getattr(cell.coord, axis) == k:
                        for c in getattr(cell, axis).cells:
                            if c.block is not self and c.values and v in c.values:
                                c.values.remove(v)
                                vals.add(v)
                                self._stats['hidden_eliminations'] += 1

        apply(rowvals, 'row')
        apply(colvals, 'column')

        if vals:
            self._stats['block_reduce'] += 1

        return vals


class Row(Group):
    """A Row is a Group of cells belonging to the same row"""
    def __init__(self, cells):
        super(Row, self).__init__(cells)
        for c in cells:
            c.row = self


class Column(Group):
    """A Column is a Group of cells belonging to the same column"""
    def __init__(self, cells):
        super(Column, self).__init__(cells)
        for c in cells:
            c.column = self


class Grid(object):
    """A Grid is a square matrix of cells"""
    def __init__(self, cells):
        self.cells = cells

    def __call__(self, i, j):
        return self.cells[i][j]

    def __iter__(self):
        return (x for y in self.cells for x in y)


class Board(Grid):
    """A Board is a collection of Cells in a sudoku Grid"""
    def __init__(self, cells=None):
        super(Board, self).__init__(cells or [[Cell(i, j) for j in range(N)] for i in range(N)])

        def block(m, n):
            return [self.cells[i][j] for i in range(m*M, (m+1)*M) for j in range(n*M, (n+1)*M)]

        def row(m):
            return [self.cells[m][j] for j in range(N)]

        def column(n):
            return [self.cells[i][n] for i in range(N)]

        self.blocks = [Block(block(m, n)) for n in range(M) for m in range(M)]
        self.rows = [Row(row(i)) for i in range(N)]
        self.columns = [Column(column(j)) for j in range(N)]
        self.stats = Counter()

    def __eq__(self, other):
        for i in range(N):
            for j in range(N):
                if self(i, j) != other(i, j):
                    return False
        return True

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(str(self))

    def __copy__(self):
        return Board([[copy(self.cells[i][j]) for j in range(N)] for i in range(N)])

    def complexity(self, attr='blocks'):
        return reduce(operator.add, map(lambda x: math.log(len(x.values)) if x.values else 0,
                                        self if attr == 'cells' else getattr(self, attr)), 0)

    def search(self):
        blocks = sorted([block.combinations() for block in self.blocks if block.values], key=len)
        rows = sorted([row.combinations() for row in self.rows if row.values], key=len)
        columns = sorted([column.combinations() for column in self.columns if column.values], key=len)
        return sorted(list(map(lambda x: next(iter(x)), filter(None, [blocks, rows, columns]))), key=len)

    def open(self, n=None):
        for c in self:
            if not c.value and (n is None or len(c.values) == n):
                yield c

    @property
    def terminal(self):
        for cell in self:
            if not cell.value:
                return False
        return True

    def reduce(self):
        """Apply single-elimination and group reduction to reduce the
        space of values available to cells in this board"""
        self.stats['complexity'] = self.complexity()

        while True:
            self.stats['reduce'] += 1

            for cell in self.open(1):
                cell.value = next(iter(cell.values))
                self.stats['singles'] += 1

            for group in chain(self.blocks, self.columns, self.rows):
                group.reduce()

            if not next(self.open(1), None):
                break

        self.block_stats = reduce(operator.add, map(lambda x: x.stats, self.blocks), Counter())
        self.row_stats = reduce(operator.add, map(lambda x: x.stats, self.rows), Counter())
        self.column_stats = reduce(operator.add, map(lambda x: x.stats, self.columns), Counter())

    @property
    def moves(self):
        return self._moves

    @property
    def marking(self):
        return [((c.coord.row, c.coord.column), c.value) for c in self if c.value]

    def __str__(self):
        return "\n".join([",".join(map(lambda x: str(x.value or 0), self.cells[i])) for i in range(N)])

    def __repr__(self):
        return str(self.marking)

