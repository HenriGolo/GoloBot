from GoloBot.Auxilliaire import *
from functools import wraps

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
				result = None
				result = await func(*args, **kwargs)
				print(f"{func.__name__} terminé en {now(True)-start}s")

			except Exception:
				await ctx.respond(environ['error_msg'], ephemeral=True)
				with open(environ['stderr'], 'a') as file:
					file.write(f"\n{start}\n{fail()}\n")

			return result
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
				result = None
				result = await func(*args, **kwargs)
				print(f"{func.__name__} terminé en {now(True)-start}s")

			except Exception as e:
				await interaction.response.send_message(environ['error_msg'], ephemeral=True)
				with open(environ['stderr'], 'a') as file:
					file.write(f"\n{start}\n{fail()}\n")

			return result
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
				result = None
				result = await func(*args, **kwargs)
				print(f"{func.__name__} terminé en {now(True)-start}s")

			except Exception:
				with open(environ['stderr'], 'a') as file:
					file.write(f"\n{start}\n{fail()}\n")

			return result
		return wrapper_error
