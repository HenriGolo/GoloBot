from discord.ext.commands import Converter, Context
from collections import namedtuple
from datetime import timedelta
from discord.ext.commands.converter import T_co

compint = namedtuple("CompNInt", ["comp", "int"])


class CompNInt(Converter):
    async def convert(self, ctx: Context, argument: str) -> T_co:
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


class Splitter(Converter):
    async def convert(self, ctx: Context, argument: str) -> T_co:
        if argument is None:
            return []
        return [e.strip() for e in argument.split(";")]


class Duree(Converter):
    async def convert(self, ctx: Context, argument: str) -> T_co:
        argument = "".join(argument.split(" "))
        jours = heures = minutes = secondes = 0
        number = ""
        for char in argument:
            if char.isdigit():
                number += char
            else:
                if char in "jd":
                    jours = int(number)
                if char == 'h':
                    heures = int(number)
                if char == 'm':
                    minutes = int(number)
                if char == 's':
                    secondes = int(number)
                else:
                    raise Exception(f"Mauvais format de {argument}. Attendu 1j 2h 3m 4s")
                number = ""
        return timedelta(days=jours, hours=heures, minutes=minutes, seconds=secondes)
