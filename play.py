from puzzle import load_su
from games import game


def main(args=None):
    g = game(load_su(args[0]))
    g.play()
    return g

if __name__ == "__main__":
    import sys
    import json
    print(json.dumps(main(sys.argv[1:]).stats(), sort_keys=True, indent=4))
