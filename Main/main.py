#!/usr/bin/env python3
from os import getpid
from GoloBot import *  # Contient tout ce qu'il faut, imports
from privatebot import PrivateResponse  # Réponses custom à certains contenus de messages


class GoloBot(AutoShardedBot):
    def __init__(self, description=None, *args, **kwargs):
        super().__init__(description, *args, **kwargs)
        # Création de session pour les requêtes
        self.session = CustomSession()
        # Jeux en cours
        self.games = dict()
        # Réponses personalisées
        self.PR = [pr() for pr in PrivateResponse.__subclasses__()]
        # Quitte tous les vocaux où le bot est solo toutes les 10 mins
        self.leave_voice.start()
        self.startTime = None
        self.dev = None

    def __str__(self):
        return self.user.name

    @tasks.loop(minutes=10)
    async def leave_voice(self):
        for vc in self.voice_clients:
            # Le bot est tout seul dans le vocal
            if len(vc.channel.members) == 1:
                await vc.disconnect()

    async def on_ready(self):
        # Heure de démarrage
        self.startTime = now()
        # Récupération de l'User du dev
        self.dev = await self.fetch_user(environ['ownerID'])
        # Message de statut du bot
        activity = Activity(name="GitHub",
                            state="https://github.com/HenriGolo/GoloBot",
                            type=ActivityType.watching)
        await self.change_presence(activity=activity)
        # View persistantes
        self.add_view(ViewRoleReact())
        self.add_view(ViewDM(self))
        # Gestion du PID pour kill proprement
        with open(environ['pidfile'], 'w') as pid:
            pid.write(str(getpid()))
        # c'est bon, on est prêts
        print(f"{self} connecté !")


# Création du Bot
intents = Intents.all()
bot = GoloBot(intents=intents)

# Ajout des commandes
for cog in commands.Cog.__subclasses__():
    bot.add_cog(cog(bot))

# Run
bot.run(token=environ['token'])
