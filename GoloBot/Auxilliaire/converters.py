import re
from discord.ext.commands import Converter, Context
from collections import namedtuple
from datetime import timedelta
from discord.ext.commands.converter import T_co
from enum import Enum


class CompNInt(Converter):
    @classmethod
    def converter(cls, argument):
        compint = namedtuple("CompNInt", ["comp", "int"])
        default = ">="
        try:
            comp = default
            value = int(argument)

        except:
            comp = argument[0]
            if comp in ["=", ">", "<"]:
                pass
            else:
                try:
                    int(comp)
                    comp = default
                except:
                    raise Exception(f"Argument Invalide : {argument}")
            if argument[1] == "=":
                comp += "="
                value = int(argument[2:])
            else:
                value = int(argument[1:])
        return compint(comp, value)

    async def convert(self, ctx: Context, argument: str) -> T_co:
        return self.converter(argument)


class Splitter(Converter):
    @classmethod
    def converter(cls, argument):
        if argument is None:
            return []
        return [e.strip() for e in argument.split(";")]

    async def convert(self, ctx: Context, argument: str) -> T_co:
        return self.converter(argument)


class Duree(Converter):
    @classmethod
    def converter(cls, argument: str):
        argument = argument.replace(' ', '')
        jours = heures = minutes = secondes = 0
        number = ""
        for char in argument:
            if char.isdigit():
                number += char
            else:
                if char in "jd":
                    jours = int(number)
                elif char == 'h':
                    heures = int(number)
                elif char == 'm':
                    minutes = int(number)
                elif char == 's':
                    secondes = int(number)
                else:
                    raise Exception(f"Mauvais format de {argument}. Attendu 1j 2h 3m 4s")
                number = ""
        return timedelta(days=jours, hours=heures, minutes=minutes, seconds=secondes)

    async def convert(self, ctx: Context, argument: str) -> T_co:
        return self.converter(argument)


class TextColor(Enum):
    gray = 30
    red = 31
    green = 32
    yellow = 33
    blue = 34
    pink = 35
    cyan = 36
    white = 37


class BackgroundColor(Enum):
    firefly_darj_blue = 40
    orange = 41
    marble_blue = 42
    greyish_turquoise = 43
    gray = 44
    indigo = 45
    light_gray = 46
    white = 47


class ANSI(Converter):
    @classmethod
    def converter(cls, argument: str):
        if not argument:
            return argument

        colors = {f"<{c.name}>": f"\u001b[{c.value}m" for c in TextColor}
        colors["<reset>"] = f"\u001b[0m"
        bgcolors = {f"<bg_{c.name}>": f"\u001b[{c.value}m" for c in BackgroundColor}
        tags = re.compile(r"<[a-z_]+>")  # Pas le filtrage le plus optimal
        found = re.findall(tags, argument)
        if not found:
            return argument

        parts = argument.split("```")
        parts[1::2] = [f"```{e}```" for e in parts[1::2]]
        modified = list()
        for part in parts[::2]:
            part = part.strip()
            need_wrap = False
            for pattern in re.findall(tags, part):
                if pattern in colors:
                    part = part.replace(pattern, colors[pattern])
                    need_wrap = True
                if pattern in bgcolors:
                    part = part.replace(pattern, bgcolors[pattern])
                    need_wrap = True
            if not part:  # str vide
                need_wrap = False
            if need_wrap:
                part = f"```ansi\n{part}\n```"
            modified.append(part)
        parts[::2] = modified
        return "\n".join(parts)

    async def convert(self, ctx: Context, argument: str) -> T_co:
        return self.converter(argument)
