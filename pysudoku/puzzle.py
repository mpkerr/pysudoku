"""puzzle serialization formats"""
import sys
import json

def load_su(file_name):
    """load a su-format text file
    :param file_name: name of file to load
    :returns: tuple of ((x,y),v) tuples"""
    def open_():
        return open(file_name, 'r') if file_name != "-" else sys.stdin

    marking = []
    with open_() as file:
        for row, line in enumerate(filter(None, map(str.strip, file))):
            for column, token in enumerate(line.split()):
                if token not in "_0.":
                    marking.append(((row, column), int(token)))

    return tuple(marking)


def load_ipuz(file_name):
    """load an http://ipuz.org/sudoku file
    :param file_name: name of file to load
    :returns: tuple of ((x,y),v) tuples"""
    def load():
        with open(file_name, 'r') as file:
            return json.load(file)

    puz = load()
    marking = []
    for row, columns in enumerate(puz['puzzle']):
        for column, token in enumerate(columns):
            if token is not None and token not in "_0.":
                marking.append((row, column), int(token))

    return marking
