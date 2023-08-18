#!/usr/bin/env python3
from subprocess import Popen, DEVNULL
import infos

# ~ __file__ contient le chemin et le nom du fichier
# ~ Sépare au niveau des / pour récupérer tous les dossiers et le fichier
# ~ Suppression du nom du fichier en conservant tout sauf le dernier élément
# ~ Recollage des morceaux avec "/".join()
pwd = "/".join(__file__.split('/')[:-1])
Popen([infos.bot],
		stdin=DEVNULL,
		stdout=open(infos.stdout, 'a'),
		stderr=open(infos.stderr, 'a'),
		start_new_session=True,
		shell=True)
