from discord.ext.commands import Converter
# On ne s'en sert pas ici, mais ce sont des converters aussi
from discord import User, Member, TextChannel
from collections import namedtuple

compint = namedtuple("CompNInt", ["comp", "int"])
class CompNInt(Converter):
	async def convert(self, ctx, arg):
		default = ">="
		try:
			comp = default
			value = int(arg)

		except:
			comp = arg[0]
			if not comp in ["=", ">", "<"]:
				try:
					int(comp)
					comp = default
				except:
					raise Exception(f"Argument Invalide : {arg}")
			if arg[1] == "=":
				comp += "="
				value = int(arg[2:])
			else:
				value = int(arg[1:])
		return compint(comp, value)

class Splitter(Converter):
	async def convert(self, ctx, arg):
		if arg == None:
			return []
		return [e.strip() for e in arg.split(";")]
