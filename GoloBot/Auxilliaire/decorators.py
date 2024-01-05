from functools import wraps
from os import environ

import discord
from discord import Forbidden, ui, Interaction, ButtonStyle
from discord.ext.commands import slash_command
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.doc import cmds


class BoutonShowFullError(ui.Button):
    def __init__(self, bot, full_embed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.full = full_embed

    async def callback(self, interaction: Interaction):
        view = GBView(self.bot)
        view.add_item(BoutonTransfert(self.bot, self.view.dev, self.view.embed_err, label="Transférer", style=ButtonStyle.success))
        await interaction.response.edit_message(embed=self.full, view=view)


class BoutonTransfert(ui.Button):
    def __init__(self, bot, dev, embed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.dev = dev
        self.embed = embed

    async def callback(self, interaction: Interaction):
        from GoloBot.UI.dm import BoutonSupprimerDM
        await self.dev.send(embed=self.embed, view=GBView(self.bot, BoutonSupprimerDM(self.bot)))
        await interaction.response.edit_message(delete_after=0)


class ViewError(GBView):
    def __init__(self, bot, dev, full_embed, embed_err):
        super().__init__()
        self.bot = bot
        self.dev = dev
        self.embed_err = embed_err
        self.add_item(BoutonShowFullError(bot, full_embed, label="Détails", style=ButtonStyle.danger))
        self.add_item(BoutonTransfert(bot, dev, embed_err, label="Transférer", style=ButtonStyle.success))


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
                embed = GBEmbed(title="Un problème est survenu ...", color=0xff0000)
                full_embed = embed.copy()
                full_embed.description = f"```python\n{err.strip()}\n```"
                embed_err = full_embed.copy()
                embed_err.title = f"Erreur de {user} avec {func.__name__}"
                view = ViewError(caller.bot, caller.bot.dev, full_embed, embed_err)
                await ctx.respond(embed=embed, view=view, ephemeral=True)
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
                await interaction.response.send_message(f"{caller.bot.emotes['error']} Manque de permissions",
                                                        ephemeral=True)
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

            except Exception:
                err = fail()
                embed = GBEmbed(title="Un problème est survenu ...", color=0xff0000)
                full_embed = embed.copy()
                full_embed.description = f"```python\n{err.strip()}\n```"
                embed_err = full_embed.copy()
                embed_err.title = f"Erreur de {user} avec {func.__name__}"
                view = ViewError(caller.bot.dev, full_embed, embed_err)
                await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
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
    func = slash_command(name=name, description=cmds[name].desc)(func)
    return func
