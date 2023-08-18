from math import log2
from statistics import mean
from datetime import timedelta

from GoloBot.Auxilliaire import *
from random import randrange

class Joueur():
	def __init__(self, nom=""):
		self.name = nom
		self.games = dict()

	def __str__(self):
		affichage = f"Stats de {self.name}\n"
		for game in self.games:
			g = self.games[game]
			affichage += f"Stats {game}\n"
			affichage += f"Sur {g['nombre']} parties de {game}\n"
			affichage += f"{round(100* g['finished'] / max(1, g['nombre']))} % de complétion\n"
			affichage += f"{round(100* g['winrate'] / max(1, g['nombre']))} % de victoire\n"
			# ~ max(1, g['nombre']) parce que diviser par 0 c'est pas une bonne idée
			affichage += f"Meilleur Score : {g['best score']}\n"
			affichage += f"Score Moyen : {g['average score']}\n"
			affichage += f"Meilleur Temps : {timedelta(seconds=round(g['best time']))}\n"
			affichage += f"Temps Moyen : {timedelta(seconds=round(g['average time']))}\n"
			affichage += "\n"
		return affichage[:-1]

	def __add__(self, game):
		if not game.jeu in self.games:
			new = dict()
			new['nombre'] = 0
			new['scores'] = list()
			new['times'] = list()
			new['finished'] = 0
			new['winrate'] = 0
			self.games[game.jeu] = new

		# ~ Données brutes
		self.games[game.jeu]['nombre'] += 1
		self.games[game.jeu]['scores'].append(game.score)
		self.games[game.jeu]['times'].append(game.duree.total_seconds())
		if game.termine:
			self.games[game.jeu]['finished'] += 1
		if game.gagne:
			self.games[game.jeu]['winrate'] += 1

		# ~ Données traitées
		self.games[game.jeu]['best score'] = max(self.games[game.jeu]['scores'])
		self.games[game.jeu]['average score'] = mean(self.games[game.jeu]['scores'])
		self.games[game.jeu]['best time'] = min(self.games[game.jeu]['times'])
		self.games[game.jeu]['average time'] = mean(self.games[game.jeu]['times'])

	def write(self, filename):
		with open(filename, 'a') as file:
			file.write(f"{self.name}!")
			for game in self.games:
				file.write(f"{game}!")
				for key in self.games[game]:
					current = self.games[game][key]
					if not type(current) == list:
						file.write(f"{current}!")
					else:
						for elt in current:
							file.write(f"{elt};")
						file.write("!")
			file.write("\n")

	# ~ line est une ligne de DB, contenant les infos de write()
	def read(self, line):
		self.name = line[0]
		game = line[1]
		self.games[game] = dict()
		self.games[game]['nombre'] = round(float(line[2]))
		self.games[game]['scores'] = [round(float(n)) for n in line[3]]
		self.games[game]['times'] = [round(float(n)) for n in line[4]]
		self.games[game]['finished'] = round(float(line[5]))
		self.games[game]['winrate'] = round(float(line[6]))
		self.games[game]['best score'] = round(float(line[7]))
		self.games[game]['average score'] = round(float(line[8]))
		self.games[game]['best time'] = round(float(line[9]))
		self.games[game]['average time'] = round(float(line[10]))

