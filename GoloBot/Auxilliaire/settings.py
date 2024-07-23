import json
import discord
from . import *
from .converters import ANSI

guild_to_settings = dict()


class Param(Storable):
    instances = list()

    def __init__(self, name, desc, value, _type):
        self.name = name
        self.desc = desc
        self.value = value
        self._type = _type
        self.__class__.instances.append(self)

    def __str__(self):
        raw = f"<green>{self.name}<reset> : {self.desc}"
        raw += "\n\tValeur : "
        raw += f"<yellow>{self.value}<reset> (<blue>{self._type.__name__}<reset>)"
        return ANSI.converter(raw)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.name == other.name and self.desc == other.desc
        return self.value == other

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self == other:
                return self.value < other.value
            return self.name < other.name
        return self.value < other

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            if self == other:
                return self.value > other.value
            return self.name > other.name
        return self.value > other

    def __bool__(self):
        return bool(self.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def update(self, value):
        if isinstance(value, self._type):
            self.value = value
            return Exit.Success
        return Exit.Fail


Param("default volume",
      "Volume sonore par défaut. Doit être compris entre 0 et 100.",
      100,
      int)

Param("autopublish bots",
      "Publie automatiquement les messages des bots.",
      False,
      bool)

Param("reponses custom",
      "Autorise le bot à réagir avec un comportement personnalisable par les utilisateurs.",
      True,
      bool)

Param.instances.sort()


class Settings:
    template = {p.name: p for p in Param.instances}
    indent = 4
    excluded = list()

    def __init__(self, guild, **kwargs):
        self.guild = guild
        self.path = kwargs.get('path', GBpath + 'Data/settings.json')
        self.json_data = None
        self.config = None
        self.reload()
        self.upgrade()

    def write(self, setting, value):
        params = {p.name: p for p in Param.instances}
        response = self.config.get(setting, params[setting]).update(value)
        with open(self.path, 'w') as source:
            json.dump(self.json_data, source, cls=GBEncoder, indent=self.indent)
        self.reload()
        return response

    def reload(self):
        with open(self.path, 'r') as source:
            self.json_data = json.load(source, cls=GBDecoder)
        target = None
        for guild_id, data in self.json_data.items():
            if self.guild is None:
                continue
            if guild_id == self.guild.id:
                target = data

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
                json.dump(self.json_data, source, cls=GBEncoder, indent=self.indent)
            self.reload()

    def create(self):
        self.json_data[self.guild.id] = self.template
        with open(self.path, 'w') as source:
            json.dump(self.json_data, source, cls=GBEncoder, indent=self.indent)
        self.reload()

    def __getitem__(self, item):
        return self.config[item]

    def __str__(self):
        return "\n".join([str(self.config[p]) for p in self.config if not p in self.excluded])

    def to_embed(self):
        color = self.guild.owner.color
        embed = GBEmbed(title=f"Paramètres de {self.guild.name}", description=str(self), color=color)
        embed.set_thumbnail(url=self.guild.icon.url)
        return embed
