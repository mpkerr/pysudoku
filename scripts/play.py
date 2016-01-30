from pysudoku.puzzle import load_su
from pysudoku.games import game
import argparse
from pprint import pprint


def main():
    def solve(g):
        pprint(g.stats(next(g.play())))

    def moves(g):
        for move in g.play():
            pprint(g.stats(move))

    def boards(g):
        for board in set(map(lambda x: x.board, g.play())):
            print("{}\n".format(board))

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--puzzle', type=str, dest='puzzle', default="-", help='sudoku puzzle file name')
    subparsers = parser.add_subparsers()
    subparsers.add_parser('solve').set_defaults(func=solve)
    subparsers.add_parser('moves').set_defaults(func=moves)
    subparsers.add_parser('boards').set_defaults(func=boards)
    args = parser.parse_args()
    args.func(game(load_su(args.puzzle)))

    return 0
