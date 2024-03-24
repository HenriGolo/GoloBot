#!/usr/bin/env python3
from os import getpid
import discord
from discord.ext import tasks
from GoloBot import *  # Contient tout ce qu'il faut, imports compris
from privatebot import *  # Réponses custom à certains contenus de messages


class GoloBot(BotTemplate):
    # Récupération des tokens
    token = environ['token']

    # Création de session pour les requêtes
    session = GBSession()

    # Jeux en cours
    games = dict()

    # Plus de 25 commandes, seul moyen d'avoir une forme d'autocomplétion
    words = {cmd: {} for cmd in cmds}
    synonyms = {cmd: {" ".join(cmd.split(" "))} for cmd in cmds}
    commands_names = Completer(words=words, synonyms=synonyms)

    # Lettres de l'alphabet en caractères Unicode, utilisable comme emotes
    alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
                '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # À priori inutile, mais nécessaire pour le décorateur @logger des events
        self.bot = self

        # Ajout des commandes
        for cog in commands.Cog.__subclasses__():
            self.add_cog(cog(self))

        # Réponses personalisées
        # On cherche dans les subclass pour se laisser la possibilité d'overwrite les fonctions
        # Ce qui ne serait pas possible (ou moins intuitif / facile) avec des instances de PrivateResponse
        self.PR = [pr(self) for pr in PrivateResponse.__subclasses__()]

        # Sera défini dans on_ready
        self.startTime: datetime = None
        self.dev: discord.User = None
        self.support: discord.Guild = None
        self.emotes: dict[discord.Emoji] = None
        self.bools: dict[discord.Emoji] = None

    def __str__(self):
        return self.user.name

    @logger
    async def on_ready(self):
        # Heure de démarrage
        self.startTime = now()

        # Récupération de l'User du dev
        self.dev = await self.fetch_user(environ.get('ownerID', self.owner_id))

        # Message de statut du bot
        activity = discord.Activity(name="GitHub",
                                    state="https://github.com/HenriGolo/GoloBot",
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)

        # Emojis personnalisés
        self.support = GoloBotGuild = await self.fetch_guild(1158154606124204072)
        self.emotes = {e.name: str(e) for e in GoloBotGuild.emojis}
        self.bools = {True: self.emotes['check'], False: self.emotes['denied']}

        # View persistantes
        self.add_view(ViewRoleReact(self))
        self.add_view(ViewDM(self))

        # Clean guilds.log
        with open('logs/guilds.log', 'w'):
            pass

        for guild in self.guilds:
            # Setup de la Musique
            await register(self, guild)

            # Enregistrement des guilds auxquelles le bot appartient
            with open('logs/guilds.log', 'a') as file:
                file.write(f"{guild.name}\n")

        # Gestion du PID pour kill proprement
        with open(environ['pidfile'], 'w') as pid:
            pid.write(str(getpid()))

        # c'est bon, on est prêt
        print(f"{self} connecté !")

    @logger
    async def on_guild_join(self, guild):
        # Setup de la Musique
        await register(self, guild)

        # Enregistrement des guilds auxquelles le bot appartient
        with open('logs/guilds.log', 'a') as file:
            file.write(f"{guild.name}\n")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        # On ne tient pas compte des join / disconnect des bots
        if member.bot:
            return
        # On prend before pour s'intéresser au vocal dont part la personne
        if before is not None:
            # Si le vocal est composé uniquement de bots
            bots = [m.bot for m in before.channel.members]
            if not False in bots:
                for member in before.channel.members:
                    # On arrête la musique éventuelle en cours
                    if member.id == self.user.id:
                        await guild_to_audiocontroller[member.guild].stop_player()
                    # Déconnexion
                    await member.move_to(None)


# Création du Bot
intents = discord.Intents.all()
bot = GoloBot(intents=intents)

# Run
bot.run(token=bot.token)
