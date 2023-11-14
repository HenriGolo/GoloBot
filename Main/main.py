#!/usr/bin/env python3
from GoloBot import *  # ~ Contient tout ce qu'il faut, imports
from privatebot import PrivateResponse  # ~ Réponses custom à certains contenus de messages


class GoloBot(Bot):
    def __init__(self, description=None, *args, **kwargs):
        super().__init__(description, args, kwargs)
        self.startTime = None
        self.session = None
        self.games = None
        self.dev = None
        self.PR = None

    async def on_ready(self):
        # ~ Heure de démarrage (no shit sherlock)
        self.startTime = now()

        # ~ Création de session pour les requêtes
        self.session = CustomSession()

        # ~ Jeux en cours
        self.games = dict()

        # ~ Récupération de l'User du dev
        self.dev = await self.fetch_user(environ['ownerID'])

        # ~ Message de statut du bot
        activite = Activity(name="GitHub",
                            state="https://github.com/HenriGolo/GoloBot",
                            type=ActivityType.watching)
        await self.change_presence(activity=activite)

        # ~ View persistantes
        self.add_view(ViewRoleReact())
        self.add_view(ViewDM(self))

        self.PR = [pr() for pr in PrivateResponse.__subclasses__()]

        # ~ Gestion pour pid pour kill proprement
        with open(environ['pidfile'], "w") as pid:
            pid.write(str(getpid()))

        print(f"{self.user} connecté !")


# ~ Création Bot
intents = Intents.all()
bot = GoloBot(intents=intents)

# ~ Ajout des commandes
for cog in commands.Cog.__subclasses__:
    bot.add_cog(cog(bot))

# ~ Run
bot.run(token=environ['token'])
