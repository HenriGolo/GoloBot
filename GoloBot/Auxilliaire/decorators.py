from functools import wraps
from os import environ
from discord import Forbidden
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.doc import cmds


def command_logger(func):
    start = now(True)

    @wraps(func)
    async def wrapper_error(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        self = args[0]
        cname = self.__class__.__name__
        ctx = args[1]
        user = ctx.author.name
        signature = "\n\t".join(args_repr + kwargs_repr)
        time = start.replace(microsecond=0)
        with open(environ['stdout'], 'a') as stdout:
            stdout.write(f"\n{time} {user} : {cname}.{func.__name__} dans {ctx.guild.name} avec comme arguments\n\t{signature}")

            result = None
            try:
                result = await func(*args, **kwargs)
                stdout.write(f"{func.__name__} terminé en {now(True) - start}s")

            except Forbidden as e:
                await ctx.respond(f"{self.bot.emotes['error']} Manque de permissions", ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

            except Exception as e:
                await ctx.respond(environ['error_msg'], ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

        return result

    return wrapper_error


def modal_logger(func):
    start = now(True)

    @wraps(func)
    async def wrapper_error(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        self = args[0]
        cname = self.__class__.__name__
        interaction = args[1]
        user = interaction.user.name
        signature = "\n\t".join(args_repr + kwargs_repr)
        time = start.replace(microsecond=0)
        with open(environ['stdout'], 'a') as stdout:
            stdout.write(f"\n{time} {user} : {cname}.{func.__name__}\
    dans {interaction.guild.name} avec comme arguments\n\t{signature}")

            result = None
            try:
                result = await func(*args, **kwargs)
                stdout.write(f"{func.__name__} terminé en {now(True) - start}s")

            except Forbidden as e:
                await interaction.response.send_message(f"{self.bot.emotes['error']} Manque de permissions", ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

            except Exception as e:
                await interaction.response.send_message(environ['error_msg'], ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

        return result

    return wrapper_error


def button_logger(func):
    start = now(True)

    @wraps(func)
    async def wrapper_error(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        self = args[0]
        cname = self.__class__.__name__
        interaction = args[2]
        user = interaction.user.name
        signature = "\n\t".join(args_repr + kwargs_repr)
        time = start.replace(microsecond=0)
        with open(environ['stdout'], 'a') as stdout:
            stdout.write(f"\n{time} {user} : {cname}.{func.__name__}\
    dans {interaction.guild.name} avec comme arguments\n\t{signature}")

            result = None
            try:
                result = await func(*args, **kwargs)
                stdout.write(f"{func.__name__} terminé en {now(True) - start}s")

            except Forbidden as e:
                await interaction.response.send_message(f"{self.bot.emotes['error']} Manque de permissions", ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

            except Exception:
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

        return result

    return wrapper_error


# Applique une liste de décorateurs
def apply_list(decorators):
    def wrapper(f):
        for d in reversed(decorators):
            f = d(f)
        return f

    return wrapper


def customSlash(func):
    name = func.__name__.strip('_')
    func = command_logger(func)
    func = apply_list(cmds[name].options)(func)
    return func
