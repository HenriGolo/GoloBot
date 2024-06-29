from .converters import ANSI
import asyncio
from collections import namedtuple
from datetime import datetime, timedelta
import discord
from discord.ext import tasks
from enum import Enum
from fast_autocomplete import AutoComplete
from functools import partial
import json
from os import environ
import pytz
import re
from requests import Session
from subprocess import check_output
from traceback import format_exc
from unicodedata import normalize

GBpath = environ.get('path', '')

url = re.compile(r'https?://[a-zA-Z0-9/.#?-]*')
all_mentions = re.compile(r'<[@#!&]+[0-9]*>')
user_mentions = re.compile(r'<@[0-9]*>')
role_mentions = re.compile(r'<@&[0-9]*>')
channel_mentions = re.compile(r'<#[0-9]*>')
slash_mention = re.compile(r'</[a-zA-Z0-9]*:[0-9]*>')
emoji = re.compile(r'<a?:[a-zA-Z0-9]*:[0-9]*>')
timestamp = re.compile(r'<t:[0-9]*:[RDdTtFf]>')


# Class à hériter pour être compatible avec la serialisation JSON
# définie par GBEncoder et GBDecoder
class Storable:
    def to_json(self):
        std = repr(self.__class__)  # de la forme <class 'nom'>
        cls = std.split("'")[1]
        kwargs = {k: v for k, v in self.__dict__.items() if k in self.__init__.__code__.co_varnames}
        return {'cls': cls, 'kwargs': kwargs}


class DictPasPareil:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __add__(self, other):
        if isinstance(other, self.__class__):
            kwargs = self.__dict__
            for key, value in other.__dict__.items():
                if not key in kwargs:
                    kwargs[key] = value
            return self.__class__(**kwargs)
        raise Exception(f"{type(other)} n'est pas un type valide pour une addition avec {type(self)}")


class Cycle(list):
    def __getitem__(self, item):
        return super().__getitem__(item % len(self))


class Exit(Enum):
    Success = True
    Fail = False


class GBSession(Storable, Session):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = dict()
        self.data = namedtuple("RequestResult", ["result", "time"])

    def get(self, url, *, timeout=timedelta(hours=1), **kwargs):
        t = now()
        try:
            resp = self._cache[f"GET {url}"]
            if t - resp.time > timeout:
                raise KeyError  # Va se faire attraper par l'except
            return resp.result

        except KeyError:
            r = super().get(url, **kwargs)
            self._cache[f"GET {url}"] = self.data(r, t)
            return r

    def post(self, url, *, timeout=timedelta(hours=1), **kwargs):
        # idem que get, mais pour post
        t = now()
        try:
            resp = self._cache[f"POST {url}"]
            if t - resp.time > timeout:
                raise KeyError  # Va se faire attraper par l'except
            return resp.result

        except KeyError:
            r = super().post(url, **kwargs)
            self._cache[f"POST {url}"] = self.data(r, t)
            return r


class Timestamp:
    def __init__(self, dt):
        if isinstance(dt, int):
            ts = dt
        elif isinstance(dt, datetime):
            ts = int(dt.timestamp())
        elif isinstance(dt, timedelta):
            dt = now() + dt
            ts = int(dt.timestamp())
        else:
            raise Exception(f"Mauvais format de {dt}")
        self.relative = f"<t:{ts}:R>"
        self.long_date = f"<t:{ts}:D>"
        self.short_date = f"<t:{ts}:d>"
        self.long_time = f"<t:{ts}:T>"
        self.short_time = f"<t:{ts}:t>"
        self.long_datetime = f"<t:{ts}:F>"
        self.short_datetime = f"<t:{ts}:f>"


class GBEmbed(discord.Embed):
    def __init__(self, *args,
                 user: discord.User | discord.Member = None,
                 guild: discord.Guild = None,
                 **kwargs):
        kwargs['timestamp'] = kwargs.get('timestamp', now())
        if hasattr(user, 'color'):
            kwargs['color'] = kwargs.get('color', user.color)
        kwargs['color'] = kwargs.get('color', 0xffffff)
        super().__init__(*args, **kwargs)
        if isinstance(guild, discord.Guild):
            self.set_author(name=guild.name, url=guild.jump_url)
            self.set_thumbnail(url=guild.icon.url)
        if isinstance(user, (discord.User, discord.Member)):
            kwargs = {'name': user.display_name,
                      'url': user.jump_url}
            if hasattr(user.avatar, 'url'):
                kwargs['icon_url'] = user.avatar.url
            self.set_author(**kwargs)
            if not self.description:
                self.description = user.mention

    def add_field(self: discord.embeds.E, *, name: str, value: str, inline: bool = False) -> discord.embeds.E:
        return super().add_field(name=name, value=value, inline=inline)


