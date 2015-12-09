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

Input files must match the dimension specification values (M, N) in 
sudoku.py. Update the M value to play sudoku games of desired dimension.

Solver
------

The basic approach is to reduce a game board, or, equivalently, to eliminate
possible cell values. Much of the extant sudoku game inventory essentially
reduces to the application of basic logical invariants. More complex games
involve a recursive tree search where multiple possible moves remain after
invariant removal.

Game Generator
--------------

In games.py are a number of utility methods to generate board and games, 
including methods to generate random games at given difficulty levels. 
Difficulty rating is an inexact measure but roughly speaking games of
difficulty less than 8 are relatively easy, between 8 and 15 are medium, 
and greater than 15 are most difficult. Games above 20 are very difficult.