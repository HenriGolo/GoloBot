import asyncio
import re
from collections import namedtuple
from datetime import datetime, timedelta
from subprocess import check_output
from traceback import format_exc
import discord
from fast_autocomplete import AutoComplete
from requests import Session
from enum import Enum
from functools import partial
import json

url = re.compile(r'https?://[a-zA-Z0-9/.#-]*')
all_mentions = re.compile(r'<[@#!&]+[0-9]*>')
user_mentions = re.compile(r'<@[0-9]*>')
role_mentions = re.compile(r'<@&[0-9]*>')
channel_mentions = re.compile(r'<#[0-9]*>')
slash_mention = re.compile(r'</[a-zA-Z0-9]*:[0-9]*>')
emoji = re.compile(r'<a?:[a-zA-Z0-9]*:[0-9]*>')
timestamp = re.compile(r'<t:[0-9]*:[RDdTtFf]>')


class Cycle(list):
    def __init__(self, *items):
        super().__init__(items)

    def __getitem__(self, item):
        return super().__getitem__(item % len(self))


class Exit(Enum):
    Success = True
    Fail = False


class GBSession:
    def __init__(self):
        self.s = Session()
        self.cache = dict()
        self.data = namedtuple("RequestResult", ["result", "time"])

    def __str__(self):
        return f"{str(self.s)}\n{[key for key in self.cache]}"

    def __len__(self):
        return len(self.cache)

    def get(self, request, timeout=timedelta(hours=1)):
        t = now()
        try:
            resp = self.cache[request]
            if t - resp.time > timeout:
                raise KeyError  # Va se faire attraper par l'except
            return resp.result

        except KeyError:
            r = self.s.get(request)
            self.cache[request] = self.data(r, t)
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


