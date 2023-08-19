#!/usr/bin/env python3

# ~ Étant donné que tu lis ce code, tu as aussi eu accès à un fichier readme.txt
# ~ Il contient des informations utiles pour faire tourner ce programme


# ~ Code Principal

# ~ Bibliothèques

# ~ Discord, la base
from discord import *
from discord.ext import commands
# ~ Gestion du temps
import time, pytz, datetime as dt
# ~ Les commandes sp ne marchent potentiellement que sous UNIX
from os import getpid
from subprocess import Popen
import random
# ~ Gestion d'erreurs
from traceback import format_exc

# ~ Mes propres fichiers python
from GoloBot.Auxilliaire import * # ~ Quelques fonctions utiles
from GoloBot.Auxilliaire.abreviations import * # ~ Raccourcis et noms customs
from GoloBot.Auxilliaire.games import * # ~ Mes jeux custom
from GoloBot.Auxilliaire.aux_maths import * # ~ Outils mathématiques
from GoloBot.WoWs.wowsAPI import * # ~ L'API de World of Warships adaptée pour lisibilité
import infos # ~ Les tokens c'est privé

# ~ À appeler à chaque commande
# ~ récupère la date, le Member du bot et le User de l'auteur
async def init(bot, guild=None, author=None):
	# ~ Récupération de la date
	currentTime = dt.datetime.strptime(time.ctime(),"%c")

	# ~ Tentative de récupérer le Member associé au bot
	botMember = bot.user
	try:
		botMember = await guild.fetch_member(bot.user.id)
	except:
		pass

	# ~ Tentative de récupérer le User de l'auteur de la commande
	authorUser = author
	try:
		authorUser = await bot.fetch_user(author.id)
	except:
		pass

	return currentTime, botMember, authorUser

# ~ Sert pas à grand chose, renvoie si le salon est un message privé
def isDM(channel):
	if type(channel) == DMChannel:
		return True
	if type(channel) == PartialMessageable:
		return True
	if str(channel.type) == 'private':
		return True
	return False

# ~ Règle la précision temporelle
def timeAccuracy(t):
	# ~ Tronque à la seconde
	t -= dt.timedelta(microseconds=t.microsecond)
	# ~ Convertis en heure française
	t = t.astimezone(pytz.timezone('Europe/Paris')).strftime('%Y-%m-%d %H:%M:%S')
	# ~ Attention, astimezone renvoie un str pas un datetime.datetime
	return t

# ~ Récupère tous les rôles mentionnés dans un message
# ~ Message.role_mentions existe mais parfois ne marche pas complétement
def rolesInStr(msg:str, guild:Guild):
	sep = [e.split(">") for e in msg.split("<@&")]
	role_ids = [int(sl[0]) for sl in sep[1:]]
	roles = [guild.get_role(e) for e in role_ids]
	return roles

def fail():
	return format_exc() + "\n\n"

def correspond(attendu:list, reponse:str):
	articles = ["le", "la", "les", "l'", "un", "une", "des", "du", "de la"]
	for mot in reponse.split(" "):
		if not mot in attendu and not mot in articles:
			return False
	return True

