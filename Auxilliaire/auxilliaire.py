#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ~ auxilliaire.py
# ~ DB = DataBase

from subprocess import check_output
from fast_autocomplete import AutoComplete
import requests

class CustomSession():
	def __init__(self):
		self.s = requests.Session()
		self.responses = dict()

	def __str__(self):
		return f"{str(self.s)}\n{[key for key in self.responses]}"

	def __len__(self):
		return len(self.responses)

	def get(self, request):
		try:
			return self.responses[request]
		except KeyError:
			r = self.s.get(request)
			self.responses[request] = r
			return r

# ~ Lis une DB
def read_db(filename:str):
	database = list()
	with open(filename, 'r') as file:
		for line in file:
			ligne = list()
			word = ""
			sList = list()
			if not line[-1] == '!':
				line += '!'
			for elt in line:
				if elt != '!' and elt != ';':
					word += elt
				elif elt == ';':
					sList.append(word.strip())
					word = ""
				elif elt == '!':
					if len(sList) != 0:
						ligne.append(sList)
						sList = list()
					else:
						ligne.append(word.strip())
						word = ""
			database.append(ligne)
	return database

# ~ Copie une DB en supprimant une ligne
# ~ nom de fichier + début de la ligne à supprimer
def copy_without(filename:str, line_start:str):
	with open(filename, "r") as file:
		lines = file.readlines()

	with open(filename, "w") as file:
		for line in lines:
			if not line.startswith(line_start):
				file.write(line)

# ~ Écris dans une DB, mode "w" ou "a" sinon erreur
# ~ nom de fichier + liste de listes
def write_db(filename:str, content:list, mode="w"):
	with open(filename, mode) as file:
		for line in content:
			for elt in line:
				if type(elt) in (list, tuple):
					for e in elt:
						file.write(f"{e};")
				else:
					file.write(str(elt))
				file.write("!")
			file.write("\n")

# ~ Modifie les lignes d'une DB existante
# ~ nom de fichier + premier élément de l'ancienne db + nouvelle ligne de la db
# ~ new_lines de la forme ["+", [machin]] va ajouter machin après l'ancien contenu de la ligne
# ~ Les anciens débuts de lignes sont supprimés
def modify_db(filename:str, old_starts:list, new_lines:list):
	db = read_db(filename)
	new_db = list()
	found = [False] * len(old_starts)
	for i in range(len(db)):
		test = True
		for j in range(len(old_starts)):
			if db[i][0] == str(old_starts[j]):
				found[j] = True
				if new_lines[0] == "+":
					nl = db[i]
					for elt in new_lines[j+1]:
						nl.append(elt)
					new_db.append(nl)
				else:
					new_db.append(new_lines[j])
				test = False
		if test:
			new_db.append(db[i])
	for i in range(len(found)):
		if not found[i]:
			new_db.append([old_starts[i], new_lines[i+int(new_lines[0] == "+")]])
			found[i] = True
	write_db(filename, new_db)

# ~ Commande bash tail avec un peu de traitement
def tail(file, lastN=10):
	cmd = check_output(f"tail -n {lastN} {file}", shell=True)
	# ~ On doit convertir l'output de check_output (de type bytes) vers un str
	cmd = str(cmd, 'UTF-8')
	return cmd

# ~ Recherche récursive d'un élément dans une matrice
def rec_in(matrice:list[list], elt):
	for line in matrice:
		if elt in line:
			return True
	return False

# ~ Convertit une DB en dictionnaire
def convert_db_dict(database:list[list], colonne:int):
	dico = dict()
	for line in database:
		key = line[colonne]
		for i in range(len(line)):
			if not i == colonne:
				add_dict(dico, key, line[i])
	return dico

def convert_dict_db(dico:dict):
	db = list()
	for key in dico:
		value = unpack(dico[key])
		if type(value) == list:
			db.append([key]+value)
		else:
			db.append([key]+pack(value, 1))
	return db

# ~ Dictionnaire de la forme {key : list()}
# ~ Ajoute un élément à la liste d'une certaine clé
# ~ Crée cette clé si inexistante
def add_dict(dico:dict, key, elt):
	try:
		dico[key].append(elt)
	except KeyError:
		dico[key] = [elt]

# ~ Enveloppe item dans n listes
def pack(item, n):
	if wanted == 0:
		return item
	return pack([item], n-1)

# ~ Opération inverse de unpack
def unpack(item):
	if not type(item) == list:
		return item
	if len(item) > 1:
		return item
	return unpack(item[0])

def insert(liste:list, pos:int, elt):
	liste[pos:pos]=[elt]

def check_unicity(string:str, elt:str):
	return len(string.split(elt)) == 2

def init_autocomplete(file):
	db = read_db(file)
	words = dict()
	synonyms = dict()

	for data in db:
		words[data[0]] = dict()
		synonyms[data[0]] = data[1]

	return AutoComplete(words=words, synonyms=synonyms)
