from sys import path
path[:0]=["../Games/"]
from board_games import *

noStatsPlayer = Joueur(nom="noStats")
noStatsPlayer + Game2048()
for game in noStatsPlayer.games:
	noStatsPlayer.games[game]['nombre'] = 0

stats = Stats()
stats + noStatsPlayer

file = "players.txt"
stats.write(file)