# ~ Les boutons pour le jeu de 2048
class View2048(ui.View):
	def __init__(self, bot):
		self.bot = bot
		super().__init__()

	# ~ Bouton "bouger vers le haut"
	@ui.button(label="Haut", style=ButtonStyle.primary, emoji='⬆️')
	async def up_button(self, button, interaction):
		# ~ Récupération du joueur
		user = interaction.user
		currentTime, _, _ = await init(self.bot, interaction.guild, user)
		try:
			# ~ Récupération de la dernière partie de 2048 du joueur
			game = [g for g in self.bot.games[user.mention] if g.jeu=="2048"][-1]
			# ~ Voir board_bot.games.py
			game.moveAll("haut")
			if not game.gagne:
				# ~ Détecte la présence d'un 2048 sur le plateau
				game.gagne = "2048" in str(game)

			# ~ Partie perdue
			if not game.canMoveAll():
				# ~ On itère sur tous les boutons de la View
				for child in self.children:
					# ~ Si le bouton n'est pas directionnel
					if not child.label.lower() in toward:
						child.label = "Partie Terminée"
					# ~ Dans tous les cas on désactive le bouton
					child.disabled = True
				# ~ Actualisation des stats
				game.termine = True
				game.duree = currentTime - game.duree
				bot.players[user.mention] + game
				bot.stats + self.bot.players[user.mention]
				bot.stats.write(infos.stats)

			# ~ On itère sur les boutons de la View
			for child in self.children:
				# ~ Bouton non directionnel
				if not child.label.lower() in toward:
					continue
				# ~ Bouton directionnel -> désactiver si mouvement impossible
				child.disabled = not game.canMove(child.label.lower())

			embed = Embed(title="2048", color=user.color)
			# ~ On envoie le jeu formatté pour du python (ou n'importe quel autre langage)
			# ~ pour colorer les chiffres et ajouter un effet visuel
			embed.add_field(name=f"Partie de {user.name}", value=f"```python\n{game}```", inline=True)
			moves = [f"{to} : {bool_reac[game.canMove(to)]}" for to in toward]
			embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
			embed.add_field(name="Score", value=game.score, inline=True)
			await interaction.response.edit_message(embed=embed, view=self)

		# ~ Si problème -> log
		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Bouton "bouger vers le bas" -> idem que pour le haut
	@ui.button(label="Bas", style=ButtonStyle.primary, emoji='⬇️')
	async def down_button(self, button, interaction):
		user = interaction.user
		currentTime, _, _ = await init(self.bot, interaction.guild, user)
		try:
			game = [g for g in self.bot.games[user.mention] if g.jeu=="2048"][-1]
			game.moveAll("bas")
			if not game.gagne:
				game.gagne = "2048" in str(game)

			if not game.canMoveAll():
				for child in self.children:
					if not child.label.lower() in toward:
						child.label = "Partie Terminée"
					child.disabled = True
				game.termine = True
				game.duree = currentTime - game.duree
				bot.players[user.mention] + game
				bot.stats + self.bot.players[user.mention]
				bot.stats.write(infos.stats)

			for child in self.children:
				if not child.label.lower() in toward:
					continue
				child.disabled = not game.canMove(child.label.lower())

			embed = Embed(title="2048", color=user.color)
			# ~ On envoie le jeu formatté pour du python ou n'importe quel autre langage
			# ~ pour colorer les chiffres et ajouter un effet visuel
			embed.add_field(name=f"Partie de {user.name}", value=f"```python\n{game}```", inline=True)
			moves = [f"{to} : {bool_reac[game.canMove(to)]}" for to in toward]
			embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
			embed.add_field(name="Score", value=game.score, inline=True)
			await interaction.response.edit_message(embed=embed, view=self)

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Bouton "bouger vers la gauche" -> idem que pour le haut
	@ui.button(label="Gauche", style=ButtonStyle.primary, emoji='⬅️')
	async def left_button(self, button, interaction):
		user = interaction.user
		currentTime, _, _ = await init(self.bot, interaction.guild, user)
		try:
			game = [g for g in self.bot.games[user.mention] if g.jeu=="2048"][-1]
			game.moveAll("gauche")
			if not game.gagne:
				game.gagne = "2048" in str(game)

			if not game.canMoveAll():
				for child in self.children:
					if not child.label.lower() in toward:
						child.label = "Partie Terminée"
					child.disabled = True
				game.termine = True
				game.duree = currentTime - game.duree
				bot.players[user.mention] + game
				bot.stats + self.bot.players[user.mention]
				bot.stats.write(infos.stats)

			for child in self.children:
				if not child.label.lower() in toward:
					continue
				child.disabled = not game.canMove(child.label.lower())

			embed = Embed(title="2048", color=user.color)
			# ~ On envoie le jeu formatté pour du python ou n'importe quel autre langage
			# ~ pour colorer les chiffres et ajouter un effet visuel
			embed.add_field(name=f"Partie de {user.name}", value=f"```python\n{game}```", inline=True)
			moves = [f"{to} : {bool_reac[game.canMove(to)]}" for to in toward]
			embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
			embed.add_field(name="Score", value=game.score, inline=True)
			await interaction.response.edit_message(embed=embed, view=self)

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Bouton "bouger vers la droite" -> idem que pour le haut
	@ui.button(label="Droite", style=ButtonStyle.primary, emoji='➡️')
	async def right_button(self, button, interaction):
		user = interaction.user
		currentTime, _, _ = await init(self.bot, interaction.guild, user)
		try:
			game = [g for g in self.bot.games[user.mention] if g.jeu=="2048"][-1]
			game.moveAll("droite")
			if not game.gagne:
				game.gagne = "2048" in str(game)

			if not game.canMoveAll():
				for child in self.children:
					if not child.label.lower() in toward:
						child.label = "Partie Terminée"
					child.disabled = True
				game.termine = True
				game.duree = currentTime - game.duree
				bot.players[user.mention] + game
				bot.stats + self.bot.players[user.mention]
				bot.stats.write(infos.stats)

			for child in self.children:
				if not child.label.lower() in toward:
					continue
				child.disabled = not game.canMove(child.label.lower())

			embed = Embed(title="2048", color=user.color)
			# ~ On envoie le jeu formatté pour du python ou n'importe quel autre langage
			# ~ pour colorer les chiffres et ajouter un effet visuel
			embed.add_field(name=f"Partie de {user.name}", value=f"```python\n{game}```", inline=True)
			moves = [f"{to} : {bool_reac[game.canMove(to)]}" for to in toward]
			embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
			embed.add_field(name="Score", value=game.score, inline=True)
			await interaction.response.edit_message(embed=embed, view=self)

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Bouton d'arrêt
	@ui.button(label="Arrêter", custom_id="stop", style=ButtonStyle.danger, emoji='❌')
	async def delete_button(self, button, interaction):
		currentTime, _, _ = await init(self.bot, interaction.guild, interaction.user)
		try:
			# ~ On déasctive tous les boutons
			for child in self.children:
				child.disabled = True
			button.label = "Partie Terminée"
			user = interaction.user

			# ~ On supprime la partie de la liste des parties en cours
			game = [g for g in self.bot.games[user.mention] if g.jeu=="2048"][-1]
			# ~ False -> abandon, True -> bloqué
			# ~ Normalement, True est impossible car détecté par les boutons directionnels
			game.termine = not game.canMoveAll()
			# ~ Détection de victoire
			game.gagne = "2048" in str(game)
			game.duree = currentTime - game.duree

			bot.players[user.mention] + game
			bot.stats + self.bot.players[user.mention]
			bot.stats.write(infos.stats)
			bot.games[user.mention] = [g for g in self.bot.games[user.mention] if g.jeu!="2048"]
			await interaction.response.edit_message(view=self)

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

