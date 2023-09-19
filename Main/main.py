#!/usr/bin/env python3
from GoloBot import * # ~ Contient tout ce qu'il faut, imports
from privatebot import PrivateResponse # ~ Réponses custom à certains contenus de messages

class GoloBot(Bot):
	async def on_ready(self):
		# ~ Heure de démarrage (no shit sherlock)
		self.startTime = now()

		# ~ Création de session pour les requêtes
		self.session = CustomSession()

		# ~ Lecture les stats précédents sérialisées
		self.stats = Stats()
		self.stats.read(infos.stats)
		self.stats = self.stats
		# ~ Jeux en cours
		self.games = dict()
		# ~ Remplissage notre dictionnaire de joueurs
		self.players = dict()
		for joueur in self.stats.joueurs:
			self.players[joueur.name] = joueur

		# ~ Récupération de l'User du dev
		self.dev = await self.fetch_user(infos.ownerID)

		# ~ Création de la bot.whitelist des User avec des permissions sur le bot
		wl = infos.whitelisted_users
		self.whitelist = [self.dev]
		for id in wl:
			self.whitelist.append(await self.fetch_user(id))

		# ~ Message de statut du bot
		activity = Activity(name="GitHub",
							state="https://github.com/HenriGolo/GoloBot",
							type=ActivityType.watching)
		await self.change_presence(activity=activity)

		# ~ View persistantes
		self.add_view(ViewRoleReact())
		self.add_view(ViewDM(bot))

		self.PR = [pr() for pr in PrivateResponse.__subclasses__()]

		# ~ Gestion pour pid pour kill proprement
		with open(infos.pidfile, "w") as file:
			file.write(str(getpid()))

		print(f"{self.user} connecté !")

# ~ Création Bot
intents = Intents.all()
bot = GoloBot(intents=intents)

# ~ Ajout des commandes
for cog in commands.Cog.__subclasses__():
	if cog.__name__ == "WorldOfWarships" and infos.tokenWOWS == "":
		continue
	bot.add_cog(cog(bot))

# ~ Run
bot.run(token=infos.tokenDSC)

