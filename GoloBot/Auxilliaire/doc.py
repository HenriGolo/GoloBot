from discord import option, Permissions as perm
from varname import nameof

docs = {"pycord" : "https://docs.pycord.dev/en/stable/",
		"discord developpers" : "https://discord.com/developers/applications",
		"crontab" : "https://www.man7.org/linux/man-pages/man5/crontab.5.html",
		"cron" : "https://www.man7.org/linux/man-pages/man8/cron.8.html"}

bool_reac = {True : "<a:check:1164580201573912677>",
			False : "<a:denied:1164580451680256041>"}

class Arg:
	def __init__(self, name, description, **kwargs):
		self.name = name
		self.desc = description
		# ~ Vive le sucre syntaxique
		self.default = kwargs["default"] = kwargs.get("default", None)
		self.required = kwargs["required"] = kwargs.get("required", self.default==None)

		kwargs = {k:v for k,v in kwargs.items() if v != None}
		self.option = option(name=self.name, description=self.desc, **kwargs)

	def __str__(self):
		name = self.name
		if not self.required:
			name += " (optionnel)"
		affichage = f"""- {name}
	{self.desc}"""
		if not self.default == None:
			affichage += "\n\tValeur par défaut : "
			affichage += str(self.default)
		return affichage

class DocCommand:
	def __init__(self, name:str, desc:str, perms, aide:str, args:list[Arg]):
		self.name = name
		self.desc = desc
		if type(perms) == perm:
			self.perms = nameof(perms)
		else:
			self.perms = "Développeur"
		self.aide = aide
		self.args = {a.name : a for a in args}

	def set_options(self):
		self.options = [self.args[arg].option for arg in self.args]

	def __str__(self):
		return "\n".join([str(self.args[e]) for e in self.args if not e == empty])

base_value = ""
empty = Arg("", "", default=base_value)
_ = [empty]

