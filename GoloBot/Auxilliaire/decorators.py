from functools import wraps
from os import environ
from discord import Forbidden, ui, Interaction, ButtonStyle
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.doc import cmds


class ShowFullError(ui.Button):
    def __init__(self, full_embed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.full = full_embed

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.full, view=None)


class ViewError(MyView):
    def __init__(self, full_embed):
        super().__init__()
        self.add_item(ShowFullError(full_embed, label="Détails", style=ButtonStyle.danger))


def command_logger(func):
    start = now(True)

    @wraps(func)
    async def wrapper_error(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        caller = args[0]
        cname = caller.__class__.__name__
        ctx = args[1]
        user = ctx.author.name
        gname = f"MP de {user}"
        if ctx.guild is not None:
            gname = ctx.guild.name
        signature = "\n\t".join(args_repr + kwargs_repr)
        time = start.replace(microsecond=0)
        with (open(environ['stdout'], 'a') as stdout):
            stdout.write(f"\n{time} {user} : {cname}.{func.__name__} dans {gname} avec comme arguments\n\t{signature}")

            result = None
            try:
                result = await func(*args, **kwargs)
                stdout.write(f"{func.__name__} terminé en {now(True) - start}s")

            except Forbidden:
                await ctx.respond(f"{caller.bot.emotes['error']} Manque de permissions", ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

            except Exception:
                err = fail()
                embed = MyEmbed(title="Un problème est survenu ...", color=0xff0000)
                full_embed = embed.copy()
                full_embed.description = f"```\n{err.strip()}\n```"
                await ctx.respond(embed=embed, view=ViewError(full_embed), ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{err}\n")

        return result

    return wrapper_error


def interaction_logger(func):
    start = now(True)

    @wraps(func)
    async def wrapper_error(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        caller = args[0]
        cname = caller.__class__.__name__
        interaction = args[1]
        user = interaction.user.name
        gname = f"MP de {user}"
        if interaction.guild is not None:
            gname = interaction.guild.name
        signature = "\n\t".join(args_repr + kwargs_repr)
        time = start.replace(microsecond=0)
        with open(environ['stdout'], 'a') as stdout:
            stdout.write(f"\n{time} {user} : {cname}.{func.__name__}\
    dans {gname} avec comme arguments\n\t{signature}")

            result = None
            try:
                result = await func(*args, **kwargs)
                stdout.write(f"{func.__name__} terminé en {now(True) - start}s")

            except Forbidden:
                await interaction.response.send_message(f"{caller.bot.emotes['error']} Manque de permissions", ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

            except Exception:
                err = fail()
                embed = MyEmbed(title="Un problème est survenu ...", color=0xff0000)
                full_embed = embed.copy()
                full_embed.description = f"```\n{err.strip()}\n```"
                await ctx.respond(embed=embed, view=ViewError(full_embed), ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{err}\n")

        return result

    return wrapper_error


modal_logger = interaction_logger
select_logger = interaction_logger
button_logger = interaction_logger


# Applique une liste de décorateurs
def apply_list(decorators):
    def wrapper(func):
        for deco in reversed(decorators):
            func = deco(func)
        return func

    return wrapper


def customSlash(func):
    name = func.__name__.strip('_')
    func = command_logger(func)
    func = apply_list(cmds[name].options)(func)
    return func
