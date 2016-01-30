from bs4 import BeautifulSoup
import urllib.request

puzzle = BeautifulSoup(urllib.request.urlopen('http://show.websudoku.com?level=1').read(), "html.parser")

for row in puzzle.find('table',id='puzzle_grid').find_all('tr'):
    print(" ".join([cell.input.get('value','0') for cell in row.find_all('td')]))
