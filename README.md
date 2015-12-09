PySudoku
========

Python 3.x Sudoku solver

Input file format
-----------------

Support is provided in puzzle.py for a simple game board format.

Example:
```
9 _ _ _ _ _ _ 2 _
2 3 4 _ _ 9 _ _ _
5 _ _ _ _ 6 _ 9 _
_ 6 _ _ _ 7 _ _ _
3 _ 8 _ _ _ 6 _ 2
_ _ _ 2 _ _ _ 4 _
_ 7 _ 1 _ _ _ _ 4
_ _ _ 3 _ _ 9 6 5
_ 5 _ _ _ _ _ _ 7
```

Blank lines are ignored. Blank grid entries can be represented as either 
"0", "_", or ".". Across a line tokens must be separated by at least one
space.

Input files must match the dimension specifications matching the M and N
values in sudoku.py.

Solver
------

The basic approach is to reduce a game board, or, equivalently, to eliminate
possible cell values. Much of the extant sudoku game inventory essentially
reduces to the application of basic logical invariants. More complex games
involve a recursive tree search where multiple possible moves remain after
invariant removal.