class Stats():
	def __init__(self):
		self.joueurs = list()
		self.bests = dict()
		self.averages = dict()
		self.games = dict()

	def __str__(self):
		affichage = "Stats Globales\n"
		for game in self.games:
			current = self.games[game]
			affichage += f"Stats {game}\n"
			affichage += f"Meilleur Score : {current[0][0]}\n"
			affichage += f"Score Moyen: {current[1][0]}\n"
			affichage += f"Meilleur Temps : {timedelta(seconds=round(current[0][1]))}\n"
			affichage += f"Temps Moyen : {timedelta(seconds=round(current[1][1]))}\n"
			affichage += f"Meilleur Taux de Complétion : {current[0][2]} %\n"
			affichage += f"Meilleur Taux de Victoire : {current[0][3]} %\n"
			affichage += "\n"
		return affichage[:-1]

	def remove(self, joueur):
		self.joueurs = [elt for elt in self.joueurs if elt.name!=joueur]
		for game in self.bests:
			self.bests[game] = [elt for elt in self.bests[game] if elt[0] != joueur]
		for game in self.averages:
			self.averages[game] = [elt for elt in self.averages[game] if elt[0] != joueur]

	def __add__(self, joueur):
		self.remove("noStats")
		self.remove(joueur.name)
		self.joueurs.append(joueur)
		for game in joueur.games:
			current = joueur.games[game]
			add_dict(self.bests, game, [joueur.name,
				current['best score'], current['best time'],
				round(100* current['finished'] / max(1, current['nombre'])),
				round(100* current['winrate'] / max(1, current['nombre']))])
			add_dict(self.averages, game, [joueur.name, current['nombre'],
				current['average score'], current['average time']])

		self.games[game] = [[], []]
		for game in self.bests:
			self.games[game][0] = [
				max([elt[1] for elt in self.bests[game]]),
				min([elt[2] for elt in self.bests[game]]),
				max([elt[3] for elt in self.bests[game]]),
				max([elt[4] for elt in self.bests[game]])]

		for game in self.averages:
			total_games = sum([elt[1] for elt in self.averages[game]])
			self.games[game][1] = [
				round(sum([elt[1]*elt[2] for elt in self.averages[game]])/max(1, total_games)),
				round(sum([elt[1]*elt[3] for elt in self.averages[game]])/max(1, total_games))]
				# ~ max(1, total_games) parce que diviser par 0 c'est pas une bonne idée

	def write(self, file):
		with open(file, 'w') as f:
			pass
		# ~ players = [p.name for p in self.joueurs]
		# ~ write_db(file, pack(players, 1))
		for player in self.joueurs:
			player.write(file)

	def read(self, file):
		path = ""
		for elt in file.split("/")[:-1]:
			path += f"{elt}/"
		self.joueurs = list()
		players = read_db(file)
		for line in players:
			joueur = Joueur()
			joueur.read(line)
			self.__add__(joueur)

class Coordonnees():
	def __init__(self, pos):
		self.pos = pos
		self.dim = len(pos)

	def __str__(self):
		pos_str = [str(n) for n in self.pos]
		return f"({','.join(pos_str)})"

	def __add__(self, other):
		ncoos = [0] * self.dim
		for i in range(self.dim):
			ncoos[i] = self.pos[i] + other.pos[i]
		return ncoos

toward = {"haut" : Coordonnees([-1, 0]),
		"bas" : Coordonnees([1, 0]),
		"gauche" : Coordonnees([0, -1]),
		"droite" : Coordonnees([0, 1])}

# ~ On définit un type Case générique
class Case():
	def __init__(self, value=0, grid_size=4, coos=Coordonnees([1,1]), vide=" ", bord=None):
		self.coos = coos
		self.gsz = grid_size
		self.value = value
		self.dim = self.coos.dim
		self.vide = vide
		self.bord = bord
		self.can_fuse = True

	def __str__(self):
		return(f"{self.value} en {self.coos}")

	def isEmpty(self):
		return self.value == self.vide

	def isWall(self):
		return self.value == self.bord

# ~ On définit un type Grid générique
class Grid():
	def __init__(self, size:int=6, vide="", bord=None):
		# ~ Pour des raisons pratiques, on rajoute un contour
		self.size = size-2
		self.vide = vide
		self.bord = bord
		self.grid = list()
		for i in range(size):
			l = list()
			for j in range(size):
				if 1 <= i <= self.size and 1 <= j <= self.size:
					l.append(Case(value=self.vide, grid_size=size, coos=Coordonnees([i,j]), vide=self.vide, bord=self.bord))
				else:
					l.append(Case(value=self.bord, grid_size=size, coos=Coordonnees([i,j]), vide=self.vide, bord=self.bord))
			self.grid.append(l)

	# ~ N'est pas censé être utilisé, ne sert qu'au débug
	def __str__(self):
		sep = ("+--"+"-"*15)*(self.size+2) + "+\n| "
		affichage = sep
		for line in self.grid:
			for case in line:
				affichage += "{:>15} | ".format(str(case))
			affichage += "\n" + sep
		return affichage[:-3]

	def __getitem__(self, key):
		return self.grid[key]

	def spawnCase(self, value):
		vides = list()
		for i in range(1, 1+self.size):
			for j in range(1, 1+self.size):
				case = self.getCase([i,j])
				if case.isEmpty():
					vides.append(case)
		if not len(vides) == 0:
			case = vides[randrange(len(vides))]
			case.value = value

	def getCase(self, pos):
		return self[pos[0]][pos[1]]

	def read(self, matrice:list[list]):
		# ~ Si la matrice n'est pas carré, on arrête
		if not len(matrice) == len(matrice[0]):
			return
		self.size = len(matrice)
		size = self.size +2
		self.grid = list()
		for i in range(size):
			l = list()
			for j in range(size):
				if 1 <= i <= self.size and 1 <= j <= self.size:
					l.append(Case(value=matrice[i-1][j-1], grid_size=size, coos=Coordonnees([i,j]), vide=self.vide, bord=self.bord))
				else:
					l.append(Case(value=self.bord, grid_size=size, coos=Coordonnees([i,j]), vide=self.vide, bord=self.bord))
			self.grid.append(l)

