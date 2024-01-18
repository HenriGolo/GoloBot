from functools import wraps
from os import environ
from discord import Forbidden, ui, Interaction, ButtonStyle
from discord.ext.commands import slash_command
from discord.commands.context import ApplicationContext
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.doc import cmds


class ManquePerms(Exception):
    pass


class BoutonShowFullError(ui.Button):
    def __init__(self, bot, full_embed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.full = full_embed

    async def callback(self, interaction: Interaction):
        view = GBView(self.bot)
        view.add_item(BoutonTransfert(self.bot, self.view.bot.dev, self.view.embed_err, label="Transférer",
                                      style=ButtonStyle.success))
        await interaction.response.edit_message(embed=self.full, view=view)


class BoutonTransfert(ui.Button):
    def __init__(self, bot, user, embed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.user = user
        self.embed = embed

    async def callback(self, interaction: Interaction):
        from GoloBot.UI.dm import BoutonSupprimerDM
        await self.user.send(embed=self.embed, view=GBView(self.bot, BoutonSupprimerDM(self.bot)))
        await interaction.response.edit_message(delete_after=0)


class ViewError(GBView):
    def __init__(self, bot, full_embed, embed_err):
        super().__init__(bot)
        self.bot = bot
        self.embed_err = embed_err
        self.add_item(BoutonShowFullError(bot, full_embed, label="Détails", style=ButtonStyle.danger))
        if hasattr(bot, "dev"):
            self.add_item(BoutonTransfert(bot, bot.dev, embed_err, label="Transférer", style=ButtonStyle.success))


class Data:
    def __init__(self, *args):
        assert len(args) > 0
        self.caller = args[0]
        self.user = None
        self.guild = None

        # on ne peut pas async un lambda, donc c'est moche
        async def donothing(*args, **kwargs):
            return None

        self.action = donothing

        if len(args) > 1:
            source = args[1]
            if isinstance(source, ApplicationContext):
                self.user = source.author
                self.guild = source.guild
                self.action = source.respond

            elif isinstance(source, Interaction):
                self.user = source.user
                self.guild = source.guild
                self.action = source.response.send_message


def logger(func):
    start = now(True)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        data = Data(*args)
        cname = data.caller.__class__.__name__
        user = "listener"
        gname = "listener"

        if data.user is not None:
            user = data.user.name
            gname = f"MP de {user}"

        if data.guild is not None:
            gname = data.guild.name

        signature = "\n\t".join(args_repr + kwargs_repr)
        time = start.replace(microsecond=0)

        try:
            result = await func(*args, **kwargs)

        except (Forbidden, ManquePerms):
            await data.action(f"{data.caller.bot.emotes['error']} Manque de permissions", ephemeral=True)
            if 'stderr' in environ:
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{fail()}\n")

        except Exception:
            err = fail()
            embed = GBEmbed(title="Un problème est survenu ...", color=0xff0000)
            full_embed = embed.copy()
            full_embed.description = f"```python\n{err.strip()}\n```"
            embed_err = full_embed.copy()
            embed_err.title = f"Erreur de {user} avec {func.__name__}"
            view = ViewError(data.caller.bot, full_embed, embed_err)
            await data.action(embed=embed, view=view, ephemeral=True)
            if 'stderr' in environ:
                with open(environ['stderr'], 'a') as stderr:
                    stderr.write(f"\n{start}\n{err}\n")

        else:
            # Sera exécuté si aucune exception n'est soulevée
            if 'stdout' in environ:
                with open(environ['stdout'], 'a') as stdout:
                    stdout.write(f"\n{time} {user} : {cname}.{func.__name__} "
                                 f"dans {gname} avec comme arguments\n\t{signature}")
                    stdout.write(f"{func.__name__} terminé en {now(True) - start}s")
            return result

    return wrapper_error
    return wrapper


# Applique une liste de décorateurs
def apply_list(decorators):
    def wrapper(func):
        for deco in reversed(decorators):
            func = deco(func)
        return func

    return wrapper


def customSlash(func):
    name = func.__name__.strip('_')
    func = logger(func)
    func = apply_list(cmds[name].options)(func)
    func = slash_command(name=name, description=cmds[name].desc)(func)
    return func
