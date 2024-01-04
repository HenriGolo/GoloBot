import json
import discord
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.converters import ANSI

guild_to_settings = dict()


class Param:
    instances = list()

    def __init__(self, name, desc, value, predicate=lambda _: False):
        self.name = name
        self.desc = desc
        self.value = value
        self.base = value
        self.predicate = predicate
        self.__class__.instances.append(self)

    def __repr__(self):
        std = repr(self.__class__)  # de la forme <class 'nom'>
        cls = std.split("'")[1]
        excluded = ["predicate", "base"]
        attr = [f"{k}={v}" for k, v in self.__dict__.items() if not k in excluded]
        return f"<{cls} {' '.join(attr)}>"

    def __str__(self):
        raw = f"<green>{self.name}<reset> : {self.desc}"
        raw += "\n\tValeur : "
        value = self.value
        if value == self.base:
            value = f"<yellow>{value}<reset>"
        raw += value
        return ANSI().converter(raw)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.desc == other.desc
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self == other:
                return self.value < other.value
            return self.name < other.name
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            if self == other:
                return self.value > other.value
            return self.name > other.name
        return False

    def update(self, value):
        if self.predicate(value):
            self.value = value
            return Exit.Success
        return Exit.Fail


Param("id",
      None,
      0)

Param("default volume",
      "Volume sonore par défaut.",
      100,
      lambda i: isinstance(i, int) and 0 <= i <= 100)

Param("autopublish bots",
      "Publie automatiquement les messages des bots.",
      False,
      lambda b: isinstance(b, bool))

Param.instances.sort()


class Settings:
    template = {p.name: p for p in Param.instances}

    def __init__(self, guild, path='logs/settings.json'):
        self.guild = guild
        self.json_data = None
        self.config = None
        self.path = path
        self.reload()
        self.upgrade()

    def write(self, setting, value):
        response = self.config.get(setting, Param()).update(value)
        with open(self.path, 'w') as source:
            json.dump(self.json_data, source, cls=GBEncoder)
        self.reload()
        return response

    def reload(self):
        source = open(self.path, 'r')
        self.json_data = json.load(source, cls=GBDecoder)
        target = None
        for server in self.json_data:
            server = self.json_data[server]
            if server['id'] == self.guild.id:
                target = server

        if target is None:
            return self.create()
        self.config = target

        for key, value in self.config.items():
            if isinstance(value, (str, bytes, bytearray)):
                self.config[key] = json.loads(value, cls=GBDecoder)

    def upgrade(self):
        refresh = False
        for key in self.template.keys():
            if key in self.config:
                continue
            self.config[key] = self.template.get(key)
            refresh = True
        if refresh:
            with open(self.path, 'w') as source:
                json.dump(self.json_data, source, cls=GBEncoder)
            self.reload()

    def create(self):
        self.json_data[self.guild.id] = self.template
        self.json_data[self.guild.id]['id'] = self.guild.id
        with open(self.path, 'w') as source:
            json.dump(self.json_data, source, cls=GBEncoder)
        self.reload()

    def __getitem__(self, item):
        return self.config[item]

    def __str__(self):
        return "\n".join([str(self.config[p]) for p in self.config])

    def to_embed(self, color=None):
        if color is None:
            color = self.guild.owner.color
        embed = GBEmbed(title=f"Paramètres de {self.guild.name}", description=str(self), color=color)
        embed.set_thumbnail(url=self.guild.icon.url)
        return embed
