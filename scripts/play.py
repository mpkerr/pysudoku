from pysudoku.puzzle import load_su
from pysudoku.games import game
import argparse
from pprint import pprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(type=str, dest='puzzle', help='sudoku puzzle file name')
    parser.add_argument('-a', '--all', dest='all', action='store_true')
    args = parser.parse_args()

    g = game(load_su(args.puzzle))

    if args.all:
        for move in g.play():
            pprint(g.stats(move))
    else:
        pprint(g.stats(next(g.play())))

    return 0
