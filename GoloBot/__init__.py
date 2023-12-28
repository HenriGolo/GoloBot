# Code Principal
import discord
from discord.ext import commands
from GoloBot.Auxilliaire import *  # Quelques fonctions utiles
from GoloBot.Auxilliaire.aux_maths import *  # Outils mathématiques
from GoloBot.Auxilliaire.converters import *  # Converters vers mes types custom
from GoloBot.Auxilliaire.decorators import *  # Decorateurs custom
from GoloBot.Auxilliaire.doc import *  # Raccourcis et noms customs
from GoloBot.Auxilliaire.games import *  # Jeux de plateau custom
from GoloBot.Musique import *  # Adapté de https://github.com/Raptor123471/DingoLingo
from GoloBot.UI import *  # Les composants de l'UI custom


# Code du bot
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Gestion des messages
    @commands.Cog.listener()
    async def on_message(self, msg):
        currentTime = now()
        try:
            # Message d'un bot → inutile
            if msg.author.bot:
                return

            # Message privé → transmission au dev
            if msg.channel.type == discord.ChannelType.private:
                if not msg.author == self.bot.dev:
                    embed = MyEmbed(title="Nouveau Message", description=msg.content, color=msg.author.color)
                    # Transmission des pièces jointes
                    files = [await fichier.to_file() for fichier in msg.attachments]
                    await self.bot.dev.send(f"Reçu de {msg.author.mention}",
                                            embed=embed,
                                            files=files,
                                            view=ViewDM(bot=self.bot))
                    with open(environ['dm'], 'a') as fichier:
                        fichier.write(f"\n{currentTime} {msg.author.name} a envoyé un DM :\n{msg.content}\n")
                    await msg.add_reaction(self.bot.bools[True])
            else:
                # S'obtient avec un '@silent' devant le message
                if not msg.flags.suppress_notifications:
                    for pr in self.bot.PR:
                        if pr.trigger(msg.content) and pr.users(msg.author) and pr.guilds(msg.guild):
                            await msg.reply(str(pr))

        except Exception:
            with open(environ['stderr'], 'a') as stderr:
                stderr.write(f"\n{currentTime}\n{fail()}\n")

    # Aide
    @commands.slash_command(description=cmds["aide"].desc)
    @customSlash
    async def aide(self, ctx, commande: str, visible: bool):
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
        embed = MyEmbed(title="Aide", description=mention, color=ctx.author.color)
        embed.add_field(name="Description", value=commande.desc, inline=False)
        embed.add_field(name="Permissions Nécessaires", value=commande.perms, inline=False)
        embed.add_field(name="Paramètres", value=str(commande))
        # Dans un if, car potentiellement non renseigné
        if not commande.aide == "":
            embed.add_field(name="Aide Supplémentaire", value=commande.aide, inline=False)
        embed.add_field(name="Encore des questions ?",
                        value=f"Le <:discord:1164579176146288650> [Serveur de Support]({environ['invite_server']}) est là pour ça",
                        inline=False)
        await ctx.respond(embed=embed, view=ViewAide(), ephemeral=not visible)

    # Renvoie un lien pour inviter le bot
    @commands.slash_command(description=cmds["invite"].desc)
    @customSlash
    async def invite(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = MyEmbed(title=f"Inviter {self.bot.user.name}",
                        description=f"""Tu peux m'inviter avec [ce lien]({environ['invite_bot']})
Et rejoindre le <:discord:1164579176146288650> Serveur de Support [avec celui ci]({environ['invite_server']})""",
                        color=ctx.author.color)
        support_qrcode = environ.get('support_qr', None)
        if support_qrcode:
            embed.set_thumbnail(url=support_qrcode)
        await ctx.respond(embed=embed, ephemeral=True)

    # Renvoie le code source du bot
    @commands.slash_command(description=cmds["github"].desc)
    @customSlash
    async def github(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = MyEmbed(title="Code Source",
                        description=f"Le code source est disponible sur <:github:1164672088934711398> [Github]({environ['github']})\n\
Tu peux aussi rejoindre le <:discord:1164579176146288650> [Serveur de Support]({environ['invite_server']})",
                        color=ctx.author.color)
        support_qrcode = environ.get('support_qr', None)
        if support_qrcode:
            embed.set_thumbnail(url=support_qrcode)
        await ctx.respond(embed=embed, ephemeral=True)

    # Quelques stats sur le nombre de box à ouvrir pour espérer un certain pourcentage
    @commands.slash_command(description=cmds["droprates"].desc)
    @customSlash
    async def droprates(self, ctx, pourcentage: float, nom: str, item: str):
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
        embed = MyEmbed(title=title, description=f"Pourcentage dans 1 lootbox : {pourcentage}", color=ctx.author.color)
        for key in seuils:
            n = seuils[key]
            embed.add_field(name=f"Au moins {key} % de chances", value=f"{n} lootboxes", inline=False)
        await ctx.respond(embed=embed, ephemeral=(nom == "" or item == ""))


# Fonctions Dev
class Dev(commands.Cog):
    def __init__(self, used_bot):
        self.bot = used_bot

    # Envoie un message privé à un User
    @commands.slash_command(description=cmds["dm"].desc)
    @customSlash
    async def dm(self, ctx):
        # Commande réservée au dev
        if not ctx.author == self.bot.dev:
            await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise Exception("N'est pas dev")

        await ctx.send_modal(ModalDM(bot=self.bot, title="Envoyer un message privé"))

    # Déconnecte le bot
    @commands.slash_command(description=cmds["logout"].desc)
    @customSlash
    async def logout(self, ctx):
        await ctx.defer(ephemeral=True)
        # Commande réservée aux User dans la whitelist
        if not ctx.author == self.bot.dev:
            if ctx.author in self.bot.whitelist:
                pass
            else:
                await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
                await self.bot.dev.send(f"{ctx.author.mention} a essayé de déconnecter le bot")
                raise Exception("N'est pas dev")

        await ctx.respond(f"En ligne depuis : {Timestamp(self.bot.startTime).relative}", ephemeral=True)
        # Déconnecte le bot
        await self.bot.close()

    # Renvoie le ping et d'autres informations
    @commands.slash_command(description=cmds["ping"].desc)
    @customSlash
    async def ping(self, ctx):
        await ctx.defer(ephemeral=True)
        embed = MyEmbed(title="Ping et autres informations", color=ctx.author.color)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)} ms", inline=False)
        embed.add_field(name="Bot en ligne depuis", value=f"{Timestamp(self.bot.startTime).relative}", inline=False)
        embed.add_field(name="Propiétaire", value=self.bot.dev.mention, inline=False)
        if ctx.author == self.bot.dev:
            embed.add_field(name="Websocket", value=self.bot.ws, inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    # Propose une suggestion
    @commands.slash_command(description=cmds["suggestions"].desc)
    @customSlash
    async def suggestions(self, ctx):
        await ctx.send_modal(ModalDM(bot=self.bot, target=self.bot.dev, title="Suggestion"))

    # Renvoie les logs
    @commands.slash_command(description=cmds["get_logs"].desc)
    @customSlash
    async def get_logs(self, ctx, last_x_lines: int):
        await ctx.defer(ephemeral=True)
        # Commande réservée au dev
        if not ctx.author == self.bot.dev:
            await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise Exception("N'est pas dev")
        stderr = discord.File(fp=environ['stderr'], filename=environ['stderr'].split("/")[-1])
        reponse = f"Dernières {last_x_lines} lignes de **{stderr}** :\n{tail(environ['stderr'], last_x_lines)[-1900:]}"
        await ctx.respond(f"Voici les logs demandés\n{reponse}", files=[stderr], ephemeral=True)

    @commands.slash_command(description=cmds["get_history"].desc)
    @customSlash
    async def get_history(self, ctx, last_x_lines: int):
        await ctx.defer(ephemeral=True)
        # Commande réservée au dev
        if not ctx.author == self.bot.dev:
            await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise Exception("N'est pas dev")
        stdout = File(fp=environ['stdout'], filename=environ['stdout'].split("/")[-1])
        reponse = f"Dernières {last_x_lines} lignes de **{stdout}** :\n{tail(environ['stdout'], last_x_lines)[-1900:]}"
        await ctx.respond(f"Voici les logs demandés\n{reponse}", files=[stdout], ephemeral=True)


# Fonctions Admin
class Admin(commands.Cog):
    def __init__(self, used_bot):
        self.bot = used_bot

    # Création de sondage
    @commands.slash_command(description=cmds["poll"].desc)
    @customSlash
    async def poll(self, ctx, question: str, reponses: Splitter, salon: discord.TextChannel):
        await ctx.defer()
        if salon == "":
            salon = ctx.channel

        # Discord oblige de répondre aux appels de commande
        await ctx.respond("Sondage en cours de création", ephemeral=True, delete_after=2)

        # Préparation les réactions
        # Étant donné le passage par l'ASCII, ajouter des réactions nécessite un changement de la procédure
        # Car les nombres, majuscules et minuscules ne sont pas accolés
        alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
                    '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
        # Première lettre de chaque réponse
        first_letters = "".join([s[0].lower() for s in reponses])
        # Tableau de bool pour savoir si les premières lettres sont uniques
        # Au moins un doublon, ou une non-lettre → alphabet standard
        if False in [check_unicity(first_letters, l) and 'a' <= l <= 'z' for l in first_letters]:
            used_alphaB = alphabet[:len(reponses)]
        # Que des lettres uniques, on répond avec les lettres correspondantes
        else:
            a = ord('a')
            used_alphaB = [alphabet[ord(i.lower()) - a] for i in first_letters]
        # Trop de réponses à gérer
        if len(reponses) > len(alphabet):
            await ctx.respond(f"Oula ... On va se calmer sur le nombre de réponses possibles, \
j'ai pas assez de symboles, mais t'as quand même les {len(used_alphaB)} premiers", ephemeral=True)

        # Préparation de l'affichage des réactions
        choix = ''
        for i in range(len(used_alphaB)):
            choix += f"{used_alphaB[i]} {reponses[i]}\n"

        # Création de l'embed
        embed = MyEmbed(title="Sondage", description=f"Créé par {ctx.author.mention}", color=ctx.author.color)
        embed.add_field(name="Question :", value=ANSI().converter(question), inline=False)
        embed.add_field(name="Réponses", value=choix, inline=False)

        # Envoi avec les réactions
        sondage = await salon.send(embed=embed)
        for i in range(len(used_alphaB)):
            emote = used_alphaB[i]
            await sondage.add_reaction(emote)
        await ctx.respond("Sondage créé !", ephemeral=True)

    # Role react
    @commands.slash_command(description=cmds["role_react"].desc)
    @commands.has_permissions(manage_roles=True)
    @discord.guild_only()
    @customSlash
    async def role_react(self, ctx, roles: str, message: str, message_id: str):
        if roles == "" and message == "" and message_id == "":
            return await ctx.respond("Veuillez renseigner au moins un paramètre")

        await ctx.defer()
        roles = rolesInStr(roles, ctx.guild)
        view = ViewRoleReact(roles=roles)
        rolesm = [e.mention for e in roles]
        if not message_id == base_value:
            msg = await ctx.channel.fetch_message(int(message_id))
            await msg.delete()
            await ctx.respond(content=msg.content, view=view)
        else:
            content = "Choisis les rôles que tu veux récupérer parmi\n- {}".format('\n- '.join(rolesm))
            if not message == "":
                content = message
            await ctx.respond(content=content, view=view)

    # Nettoyage des messages d'un salon
    @commands.slash_command(description=cmds["clear"].desc)
    @customSlash
    async def clear(self, ctx, nombre: int, salon: discord.TextChannel, user: discord.User):
        if salon == base_value:
            salon = ctx.channel
        await ctx.defer(ephemeral=True)
        if ctx.channel.type == ChannelType.private:
            with open("logs/logs_dm.txt", "a") as logs:
                await ctx.respond("Début du clear", ephemeral=True, delete_after=2)
                hist = ctx.channel.historique(limit=nombre).flatten()
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
                logs.write(f"\n{now()} Les derniers messages envoyés à {ctx.author.name} on été effacés\n")
            return

        # Manque de permissions
        if not ctx.channel.permissions_for(ctx.author).manage_messages:
            await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            raise Exception("Manque de permissions")

        await ctx.respond(f"Début du clear de {salon.mention}", ephemeral=True)
        cpt = 0
        with open(f'logs/logs_{ctx.guild.name}.txt', 'a') as logs:
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
    @commands.slash_command(description=cmds["ban"].desc)
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    @customSlash
    async def ban(self, ctx, user: discord.Member, raison: str):
        await ctx.defer(ephemeral=True)
        # Rôle de la cible trop élevé
        if user.top_role >= ctx.author.top_role:
            await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            await self.bot.dev.send(f"{ctx.author.mention} a voulu ban {user.mention} de {ctx.guild}")
            await ctx.author.timeout(until=now() + timedelta(minutes=2), reason=f"A voulu ban {user.name}")
            raise Exception("Rôle trop faible")

        try:
            who = f" (demandé par {ctx.author.name})"
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
    @commands.slash_command(description=cmds["mute"].desc)
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    @customSlash
    async def mute(self, ctx, user: discord.Member, duree: Duree, raison: str):
        await ctx.defer(ephemeral=True)
        end_mute = now() + duree
        # Rôle trop élevé
        if user.top_role >= ctx.author.top_role:
            await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
            await ctx.author.timeout(until=end_mute, reason=f"A voulu mute {user.name}")
            raise Exception("Rôle trop faible")

        try:
            who = f" (demandé par {ctx.author.name})"
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

    # Affiche les informations d'un Member
    @commands.slash_command(description=cmds["user_info"].desc)
    @customSlash
    async def user_info(self, ctx, user: discord.Member):
        await ctx.defer(ephemeral=True)
        embed = MyEmbed(title="Informations", description=f"À propos de {user.mention}", color=user.color)
        embed.add_field(name="Nom", value=str(user), inline=False)
        embed.set_thumbnail(url=user.avatar.url)
        if user.banner is not None:
            embed.add_field(name="Bannière", value=user.banner.url, inline=False)
        embed.add_field(name="Date de Création", value=Timestamp(user.created_at).relative, inline=False)
        embed.add_field(name="Dans le serveur depuis", value=Timestamp(user.joined_at).relative, inline=False)
        if user.premium_since is not None:
            embed.add_field(name="Booste le serveur depuis", value=Timestamp(user.premium_since).relative, inline=False)
        if ctx.channel.permissions_for(ctx.author).manage_roles:
            roles = [r.mention for r in user.roles[1:]]
            roles.reverse()
            embed.add_field(name="Rôles", value="- " + "\n- ".join(roles), inline=False)
        await ctx.respond(embed=embed)

    @commands.slash_command(description=cmds["embed"].desc)
    @commands.has_permissions(manage_messages=True)
    @customSlash
    async def embed(self, ctx, edit: str):
        if edit == base_value:
            await ctx.send_modal(ModalNewEmbed(edit, title="Nouvel Embed"))
        else:
            msg = await ctx.channel.fetch_message(int(edit))
            embeds = msg.embeds
            embed = embeds[0]
            await ctx.send_modal(ModalEditEmbed(embeds, embed, edit, send_new=True, title="Modifier l'Embed"))


# Fonctions Random
class MiniGames(commands.Cog):
    def __init__(self, used_bot):
        self.bot = used_bot

    # QPUP, bon courage pour retrouver le lore ...
    @commands.slash_command(description=cmds["qpup"].desc)
    @customSlash
    async def qpup(self, ctx, nbquestions: int):
        await ctx.defer()
        self.bot.qpup = read_db(environ['qpup'])
        # Boucle sur le nombre de questions à poser
        for loop in range(nbquestions):
            # Tirage au sort d'une question
            line = randrange(len(self.bot.qpup))
            # Envoi de la question
            await ctx.respond(self.bot.qpup[line][0], view=ViewQPUP(rep=self.bot.qpup[line][1]))

    # 2048, le _ est nécessaire, une fonction ne commence pas à un chiffre
    @commands.slash_command(name="2048", description=cmds["2048"].desc)
    @customSlash
    async def _2048(self, ctx, size: int):
        await ctx.defer()
        # Création d'un 2048
        game = Game2048(size=size)
        game.duree = now()
        add_dict(self.bot.games, ctx.author.mention, game)
        embed = MyEmbed(title="2048", color=ctx.author.color)
        # Envoie du jeu formatté en python ou n'importe quel autre langage
        # pour colorer les chiffres et ajouter un effet visuel
        embed.add_field(name=f"Partie de {ctx.author.name}", value=str(game), inline=True)
        moves = [f"{to} : {self.bot.bools[game.canMove(to)]}" for to in list(Directions)]
        embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
        embed.add_field(name="Score", value=game.score, inline=True)
        await ctx.respond(embed=embed, view=View2048(self.bot))


class Troll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    # Spamme un texte (emote ou autre) jusqu'à atteindre la limite de caractères
    @commands.slash_command(description=cmds["spam_emote"].desc)
    @customSlash
    async def spam_emote(self, ctx, emote: str, user: discord.User):
        await ctx.defer(ephemeral=True)
        emote = str(emote) + " "
        lim = ""
        if not user == base_value:
            lim = user.mention
        msg = emote * ((2000 - len(lim)) // len(emote))
        msg += lim
        await ctx.channel.send(msg)
        await ctx.respond(emote, ephemeral=True)

    # Désactive les réponses custom dans le serveur
    @commands.slash_command(description=cmds["disable_custom_responses"].desc)
    @commands.has_permissions(administrator=True)
    @customSlash
    async def disable_custom_responses(self, ctx):
        serveur = ctx.guild
        await ctx.defer(ephemeral=True)
        for pr in self.bot.PR:
            pr.Dguilds.append(serveur.id)
        await self.bot.dev.send(
            f"Ajouter {serveur.id} ({serveur.name}) sur blacklist des PR à la demande de {ctx.author} ({ctx.author.id})")
        await ctx.respond(f"""Les messages de réponses customs sont désormais désactivés sur ce serveur.
    Pour changer ça, envoyer un message privé au bot.""", ephemeral=True)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description=cmds["play"].desc)
    @discord.guild_only()
    @customSlash
    async def play(self, ctx, search: str):
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

    @commands.slash_command(description=cmds["playlist"].desc)
    @discord.guild_only()
    @customSlash
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
        embed = MyEmbed(title=f"À venir ({len(playlist.playque)} en tout)", color=ctx.author.color)
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

    @commands.slash_command(description=cmds["stop"].desc)
    @discord.guild_only()
    @customSlash
    async def stop(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        audiocontroller = guild_to_audiocontroller[ctx.guild]
        audiocontroller.playlist.loop = False
        await guild_to_audiocontroller[ctx.guild].stop_player()
        await ctx.guild.voice_client.disconnect()
        await ctx.respond(f"Arrêt de la musique {self.bot.bools[False]}")

    @commands.slash_command(description=cmds["skip"].desc)
    @discord.guild_only()
    @customSlash
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

    @commands.slash_command(description=cmds["songinfo"].desc)
    @discord.guild_only()
    @customSlash
    async def songinfo(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        song = guild_to_audiocontroller[ctx.guild].current_song
        if song is None:
            return
        await ctx.respond(embed=song.info.format_output("Infos", color=ctx.author.color))

    @commands.slash_command(description=cmds["historique"].desc)
    @discord.guild_only()
    @customSlash
    async def historique(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        await ctx.respond(guild_to_audiocontroller[ctx.guild].track_history())

    @commands.slash_command(description=cmds["volume"].desc)
    @discord.guild_only()
    @customSlash
    async def volume(self, ctx, volume: float):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return

        if not 0 < volume <= 100:
            return await ctx.respond(f"{volume} n'est pas compris entre 1 et 100")
        guild_to_audiocontroller[ctx.guild].volume = volume
        await ctx.respond(f"Nouveau volume défini sur {volume}")

    @commands.slash_command(description=cmds["loop"].desc)
    @discord.guild_only()
    @customSlash
    async def loop(self, ctx):
        await ctx.defer(ephemeral=True)
        if not await play_check(ctx):
            return
        loop = guild_to_audiocontroller[ctx.guild].playlist.loop
        guild_to_audiocontroller[ctx.guild].playlist.loop = not loop
        await ctx.respond(f"Changement de la boucle dans la PlayList : {self.bot.bools[loop]} -> {self.bot.bools[not loop]}", ephemeral=True)