class GBView(discord.ui.View):
    def __init__(self, bot: discord.AutoShardedBot, *args, **kwargs):
        kwargs['timeout'] = None
        super().__init__(*args, **kwargs)
        self.bot = bot

    async def on_timeout(self):
        self.disable_all_items()

    def add_links(self, *, meme_ligne: bool = True, **buttons):
        row = 0
        if len(buttons) > 5:
            meme_ligne = True
        for label, url in buttons.items():
            self.add_item(discord.ui.Button(label=label, url=url, row=row))
            if not meme_ligne:
                row += 1
        return self


class GButton(discord.ui.Button):
    def __init__(self, bot, *args, **kwargs):
        kwargs['label'] = kwargs.get('label', "Gneu ! Bouton !")
        kwargs['custom_id'] = kwargs.get('custom_id', kwargs['label'].lower().replace(' ', '_'))
        super().__init__(*args, **kwargs)
        self.bot = bot


class Trigger:
    def __init__(self, trigger: str, *,
                 rmurl: bool = True, rmention: bool = True,
                 rmoji: bool = False, rmstr: list[str] = (),
                 casse: bool = True, complet: bool = False):
        self.trigger = trigger
        self.rmurl = rmurl  # Enlever les url
        self.rmention = rmention  # Enlever les mentions
        self.rmoji = rmoji  # Enlever les noms des emotes
        self.rmstr = rmstr  # Enlever certaines str
        self.casse = casse  # Sensible à la casse
        self.complet = complet  # Mot complet

    def __str__(self):
        return self.trigger

    @staticmethod
    def remove_pattern(pattern: re.Pattern, string: str) -> str:
        occs = re.findall(pattern, string)
        retour = string
        for o in occs:
            retour = retour.replace(o, '')
        return retour

    def check(self, string: str) -> bool:
        if not self.casse:
            string = string.lower()
        if self.rmurl:
            string = self.remove_pattern(url, string)
        if self.rmention:
            string = self.remove_pattern(all_mentions, string)
        for s in self.rmstr:
            string.replace(s, '')
        if not self.rmoji:
            # Présent dans le nom, mais pas dans l'id
            emotes = re.findall(emoji, string)
            for e in emotes:
                if str(self).strip(':') in e.split(':')[1]:
                    return True
        string = self.remove_pattern(emoji, string)
        pattern = str(self)
        if self.complet:
            sep = "[ \.\?!,;/|]"
            pattern = sep + pattern + sep
            string = ' ' + string + ' '
        pattern = re.compile(pattern)
        return len(re.findall(pattern, string)) > 0


class PrivateResponse:
    def __init__(self, bot: discord.AutoShardedBot, *,
                 triggers: list[Trigger] = (Trigger(""),),
                 message: str = "",
                 reac: set[int | str | discord.Emoji] = (),
                 allowed_guilds: list[int] = ()):
        self.bot = bot
        self.triggers = triggers  # Contenu d'un message pour activer la réponse
        self.message = message  # Réponse à envoyer
        self.reac = reac  # Réactions à ajouter
        self.Aguilds = allowed_guilds  # Servers sur lesquels la réponse fonctionne ([] = tous)

    def __str__(self):
        return self.message

    async def trigger(self, msg: discord.Message) -> bool:
        content = msg.content
        for t in self.triggers:
            if t.check(content):
                return True
        return False

    @staticmethod
    async def users(msg: discord.Message) -> bool:
        user = msg.author
        return not user.bot

    async def guilds(self, msg: discord.Message) -> bool:
        return self.Aguilds == () or msg.guild.id in self.Aguilds

    async def do_stuff(self, msg: discord.Message) -> bool:
        if await self.trigger(msg) and await self.guilds(msg) and await self.users(msg):
            if self.message.strip():
                await msg.reply(self.message)

            for reac in self.reac:
                if isinstance(reac, int):
                    emoji = self.bot.get_emoji(reac)
                elif isinstance(reac, (discord.Emoji, str)):
                    emoji = reac
                else:
                    return True
                await msg.add_reaction(emoji)

            return True
        return False


