# Code Principal
import asyncio
import json
import discord
from discord.ext import commands, tasks
from discord.commands.context import ApplicationContext
from .Auxilliaire import *  # Quelques fonctions utiles
from .Auxilliaire.aux_maths import *  # Outils mathématiques
from .Auxilliaire.converters import *  # Converters vers mes types custom
from .Auxilliaire.decorators import *  # Decorateurs custom
from .Auxilliaire.doc import *  # Raccourcis et noms customs
from .Auxilliaire.games import *  # Jeux de plateau custom
from .Musique import *  # Adapté de https://github.com/Raptor123471/DingoLingo
from .UI import *  # Les composants de l'UI custom
from .template import *  # Signatures du bot défini dans 'main.py' et donc pas importable
from .Twitch import *


# Code du bot
class CogGeneral(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot

    # Aide
    @CustomSlash
    async def aide(self, ctx: ApplicationContext, commande: str, visible: bool):
        await ctx.defer(ephemeral=not visible)
        if not commande in cmds:
            commande = self.bot.commands_names.search(commande)[0][0]
        # Nom, ID et mention de la commande concernée
        commande = self.bot.get_application_command(commande)
        name = commande.qualified_name
        cmd_id = commande.qualified_id
        mention = f"</{name}:{cmd_id}>"
        commande = cmds[name]
        # Embed des informations sur la commande
        embed = GBEmbed(title="Aide", description=mention, color=ctx.author.color)
        embed.set_author(name=self.bot.support.name,
                         url=environ.get('invite_server', ''),
                         icon_url=self.bot.support.icon.url)
        embed.add_field(name="Description", value=commande.desc, inline=False)
        embed.add_field(name="Permissions Nécessaires", value=commande.perms, inline=False)
        embed.add_field(name="Paramètres", value=str(commande))
        # Dans un if, car potentiellement non renseigné
        if not commande.aide == "":
            embed.add_field(name="Aide Supplémentaire", value=commande.aide, inline=False)
        embed.add_field(name="Encore des questions ?",
                        value=f"Le <:discord:1164579176146288650> [Serveur de Support]({environ.get('invite_server', None)}) est là pour ça",
                        inline=False)
        await ctx.respond(embed=embed, view=ViewAide(self.bot), ephemeral=not visible)

    # Renvoie un lien pour inviter le bot
    @CustomSlash
    async def invite(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title=f"Inviter {self.bot.user.display_name}",
                        description=f"""Tu peux m'inviter avec [ce lien]({environ.get('invite_bot', None)})
Et rejoindre le <:discord:1164579176146288650> Serveur de Support [avec celui ci]({environ.get('invite_server', None)})""",
                        color=ctx.author.color)
        support_qrcode = environ.get('support_qr', None)
        if support_qrcode:
            embed.set_thumbnail(url=support_qrcode)
        await ctx.respond(embed=embed, ephemeral=True)

    # Renvoie le code source du bot
    @CustomSlash
    async def github(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title="Code Source",
                        description=f"Le code source est disponible sur <:github:1164672088934711398> [Github]({environ.get('github', None)})\n\
Tu peux aussi rejoindre le <:discord:1164579176146288650> [Serveur de Support]({environ.get('invite_server', None)})",
                        color=ctx.author.color)
        support_qrcode = environ.get('support_qr', None)
        if support_qrcode:
            embed.set_thumbnail(url=support_qrcode)
        await ctx.respond(embed=embed, ephemeral=True)

    # Quelques stats sur le nombre de box à ouvrir pour espérer un certain pourcentage
    @CustomSlash
    async def droprates(self, ctx: ApplicationContext, pourcentage: float, nom: str, item: str):
        await ctx.defer(ephemeral=(nom == "" or item == ""))
        p = pourcentage / 100
        seuils = {50: 0,
                  75: 0,
                  90: 0}
        klist = [key for key in seuils]
        klist.sort()
        n = 1
        b = Binomiale(n, p)
        proba = b.proba_sup(1)
        while proba * 100 < klist[-1]:
            for key in klist[:-1]:
                if not seuils[key] == 0:
                    continue
                if proba * 100 >= key:
                    seuils[key] = n

            # Incrémentation compteur
            n += 1
            b = Binomiale(n, p)
            proba = b.proba_sup(1)
        seuils[klist[-1]] = n

        title = f"Chances de drop {item}"
        if not nom == "":
            title += f" dans {nom}"
        embed = GBEmbed(title=title, description=f"Pourcentage dans 1 lootbox : {pourcentage}", color=ctx.author.color)
        for key in seuils:
            n = seuils[key]
            embed.add_field(name=f"Au moins {key} % de chances", value=f"{n} lootboxes", inline=False)
        await ctx.respond(embed=embed, ephemeral=(nom == "" or item == ""))


# Fonctions Dev
class CogDev(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot

    # Les ID sont ceux de mon serveur de test et du serveur de support
    @commands.slash_command(guild_ids=[664006363508244481, 1158154606124204072],
                            description="Commande de test, ne pas utiliser.")
    async def test(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=...)
        embed = GBEmbed(title="test", user=ctx.author, guild=ctx.guild)
        values = list()
        values.append("truc à afficher")
        embed.description = '\n'.join([str(e) for e in values])
        await ctx.respond(embed=embed)

    # Envoie un message privé à un User
    @CustomSlash
    async def dm(self, ctx):
        # Commande réservée au dev
        if not ctx.author == self.bot.dev:
            await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise ManquePerms("N'est pas dev")

        await ctx.send_modal(ModalDM(bot=self.bot, title="Envoyer un message privé"))

    # Déconnecte le bot
    @CustomSlash
    async def logout(self, ctx):
        await ctx.defer(ephemeral=True)
        # Commande réservée aux User dans la whitelist
        if not ctx.author == self.bot.dev:
            if ctx.author in self.bot.whitelist:
                pass
            else:
                await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
                await self.bot.dev.send(f"{ctx.author.mention} a essayé de déconnecter le bot")
                raise ManquePerms("N'est pas dev")

        await ctx.respond(f"En ligne depuis : {Timestamp(self.bot.startTime).relative}", ephemeral=True)
        # Déconnecte le bot
        await self.bot.close()

    # Renvoie le ping et d'autres informations
    @CustomSlash
    async def ping(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title="Ping et autres informations", color=ctx.author.color)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)} ms", inline=False)
        embed.add_field(name="Bot en ligne depuis", value=f"{Timestamp(self.bot.startTime).relative}", inline=False)
        embed.add_field(name="Propiétaire", value=self.bot.dev.mention, inline=False)
        if ctx.author == self.bot.dev:
            embed.add_field(name="Websocket", value=self.bot.ws, inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    # Propose une suggestion
    @CustomSlash
    async def suggestions(self, ctx):
        await ctx.send_modal(ModalDM(bot=self.bot, target=self.bot.dev, title="Suggestion"))

    # Renvoie les logs
    @CustomSlash
    async def get_logs(self, ctx: ApplicationContext, last_x_lines: int):
        await ctx.defer(ephemeral=True)
        # Commande réservée au dev
        if not ctx.author == self.bot.dev:
            await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise ManquePerms("N'est pas dev")

        if not 'stderr' in environ:
            raise Exception("Aucun fichier de log renseigné")

        stderr = discord.File(fp=environ['stderr'], filename=environ['stderr'].split("/")[-1])
        embed = GBEmbed(title=f"Dernières {last_x_lines} lignes de {stderr.filename}", user=ctx.author)
        embed.description = f"```python\n{tail(environ['stderr'], last_x_lines)}\n```"
        await ctx.respond(embed=embed, files=[stderr], ephemeral=True)

    @CustomSlash
    async def get_history(self, ctx: ApplicationContext, last_x_lines: int):
        await ctx.defer(ephemeral=True)
        # Commande réservée au dev
        if not ctx.author == self.bot.dev:
            await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise ManquePerms("N'est pas dev")

        if not 'stdout' in environ:
            raise Exception("Aucun fichier de sortie renseigné")

        stdout = File(fp=environ['stdout'], filename=environ['stdout'].split("/")[-1])
        reponse = f"Dernières {last_x_lines} lignes de **{stdout}** :\n{tail(environ['stdout'], last_x_lines)[-1900:]}"
        await ctx.respond(f"Voici les logs demandés\n{reponse}", files=[stdout], ephemeral=True)


# Fonctions Admin
class CogAdmin(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot

    # Création de sondage
    @CustomSlash
    async def poll(self, ctx: ApplicationContext, question: str, reponses: Splitter, salon: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        if salon == base_value:
            salon = ctx.channel

        # Discord oblige de répondre aux appels de commande
        await ctx.respond("Sondage en cours de création", ephemeral=True, delete_after=2)

        # Préparation les réactions
        # Étant donné le passage par l'ASCII, ajouter des réactions nécessite un changement de la procédure
        # Car les nombres, majuscules et minuscules ne sont pas accolés
        # Première lettre de chaque réponse
        first_letters = "".join([s[0].lower() for s in reponses])
        # Tableau de bool pour savoir si les premières lettres sont uniques
        # Au moins un doublon, ou une non-lettre → alphabet standard
        if False in [check_unicity(first_letters, l) and 'a' <= l <= 'z' for l in first_letters]:
            used_alphaB = self.bot.alphabet[:len(reponses)]
        # Que des lettres uniques, on répond avec les lettres correspondantes
        else:
            a = ord('a')
            used_alphaB = [self.bot.alphabet[ord(i.lower()) - a] for i in first_letters]
        # Trop de réponses à gérer
        if len(reponses) > len(self.bot.alphabet):
            await ctx.respond(f"""Oula ... On va se calmer sur le nombre de réponses possibles,
j'ai pas assez de symboles, mais t'as quand même les {len(used_alphaB)} premiers""", ephemeral=True)

        # Préparation de l'affichage des réactions
        choix = [f"{used_alphaB[i]} {reponses[i]}" for i in range(len(used_alphaB))]
        final = "\n".join(choix)

        # Création de l'embed
        embed = GBEmbed(user=ctx.author, title="Sondage")
        embed.add_field(name="Question", value=ANSI.converter(question), inline=False)
        embed.add_field(name="Réponses", value=final, inline=False)

        # Envoi avec les réactions
        sondage = await salon.send(embed=embed)
        for i in range(len(used_alphaB)):
            emote = used_alphaB[i]
            await sondage.add_reaction(emote)
        await ctx.respond("Sondage créé !", ephemeral=True)

    # Role react
    @CustomSlash
    @commands.has_permissions(manage_roles=True)
    @discord.guild_only()
    async def role_react(self, ctx: ApplicationContext, roles: str, texte: str, message: discord.Message):
        if roles == base_value and texte == base_value and message == base_value:
            return await ctx.respond("Veuillez renseigner au moins un paramètre")

        await ctx.defer()
        roles = rolesInStr(roles, ctx.guild)
        view = ViewRoleReact(self.bot, roles=roles)
        rolesm = [e.mention for e in roles]
        if not message == base_value:
            await message.delete()
            await ctx.respond(content=msg.content, view=view)
        else:
            content = "Choisis les rôles que tu veux récupérer parmi\n- {}".format('\n- '.join(rolesm))
            if not texte == "":
                content = texte
            await ctx.respond(content=content, view=view)

    # Nettoyage des messages d'un salon
    @CustomSlash
    async def clear(self, ctx: ApplicationContext, nombre: int, salon: discord.TextChannel, user: discord.User):
        if salon == base_value:
            salon = ctx.channel
        await ctx.defer(ephemeral=True)
        if ctx.channel.type == discord.ChannelType.private:
            with open(GBpath + "logs/logs_dm.txt", "a") as logs:
                await ctx.respond("Début du clear", ephemeral=True, delete_after=2)
                hist = ctx.channel.history(limit=nombre).flatten()
                for msg in await hist:
                    try:
                        await msg.delete()
                        logs.write(f"""
{now()} message de {msg.author} supprimé dans #{salon.name} :
    {msg.content}
""")
                    # Erreur la plus probable : message de l'humain, pas du bot
                    except:
                        pass

                await ctx.respond(f"Mes derniers messages ont été clear", ephemeral=True)
                logs.write(f"\n{now()} Les derniers messages envoyés à {ctx.author.display_name} on été effacés\n")
            return

        # Manque de permissions
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise ManquePerms("Manque de permissions")

        await ctx.respond(f"Début du clear de {salon.mention}", ephemeral=True)
        cpt = 0
        with open(GBpath + f'logs/logs_{ctx.guild.name}.txt', 'a') as logs:
            hist = await salon.history(limit=nombre).flatten()
            for msg in hist:
                if user == base_value or user == msg.author:
                    await msg.delete()
                    logs.write(f"""
{now()} message de {msg.author} supprimé dans #{salon.name} :
    {msg.content}
""")
                    cpt += 1

        await ctx.respond(f"{salon.mention} a été clear de {cpt} messages", ephemeral=True, delete_after=10)

    # Bannir un Member
    @CustomSlash
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: ApplicationContext, user: discord.Member, raison: str):
        await ctx.defer(ephemeral=True)
        # Rôle de la cible trop élevé
        if user.top_role >= ctx.author.top_role:
            await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            await self.bot.dev.send(f"{ctx.author.mention} a voulu ban {user.mention} de {ctx.guild}")
            await ctx.author.timeout(until=now() + timedelta(minutes=2), reason=f"A voulu ban {user.display_name}")
            raise ManquePerms("Rôle trop faible")

        try:
            who = f" (demandé par {ctx.author.display_name})"
            raison += who
            await user.ban(reason=raison)
            await ctx.respond(f"{user.mention} a été ban, raison : **{raison[:-len(who)]}**", ephemeral=True)

        except Exception as error:
            msg = f"Échec du ban de {user.mention} : ```{error}```"
            if not ctx.author == self.bot.dev:
                await self.bot.dev.send(
                    f"{ctx.author.mention} a raté son ban de {user.mention}, message d'erreur : ```{fail()}```")
                msg += "(message d'erreur envoyé au dev en copie)"
            await ctx.respond(msg, ephemeral=True)

    # Mute un Member
    @CustomSlash
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx: ApplicationContext, user: discord.Member, duree: Duree, raison: str):
        await ctx.defer(ephemeral=True)
        end_mute = now() + duree
        # Rôle trop élevé
        if user.top_role >= ctx.author.top_role:
            await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            await ctx.author.timeout(until=end_mute, reason=f"A voulu mute {user.display_name}")
            raise ManquePerms("Rôle trop faible")

        try:
            who = f" (demandé par {ctx.author.display_name})"
            raison += who
            await user.timeout(until=end_mute, reason=raison)
            await ctx.respond(f"{user.mention} a été mute, raison : **{raison[:-len(who)]}**", ephemeral=True)

        except Exception as error:
            msg = f"Échec du mute de {user.mention} : ```{error}```"
            if not ctx.author == self.bot.dev:
                await self.bot.dev.send(
                    f"{ctx.author.mention} a raté son mute de {user.mention}, message d'erreur : ```{fail()}```")
                msg += "(message d'erreur envoyé au dev en copie)"
            await ctx.respond(msg, ephemeral=True)

    @CustomSlash
    @commands.has_permissions(manage_messages=True)
    async def embed(self, ctx: ApplicationContext, edit: str):
        if edit == base_value:
            await ctx.send_modal(ModalNewEmbed(self.bot, edit, title="Nouvel Embed"))
        else:
            msg = await ctx.channel.fetch_message(int(edit))
            embeds = msg.embeds
            embed = embeds[0]
            await ctx.send_modal(ModalEditEmbed(self.bot, embeds, embed, edit, send_new=True, title="Modifier l'Embed"))

    @CustomSlash
    @commands.has_permissions(manage_guild=True)
    async def dashboard(self, ctx):
        await ctx.defer()
        sett = guild_to_settings[ctx.guild]
        view = GBView(self.bot)
        view.add_item(SelectDashboard(self.bot, ctx.guild))
        await ctx.respond(embed=sett.to_embed(), view=view)

    # Donner un rôle
    @CustomSlash
    @commands.has_permissions(manage_roles=True)
    async def roles(self, ctx: ApplicationContext, mode: str, users: str, roles: str):
        await ctx.defer(ephemeral=True)
        conversion = {"ajouter": "add", "enlever": "remove"}
        func = getattr(discord.Member, f"{conversion[mode]}_roles")
        users = await usersInStr(users, self.bot)
        members = [await User2Member(ctx.guild, u) for u in users]
        roles = rolesInStr(roles, ctx.guild)
        for member in members:
            await func(member, *roles)
        await ctx.respond(
            f"{', '.join([r.mention for r in roles])} {mode[:-2] + 'é'} à {', '.join([m.mention for m in members])}",
            ephemeral=True)

    @CustomSlash
    @commands.has_guild_permissions(move_members=True)
    async def move(self, ctx: ApplicationContext, users: str, depuis_salon: discord.VoiceChannel,
                   vers_salon: discord.VoiceChannel):
        await ctx.defer(ephemeral=True)
        # Pourrait éventuellement ne pas être renseigné
        embed = GBEmbed(title="Personnes déplacées", user=ctx.author)
        if isinstance(vers_salon, discord.VoiceChannel):
            if not vers_salon.permissions_for(ctx.author).connect or \
                    not vers_salon.permissions_for(ctx.guild.me).connect:
                raise ManquePerms
            embed.add_field(name="Vers", value=vers_salon.mention)
        else:
            vers_salon = None
            embed.add_field(name="Vers", value="Aucun, déconnexion")
        users = await usersInStr(users, self.bot)
        members = [await User2Member(ctx.guild, u) for u in users]
        # Pourrait éventuellement ne pas être renseigné
        if isinstance(depuis_salon, discord.VoiceChannel):
            members += depuis_salon.members
        affected = list()
        for member in members:
            if member.voice is None or \
                    not member.voice.channel.permissions_for(ctx.author).connect:
                continue
            affected.append(member.mention)
            await member.move_to(vers_salon)
        embed.description = '- ' + '\n- '.join(affected)
        await ctx.respond(embed=embed, ephemeral=True)


# Fonctions Random
class CogMiniGames(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot

    # QPUP, bon courage pour retrouver le lore ...
    @CustomSlash
    async def qpup(self, ctx: ApplicationContext, nbquestions: int):
        await ctx.defer()
        self.bot.qpup = json.load(open(GBpath + environ['qpup']))
        # Boucle sur le nombre de questions à poser
        for loop in range(nbquestions):
            # Tirage au sort d'une question
            line = randrange(len(self.bot.qpup))
            # Envoi de la question
            await ctx.respond(self.bot.qpup[line][0], view=ViewQPUP(self.bot, rep=self.bot.qpup[line][1]))

    # 2048, le _ est nécessaire, une fonction ne commence pas à un chiffre
    @CustomSlash
    async def _2048(self, ctx: ApplicationContext, size: int):
        await ctx.defer()
        # Création d'un 2048
        game = Game2048(size=size)
        game.duree = now()
        add_dict(self.bot.games, ctx.author.mention, game)
        embed = GBEmbed(title="2048", color=ctx.author.color)
        # Envoie du jeu formatté en python ou n'importe quel autre langage
        # pour colorer les chiffres et ajouter un effet visuel
        embed.add_field(name=f"Partie de {ctx.author.display_name}", value=str(game), inline=True)
        moves = [f"{to} : {self.bot.bools[game.canMove(to)]}" for to in list(Directions)]
        embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
        embed.add_field(name="Score", value=game.score, inline=True)
        await ctx.respond(embed=embed, view=View2048(self.bot))


class CogTroll(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot
        super().__init__()

    # Spamme un texte (emote ou autre) jusqu'à atteindre la limite de caractères
    @CustomSlash
    async def write_emote(self, ctx: ApplicationContext, mot: str, message: discord.Message):
        await ctx.defer(ephemeral=True)
        nbchars = nb_char_in_str(mot)
        a = ord('a')
        for char, i in nbchars.items():
            if i > 1:
                msg = f"<red>{char}<reset> apparait <yellow>{i}<reset> fois, impossible d'écrire <red>{mot}<reset> en réactions"
                embed = GBEmbed(title="Erreur", description=ANSI.converter(msg), color=ctx.author.color)
                return await ctx.respond(embed=embed, ephemeral=True)

        emotes = [self.bot.alphabet[ord(c) - a] for c in mot]
        for e in emotes:
            await message.add_reaction(e)
        embed = GBEmbed(color=ctx.author.color)
        embed.description = f"""Tu as écrit {' '.join(emotes)} en dessous de ```
{message.content}
```(Certaines lettres étaient peut être déjà prises)"""
        await ctx.respond(embed=embed, ephemeral=True)

    @CustomSlash
    async def spam_emote(self, ctx: ApplicationContext, emote: str, user: discord.User):
        await ctx.defer(ephemeral=True)
        emote = str(emote) + " "
        lim = ""
        if not user == base_value:
            lim = user.mention
        msg = emote * ((2000 - len(lim)) // len(emote))
        msg += lim
        await ctx.channel.send(msg)
        await ctx.respond(emote, ephemeral=True)


class CogMusic(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot

    @CustomSlash
    @discord.guild_only()
    async def play(self, ctx: ApplicationContext, search: str):
        await ctx.defer(invisible=False)
        audiocontroller = guild_to_audiocontroller[ctx.guild]
        if await is_connected(ctx) is None:
            if not await audiocontroller.uconnect(ctx):
                return
        if not await play_check(ctx):
            return

        # reset timer
        audiocontroller.timer.cancel()
        audiocontroller.timer = Timer(audiocontroller.timeout_handler)
        song = await audiocontroller.process_song(search)
        if song is None:
            return await ctx.respond("Échec de récupération de la vidéo.")

        if song.origin == Origins.Default:
            if audiocontroller.current_song is not None and len(audiocontroller.playlist.playque) == 0:
                await ctx.respond(embed=song.info.format_output("En cours", color=ctx.author.color))
            else:
                await ctx.respond(embed=song.info.format_output("Ajouté à la playlist", color=ctx.author.color))

        elif song.origin == Origins.Playlist:
            await ctx.invoke(self.playlist)

    @CustomSlash
    @discord.guild_only()
    async def playlist(self, ctx):
        try:
            await ctx.defer(ephemeral=True)
        except:
            pass
        if not await play_check(ctx):
            return
        if ctx.guild.voice_client is None or not ctx.guild.voice_client.is_playing():
            await ctx.respond(f"La playlist est vide {self.bot.bools[False]}")
            return

        playlist = guild_to_audiocontroller[ctx.guild].playlist
        embed = GBEmbed(title=f"À venir ({len(playlist.playque)} en tout)", color=ctx.author.color)
        current = guild_to_audiocontroller[ctx.guild].current_song
        if current:
            current = current.info.format_output("En Cours", color=ctx.author.color)
        for counter, song in enumerate(list(playlist.playque)[:5], start=1):
            if song.info.title is not None:
                embed.add_field(name=f"{counter}.", value=f"[{song.info.title}]({song.info.webpage_url})", inline=False)
            else:
                embed.add_field(name=f"{counter}.", value=song.info.webpage_url, inline=False)
        if current:
            await ctx.respond(embeds=[current, embed])
        else:
            await ctx.respond(embed=embed)

    @CustomSlash
    @discord.guild_only()
    async def stop(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        audiocontroller = guild_to_audiocontroller[ctx.guild]
        audiocontroller.playlist.loop = False
        await guild_to_audiocontroller[ctx.guild].stop_player()
        await ctx.guild.voice_client.disconnect()
        await ctx.respond(f"Arrêt de la musique {self.bot.bools[False]}")

    @CustomSlash
    @discord.guild_only()
    async def skip(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        audiocontroller = guild_to_audiocontroller[ctx.guild]
        audiocontroller.playlist.loop = False
        audiocontroller.timer.cancel()
        audiocontroller.timer = Timer(audiocontroller.timeout_handler)
        if ctx.guild.voice_client is None or (
                not ctx.guild.voice_client.is_paused() and not ctx.guild.voice_client.is_playing()):
            await ctx.respond(f"La playlist est vide {self.bot.bools[False]}")
            return
        ctx.guild.voice_client.stop()
        await ctx.respond(f"Passage à la musique suivante {self.bot.emotes['skip']}")

    @CustomSlash
    @discord.guild_only()
    async def songinfo(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        song = guild_to_audiocontroller[ctx.guild].current_song
        if song is None:
            return
        await ctx.respond(embed=song.info.format_output("Infos", color=ctx.author.color))

    @CustomSlash
    @discord.guild_only()
    async def historique(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        await ctx.respond(guild_to_audiocontroller[ctx.guild].track_history())

    @CustomSlash
    @discord.guild_only()
    async def volume(self, ctx: ApplicationContext, volume: int):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return

        if not 0 < volume <= 100:
            return await ctx.respond(f"{volume} n'est pas compris entre 1 et 100")
        guild_to_audiocontroller[ctx.guild].volume = volume
        await ctx.respond(f"Nouveau volume défini sur {volume}")

    @CustomSlash
    @discord.guild_only()
    async def loop(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        loop = guild_to_audiocontroller[ctx.guild].playlist.loop
        guild_to_audiocontroller[ctx.guild].playlist.loop = not loop
        await ctx.respond(
            f"Changement de la boucle dans la PlayList : {self.bot.bools[loop]} -> {self.bot.bools[not loop]}",
            ephemeral=True)


class CogCommandesPasSlash(commands.Cog):
    def __init__(self, bot: BotTemplate):
        self.bot = bot

    # Affiche les informations d'un Member
    @CustomUser
    async def informations_utilisateur(self, ctx: ApplicationContext, member: discord.Member):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title="Informations", user=member, guild=ctx.guild)
        kwargs = {'embed': embed, 'ephemeral': True}
        embed.add_field(name="Nom", value=f"{member.display_name} - {member.nick}", inline=False)
        embed.add_field(name="Identifiant", value=member.id, inline=False)
        if member.banner is not None:
            embed.set_image(url=member.banner.url)
        embed.add_field(name="Date de Création", value=Timestamp(member.created_at).relative, inline=False)
        embed.add_field(name="Dans le serveur depuis", value=Timestamp(member.joined_at).relative, inline=False)
        if member.premium_since is not None:
            embed.add_field(name="Booste le serveur depuis", value=Timestamp(member.premium_since).relative, inline=False)
        if ctx.author.guild_permissions.manage_roles:
            # Le 1er rôle de la liste est "everyone"
            roles = [r.mention for r in member.roles[1:]]
            # On affiche les rôles par ordre de permissions
            roles.reverse()
            embed.add_field(name="Rôles", value="- " + "\n- ".join(roles), inline=False)
        if ctx.author.guild_permissions.manage_permissions:
            kwargs['view'] = ViewUserInfo(self.bot)
        await ctx.respond(**kwargs)

    @CustomMsg
    async def informations_message(self, ctx: ApplicationContext, message: discord.Message):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title="Informations")
        kwargs = {'embed': embed, 'ephemeral': True}
        embed.add_field(name="Auteur", value=f"{message.author.mention}")
        embed.add_field(name="Identifiant", value=message.id)
        embed.add_field(name="Date d'envoi", value=Timestamp(message.created_at).relative)
        if message.edited_at is not None:
            embed.add_field(name="Dernière modification", value=Timestamp(message.edited_at).relative)
        await ctx.respond(**kwargs)


class CogTwitch(commands.Cog):
    def __init__(self, bot: BotTemplate, **kwargs):
        self.bot = bot
        self.db = kwargs.get('db', GBpath + 'Data/annonces_streams.json')
        self.task_annonces.start()

    @tasks.loop(minutes=5)
    async def task_annonces(self):
        while not self.bot.setup_fini:
            await asyncio.sleep(1)
        self.bot.token.twitch.reload()
        annonces = json.load(open(self.db, 'r'), cls=GBDecoder)
        for guild_id, channels in annonces.items():
            guild = await self.bot.fetch_guild(guild_id)
            for channel_id, streamers in channels.items():
                channel = await guild.fetch_channel(channel_id)
                for i in range(len(streamers)):
                    kwargs = streamers[i]
                    streamer = Streamer(token=self.bot.token.twitch, session=self.bot.session, **kwargs)
                    await streamer.annonce(self.bot, channel)
                    # on note qu'un message a été créé / modifié
                    annonces[guild_id][channel_id][i] = streamer.json()
        json.dump(annonces, open(self.db, 'w'), cls=GBEncoder, indent=4)

    @CustomSlash
    async def liste_streams(self, ctx: ApplicationContext):
        await ctx.defer(ephemeral=True)
        embed = GBEmbed(title="Alertes de streams", guild=ctx.guild)
        db = json.load(open(self.db, 'r'), cls=GBDecoder)
        if not ctx.guild.id in db:
            await ctx.respond(f"Aucune alerte configurée sur ce serveur")
            return

        for channel_id, kwargs in db[ctx.guild.id].items():
            channel = await ctx.guild.fetch_channel(channel_id)
            streamers = [Streamer(token=self.bot.token.twitch, session=self.bot.session, **k) for k in kwargs]
            values = [s.url for s in streamers]
            values.sort()
            embed.add_field(name=f"Poste dans {channel.name}",
                            value='- ' + '\n- '.join(values))
        await ctx.respond(embed=embed)

    @CustomSlash
    async def add_stream(self, ctx: ApplicationContext, chaine: str, salon: discord.TextChannel, notif: str):
        await ctx.defer(ephemeral=True)
        streamer = Streamer(self.bot.token.twitch, chaine, notif, None, session=self.bot.session)
        db = json.load(open(self.db, 'r'), cls=GBDecoder)
        gid = salon.guild.id
        cid = salon.id
        if not gid in db:
            db[gid] = dict()
        if not cid in db[gid]:
            db[gid][cid] = list()
        kwargs = streamer.json()
        if not kwargs in db[gid][cid]:
            db[gid][cid].append(kwargs)
            json.dump(db, open(self.db, 'w'), cls=GBEncoder, indent=4)
            await ctx.respond(f"{streamer.url} va maintenant être annoncé dans {salon.mention}")
        else:
            await ctx.respond(f"{streamer.url} est déjà annoncé dans {salon.mention}")

    @CustomSlash
    async def remove_stream(self, ctx: ApplicationContext, chaine: str, salon: discord.TextChannel):
        await ctx.defer(ephemeral=True)
        db = json.load(open(self.db, 'r'), cls=GBDecoder)
        suppr = list()
        gid = ctx.guild.id
        gdel = list()  # guilds à supprimer après le parcours
        if gid in db:
            cdel = list()  # salons à supprimer après le parcours
            for cid, streamers in db[gid].items():
                skip = False
                remove = list()
                if isinstance(salon, discord.TextChannel):
                    skip = not int(cid) == salon.id
                if skip:
                    continue

                for i in range(len(streamers)):
                    kwargs = streamers[i]
                    kwargs['token'] = self.bot.token.twitch
                    kwargs['session'] = self.bot.session
                    streamer = Streamer(**kwargs)
                    if streamer.url.strip('/').endswith(chaine):
                        suppr.append(f'<#{cid}>')  # pour l'affichage à la fin
                        remove.append(i)  # on ajoute l'indice à la liste de suppression

                # parcours en sens inverse pour éviter les out of range
                for i in reversed(remove):
                    del db[gid][cid][i]

                if len(streamers) == 0:
                    cdel.append(cid)
            for cid in cdel:
                del db[gid][cid]

            if len(db[gid]) == 0:
                gdel.append(gid)
        for gid in gdel:
            del db[gid]

        json.dump(db, open(self.db, 'w'), cls=GBEncoder, indent=4)
        await ctx.respond(f"Les annonces de stream de {chaine} ne seront plus postées dans {', '.join(suppr)}")