# ~ On définit un type 2048 contenant les règles du jeu
class Game2048():
	def __init__(self, size:int=4):
		self.grid = Grid(size=size+2, vide="", bord=None)
		self.grid.spawnCase(2)
		self.jeu = "2048"
		self.score = 0
		self.duree = timedelta(seconds=0)
		self.termine = False
		self.gagne = False

	def __str__(self):
		sep = ("+--"+"-"*5)*self.grid.size + "+\n| "
		affichage = sep
		for i in range(1, 1+ self.grid.size):
			for j in range(1, 1+ self.grid.size):
				affichage += "{:>5} | ".format(str(self.grid.getCase([i,j]).value))
			affichage += "\n" + sep
		return affichage[:-3]

	def _score(self):
		# ~ Calculs d'après https://medium.com/@kotamori/total-score-formula-of-the-2048-game-d9a8c9a1f1ac
		score = 0
		for i in range(1, 1+ self.grid.size):
			for j in range(1, 1+ self.grid.size):
				case = self.grid.getCase([i,j])
				if case.isEmpty() or case.isWall():
					continue
				n = int(log2(case.value))
				score += (n-1) * 2**n
		return score

	def canMove(self, to):
		for i in range(1, 1+self.grid.size):
			for j in range(1, 1+self.grid.size):
				case = self.grid.getCase([i,j])
				if case.isEmpty():
					continue
				nearCase = self.grid.getCase(Coordonnees([i,j]) + toward[to])
				if nearCase.isWall():
					continue
				if self.canFuse(case, nearCase) or nearCase.isEmpty():
					return True
		return False

	def canMoveAll(self):
		for to in toward:
			if self.canMove(to):
				return True
		return False

	def reset_fuse(self):
		for line in self.grid.grid:
			for case in line:
				case.can_fuse = True

	def canFuse(self, case1, case2):
		c1 = case1.value == case2.value and not case2.isWall()
		c2 = case1.can_fuse and case2.can_fuse
		adjacents = list()
		for to in toward:
			adjacents.append(case1.coos + toward[to])
		c3 = case2.coos.pos in adjacents
		return c1 and c2 and c3

	def fusion(self, case1, case2): # ~ Fusionne case1 vers case2
		if self.canFuse(case1, case2):
			case2.value *= 2
			case1.value = self.grid.vide
			case1.can_fuse = False
			case2.can_fuse = False

	def move(self, case1, case2):
		if case1.isEmpty() or case1.isWall():
			return
		if case2.isEmpty():
			case2.value = case1.value
			case1.value = self.grid.vide
			case1.can_fuse, case2.can_fuse = case2.can_fuse, case1.can_fuse
		else:
			self.fusion(case1, case2)

	def moveAll(self, to):
		if not self.canMove(to):
			return

		# ~ while self.canMove(to):
		while self.canMove(to):
			if to == "haut":
				for i in range(1, 1+ self.grid.size):
					for j in range(1, 1+ self.grid.size):
						case1 = self.grid.getCase([i,j])
						case2 = self.grid.getCase(Coordonnees([i,j]) + toward[to])
						self.move(case1, case2)

			if to == "bas":
				for i in range(self.grid.size, 0, -1):
					for j in range(1, 1+ self.grid.size):
						case1 = self.grid.getCase([i,j])
						case2 = self.grid.getCase(Coordonnees([i,j]) + toward[to])
						self.move(case1, case2)

			if to == "gauche":
				for i in range(1, 1+ self.grid.size):
					for j in range(1, 1+ self.grid.size):
						case1 = self.grid.getCase([i,j])
						case2 = self.grid.getCase(Coordonnees([i,j]) + toward[to])
						self.move(case1, case2)

			if to == "droite":
				for i in range(1, 1+ self.grid.size):
					for j in range(self.grid.size, 0, -1):
						case1 = self.grid.getCase([i,j])
						case2 = self.grid.getCase(Coordonnees([i,j]) + toward[to])
						self.move(case1, case2)

		self.score = self._score()
		rd = randrange(4)
		if rd -2 <= 0:
			self.grid.spawnCase(2)
		else:
			self.grid.spawnCase(4)
		self.reset_fuse()