class GBEmbed(discord.Embed):
    def __init__(self, *args, user=None, guild=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = now()
        if isinstance(guild, discord.Guild):
            self.set_author(name=guild.name, url=guild.jump_url)
            if guild.banner is not None:
                self.set_image(url=guild.banner.url)
            self.set_thumbnail(url=guild.icon.url)
        if isinstance(user, (discord.User, discord.Member)):
            self.color = user.color
            self.set_author(name=user.name, url=user.jump_url, icon_url=user.avatar.url)


class GBView(discord.ui.View):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def on_timeout(self):
        self.disable_all_items()


class Trigger:
    def __init__(self, trigger: str, rmurl=True, rmention=True, rmoji=False, casse=True):
        self.trigger = trigger
        self.rmurl = rmurl  # Enlever les url
        self.rmention = rmention  # Enlever les mentions
        self.rmoji = rmoji  # Enlever les noms des emotes
        self.casse = casse  # Sensible à la casse

    def __str__(self):
        return self.trigger

    @staticmethod
    def remove_pattern(pattern, string):
        occs = re.findall(pattern, string)
        retour = string
        for o in occs:
            retour = "".join(retour.split(o))
        return retour

    def check(self, string: str):
        if not self.casse:
            string = string.lower()
        if self.rmurl:
            string = self.remove_pattern(url, string)
        if self.rmention:
            string = self.remove_pattern(all_mentions, string)
        if not self.rmoji:
            # Présent dans le nom, mais pas dans l'id
            emotes = re.findall(emoji, string)
            for e in emotes:
                if str(self).strip(':') in e.split(':')[1]:
                    return True
        string = self.remove_pattern(emoji, string)
        return str(self) in string


class PrivateResponse:
    def __init__(self, bot, triggers=(Trigger(""),), message="", allowed_guilds=()):
        self.bot = bot
        self.triggers = triggers  # Contenu d'un message pour activer la réponse
        self.message = message  # Réponse à envoyer
        self.Aguilds = allowed_guilds  # Servers sur lesquels la réponse fonctionne ([] = tous)

    def __str__(self):
        return self.message

    async def trigger(self, msg: discord.Message):
        content = msg.content
        for t in self.triggers:
            if t.check(content):
                return True
        return False

    @staticmethod
    async def users(msg: discord.Message):
        user = msg.author
        return not user.bot

    async def guilds(self, msg: discord.Message):
        return self.Aguilds == () or msg.guild.id in self.Aguilds

    async def do_stuff(self, msg: discord.Message):
        if await self.trigger(msg) and await self.guilds(msg) and await self.users(msg):
            await msg.reply(str(self))
            return True
        return False


class Completer(AutoComplete):
    def search(self, word, max_cost=None, size=1):
        if max_cost is None:
            max_cost = len(word)
        return super().search(word=word, max_cost=max_cost, size=size)

    @staticmethod
    def from_db(db):
        words = dict()
        synonyms = dict()

        for data in db:
            words[data[0].lower()] = dict()
            if not data[1] == ['']:
                synonyms[data[0].lower()] = [e.lower() for e in data[1]]

        return Completer(words=words, synonyms=synonyms)


# Stocke un set comme une liste
class SetEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return [e for e in o]
        return super().default(o)


# Interprête une liste comme un set
class SetDecoder(json.JSONDecoder):
    def decode(self, s, _w=...):
        std = super().decode(s)
        if isinstance(std, list):
            return {e for e in std}
        return std


class GBEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            return repr(o)


class GBDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_instance = True

    def decode(self, s, _w=...):
        s = s.strip('"').strip("'")
        if s.startswith('<') and s.endswith('>'):
            s = s[1:-1].strip('"').strip("'")
            if s.startswith("class "):
                self.create_instance = False
                return self.decode(f"<{s[7:]}>")  # s de la forme <class truc>

            cls, kwargs = self.repr_parser(s)
            cls = self.instanciate(cls)
            if not self.create_instance:
                return cls

            if hasattr(cls, "instances"):
                instances_dict = {i.name: i for i in cls.instances}
                item = instances_dict.get(kwargs["name"], cls(**kwargs))
                for key, value in kwargs.items():
                    setattr(item, key, value)
                return item
            else:
                return cls(**kwargs)

        try:
            std = super().decode(s)
        except:
            try:
                std = super().decode(f"'{s}'")
            except:
                std = s

        if isinstance(std, str):
            if std.lower() in ["oui", "o", "yes", "y", "vrai", "v", "true"]:
                std = True
            elif std.lower() in ["non", "n", "no", "faux", "f", "false"]:
                std = False
        return std

    @classmethod
    def repr_parser(cls, s):
        # s de la forme <path.to.class.classname champ1=valeur1 champ2=valeur2>
        s = s.strip('<').strip('>') + ' '
        elts = s.split('=')  # on commence par split sur = sinon c'est + dur de s'y retrouver
        elts = [e.split(' ') for e in elts]
        klass = elts[0][0]  # cls de la forme path.to.class.classname
        klass = klass.split('.')
        kwargs = dict()
        for i in range(1, len(elts)):
            data = ' '.join(elts[i][:-1])
            try:
                data = json.loads(data, cls=GBDecoder)
            except:
                pass
            finally:
                kwargs[elts[i - 1][-1]] = data
        return klass, kwargs

    @classmethod
    def instanciate(cls, path: list[str], _from=None):
        if not path:
            return _from
        try:
            return __builtins__[path[-1]]
        except:
            try:
                return globals()[path[-1]]
            except KeyError:
                if _from is None:
                    _from = __import__(path[0])
                    path = path[1:]
                return cls.instanciate(path[1:], getattr(_from, path[0]))


# Commande bash tail avec un peu de traitement
def tail(file: str, lastN=10):
    cmd = check_output(["tail", file, "-n", str(lastN)])
    # On doit convertir l'output de check_output (de type bytes) vers un str
    cmd = str(cmd, 'UTF-8')
    return cmd


# Recherche récursive d'un élément dans une matrice
def rec_in(matrice: list[list], elt):
    for line in matrice:
        if elt in line:
            return True
    return False


# Dictionnaire de la forme {key : list()}
# Ajoute un élément à la liste d'une certaine clé
# Crée cette clé si inexistante
def add_dict(dico: dict, key, elt):
    try:
        dico[key].append(elt)
    except KeyError:
        dico[key] = [elt]


# Enveloppe item dans n listes
def pack(item, n):
    if n == 0:
        return item
    return pack([item], n - 1)


# Opération inverse d'unpack
def unpack(item):
    if not isinstance(item, (list, tuple)):
        return item
    if len(item) > 1:
        return item
    return unpack(item[0])


def insert(liste: list, pos: int, elt):
    liste[pos:pos] = [elt]


def nb_char_in_str(string):
    dejavu = dict()
    for c in string:
        dejavu[c] = dejavu.get(c, 0) + 1
    return dejavu


def check_unicity(string: str, elt: str):
    # existence + unicité
    return len(string.split(elt)) == 2


def fail():
    return f"\n{format_exc()}\n\n"


def correspond(attendu: list, reponse: str):
    articles = ["le", "la", "les", "l'", "un", "une", "des", "du", "de la"]
    for mot in reponse.split(" "):
        if not (mot in attendu or mot in articles):
            return False
    return True


def now(ms: bool = False):
    time = datetime.now()
    if not ms:
        time.replace(microsecond=0)
    return time


async def User2Member(guild, user):
    return await guild.fetch_member(user.id)


async def Member2User(bot, member):
    return await bot.fetch_user(member.id)


# Récupère toutes les sous-chaînes encadrées par start et end
def eltInStr(string, start, end, to_type=str):
    sep = [e.split(end) for e in string.split(start)]
    return [to_type(e[0]) for e in sep[1:]]


# Message.role_mentions existe, mais parfois ne marche pas complétement
def rolesInStr(string, guild):
    mentions = re.findall(role_mentions, string)
    # Il faut enlever les <@&> autour de la mention
    roles_ids = [int(r[3:-1]) for r in mentions]
    roles = [guild.get_role(r) for r in roles_ids]
    return roles


async def usersInStr(string, bot):
    mentions = re.findall(user_mentions, string)
    # Il faut enlever les <@> autour de la mention
    users_ids = [int(u[2:-1]) for u in mentions]
    users = [await bot.fetch_user(u) for u in users_ids]
    return users


async def wait_until(dt: datetime):
    delay = dt - now()
    await asyncio.sleep(delay.total_seconds())