class Completer(AutoComplete):
    def search(self, word: str, max_cost=None, size=1) -> list[list[str]]:
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
            return {self.decode(e) for e in std}
        return std


class GBEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            return super().default(o)
        except TypeError:
            # o est une classe, pas un objet
            if isinstance(o, type):
                # repr d'une classe de la forme <class 'foo'>
                # None va être interprété par GBDecoder
                return {'cls': repr(o).split("'")[1], 'kwargs': None}

            for fun in ['to_json', 'json']:
                if hasattr(o, fun):
                    f = getattr(o, fun)
                    if callable(f):
                        return f()
            return repr(o)


class GBDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_instance = True

    def decode(self, s, _w=...):
        if not isinstance(s, str):
            std = s
        else:
            try:
                std = super().decode(s)
            except:
                std = super().decode(f'"{s}"')

        if isinstance(std, (list, tuple)):
            return [self.decode(e) for e in std]

        elif isinstance(std, set):
            return {self.decode(e) for e in std}

        elif isinstance(std, dict):
            std = {self.decode(k): self.decode(v) for k, v in std.items()}
            if {'cls', 'kwargs'}.issubset(std.keys()):
                cls = self.instanciate(std['cls'].split('.'))
                kwargs = std['kwargs']
                if kwargs is None:
                    return cls
                return cls(**kwargs)

        elif isinstance(std, str):
            if std.lower() in ['oui', 'o', 'yes', 'y', 'vrai', 'v', 'true']:
                std = True
            elif std.lower() in ['non', 'n', 'no', 'faux', 'f', 'false']:
                std = True
            elif std.lower() in ['none', 'null']:
                std = None
            elif std.isdigit():
                std = int(std)
        return std

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


class DataBase(Storable):
    def __init__(self, path, auto_update=True):
        self.path: str = path
        self.auto_update: bool = auto_update
        self.data = dict()
        self.read()

    def read(self, **kwargs):
        kwargs['cls'] = kwargs.get('cls', GBDecoder)
        self.data = json.load(open(self.path, 'r'), **kwargs)
        return self

    def write(self, **kwargs):
        kwargs['cls'] = kwargs.get('cls', GBEncoder)
        kwargs['indent'] = kwargs.get('indent', 4)
        json.dump(self.data, open(self.path, 'w'), **kwargs)

    def items(self):
        return self.data.items()

    def __getitem__(self, item):
        try:
            return self.data.__getitem__(item)
        except KeyError:
            return self.data.__getitem__(str(item))

    def __contains__(self, item):
        return self.data.__contains__(item) or self.data.__contains__(str(item))

    def __bool__(self):
        return bool(self.data)

    def __len__(self):
        return len(self.data)

    def __str__(self):
        return f"{type(self.data)} de taille {len(self.data)} stocké dans {self.path}"

    def __setitem__(self, key, value):
        self.data[key] = value
        if self.auto_update:
            self.write()

    def __delitem__(self, key):
        try:
            del self.data[key]
        except KeyError:
            del self.data[str(key)]
        if self.auto_update:
            self.write()


# Commande bash tail avec un peu de traitement
def tail(file: str, lastN=10) -> str:
    cmd = check_output(["tail", file, "-n", str(lastN)])
    # On doit convertir l'output de check_output (de type bytes) vers un str
    cmd = str(cmd, 'UTF-8')
    return cmd


# Recherche récursive
def rec_in(search, elt, profondeur=-1) -> bool:
    # Comme ça on cherche autant dans les clés que dans les valeurs
    if isinstance(search, dict):
        search = search.items()
    # Profondeur -1 pour chercher partout
    if profondeur == 0:
        # On ne cherche pas plus loin
        try:
            # Évaluation paresseuse :
            # si == le 'in' ne sera pas évalué,
            # même si censé produire une erreur
            return elt == search or elt in search
        except:
            return False

    try:
        for sub in search:
            trouve = rec_in(sub, elt, 0)  # On a trouvé ce qu'on cherche
            if trouve or rec_in(sub, elt, profondeur - 1):
                # On l'a trouvé dans les appels récursifs
                return True
    except:
        pass
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


