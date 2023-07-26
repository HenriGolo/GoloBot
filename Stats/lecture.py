#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sys import path
path[:0]=["../Games/"]
from board_games import *

stats = Stats()
stats.read("players.txt")
print(stats)

for player in stats.joueurs:
	print(player)
