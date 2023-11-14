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
from discord import Embed
from GoloBot.Auxilliaire.stdio import *  # ~ Mes fonctions pour stocker des données


class CustomSession:
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
                raise KeyError  # ~ Va se faire attraper par le except
            return resp.result

        except KeyError:
            r = self.s.get(request)
            self.responses[request] = self.data(r, t)
            return r


class Timestamp:
    def __init__(self, dt: datetime):
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
    def __init__(self, triggers=("",), message="", allowed_guilds=(), denied_guilds=()):
        self.triggers = triggers  # ~ Contenu d'un message pour activer la réponse
        self.message = message  # ~ Réponse à envoyer
        self.Aguilds = allowed_guilds  # ~ Servers sur lesquels la réponse fonctionne ([] = tous)
        self.Dguilds = denied_guilds  # ~ Servers sur lesquels la réponse est désactivée

    def __str__(self):
        return self.message

    def trigger(self, content):
        for t in self.triggers:
            if t in content:
                return True
        return False

    @staticmethod
    def users(user):
        return True

    def guilds(self, guild):
        allowed = self.Aguilds == [] or guild.id in self.Aguilds
        denied = guild.id in self.Dguilds
        return allowed and not denied


# ~ Commande bash tail avec un peu de traitement
def tail(file: str, lastN=10):
    cmd = check_output(["tail", file, "-n", str(lastN)])
    # ~ On doit convertir l'output de check_output (de type bytes) vers un str
    cmd = str(cmd, 'UTF-8')
    return cmd


# ~ Recherche récursive d'un élément dans une matrice
def rec_in(matrice: list[list], elt):
    for line in matrice:
        if elt in line:
            return True
    return False


# ~ Convertit une DB en dictionnaire
def convert_db_dict(database: list[list], colonne: int):
    dico = dict()
    for line in database:
        key = line[colonne]
        for i in range(len(line)):
            if not i == colonne:
                add_dict(dico, key, line[i])
    return dico


def convert_dict_db(dico: dict):
    db = list()
    for key in dico:
        value = unpack(dico[key])
        if isinstance(value, list):
            db.append([key] + value)
        else:
            db.append([key] + pack(value, 1))
    return db


# ~ Dictionnaire de la forme {key : list()}
# ~ Ajoute un élément à la liste d'une certaine clé
# ~ Crée cette clé si inexistante
def add_dict(dico: dict, key, elt):
    try:
        dico[key].append(elt)
    except KeyError:
        dico[key] = [elt]


# ~ Enveloppe item dans n listes
def pack(item, n):
    if n == 0:
        return item
    return pack([item], n - 1)


# ~ Opération inverse de unpack
def unpack(item):
    if not isinstance(item, list):
        return item
    if len(item) > 1:
        return item
    return unpack(item[0])


def insert(liste: list, pos: int, elt):
    liste[pos:pos] = [elt]


def check_unicity(string: str, elt: str):
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
    return f"\n{format_exc()}\n\n"


def correspond(attendu: list, reponse: str):
    articles = ["le", "la", "les", "l'", "un", "une", "des", "du", "de la"]
    for mot in reponse.split(" "):
        if not (mot in attendu or mot in articles):
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


# ~ Message.role_mentions existe, mais parfois ne marche pas complétement
def rolesInStr(string, guild):
    roles_ids = eltInStr(string, "<@&", ">", to_type=int)
    roles = [guild.get_role(r) for r in roles_ids]
    return roles


async def usersInStr(string, bot):
    users_ids = eltInStr(string, "<@", ">", to_type=int)
    users = [await bot.fetch_user(u) for u in users_ids]
    return users


def clanships(clan):
    return f"clan{clan}.txt"
