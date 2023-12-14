from math import log2
from random import randrange, choice
from enum import Enum
from discord import Colour
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.converters import ANSI


class Coordonnees:
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


class Directions(Enum):
    Haut = Coordonnees([-1, 0])
    Bas = Coordonnees([1, 0])
    Gauche = Coordonnees([0, -1])
    Droite = Coordonnees([0, 1])


# On définit un type Case générique
class Case:
    def __init__(self, value=0, grid_size=4, coos=Coordonnees([1, 1]), vide=" ", bord=None):
        self.coos = coos
        self.gsz = grid_size
        self.value = value
        self.dim = self.coos.dim
        self.vide = vide
        self.bord = bord
        self.can_fuse = True

    def __str__(self):
        return f"{self.value} en {self.coos}"

    def isEmpty(self):
        return self.value == self.vide

    def isWall(self):
        return self.value == self.bord


# On définit un type Grid générique
class Grid:
    def __init__(self, size: int = 6, vide="", bord=None):
        # Pour des raisons pratiques, on rajoute un contour
        self.size = size - 2
        self.vide = vide
        self.bord = bord
        self.grid = list()
        for i in range(size):
            l = list()
            for j in range(size):
                if 1 <= i <= self.size and 1 <= j <= self.size:
                    l.append(
                        Case(value=self.vide, grid_size=size, coos=Coordonnees([i, j]), vide=self.vide, bord=self.bord))
                else:
                    l.append(
                        Case(value=self.bord, grid_size=size, coos=Coordonnees([i, j]), vide=self.vide, bord=self.bord))
            self.grid.append(l)

    # Pas censé être utilisé, ne sert qu'au débug
    def __str__(self):
        sep = ("+--" + "-" * 15) * (self.size + 2) + "+\n| "
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
        for i in range(1, 1 + self.size):
            for j in range(1, 1 + self.size):
                case = self.getCase([i, j])
                if case.isEmpty():
                    vides.append(case)
        if not len(vides) == 0:
            case = vides[randrange(len(vides))]
            case.value = value

    def getCase(self, pos):
        return self[pos[0]][pos[1]]

    def read(self, matrice: list[list]):
        # Si la matrice n'est pas carré, on arrête
        if not len(matrice) == len(matrice[0]):
            return
        self.size = len(matrice)
        size = self.size + 2
        self.grid = list()
        for i in range(size):
            l = list()
            for j in range(size):
                if 1 <= i <= self.size and 1 <= j <= self.size:
                    l.append(Case(value=matrice[i - 1][j - 1], grid_size=size, coos=Coordonnees([i, j]), vide=self.vide,
                                  bord=self.bord))
                else:
                    l.append(
                        Case(value=self.bord, grid_size=size, coos=Coordonnees([i, j]), vide=self.vide, bord=self.bord))
            self.grid.append(l)


# On définit un type 2048 contenant les règles du jeu
class Game2048:
    def __init__(self, size: int = 4):
        self.grid = Grid(size=size + 2, vide="", bord=None)
        self.grid.spawnCase(2)
        self.jeu = "2048"
        self.score = 0
        self.duree = timedelta(seconds=0)
        self.termine = False
        self.gagne = False

    def __str__(self):
        sep = ("+--" + "-" * 5) * self.grid.size + "+\n| "
        sep = f"<red>{sep}<reset>"
        affichage = sep
        for i in range(1, 1 + self.grid.size):
            for j in range(1, 1 + self.grid.size):
                affichage += "<cyan>{:>5} <red>|<reset> ".format(str(self.grid.getCase([i, j]).value))
            affichage += "\n" + sep
        return ANSI().converter(affichage[:-11])

    def _score(self):
        # Calculs d'après https://medium.com/@kotamori/total-score-formula-of-the-2048-game-d9a8c9a1f1ac
        score = 0
        for i in range(1, 1 + self.grid.size):
            for j in range(1, 1 + self.grid.size):
                case = self.grid.getCase([i, j])
                if case.isEmpty() or case.isWall():
                    continue
                n = int(log2(case.value))
                score += (n - 1) * 2 ** n
        return score

    def canMove(self, toward):
        for i in range(1, 1 + self.grid.size):
            for j in range(1, 1 + self.grid.size):
                case = self.grid.getCase([i, j])
                if case.isEmpty():
                    continue
                nearCase = self.grid.getCase(Coordonnees([i, j]) + toward.value)
                if nearCase.isWall():
                    continue
                if self.canFuse(case, nearCase) or nearCase.isEmpty():
                    return True
        return False

    def canMoveAll(self):
        for toward in list(Directions):
            if self.canMove(toward):
                return True
        return False

    def reset_fuse(self):
        for line in self.grid.grid:
            for case in line:
                case.can_fuse = True

    @staticmethod
    def canFuse(case1, case2):
        c1 = case1.value == case2.value and not case2.isWall()
        c2 = case1.can_fuse and case2.can_fuse
        adjacents = list()
        for toward in list(Directions):
            adjacents.append(case1.coos + toward.value)
        c3 = case2.coos.pos in adjacents
        return c1 and c2 and c3

    def fusion(self, case1, case2):  # Fusionne case1 vers case2
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

    def moveAll(self, toward):
        if not self.canMove(toward):
            return

        # while self.canMove(to):
        while self.canMove(toward):
            if toward == Directions.Haut:
                for i in range(1, 1 + self.grid.size):
                    for j in range(1, 1 + self.grid.size):
                        case1 = self.grid.getCase([i, j])
                        case2 = self.grid.getCase(Coordonnees([i, j]) + toward.value)
                        self.move(case1, case2)

            if toward == Directions.Bas:
                for i in range(self.grid.size, 0, -1):
                    for j in range(1, 1 + self.grid.size):
                        case1 = self.grid.getCase([i, j])
                        case2 = self.grid.getCase(Coordonnees([i, j]) + toward.value)
                        self.move(case1, case2)

            if toward == Directions.Gauche:
                for i in range(1, 1 + self.grid.size):
                    for j in range(1, 1 + self.grid.size):
                        case1 = self.grid.getCase([i, j])
                        case2 = self.grid.getCase(Coordonnees([i, j]) + toward.value)
                        self.move(case1, case2)

            if toward == Directions.Droite:
                for i in range(1, 1 + self.grid.size):
                    for j in range(self.grid.size, 0, -1):
                        case1 = self.grid.getCase([i, j])
                        case2 = self.grid.getCase(Coordonnees([i, j]) + toward.value)
                        self.move(case1, case2)

        self.score = self._score()
        rd = randrange(4)
        if rd - 2 <= 0:
            self.grid.spawnCase(2)
        else:
            self.grid.spawnCase(4)
        self.reset_fuse()
