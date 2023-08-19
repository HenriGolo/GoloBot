#!/usr/bin/env python3
from GoloBot import * # ~ Contient tout ce qu'il faut, imports compris

# ~ Création Bot
intents = Intents.all()
bot = Bot(intents=intents)

@bot.event
async def on_ready():
	currentTime, _, _ = await init()
	bot.startTime = currentTime
	# ~ Récupération du chemin du fichier
	bot.pwd = "/".join(__file__.split('/')[:-1])+"/"
	# ~ Création de session pour les requêtes
	bot.session = CustomSession()
	# ~ Lecture les bot.stats sérialisées
	bot.stats = Stats()
	bot.stats.read(infos.stats)
	bot.stats = bot.stats
	# ~ Remplissage notre dictionnaire de joueurs
	bot.players = dict()
	for joueur in bot.stats.joueurs:
		bot.players[joueur.name] = joueur
	# ~ Récupération de l'User du dev
	bot.dev = await bot.fetch_user(infos.ownerID)
	bot.lastDM = bot.dev
	bot.games = dict()
	# ~ Création de la bot.whitelist des User avec des permissions sur le bot
	wl = infos.whitelisted_users
	bot.whitelist = [bot.dev]
	for id in wl:
		bot.whitelist.append(await bot.fetch_user(id))
	activity = Activity(name="GitHub",
						state="https://github.com/HenriGolo/GoloBot",
						type=ActivityType.watching)
	await bot.change_presence(activity=activity)
	bot.add_view(ViewRoleReact())
	with open(infos.pidfile, "w") as file:
		file.write(str(getpid()))
	print(f'Logged on as {bot.user}!')

# ~ Ajout commandes
bot.add_cog(General(bot))
bot.add_cog(Dev(bot))
bot.add_cog(Admin(bot))
bot.add_cog(Fun(bot))
bot.add_cog(WorldOfWarships(bot))

# ~ Run
bot.run(token=infos.tokenDSC)

