from setuptools import setup, find_packages

setup(
    name='pysudoku',
    version='0.1',
    description='Sudoku solver and game generator',
    author='M.P. Kerr',
    author_email="mpkerr@computer.org",
    url="https://github.com/mpkerr/pysudoku",
    download_url="https://github.com/mpkerr/pysudoku/tarball/0.1",
    keywords=["sudoku", "games", "puzzles"],
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "pysudoku = scripts.play:main"
        ]
    }
)
