from discord import Permissions as perm
from varname import nameof

docs = {"pycord" : "https://docs.pycord.dev/en/stable/",
		"discord developpers" : "https://discord.com/developers/applications",
		"crontab" : "https://www.man7.org/linux/man-pages/man5/crontab.5.html",
		"cron" : "https://www.man7.org/linux/man-pages/man8/cron.8.html"}

bool_reac = {True : "<a:check:1164580201573912677>",
			False : "<a:denied:1164580451680256041>"}

class Arg:
	def __init__(self, n, d, r):
		self.name = n
		self.desc = d
		self.required = r

	def __str__(self):
		name = self.name
		if not self.required:
			name += " (optionnel)"
		return f"""- {name}
	{self.desc}"""

class DocCommand:
	def __init__(self, desc:str, perms, aide:str, args:list[Arg]):
		self.desc = desc
		if type(perms) == perm:
			self.perms = nameof(perms)
		else:
			self.perms = "Développeur"
		self.aide = aide
		self.args = {a.name : a for a in args}

	def __str__(self):
		return "\n".join([str(self.args[e]) for e in self.args if not e == empty])

empty = Arg("", "", True)
_ = [empty]

cmds = {"aide" : DocCommand("Affiche la liste des commandes.",
				perm.none,
				"",
				[Arg("commande", "Une commande en particulier. 'aide' par défaut.", False),
				Arg("visible", "Affiche la fenêtre d'aide à tout le monde. Désactivé par défaut.", False)]),
		"dm" : DocCommand("Envoie un MP",
				"dev",
				"",
				_),
		"logout" : DocCommand("Déconnecte le bot.",
				"dev",
				"",
				_),
		"ping" : DocCommand("Ping et autres infos",
				perm.none,
				"Informations : latence du bot, running time ... ce genre de trucs.",
				_),
		"poll" : DocCommand("Crée un sondage, séparer les réponses par un point virgule.",
				perm.none,
				"",
				[Arg("question", "Question à poser dans le sondage.", True),
				Arg("réponses", "Réponses possibles dans le sondage, séparer par un point virgule.", True),
				Arg("salon", "Salon où envoyer le sondage.", False)]),
		"role_react" : DocCommand("Ajoute un menu déroulant à un message pour choisir des rôles.",
				perm.manage_roles,
				"""`roles` et `message` n'ont pas besoin d'être renseignés tous les 2.
Dans le cas où `message_id` est renseigné, un nouveau message avec le même contenu sera envoyé et l'original sera supprimé.
Si échec suivi d'une possibilité `Actualiser`, choisir `Actualiser` et continuer normalement.""",
				[Arg("roles", "Mentions des rôles à attribuer, avec ou sans séparation.", True),
				Arg("message", "Toutes les mentions des rôles à attribuer.", False),
				Arg("message_id", "Identifiant d'un message à utiliser. ⚠ le message sera supprimé puis envoyé par le bot.", False)]),
		"spam_emote" : DocCommand("Spamme une emote.",
				perm.none,
				"",
				[Arg("emote", "Une emote qui va être spam pour atteindre la limite de 2000 caractères.", False),
				Arg("user", "Mentionne un utilisateur en particulier.", False)]),
		"clear" : DocCommand("Nettoie un salon.",
				perm.manage_messages,
				"Préciser le nombre de messages et le salon (par défaut : le salon actuel), éventuellement l'auteur.",
				[Arg("nombre", "Nombre de messages à chercher dans l'historique.", True),
				Arg("salon", "Salon où supprimer les messages.", False),
				Arg("user", "Ne supprimer que les messages de l'utilisateur en question.", False)]),
		"ban" : DocCommand("Si tu sais pas ce que c'est, t'es pas concerné.",
				perm.ban_members,
				"",
				[Arg("user", "Utilisateur à bannir.", True),
				Arg("raison", "Motif du ban.", False)]),
		"mute" : DocCommand("Mute une personne.",
				perm.moderate_members,
				"""Durée sous forme d'un nombre et `d` ou `j` (jour), `h` (heure), `m` (minute), `s` (secondes).
Ne pas combiner, par exemple `3m30s` est invalide, utilisez `210s`.""",
				[Arg("user", "Utilisateur à mute.", True),
				Arg("durée", "Durée du mute (par defaut 30 minutes).", False),
				Arg("raison", "Motif du mute.", False)]),
		"invite" : DocCommand("Affiche un lien pour inviter le bot.",
				perm.none,
				"",
				_),
		"code" : DocCommand("Lien vers GitHub pour accéder aux fichiers du bot.",
				perm.none,
				f"""Doc Pycord : [ici]({docs['pycord']}).
Portail des Développeurs : [ici]({docs['discord developpers']}).
Doc Cron : [ici]({docs['crontab']}) et [là]({docs['cron']}).""",
				_),
		"get_logs" : DocCommand("Envoie les logs des erreurs.",
				"dev",
				"",
				[Arg("last_x_lines", "Les X dernières lignes de stderr.", False)]),
		"qpup" : DocCommand("Lance le quiz Questions Pour Un Poulet !",
				perm.none,
				"Tellement de lore derrière ce nom ... Même avec le nom vous devinerez pas ...",
				[Arg("nbquestions", "Nombre de questions désirées.", False)]),
		"user_info" : DocCommand("Donne des informations sur la personne demandée.",
				perm.none,
				"Nom, date de création du compte, membre du serveur depuis <date>, rôles (si permission `Gérer les Rôles`))",
				[Arg("user", "Utilisateur ciblé.", True)]),
		"2048" : DocCommand("Démarre une partie de 2048.",
				perm.none,
				"",
				[Arg("size", "Taille de la grille (par défaut 4).", False)]),
		"suggestions" : DocCommand("Envoie un MP au dev à propos d'une suggestion que vous avez.",
				perm.none,
				"Vous pouvze aussi passer par le Serveur de Support",
				_),
		"droprates" : DocCommand("Indique le nombre de lootbox attendu pour une certaine probabilité de drop.",
				perm.none,
				"Renseigner le nom de la lootbox **et** l'item voulu va afficher la fenêtre de résultats à tout le monde.",
				[Arg("pourcentage", "Pourcentage de drop de l'item désiré.", True),
				Arg("nom", "Nom de la lootbox.", False),
				Arg("item", "Item désiré.", False)]),
		"embed" : DocCommand("Crée un nouvel embed, entièrement customisable.",
				perm.none,
				"Si modification d'un Embed existant : aucune modification n'est effective avant de valider à la toute fin.",
				[Arg("edit", "ID du message à modifier.", False)]),
		"no_custom_messages" : DocCommand("Désactive les messages de réponses personnalisées sur ce serveur.",
				perm.administrator,
				"Désactive tout, pour en remettre seulement certaines en service, envoyer un MP au bot à ce sujet.",
				_)}