cmds = {"aide" : DocCommand("aide",
				"Affiche la liste des commandes.",
				perm.none,
				"",
				[empty, # ~ Défini plus tard car besoin d'avoir la liste complète des commandes
				Arg("visible", "Affiche la fenêtre d'aide à tout le monde. Désactivé par défaut.", default=False)]),

		"dm" : DocCommand("dm",
				"Envoie un MP",
				"dev",
				"",
				_),

		"logout" : DocCommand("logout",
				"Déconnecte le bot.",
				"dev",
				"",
				_),

		"ping" : DocCommand("ping",
				"Ping et autres infos",
				perm.none,
				"Informations : latence du bot, running time ... ce genre de trucs.",
				_),

		"poll" : DocCommand("poll",
				"Crée un sondage, séparer les réponses par un point virgule.",
				perm.none,
				"",
				[Arg("question", "Question à poser dans le sondage."),
				Arg("réponses", "Réponses possibles dans le sondage, séparer par un point virgule."),
				Arg("salon", "Salon où envoyer le sondage.", default=base_value)]),

		"role_react" : DocCommand("role_react",
				"Ajoute un menu déroulant à un message pour choisir des rôles.",
				perm.manage_roles,
				"""`roles` et `message` n'ont pas besoin d'être renseignés tous les 2.
Dans le cas où `message_id` est renseigné, un nouveau message avec le même contenu sera envoyé et l'original sera supprimé.
Si échec suivi d'une possibilité `Actualiser`, choisir `Actualiser` et continuer normalement.""",
				[Arg("roles", "Mentions des rôles à attribuer, avec ou sans séparation."),
				Arg("message", "Toutes les mentions des rôles à attribuer.", default=base_value),
				Arg("message_id", "Identifiant d'un message à utiliser. ⚠ le message sera supprimé puis envoyé par le bot.", default=base_value)]),

		"spam_emote" : DocCommand("spam_emote",
				"Spamme une emote.",
				perm.none,
				"",
				[Arg("emote", "Une emote qui va être spam pour atteindre la limite de 2000 caractères.", default="<:pepe_fuck:943761805703020614>"),
				Arg("user", "Mentionne un utilisateur en particulier.", default=base_value)]),

		"clear" : DocCommand("clear",
				"Nettoie un salon.",
				perm.manage_messages,
				"Préciser le nombre de messages et le salon (par défaut : le salon actuel), éventuellement l'auteur.",
				[Arg("nombre", "Nombre de messages à chercher dans l'historique."),
				Arg("salon", "Salon où supprimer les messages.", default=base_value),
				Arg("user", "Ne supprimer que les messages de l'utilisateur en question.", default=base_value)]),

		"ban" : DocCommand("ban",
				"Si tu sais pas ce que c'est, t'es pas concerné.",
				perm.ban_members,
				"",
				[Arg("user", "Utilisateur à bannir."),
				Arg("raison", "Motif du ban.", default=" ")]),

		"mute" : DocCommand("mute",
				"Mute une personne.",
				perm.moderate_members,
				"""Durée sous forme d'un nombre et `d` ou `j` (jour), `h` (heure), `m` (minute), `s` (secondes).
Ne pas combiner, par exemple `3m30s` est invalide, utilisez `210s`.""",
				[Arg("user", "Utilisateur à mute."),
				Arg("durée", "Durée du mute.", default="30m"),
				Arg("raison", "Motif du mute.", default=" ")]),

		"invite" : DocCommand("invite",
				"Affiche un lien pour inviter le bot.",
				perm.none,
				"",
				_),

		"code" : DocCommand("code",
				"Lien vers GitHub pour accéder aux fichiers du bot.",
				perm.none,
				f"""Doc Pycord : [ici]({docs['pycord']}).
Portail des Développeurs : [ici]({docs['discord developpers']}).
Doc Cron : [ici]({docs['crontab']}) et [là]({docs['cron']}).""",
				_),

		"get_logs" : DocCommand("get_logs",
				"Envoie les logs des erreurs.",
				"dev",
				"",
				[Arg("last_x_lines", "Les X dernières lignes de stderr.", default=50)]),

		"qpup" : DocCommand("qpup",
				"Lance le quiz Questions Pour Un Poulet !",
				perm.none,
				"Tellement de lore derrière ce nom ... Même avec le nom vous devinerez pas ...",
				[Arg("nbquestions", "Nombre de questions désirées.", default=1)]),

		"user_info" : DocCommand("user_info",
				"Donne des informations sur la personne demandée.",
				perm.none,
				"Nom, date de création du compte, membre du serveur depuis <date>, rôles (si permission `Gérer les Rôles`))",
				[Arg("user", "Utilisateur ciblé.")]),

		"2048" : DocCommand("2048",
				"Démarre une partie de 2048.",
				perm.none,
				"",
				[Arg("size", "Taille de la grille (par défaut 4).", default=4)]),

		"suggestions" : DocCommand("suggestions",
				"Envoie un MP au dev à propos d'une suggestion que vous avez.",
				perm.none,
				"Vous pouvze aussi passer par le Serveur de Support",
				_),

		"droprates" : DocCommand("droprates",
				"Indique le nombre de lootbox attendu pour une certaine probabilité de drop.",
				perm.none,
				"Renseigner le nom de la lootbox **et** l'item voulu va afficher la fenêtre de résultats à tout le monde.",
				[Arg("pourcentage", "Pourcentage de drop de l'item désiré."),
				Arg("nom", "Nom de la lootbox.", default=base_value),
				Arg("item", "Item désiré.", default=base_value)]),

		"embed" : DocCommand("emebd",
				"Crée un nouvel embed, entièrement customisable.",
				perm.none,
				"Si modification d'un Embed existant : aucune modification n'est effective avant de valider à la toute fin.",
				[Arg("edit", "ID du message à modifier.", default=base_value)]),

		"disable_custom_responses" : DocCommand("disable_custom_responses",
				"Désactive les messages de réponses personnalisées sur ce serveur.",
				perm.administrator,
				"Désactive tout, pour en remettre seulement certaines en service, envoyer un MP au bot à ce sujet.",
				_)}

cmds["aide"].args["commande"] = Arg("commande", "Une commande en particulier. 'aide' par défaut.", default="aide", choices=[cmd for cmd in cmds])
for cmd in cmds:
	cmds[cmd].set_options()
