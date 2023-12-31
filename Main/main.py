#!/usr/bin/env python3
from os import getpid
from GoloBot import *  # Contient tout ce qu'il faut, imports
from privatebot import PrivateResponse  # Réponses custom à certains contenus de messages


class GoloBot(discord.AutoShardedBot):
    def __init__(self, description=None, *args, **kwargs):
        super().__init__(description, *args, **kwargs)
        # Création de session pour les requêtes
        self.session = CustomSession()
        # Jeux en cours
        self.games = dict()
        # Réponses personalisées
        self.PR = [pr() for pr in PrivateResponse.__subclasses__()]
        # Plus de 25 commandes, seul moyen d'avoir une forme d'autocomplétion
        words = {cmd: {} for cmd in cmds}
        synonyms = {cmd: {" ".join(cmd.split(" "))} for cmd in cmds}
        self.commands_names = Completer(words=words, synonyms=synonyms)
        self.alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
                         '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
        self.startTime = None
        self.dev = None
        self.emotes = None
        self.bools = None

    def __str__(self):
        return self.user.name

    async def on_ready(self):
        # Heure de démarrage
        self.startTime = now()
        # Récupération de l'User du dev
        self.dev = await self.fetch_user(environ['ownerID'])
        # Message de statut du bot
        activity = discord.Activity(name="GitHub",
                                    state="https://github.com/HenriGolo/GoloBot",
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)
        # Emojis personnalisés
        GoloBotGuild = await self.fetch_guild(1158154606124204072)
        self.emotes = {e.name: str(e) for e in GoloBotGuild.emojis}
        self.bools = {True: self.emotes['check'], False: self.emotes['denied']}
        # View persistantes
        self.add_view(ViewRoleReact())
        self.add_view(ViewDM(self))
        # Setup de la Musique
        for guild in self.guilds:
            await register(self, guild)
        # Gestion du PID pour kill proprement
        with open(environ['pidfile'], 'w') as pid:
            pid.write(str(getpid()))
        # c'est bon, on est prêt
        print(f"{self} connecté !")

    async def on_guild_join(self, guild):
        await register(self, guild)

    @staticmethod
    async def on_voice_state_update(member, before, after):
        # Déconnecte le bot du vocal quand il est tout seul dedans
        vc = member.guild.voice_client
        if vc is not None:
            if len(vc.channel.members) == 1:
                await guild_to_audiocontroller[vc.guild].stop_player()
                await vc.disconnect()


# Création du Bot
intents = discord.Intents.all()
bot = GoloBot(intents=intents)

# Ajout des commandes
for cog in commands.Cog.__subclasses__():
    bot.add_cog(cog(bot))

# Run
bot.run(token=environ['token'])
