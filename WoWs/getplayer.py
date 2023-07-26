#!/usr/bin/env python3
from sys import argv, path
path[:0]=["../"]
from auxilliaire import *
from wowsAPI import * # ~ L'API de World of Warships adaptée pour lisibilité

# ~ Format d'éxécution
# ~ path/getplayer.py <PlayerID> <ClanName>

file = argv[2]
player = Player(argv[1])

modify_db(file, [player.name], [player.serialise()])