def nb_char_in_str(string: str) -> dict:
    dejavu = dict()
    for c in string:
        dejavu[c] = dejavu.get(c, 0) + 1
    return dejavu


def check_unicity(string: str, elt: str) -> bool:
    # existence + unicité
    return len(string.split(elt)) == 2


def fail() -> str:
    # Juste du formatage
    return f"\n{format_exc()}\n\n"


def correspond(attendu: list, reponse: str) -> bool:
    articles = ["le", "la", "les", "l'", "un", "une", "des", "du", "de la"]
    for mot in reponse.split(" "):
        if not (mot in attendu or mot in articles):
            return False
    return True


def now(ms: bool = False) -> datetime:
    time = datetime.now()
    if not ms:
        time.replace(microsecond=0)
    return time


async def User2Member(guild: discord.Guild, user: discord.User) -> discord.Member:
    return await guild.fetch_member(user.id)


async def Member2User(bot: discord.AutoShardedBot, member: discord.Member) -> discord.User:
    return await bot.fetch_user(member.id)


# Récupère toutes les sous-chaînes encadrées par start et end
def eltInStr(string: str, start: str, end: str, to_type: type = str):
    sep = [e.split(end) for e in string.split(start)]
    return [to_type(e[0]) for e in sep[1:]]


# Message.role_mentions existe, mais parfois ne marche pas complétement
def rolesInStr(string: str, guild: discord.Guild) -> list[discord.Role]:
    mentions = re.findall(role_mentions, string)
    # Il faut enlever les <@&> autour de la mention
    roles_ids = [int(r[3:-1]) for r in mentions]
    roles = [guild.get_role(r) for r in roles_ids]
    return roles


async def usersInStr(string: str, bot: discord.AutoShardedBot) -> list[discord.User]:
    mentions = re.findall(user_mentions, string)
    # Il faut enlever les <@> autour de la mention
    users_ids = [int(u[2:-1]) for u in mentions]
    users = [await bot.fetch_user(u) for u in users_ids]
    return users


async def wait_until(dt: datetime):
    delay = dt - now()
    await asyncio.sleep(delay.total_seconds())


def color_permissions(perm: discord.Permissions) -> str:
    perms = list()
    perm_list = [k for k, v in discord.Permissions.__dict__.items() if isinstance(v, discord.flags.flag_value)]
    perm_list.sort()
    for key in perm_list:
        if getattr(perm, key):
            color = "{}"
            if getattr(discord.Permissions.advanced(), key):
                color = "<red>{}<reset>"
            elif getattr(discord.Permissions.general(), key):
                color = "<yellow>{}<reset>"
            elif getattr(discord.Permissions.membership(), key):
                color = "<cyan>{}<reset>"
            perms.append(color.format(key))
    return ANSI.converter('\n'.join(perms))


async def jumpurl2Message(bot: discord.AutoShardedBot, url: str) -> discord.Message:
    # url au format "https://discord.com/channels/guild_id/channel_id/message_id"
    try:
        gid, cid, mid = url.strip('/').split('/')[-3:]
        guild = await bot.fetch_guild(gid)
        chanel = await guild.fetch_channel(cid)
        message = await chanel.fetch_message(mid)
        return message
    except:
        return None


def strip_accents(text: str):
    text = normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    return text


# liste des timezones dans pytz.all_timezones
def convert_timezone(dt: datetime, tz1, tz2) -> datetime:
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    if not isinstance(dt, datetime):
        dt = datetime.strptime(dt, "%Y-%m%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    return dt


def get_all(parse):
    if isinstance(parse, dict):
        parse = parse.items()

    if isinstance(parse, str):
        yield parse

    try:
        for elt in parse:
            for e in get_all(elt):
                yield e
    except:
        yield parse


@tasks.loop(count=1)
async def delay(until: datetime, coro, *args, **kwargs):
    await wait_until(until)
    await coro(*args, **kwargs)


# générateur qui renvoie un gradient de couleur
def grad(start: discord.Color, end: discord.Color, nb: int):
    pas = {c: (getattr(end, c) - getattr(start, c)) // nb for c in 'rgb'}
    for i in range(nb):
        kwargs = {c: getattr(start, c) + i * pas[c] for c in 'rgb'}
        yield Color.from_rgb(**kwargs)
    yield end
