#!/usr/bin/python3
# -*- coding: utf-8 -*-

# ~ auxilliaire.py
# ~ DB = DataBase

from subprocess import check_output
from fast_autocomplete import AutoComplete
from datetime import datetime, timedelta
from requests import Session
from collections import namedtuple
from traceback import format_exc
from discord import DMChannel, PartialMessageable, Embed
from discord.ext import commands
from functools import wraps
from os import environ

class CustomSession():
	def __init__(self):
		self.s = Session()
		self.responses = dict()
		self.data = namedtuple("RequestResult", ["result", "time"])

	def __str__(self):
		return f"{str(self.s)}\n{[key for key in self.responses]}"

	def __len__(self):
		return len(self.responses)

	def get(self, request, timeout=timedelta(hours=1)):
		t = datetime.now().replace(microsecond=0)
		try:
			resp = self.responses[request]
			if t - resp.time > timeout:
				raise KeyError # ~ Va se faire attraper par le except
			return resp.result

		except KeyError:
			r = self.s.get(request)
			self.responses[request] = self.data(r, t)
			return r

class Timestamp:
	def __init__(self, dt:datetime):
		ts = int(dt.timestamp())
		self.relative = f"<t:{ts}:R>"
		self.long_date = f"<t:{ts}:D>"
		self.short_date = f"<t:{ts}:d>"
		self.long_time = f"<t:{ts}:T>"
		self.short_time = f"<t:{ts}:t>"
		self.long_datetime = f"<t:{ts}:F>"
		self.short_datetime = f"<t:{ts}:f>"

class MyEmbed(Embed):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.timestamp = now()

class PrivateResponse:
	def __init__(self, triggers=[""], message="", allowed_guilds=[], denied_guilds=[]):
		self.triggers = triggers # ~ Contenu d'un message pour activer la réponse
		self.message = message # ~ Réponse à envoyer
		self.Aguilds = allowed_guilds # ~ Servers sur lesquels la réponse fonctionne ([] = tous)
		self.Dguilds = denied_guilds # ~ Servers sur lesquels la réponse est désactivée

	def __str__(self):
		return self.message

	def trigger(self, content):
		for t in self.triggers:
			if t in content:
				return True
		return False

	def users(self, user):
		return True

	def guilds(self, guild):
		allowed = self.Aguilds == [] or guild.id in self.Aguilds
		denied = guild.id in self.Dguilds
		return allowed and not denied

class Logger:
	def command_logger(func):
		start = now(True)
		@wraps(func)
		async def wrapper_error(*args, **kwargs):
			args_repr = [repr(a) for a in args]
			kwargs_repr = [f"{k}={v!r}" for k,v in kwargs.items()]
			self = args[0]
			cname = self.__class__.__name__
			ctx = args[1]
			user = ctx.author.name
			signature = "\n\t".join(args_repr + kwargs_repr)
			time = start.replace(microsecond=0)
			print(f"\n{time} {user} : {cname}.{func.__name__} dans {ctx.guild.name} avec comme arguments\n\t{signature}")

			try:
				value = await func(*args, **kwargs)
				print(f"{func.__name__} terminé en {now(True)-start}s")

			except Exception:
				await ctx.respond(environ['error_msg'], ephemeral=True)
				with open(environ['stderr'], 'a') as file:
					file.write(f"\n{start}\n{fail()}\n")

			return value
		return wrapper_error

	def modal_logger(func):
		start = now(True)
		@wraps(func)
		async def wrapper_error(*args, **kwargs):
			args_repr = [repr(a) for a in args]
			kwargs_repr = [f"{k}={v!r}" for k,v in kwargs.items()]
			self = args[0]
			cname = self.__class__.__name__
			interaction = args[1]
			user = interaction.user.name
			signature = "\n\t".join(args_repr + kwargs_repr)
			time = start.replace(microsecond=0)
			print(f"\n{time} {user} : {cname}.{func.__name__} dans {interaction.guild.name} avec comme arguments\n\t{signature}")

			try:
				value = await func(*args, **kwargs)
				print(f"{func.__name__} terminé en {now(True)-start}s")

			except Exception as e:
				await interaction.response.send_message(environ['error_msg'], ephemeral=True)
				with open(environ['stderr'], 'a') as file:
					file.write(f"\n{start}\n{fail()}\n")

			return value
		return wrapper_error

	def button_logger(func):
		start = now(True)
		@wraps(func)
		async def wrapper_error(*args, **kwargs):
			args_repr = [repr(a) for a in args]
			kwargs_repr = [f"{k}={v!r}" for k,v in kwargs.items()]
			self = args[0]
			cname = self.__class__.__name__
			interaction = args[2]
			user = interaction.user.name
			signature = "\n\t".join(args_repr + kwargs_repr)
			time = start.replace(microsecond=0)
			print(f"\n{time} {user} : {cname}.{func.__name__} dans {interaction.guild.name} avec comme arguments\n\t{signature}")

			try:
				value = await func(*args, **kwargs)
				print(f"{func.__name__} terminé en {now(True)-start}s")

			except Exception:
				with open(environ['stderr'], 'a') as file:
					file.write(f"\n{start}\n{fail()}\n")

			return value
		return wrapper_error

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
def tail(file:str, lastN=10):
	cmd = check_output(["tail", file,  "-n", str(lastN)])
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
	if n == 0:
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

def init_autocomplete(db):
	words = dict()
	synonyms = dict()

	for data in db:
		words[data[0].lower()] = dict()
		if not data[1] == ['']:
			synonyms[data[0].lower()] = [e.lower() for e in data[1]]

	return AutoComplete(words=words, synonyms=synonyms)

def fail():
	return format_exc() + "\n\n"

def correspond(attendu:list, reponse:str):
	articles = ["le", "la", "les", "l'", "un", "une", "des", "du", "de la"]
	for mot in reponse.split(" "):
		if not mot in attendu and not mot in articles:
			return False
	return True

def now(ms=False):
	time = datetime.now()
	if not ms:
		time.replace(microsecond=0)
	return time

async def User2Member(guild, user):
	return await guild.fetch_member(user.id)

async def Member2User(bot, member):
	return await bot.fetch_user(member.id)

# ~ Récupère toutes les sous-chaînes encadrées par start et end
def eltInStr(string, start, end, to_type=str):
	sep = [e.split(end) for e in string.split(start)]
	return [to_type(e[0]) for e in sep[1:]]

# ~ Message.role_mentions existe mais parfois ne marche pas complétement
def rolesInStr(string, guild):
	roles_ids = eltInStr(string, "<@&", ">", to_type=int)
	roles = [guild.get_role(r) for r in role_ids]
	return roles

async def usersInStr(string, bot):
	users_ids = eltInStr(string, "<@", ">", to_type=int)
	users = [await bot.fetch_user(u) for u in users_ids]
	return users

def clanships(clan):
	return f"clan{clan}.txt"