# ~ Menu déroulant pour le role react
class SelectRoleReact(ui.Select):
	def __init__(self, roles:list[Role]):
		self.roles = roles
		# ~ Création des options du menu déroulant
		options = [SelectOption(label=e.name, description=f"Récupérer / Enlever {e.name}") for e in roles]
		if options == []:
			options = [SelectOption(label="Actualiser", description="Actualise la liste")]
		# ~ Création du menu déroulant
		super().__init__(placeholder="Choisir un rôle", min_values=1, options=options, custom_id="role_react")

	async def callback(self, interaction):
		user = interaction.user
		msg = interaction.message
		guild = interaction.guild
		currentTime, _, _ = await init(self.bot, guild, user)
		try:
			if self.values[0] == "Actualiser":
				await interaction.response.edit_message(view=ViewRoleReact(rolesInStr(msg.content, guild)))
				return

			for role in self.roles:
				if self.values[0] == role.name:
					if not role in user.roles:
						await user.add_roles(role)
						await interaction.response.send_message(content=f"Rôle ajouté : {role.mention}", ephemeral=True)
					else:
						await user.remove_roles(role)
						await interaction.response.send_message(content=f"Rôle supprimé : {role.mention}", ephemeral=True)
			await msg.edit(view=ViewRoleReact(self.roles))

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

class ViewRoleReact(ui.View):
	def __init__(self ,roles:list[Role]=[]):
		super().__init__(timeout=None)
		self.add_item(SelectRoleReact(roles))

# ~ Code du bot
class General(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Gestion des messages
	@commands.Cog.listener()
	async def on_message(self, msg):
		currentTime, _, _ = await init(self.bot, msg.guild)
		try:
			# ~ Message d'un bot -> inutile
			if msg.author.bot:
				return

			# ~ Message privé -> transmission au dev
			if isDM(msg.channel):
				log = f"MP reçu de {msg.author.mention} : ```{msg.content} ```"
				# ~ Sert pour la commande reply
				self.bot.lastDM = msg.author
				files = list()
				# ~ Transmission des pièces jointes
				for file in msg.attachments:
					files.append(await file.to_file())
				await self.bot.dev.send(log, files=files)
				with open(infos.dm, 'a') as fichier:
					fichier.write(f"\n{currentTime} {msg.author.name} a envoyé un DM :\n{msg.content}\n")
				await msg.add_reaction("✅")
			else:
				if "313" in "".join(msg.content.split(" ")) and msg.guild.id in infos.main_servers:
					await msg.reply(gif313)
				with open(infos.log(msg.guild.name), 'a') as fichier:
					fichier.write(f"\n{currentTime} #{msg.channel.name} :\n{msg.content}\n{len(msg.attachments)} pièces jointes\n\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Aide
	@commands.slash_command(description=cmds["aide"][0])
	@option("commande", choices=[cmd for cmd in cmds], description=cmds["aide"][3]["commande o"])
	@option("visible", choices=[True, False], description=cmds["aide"][3]["visible o"])
	async def aide(self, ctx, commande="aide", visible:bool=False):
		currentTime, authorUser, _ = await init(self.bot, ctx.guild, ctx.author)
		cmd = commande # ~ Abbréviation pour cause de flemme
		try:
			await ctx.defer(ephemeral=not visible)
			# ~ Informations sur la commande
			embed = Embed(title="Aide", color=ctx.author.color)
			msg = f"""**__Description__** : {cmds[cmd][0]}
**__Permissions nécessaires__** : {cmds[cmd][1]}
**__Paramètres__** :\n"""
			# ~ Paramètres de la commande
			for param in cmds[cmd][3]:
				if len(param) == 0:
					continue
				msg += f"*{param[:-1]}"
				if param[-1] == "o":
					msg += ("(optionnel)")
				else:
					msg += param[-1]
				msg += f"* : {cmds[cmd][3][param]}.\n"
			# ~ Dans un if car potentiellement non renseigné
			aide_sup = cmds[cmd][2]
			if aide_sup != "":
				msg += f"\n**__Aide supplémentaire__** : {aide_sup}\n"
			embed.add_field(name=f"/{cmd}", value=msg, inline=False)
			await ctx.respond(embed=embed, ephemeral=not visible)
			print(f"\n{currentTime} {ctx.author.name} a utilisé de l'aide\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Renvoie un lien pour inviter le bot
	@commands.slash_command(description=cmds["invite"][0])
	async def invite(self, ctx):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			await ctx.respond(f"Le lien pour m'inviter : {infos.invitation}", ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a demandé le lien d'invitation\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Renvoie le code source du bot
	@commands.slash_command(description=cmds["code"][0])
	async def code(self, ctx):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			embed = Embed(title="Code Source",
				description="Le code source du bot est disponible sur [github](https://github.com/HenriGolo/GoloBot/)",
				color=ctx.author.color)
			await ctx.respond(embed=embed, ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a récupéré le code source\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Renvoie les logs
	@commands.slash_command(description=cmds["get_logs"][0])
	@option("files", description=cmds["get_logs"][3]["files"])
	@option("last_x_lines", description=cmds["get_logs"][3]["last_x_lines o"])
	@default_permissions(manage_messages=True)
	async def get_logs(self, ctx, files, last_x_lines:int=50):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			fichiers = list()
			sent = str()
			path = self.bot.pwd
			reponse = ""
			if "all" in files:
				files = "guild ; dev ; dm ; stderr"
			for fl in [e.strip() for e in files.split(";")]:
				# ~ Logs du serveur accessible à tous
				if fl == "guild":
					file = None
					if not ctx.guild == None:
						file = infos.log(ctx.guild.name)

				# ~ Autres logs, réservés aux gens dans la whitelist
				elif not ctx.author in self.bot.whitelist:
					continue
				elif fl == "dev":
					file = infos.stdout
				elif fl == "dm":
					file = infos.dm
				elif fl == "stderr":
					file = infos.stderr
					# ~ Récupération des dernière lignes
					# ~ Le [-1900:] s'assure que le message ne dépasse pas les 2000 caractères
					reponse += f"Dernières {last_x_lines} lignes de **{file}** :\n{tail(path+file, last_x_lines)[-1900:]}"

				# ~ On ajoute le fichier à la liste des renvois
				if not file == None:
					fichiers.append(File(fp=path+file, filename=file))
					sent += f"{file}, "
			await ctx.respond(f"Voici les logs demandés\n{reponse}", files=fichiers, ephemeral=True)
			print(f"\n{currentTime} Logs envoyés : {sent[:-2]}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	@commands.slash_command(description=cmds["droprates"][0])
	@option("pourcentage", description=cmds["droprates"][3]["pourcentage"])
	@option("nom", description=cmds["droprates"][3]["nom o"])
	@option("item", description=cmds["droprates"][3]["item o"])
	async def droprates(self, ctx, pourcentage:float, nom="", item=""):
		currentTime, _, authorUser = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=(nom == "" or item == ""))
			p = pourcentage / 100
			seuils = {50 : 0,
					  75 : 0,
					  90 : 0}
			klist = [key for key in seuils]
			n = 1
			b = Binomiale(n, p)
			proba = b.proba_sup(1)
			while proba < klist[-1]/100:
				for key in klist[:-1]:
					if not seuils[key] == 0:
						continue
					if proba *100 >= key:
						seuils[key] = n

				# ~ Incrémentation compteur
				n += 1
				b = Binomiale(n, p)
				proba = b.proba_sup(1)
			seuils[klist[-1]] = n

			title = f"Chances de drop {item}"
			if not nom == "":
				title += f" dans {nom}"
			embed = Embed(title=title, description=f"Pourcentage dans 1 conteneur : {pourcentage}", color=ctx.author.color)
			for key in seuils:
				n = seuils[key]
				embed.add_field(name=f"Au moins {key}% de chances", value=f"{n} conteneurs", inline=False)
			await ctx.respond(embed=embed, ephemeral=(nom == "" or item == ""))
			print(f"\n{currentTime} droprates pour {pourcentage}% de chance de drop {item} dans {nom}\n")

		# ~ Erreur dans la fonction
		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

# ~ Fonctions Dev
class Dev(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Envoie un message privé à un User
	@commands.slash_command(description=cmds["dm"][0])
	@option("user_id", description=cmds["dm"][3]["user_id"])
	@option("message", description=cmds["dm"][3]["message"])
	async def dm(self, ctx, user_id, message):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			user = await self.bot.fetch_user(user_id)
			# ~ Commande réservée au dev
			if not ctx.author == self.bot.dev:
				await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
				await self.bot.dev.send(f"{ctx.author.mention} a essayé de MP {user.mention} pour envoyer ```{message}```")
				print(f"\n{currentTime} {ctx.author.name} a essayé de MP {user.name} :\n{message}\n")
				return

			try:
				await user.send(message)
				await ctx.respond(f"MP envoyé à {user.mention} : ```{message}```", ephemeral=True)
				print(f"\n{currentTime} : MP envoyé à {user.name} :\n{message}\n")

			# ~ Erreur dans l'envoi
			except Exception as error:
				await ctx.respond(f"Échec d'envoi de MP à {user.mention}```{error}```", ephemeral=True)
				print(f"\n{currentTime} : échec d'envoi de MP à {user.name} :\n{message}\n")

		# ~ Erreur dans la fonction
		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Similaire à dm, le destinataire est déjà pré-rempli
	@commands.slash_command(description=cmds["reply"][0])
	@option("message", description=cmds["reply"][3]["message"])
	async def reply(self, ctx, message):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			# ~ Commande réservée au dev
			if not ctx.author == self.bot.dev:
				await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
				await self.bot.dev.send(f"{ctx.author.mention} a essayé de /reply {bot.lastDM.mention} pour envoyer ```{message}```")
				print(f"\n{currentTime} {ctx.author.name} a essayé de MP {bot.lastDM.name} :\n{message}\n")
				return

			# ~ On envoie une réponse à la dernière personne qui a envoyé un message au bot
			await self.bot.lastDM.send(message)
			await ctx.respond(f"MP envoyé à {bot.lastDM.mention} : ```{message}```", ephemeral=True)
			print(f"\n{currentTime} : MP envoyé à {bot.lastDM.name} :\n{message}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Déconnecte le bot
	@commands.slash_command(description=cmds["logout"][0])
	@option("restart", description=cmds["logout"][3]["restart o"])
	@option("update", description=cmds["logout"][3]["update o"])
	async def logout(self, ctx, restart=None):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			# ~ Commande réservée aux User dans la whitelist
			if not ctx.author == self.bot.dev:
				if not ctx.author in self.bot.whitelist or restart == None:
					await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
					await self.bot.dev.send(f"{ctx.author.mention} a essayé de déconnecter le bot, redémarrage : {restart != None}")
					print(f"\n{currentTime} {ctx.author.name} a voulu déconnecter le bot\n")
					return

				# ~ Autorisation pour la whitelist seulement si redémarrage
				elif not restart == None:
					await self.bot.dev.send(f"{ctx.author.mention} a redémarré le bot")
					print(f"\n{currentTime} {ctx.author.name} a redémarré le bot")

			await ctx.respond(f"Running time : {currentTime - self.bot.startTime}", ephemeral=True)
			# ~ restart != None -> redémarrage
			if not restart == None:
				Popen([infos.restart])
			# ~ Déconnecte le bot
			await self.bot.close()
			print(f"\n{currentTime} Bot déconnecté\n")

		except Exception:
			await ctx.respond(fail(), ephemeral=True)
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Renvoie le ping et d'autres informations
	@commands.slash_command(description=cmds["ping"][0])
	async def ping(self, ctx):
		currentTime, authorUser, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			embed = Embed(title="Ping et autres informations", color=ctx.author.color)
			embed.add_field(name="Ping", value=f"{round(self.bot.latency*1000)} ms", inline=False)
			embed.add_field(name="Bot en ligne depuis", value=f"{currentTime - self.bot.startTime}", inline=False)
			embed.add_field(name="Propiétaire", value=self.bot.dev.mention, inline=False)
			if ctx.author == self.bot.dev:
				embed.add_field(name="Websocket", value=self.bot.ws, inline=False)
				embed.add_field(name="Dernier MP", value=bot.lastDM, inline=False)
			await ctx.respond(embed=embed, ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a utilisé ping\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Propose une suggestion
	@commands.slash_command(name="suggestions", description=cmds["suggestions"][0])
	@option("suggestion", description=cmds["suggestions"][3]["suggestion"])
	async def suggest(self, ctx, suggestion):
		currentTime, authorUser, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			idea = Embed(title="Nouvelle suggestion}", description=suggestion, color=ctx.author.color)
			idea.add_field(name="Informations", value=ctx.author.mention)
			await self.bot.dev.send(embed=idea)
			await ctx.respond("Ta suggestion a été transmise, \
tu vas très probablement recevoir une réponse en MP et pouvoir y discuter directement avec le dev", ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a fait une suggestion\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

# ~ Fonctions Admin
class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Création de sondage
	@commands.slash_command(description=cmds["poll"][0])
	@option("question", description=cmds["poll"][3]["question"])
	@option("reponses", description=cmds["poll"][3]["réponses"])
	@option("salon", description=cmds["poll"][3]["salon o"])
	async def poll(self, ctx, question, reponses, salon:TextChannel=None):
		currentTime, authorUser, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer()
			if salon == None:
				channel = ctx.channel
			else:
				channel = channel

			# ~ Discord oblige de répondre aux appels de commande
			await ctx.respond("Sondage en cours de création", ephemeral=True, delete_after=2)

			# ~ Préparation les réactions
			# ~ Étant donné le passage par l'ASCII, ajouter des réactions nécessite un changement de la procédure
			# ~ Car les nombres, majuscules et minuscules ne sont pas accolés
			alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
						'🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
			# ~ Ensemble des réponses possibles
			reps = [e.strip() for e in reponses.split(';')]
			# ~ Première lettre de chaque réponse
			first_letters = "".join([s[0].lower() for s in reps])
			# ~ Tableau de bool pour savoir si les premières lettres sont uniques
			# ~ Au moins un doublon, ou une non lettre -> alphabet standard
			if False in [check_unicity(first_letters, l) and 'a' <= l <= 'z' for l in first_letters]:
				used_alphaB = alphabet[:len(reps)]
			# ~ Que des lettres uniques, on répond avec les lettres correspondantes
			else:
				a = ord('a')
				used_alphaB = [alphabet[ord(i.lower())-a] for i in first_letters]
			# ~ Trop de réponses à gérer
			if len(reps) > len(alphabet):
				await ctx.respond(f"Oula ... On va se calmer sur le nombre de réponses possibles, \
j'ai pas assez de symboles, mais t'as quand même les {len(used_alphaB)} premiers", ephemeral=True)

			# ~ Préparation de l'affichage des réactions
			choix = ''
			for i in range(len(used_alphaB)):
				choix += f"{used_alphaB[i]} {reps[i]}\n"

			# ~ Création de l'embed
			embed = Embed(title="Sondage", description=f"Créé par {ctx.author.mention}", color=ctx.author.color)
			embed.add_field(name="Question :", value=question, inline=False)
			embed.add_field(name="Réponses", value=choix, inline=False)

			# ~ Envoi avec les réactions
			sondage = await channel.send(embed=embed)
			for i in range(len(used_alphaB)):
				emoji = used_alphaB[i]
				await sondage.add_reaction(emoji)
			await ctx.respond("Sondage créé !", ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a créé un sondage dans {channel.name}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Role react
	@commands.slash_command(description=cmds["role_react"][0])
	@option("roles", description=cmds["role_react"][3]["roles"])
	@option("message", description=cmds["role_react"][3]["message o"])
	@option("message_id", description=cmds["role_react"][3]["message_id o"])
	@default_permissions(manage_roles=True)
	@guild_only()
	async def role_react(self, ctx, roles:str="", message:str="", message_id=None):
		currentTime, _, botMember = await init(self.bot, ctx.guild, ctx.author)
		if roles == "" and message == "" and message_id == None:
			await ctx.respond("Veuillez renseigner au moins un paramètre")
		try:
			await ctx.defer()
			roles = rolesInStr(roles, ctx.guild)
			view = ViewRoleReact(roles=roles)
			rolesm = [e.mention for e in roles]
			if not message_id == None:
				msg = await ctx.channel.fetch_message(int(message_id))
				await msg.delete()
				await ctx.respond(content=msg.content, view=view)
			else:
				content = "Choisis les rôles que tu veux récupérer parmi\n- {}".format('\n- '.join(rolesm))
				if not message == "":
					content = message
				await ctx.respond(content=content, view=view)

			print(f"\n{currentTime} Ajout d'un role réaction pour {','.join([e.name for e in roles])}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Nettoyage des messages d'un salon
	@commands.slash_command(description=cmds["clear"][0])
	@option("nombre", description=cmds["clear"][3]["nombre"])
	@option("salon", description=cmds["clear"][3]["salon o"])
	@option("user", description=cmds["clear"][3]["user o"])
	async def clear(self, ctx, nombre:int, salon:TextChannel=None, user:User=None):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			if isDM(ctx.channel):
				with open("logs/logs_dm.txt", "a") as file:
					await ctx.respond("Début du clear", ephemeral=True, delete_after=2)
					hist = ctx.channel.history(limit=nombre).flatten()
					for msg in await hist:
						try:
							await msg.delete()
							file.write(f"""
{currentTime} message de {message.author} supprimé dans #{salon.name} :
	{message.content}
""")
						# ~ Erreur la plus probable : message de l'humain, pas du bot
						except:
							pass

					await ctx.respond(f"Mes derniers messages ont été clear", ephemeral=True)
					file.write(f"\n{currentTime} Les derniers messages envoyés à {ctx.author.name} on été effacés\n")
				return

			# ~ Le salon à nettoyer n'a pas été spécifié
			if salon == None:
				salon = ctx.channel

			# ~ Manque de permissions
			if not ctx.channel.permissions_for(ctx.author).manage_messages:
				await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
				print(f"\n{currentTime} {ctx.author.name} a voulu clear {salon.name} de {nombre} messages\n")
				return

			await ctx.respond(f"Début du clear de {salon.mention}", ephemeral=True)
			cpt = 0
			with open(f'logs/logs_{ctx.guild.name}.txt', 'a') as file:
				hist = await salon.history(limit=nombre).flatten()
				for message in hist:
					if user == None or user == message.author:
						await message.delete()
						file.write(f"""
{currentTime} message de {message.author} supprimé dans #{salon.name} :
	{message.content}
""")
						cpt += 1

			await ctx.respond(f"{salon.mention} a été clear de {cpt} messages", ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a clear {salon.name} de {cpt} messages\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Bannir un Member
	@commands.slash_command(description=cmds["ban"][0])
	@option("user", description=cmds["ban"][3]["user"])
	@option("raison", description=cmds["ban"][3]["raison o"])
	@default_permissions(ban_members=True)
	async def ban(self, ctx, user:Member, raison=""):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			# ~ Rôle de la cible trop élevé
			if user.top_role >= ctx.author.top_role:
				await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
				await self.bot.dev.send(f"{ctx.author.mention} a voulu ban {user.mention} de {ctx.guild}")
				await ctx.author.timeout(until=currentTime+dt.timedelta(minutes=2), reason=f"A voulu ban {user.name}")
				print(f"\n{currentTime} {ctx.author.name} a voulu ban {user.name} de {ctx.guild}\n")
				return

			try:
				who = f" (demandé par {ctx.author.name})"
				raison += who
				await user.ban(reason=raison)
				await ctx.respond(f"{user.mention} a été ban, raison : **{raison[:-len(who)]}**", ephemeral=True)
				print(f"\n{currentTime} {user.name} a été banni de {ctx.guild}\n")

			except Exception as error:
				msg = f"Échec du ban de {user.mention} : ```{error}```"
				if not ctx.author == self.bot.dev:
					await self.bot.dev.send(f"{ctx.author.mention} a raté son ban de {user.mention}, message d'erreur : ```{fail()}```")
					msg += "(message d'erreur envoyé au dev en copie)"
				await ctx.respond(msg, ephemeral=True)
				print(f"\n{currentTime} échec du ban de {user.name}, erreur :\n{error}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Mute un Member
	@commands.slash_command(description=cmds["mute"][0])
	@option("user", description=cmds["mute"][3]["user"])
	@option("duree", description=cmds["mute"][3]["durée o"])
	@option("raison", description=cmds["mute"][3]["raison o"])
	@default_permissions(moderate_members=True)
	async def mute(self, ctx, user:Member, duree="30m", raison=" "):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			tps = currentTime
			# ~ Interprétation de la durée donnée
			if duree[-1] == "s":
				tps += dt.timedelta(seconds=int(duree[:-1]))
			elif duree[-1] == "m":
				tps += dt.timedelta(minutes=int(duree[:-1]))
			elif duree[-1] == "h":
				tps += dt.timedelta(hours=int(duree[:-1]))
			elif duree[-1] == "j" or duree[:-1] == "d":
				tps += dt.timedelta(days=int(duree[:-1]))
			else:
				await ctx.respond(f"{duree} n'a pas le bon format, `/aide mute` pour plus d'infos", ephemeral=True)
				return

			# ~ Rôle trop élevé
			if user.top_role >= ctx.author.top_role:
				await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
				await ctx.author.timeout(until=tps, reason=f"A voulu mute {user.name}")
				print(f"\n{currentTime} {ctx.author.name} a voulu mute {user.name} de {ctx.guild} pour {duree}\n")
				return

			try:
				who = f" (demandé par {ctx.author.name})"
				raison += who
				await user.timeout(until=tps, reason=raison)
				await ctx.respond(f"{user.mention} a été mute, raison : **{raison[:-len(who)]}**", ephemeral=True)
				print(f"\n{currentTime} {user.name} a été mute de {ctx.guild} pour {duree}\n")

			except Exception as error:
				msg = f"Échec du mute de {user.mention} : ```{error}```"
				if not ctx.author == self.bot.dev:
					await self.bot.dev.send(f"{ctx.author.mention} a raté son mute de {user.mention}, message d'erreur : ```{fail()}```")
					msg += "(message d'erreur envoyé au dev en copie)"
				await ctx.respond(msg, ephemeral=True)
				print(f"\n{currentTime} échec du mute de {user.name}, erreur :\n{error}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Affiche les informations d'un Member
	@commands.slash_command(description=cmds["user_info"][0])
	@option("user", description=cmds["user_info"][3]["user"])
	async def user_info(self, ctx, user:Member):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			embed = Embed(title="Informations", description=f"À propos de {user.mention}", color=user.color)
			embed.add_field(name="Nom", value=str(user), inline=False)
			embed.set_thumbnail(url=user.avatar.url)
			if not user.banner == None:
				embed.add_field(name="Bannière", value=user.banner.url, inline=False)
			embed.add_field(name="Date de Création", value=timeAccuracy(user.created_at), inline=False)
			embed.add_field(name="Dans le serveur depuis", value=timeAccuracy(user.joined_at), inline=False)
			if not user.premium_since == None:
				embed.add_field(name="Booste le serveur depuis", value=user.premium_since, inline=False)
			if ctx.channel.permissions_for(ctx.author).administrator:
				roles = [r.mention for r in user.roles[1:]]
				embed.add_field(name="Rôles", value=", ".join(roles), inline=False)
			await ctx.respond(embed=embed)
			print(f"\n{currentTime} {ctx.author.name} a récupéré les infos de {user.name}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

# ~ Fonctions Random
class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Spamme un texte (emote ou autre) jusqu'à atteindre la limite de caractères
	@commands.slash_command(description=cmds["spam_emote"][0])
	@option("emote", description=cmds["spam_emote"][3]["emote o"])
	@option("user", description=cmds["spam_emote"][3]["user o"])
	async def spam_emote(self, ctx, emote="<:pepe_fuck:943761805703020614>", user:User=None):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer()
			emoji = str(emote) + " "
			lim = ""
			if not user == None:
				lim = user.mention
			msg = emoji * ((2000 - len(lim)) // len (emoji))
			msg += lim
			await ctx.channel.send(msg)
			await ctx.respond(emote, ephemeral=True)
			log = f"\n{currentTime} {ctx.author.name} a spam {emoji}"
			if user != None:
				log += f" et ping {user.name}"
			log += "\n"
			print(log)

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ QPUP, bon courage pour retrouver le lore ...
	@commands.slash_command(description=cmds["qpup"][0])
	@option("nbquestions", description=cmds["qpup"][3]["nbquestions o"])
	async def qpup(self, ctx, nbquestions:int=1):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer()
			qpup = read_db(infos.qpup)
			# ~ Boucle sur le nombre de questions à poser
			for loop in range(nbquestions):
				# ~ Tirage au sort d'une question
				line = random.randrange(len(qpup))
				# ~ Envoi de la question
				await ctx.respond(qpup[line][0])
				# ~ Initialisation des compteurs
				start = 5
				essais = start
				reponse = qpup[line][1].lower()
				# ~ Boucle sur le nombre d'essais restants
				while essais >= 0:
					# ~ Attente d'une proposition de réponse
					rep = await self.bot.wait_for('message', check=lambda msg: msg.channel == ctx.channel and msg.author != self.bot.user)
					essais -= 1
					if correspond(reponse, rep.content.lower()):
						await ctx.respond(f"Bravo ! Tu es un poulet confirmé, nombre d'essais : {start - essais}")
						break
					else:
						await ctx.respond(f"Dommage, il vous reste {essais} essais")
				if essais < 0:
					await ctx.respond(f"La bonne réponse était : {reponse}")
			print(f"\n{currentTime} Fin du QPUP démarré par {ctx.author}\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ 2048, le _ est nécessaire, une fonction ne commence pas à un chiffre
	@commands.slash_command(name="2048", description=cmds["2048"][0])
	@option("size", description=cmds["2048"][3]["size o"])
	async def _2048(self, ctx, size:int=4):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer()
			# ~ Nouveau joueur
			if not ctx.author.mention in self.bot.players:
				bot.players[ctx.author.mention] = Joueur(nom=ctx.author.mention)
			# ~ Création d'un 2048
			game = Game2048(size=size)
			game.duree = currentTime
			add_dict(bot.games, ctx.author.mention, game)
			embed = Embed(title="2048", color=ctx.author.color)
			# ~ Envoie du jeu formatté en python ou n'importe quel autre langage
			# ~ pour colorer les chiffres et ajouter un effet visuel
			embed.add_field(name=f"Partie de {ctx.author.name}", value=f"```python\n{game}```", inline=True)
			moves = [f"{to} : {bool_reac[game.canMove(to)]}" for to in toward]
			embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
			embed.add_field(name="Score", value=game.score, inline=True)
			await ctx.respond(embed=embed, view=View2048())
			with open(f"logs/logs_{ctx.guild.name}.txt", "a") as file:
				file.write(f"\n{currentTime} {ctx.author.name} a lancé un 2048\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Renvoie les stats sur les différents jeux
	@commands.slash_command(name="stats_jeux", description=cmds["stats_jeux"][0])
	async def stats_jeux(self, ctx):
		currentTime, _, botMember = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer()
			embed = Embed(title="Stats", description=str(bot.stats), color=botMember.color)
			for joueur in self.bot.stats.joueurs:
				if joueur.name == ctx.author.mention:
					embed.add_field(name="Stats Personnelles", value=str(joueur))
			await ctx.respond(embed=embed)
			print(f"\n{currentTime} {ctx.author.name} a affiché ses stats\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

class WorldOfWarships(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.shipsAutoComp = init_autocomplete(infos.shipnames)

	def getship(self, ship:str):
		return self.shipsAutoComp.search(word=ship, max_cost=3, size=1)[0][0]

	@commands.slash_command(name="clanships", description=cmds["clanships"][0])
	@option("clan", description=cmds["clanships"][3]["clan"])
	async def clanships(self, ctx, clan:str):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			clanID = getClanID(infos.tokenWOWS, clan, self.bot.session)
			clan = Clan(infos.tokenWOWS, clanID, self.bot.session)
			file = infos.shiplist(clan.tag)
			clan.serialise(file)
			await ctx.respond(f"Liste des ships du clan [{clan.tag}] actualisée", ephemeral=True)
			print(f"\n{currentTime} {ctx.author.name} a lancé l'actualisation des ships du clan [{clan}]\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	@commands.slash_command(name="compo", description=cmds["compo"][0])
	@option("clan", description=cmds["compo"][3]["clan"])
	async def compo(self, ctx, clan:str):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer()
			ships = dict()
			players_db = read_db(infos.shiplist(clan))
			players = convert_db_dict(players_db, 0)
			for player in players:
				for ship in player:
					add_dict(ships, ship, player)

			embed = Embed(title="Joueurs avec les ships de la compo", color=ctx.author.color)
			for ship in ships:
				joueurs = ships[ship]
				if not "compo" in joueurs:
					continue
				_joueurs = [j for j in joueurs if j != "compo"]
				embed.add_field(name=ship, value=", ".join(_joueurs), inline=False)

			await ctx.respond(embed=embed)
			print(f"\n{currentTime} {ctx.author.name} a récupéré la compo du clan [{clan}]\n")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	@commands.slash_command(name="set_compo", description=cmds["set_compo"][0])
	@option("clan", description=cmds["set_compo"][3]["clan"])
	@option("ships", description=cmds["set_compo"][3]["ships"])
	async def set_compo(self, ctx, clan:str, ships:str):
		currentTime, _, _ = await init(self.bot, ctx.guild, ctx.author)
		try:
			await ctx.defer(ephemeral=True)
			ships = [self.getship(e.strip()) for e in ships.split(';')]
			file = infos.shiplist(clan)
			modify_db(file, ["compo"], [ships])
			await ctx.respond(f"La composition pour le clan [{clan}] est maintenant *{'*, *'.join(ships)}*")
			print(f"{currentTime} {ctx.author.name} a redéfni la compo pour le clan [{clan}]")

		except Exception:
			with open(infos.stderr, 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")
