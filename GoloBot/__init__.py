#!/usr/bin/env python3

# ~ Code Principal

# ~ Bibliothèques

# ~ Discord, la base
from discord import *
from discord.ext import commands

# ~ Gestion du temps
from datetime import datetime, timedelta
from pytz import timezone

# ~ Les commandes subprocess ne marchent potentiellement que sous UNIX
from os import getpid, environ
from subprocess import Popen
import random

# ~ Mes propres fichiers python
from GoloBot.Auxilliaire import * # ~ Quelques fonctions utiles
from GoloBot.Auxilliaire.abreviations import * # ~ Raccourcis et noms customs
from GoloBot.Auxilliaire.games import * # ~ Jeux de plateau custom
from GoloBot.Auxilliaire.aux_maths import * # ~ Outils mathématiques
from GoloBot.views import * # ~ Les composants de l'UI custom

# ~ Privé
# ~ import infos # ~ Tokens entre autres, voir README.md

# ~ Code du bot
class General(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Gestion des messages
	@commands.Cog.listener()
	async def on_message(self, msg):
		currentTime = now()
		author = msg.author
		channel = msg.channel
		guild = msg.guild
		try:
			# ~ Message d'un bot -> inutile
			if author.bot:
				return

			# ~ Message privé -> transmission au dev
			if channel.type == ChannelType.private:
				if not author == self.bot.dev:
					embed = MyEmbed(title="Nouveau Message", description=msg.content, color=author.color)
					# ~ Transmission des pièces jointes
					files = [await file.to_file() for file in msg.attachments]
					await self.bot.dev.send(f"Reçu de {author.mention}",
							embed=embed,
							files=files,
							view=ViewDM(bot=self.bot))
					with open(environ['dm'], 'a') as fichier:
						fichier.write(f"\n{currentTime} {msg.author.name} a envoyé un DM :\n{msg.content}\n")
					await msg.add_reaction("✅")
			else:
				if not msg.flags.suppress_notifications:
					for pr in self.bot.PR:
						if pr.trigger(msg.content) and pr.users(author) and pr.guilds(guild):
							await msg.reply(str(pr))

		except Exception:
			with open(environ['stderr'], 'a') as file:
				file.write(f"\n{currentTime}\n{fail()}\n")

	# ~ Aide
	@commands.slash_command(description=cmds["aide"][0])
	@option("commande", choices=[cmd for cmd in cmds], description=cmds["aide"][3]["commande o"])
	@option("visible", choices=[True, False], description=cmds["aide"][3]["visible o"])
	@Logger.command_logger # ~ Decorator custom
	async def aide(self, ctx, commande="aide", visible:bool=False):
		authorUser = await Member2User(self.bot, ctx.author)
		cmd = commande # ~ Abbréviation pour cause de flemme
		await ctx.defer(ephemeral=not visible)
		# ~ Informations sur la commande
		embed = MyEmbed(title="Aide", color=ctx.author.color)
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
		if not aide_sup == "":
			msg += f"\n**__Aide supplémentaire__** : {aide_sup}\n"
		embed.add_field(name=f"/{cmd}", value=msg, inline=False)
		await ctx.respond(embed=embed, ephemeral=not visible)

	# ~ Renvoie un lien pour inviter le bot
	@commands.slash_command(description=cmds["invite"][0])
	@Logger.command_logger
	async def invite(self, ctx):
		await ctx.defer(ephemeral=True)
		await ctx.respond(f"""Inviter [GoloBot]({environ['invite_bot']})
Rejoindre le [Serveur de Support]({environ['invite_server']})""", ephemeral=True)

	# ~ Renvoie le code source du bot
	@commands.slash_command(description=cmds["code"][0])
	@Logger.command_logger
	async def code(self, ctx):
		await ctx.defer(ephemeral=True)
		embed = MyEmbed(title="Code Source",
			description="Le code source du bot est disponible sur [github](https://github.com/HenriGolo/GoloBot/)",
			color=ctx.author.color)
		await ctx.respond(embed=embed, ephemeral=True)

	# ~ Renvoie les logs
	@commands.slash_command(description=cmds["get_logs"][0])
	@option("last_x_lines", description=cmds["get_logs"][3]["last_x_lines o"])
	@commands.has_permissions(manage_messages=True)
	@Logger.command_logger
	async def get_logs(self, ctx, last_x_lines:int=50):
		await ctx.defer(ephemeral=True)
		# ~ Commande réservée au dev
		if not ctx.author == self.bot.dev:
			await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
			raise Exception("N'est pas dev")

		file = File(fp=environ['stderr'], filename=environ['stderr'].split("/")[-1])
		reponse = f"Dernières {last_x_lines} lignes de **{file}** :\n{tail(environ['stderr'], last_x_lines)[-1900:]}"
		await ctx.respond(f"Voici les logs demandés\n{reponse}", files=[file], ephemeral=True)

	@commands.slash_command(description=cmds["droprates"][0])
	@option("pourcentage", description=cmds["droprates"][3]["pourcentage"])
	@option("nom", description=cmds["droprates"][3]["nom o"])
	@option("item", description=cmds["droprates"][3]["item o"])
	@Logger.command_logger
	async def droprates(self, ctx, pourcentage:float, nom="", item=""):
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
		embed = MyEmbed(title=title, description=f"Pourcentage dans 1 conteneur : {pourcentage}", color=ctx.author.color)
		for key in seuils:
			n = seuils[key]
			embed.add_field(name=f"Au moins {key}% de chances", value=f"{n} conteneurs", inline=False)
		await ctx.respond(embed=embed, ephemeral=(nom == "" or item == ""))

# ~ Fonctions Dev
class Dev(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Envoie un message privé à un User
	@commands.slash_command(description=cmds["dm"][0])
	@Logger.command_logger
	async def dm(self, ctx):
		# ~ Commande réservée au dev
		if not ctx.author == self.bot.dev:
			await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
			raise Exception("N'est pas dev")

		await ctx.send_modal(ModalDM(bot=self.bot, title="Envoyer un message privé"))

	# ~ Déconnecte le bot
	@commands.slash_command(description=cmds["logout"][0])
	@Logger.command_logger
	async def logout(self, ctx):
		await ctx.defer(ephemeral=True)
		# ~ Commande réservée aux User dans la whitelist
		if not ctx.author == self.bot.dev:
			if not ctx.author in self.bot.whitelist:
				await ctx.respond("Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
				await self.bot.dev.send(f"{ctx.author.mention} a essayé de déconnecter le bot")
				raise Exception("N'est pas dev")

		await ctx.respond(f"En ligne depuis : {Timestamp(self.bot.startTime).relative}", ephemeral=True)
		# ~ Déconnecte le bot
		await self.bot.close()

	# ~ Renvoie le ping et d'autres informations
	@commands.slash_command(description=cmds["ping"][0])
	@Logger.command_logger
	async def ping(self, ctx):
		await ctx.defer(ephemeral=True)
		authorUser = await Member2User(self.bot, ctx.author)
		embed = MyEmbed(title="Ping et autres informations", color=ctx.author.color)
		embed.add_field(name="Ping", value=f"{round(self.bot.latency*1000)} ms", inline=False)
		embed.add_field(name="Bot en ligne depuis", value=f"{Timestamp(self.bot.startTime).relative}", inline=False)
		embed.add_field(name="Propiétaire", value=self.bot.dev.mention, inline=False)
		if ctx.author == self.bot.dev:
			embed.add_field(name="Websocket", value=self.bot.ws, inline=False)
		await ctx.respond(embed=embed, ephemeral=True)

	# ~ Propose une suggestion
	@commands.slash_command(name="suggestion", description=cmds["suggestions"][0])
	@Logger.command_logger
	async def suggest(self, ctx):
		await ctx.send_modal(ModalDM(bot=self.bot, target=self.bot.dev, title="Suggestion"))

# ~ Fonctions Admin
class Admin(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Création de sondage
	@commands.slash_command(description=cmds["poll"][0])
	@option("question", description=cmds["poll"][3]["question"])
	@option("reponses", description=cmds["poll"][3]["réponses"])
	@option("salon", description=cmds["poll"][3]["salon o"])
	@Logger.command_logger
	async def poll(self, ctx, question, reponses, salon:TextChannel=None):
		authorUser = await Member2User(self.bot, ctx.author)
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
		embed = MyEmbed(title="Sondage", description=f"Créé par {ctx.author.mention}", color=ctx.author.color)
		embed.add_field(name="Question :", value=question, inline=False)
		embed.add_field(name="Réponses", value=choix, inline=False)

		# ~ Envoi avec les réactions
		sondage = await channel.send(embed=embed)
		for i in range(len(used_alphaB)):
			emoji = used_alphaB[i]
			await sondage.add_reaction(emoji)
		await ctx.respond("Sondage créé !", ephemeral=True)

	# ~ Role react
	@commands.slash_command(description=cmds["role_react"][0])
	@option("roles", description=cmds["role_react"][3]["roles"])
	@option("message", description=cmds["role_react"][3]["message o"])
	@option("message_id", description=cmds["role_react"][3]["message_id o"])
	@commands.has_permissions(manage_roles=True)
	@guild_only()
	@Logger.command_logger
	async def role_react(self, ctx, roles:str="", message:str="", message_id=None):
		if roles == "" and message == "" and message_id == None:
			await ctx.respond("Veuillez renseigner au moins un paramètre")
			return

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

	# ~ Nettoyage des messages d'un salon
	@commands.slash_command(description=cmds["clear"][0])
	@option("nombre", description=cmds["clear"][3]["nombre"])
	@option("salon", description=cmds["clear"][3]["salon o"])
	@option("user", description=cmds["clear"][3]["user o"])
	@Logger.command_logger
	async def clear(self, ctx, nombre:int, salon:TextChannel=None, user:User=None):
		if salon == None:
			salon = ctx.channel
		await ctx.defer(ephemeral=True)
		if ctx.channel.type == ChannelType.private:
			with open("logs/logs_dm.txt", "a") as file:
				await ctx.respond("Début du clear", ephemeral=True, delete_after=2)
				hist = ctx.channel.history(limit=nombre).flatten()
				for msg in await hist:
					try:
						await msg.delete()
						file.write(f"""
{now()} message de {message.author} supprimé dans #{salon.name} :
	{message.content}
""")
					# ~ Erreur la plus probable : message de l'humain, pas du bot
					except:
						pass

				await ctx.respond(f"Mes derniers messages ont été clear", ephemeral=True)
				file.write(f"\n{now()} Les derniers messages envoyés à {ctx.author.name} on été effacés\n")
			return

		# ~ Manque de permissions
		if not ctx.channel.permissions_for(ctx.author).manage_messages:
			await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
			raise Exception("Manque de permissions")

		await ctx.respond(f"Début du clear de {salon.mention}", ephemeral=True)
		cpt = 0
		with open(f'logs/logs_{ctx.guild.name}.txt', 'a') as file:
			hist = await salon.history(limit=nombre).flatten()
			for message in hist:
				if user == None or user == message.author:
					await message.delete()
					file.write(f"""
{now()} message de {message.author} supprimé dans #{salon.name} :
	{message.content}
""")
					cpt += 1

		await ctx.respond(f"{salon.mention} a été clear de {cpt} messages", ephemeral=True, delete_after=10)

	# ~ Bannir un Member
	@commands.slash_command(description=cmds["ban"][0])
	@option("user", description=cmds["ban"][3]["user"])
	@option("raison", description=cmds["ban"][3]["raison o"])
	@commands.has_permissions(ban_members=True)
	@commands.bot_has_permissions(ban_members=True)
	@Logger.command_logger
	async def ban(self, ctx, user:Member, raison=""):
		await ctx.defer(ephemeral=True)
		# ~ Rôle de la cible trop élevé
		if user.top_role >= ctx.author.top_role:
			await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
			await self.bot.dev.send(f"{ctx.author.mention} a voulu ban {user.mention} de {ctx.guild}")
			await ctx.author.timeout(until=now()+timedelta(minutes=2), reason=f"A voulu ban {user.name}")
			raise Exception("Rôle trop faible")

		try:
			who = f" (demandé par {ctx.author.name})"
			raison += who
			await user.ban(reason=raison)
			await ctx.respond(f"{user.mention} a été ban, raison : **{raison[:-len(who)]}**", ephemeral=True)

		except Exception as error:
			msg = f"Échec du ban de {user.mention} : ```{error}```"
			if not ctx.author == self.bot.dev:
				await self.bot.dev.send(f"{ctx.author.mention} a raté son ban de {user.mention}, message d'erreur : ```{fail()}```")
				msg += "(message d'erreur envoyé au dev en copie)"
			await ctx.respond(msg, ephemeral=True)

	# ~ Mute un Member
	@commands.slash_command(description=cmds["mute"][0])
	@option("user", description=cmds["mute"][3]["user"])
	@option("duree", description=cmds["mute"][3]["durée o"])
	@option("raison", description=cmds["mute"][3]["raison o"])
	@commands.has_permissions(moderate_members=True)
	@commands.bot_has_permissions(moderate_members=True)
	@Logger.command_logger
	async def mute(self, ctx, user:Member, duree="30m", raison=" "):
		await ctx.defer(ephemeral=True)
		tps = now()
		# ~ Interprétation de la durée donnée
		if duree[-1] == "s":
			tps += timedelta(seconds=int(duree[:-1]))
		elif duree[-1] == "m":
			tps += timedelta(minutes=int(duree[:-1]))
		elif duree[-1] == "h":
			tps += timedelta(hours=int(duree[:-1]))
		elif duree[-1] == "j" or duree[:-1] == "d":
			tps += timedelta(days=int(duree[:-1]))
		else:
			await ctx.respond(f"{duree} n'a pas le bon format, `/aide mute` pour plus d'infos", ephemeral=True)
			return

		# ~ Rôle trop élevé
		if user.top_role >= ctx.author.top_role:
			await ctx.respond(f"Tu n'as pas la permission d'utiliser cette commande", ephemeral=True)
			await ctx.author.timeout(until=tps, reason=f"A voulu mute {user.name}")
			raise Exception("Rôle trop faible")

		try:
			who = f" (demandé par {ctx.author.name})"
			raison += who
			await user.timeout(until=tps, reason=raison)
			await ctx.respond(f"{user.mention} a été mute, raison : **{raison[:-len(who)]}**", ephemeral=True)

		except Exception as error:
			msg = f"Échec du mute de {user.mention} : ```{error}```"
			if not ctx.author == self.bot.dev:
				await self.bot.dev.send(f"{ctx.author.mention} a raté son mute de {user.mention}, message d'erreur : ```{fail()}```")
				msg += "(message d'erreur envoyé au dev en copie)"
			await ctx.respond(msg, ephemeral=True)

	# ~ Affiche les informations d'un Member
	@commands.slash_command(description=cmds["user_info"][0])
	@option("user", description=cmds["user_info"][3]["user"])
	@Logger.command_logger
	async def user_info(self, ctx, user:Member):
		await ctx.defer(ephemeral=True)
		embed = MyEmbed(title="Informations", description=f"À propos de {user.mention}", color=user.color)
		embed.add_field(name="Nom", value=str(user), inline=False)
		embed.set_thumbnail(url=user.avatar.url)
		if not user.banner == None:
			embed.add_field(name="Bannière", value=user.banner.url, inline=False)
		embed.add_field(name="Date de Création", value=Timestamp(user.created_at).relative, inline=False)
		embed.add_field(name="Dans le serveur depuis", value=Timestamp(user.joined_at).relative, inline=False)
		if not user.premium_since == None:
			embed.add_field(name="Booste le serveur depuis", value=Timestamp(user.premium_since).relative, inline=False)
		if ctx.channel.permissions_for(ctx.author).administrator:
			roles = [r.mention for r in user.roles[1:]]
			embed.add_field(name="Rôles", value=", ".join(roles), inline=False)
		await ctx.respond(embed=embed)

	@commands.slash_command(description=cmds["embed"][0])
	@option("edit", description=cmds["embed"][3]["edit"])
	@commands.has_permissions(manage_messages=True)
	@Logger.command_logger
	async def embed(self, ctx, edit=None):
		if edit == None:
			await ctx.send_modal(ModalNewEmbed(ctx.author.id, title="Nouvel Embed"))

		else:
			await ctx.defer(ephemeral=True)
			msg = await ctx.channel.fetch_message(int(edit))
			await msg.edit(view=ViewEditEmbed(msg.embeds, msg.embeds[-1], ctx.author.id))
			await ctx.respond(".", delete_after=0)

# ~ Fonctions Random
class Fun(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	# ~ Spamme un texte (emote ou autre) jusqu'à atteindre la limite de caractères
	@commands.slash_command(description=cmds["spam_emote"][0])
	@option("emote", description=cmds["spam_emote"][3]["emote o"])
	@option("user", description=cmds["spam_emote"][3]["user o"])
	@Logger.command_logger
	async def spam_emote(self, ctx, emote="<:pepe_fuck:943761805703020614>", user:User=None):
		await ctx.defer(ephemeral=True)
		emoji = str(emote) + " "
		lim = ""
		if not user == None:
			lim = user.mention
		msg = emoji * ((2000 - len(lim)) // len (emoji))
		msg += lim
		await ctx.channel.send(msg)
		await ctx.respond(emote, ephemeral=True)

	# ~ QPUP, bon courage pour retrouver le lore ...
	@commands.slash_command(description=cmds["qpup"][0])
	@option("nbquestions", description=cmds["qpup"][3]["nbquestions o"])
	@Logger.command_logger
	async def qpup(self, ctx, nbquestions:int=1):
		await ctx.defer()
		self.bot.qpup = read_db(environ['qpup'])
		# ~ Boucle sur le nombre de questions à poser
		for loop in range(nbquestions):
			# ~ Tirage au sort d'une question
			line = random.randrange(len(self.bot.qpup))
			# ~ Envoi de la question
			await ctx.respond(self.bot.qpup[line][0], view=ViewQPUP(rep=self.bot.qpup[line][1]))

	# ~ 2048, le _ est nécessaire, une fonction ne commence pas à un chiffre
	@commands.slash_command(name="2048", description=cmds["2048"][0])
	@option("size", description=cmds["2048"][3]["size o"])
	@Logger.command_logger
	async def _2048(self, ctx, size:int=4):
		await ctx.defer()
		# ~ Nouveau joueur
		if not ctx.author.mention in self.bot.players:
			self.bot.players[ctx.author.mention] = Joueur(nom=ctx.author.mention)
		# ~ Création d'un 2048
		game = Game2048(size=size)
		game.duree = now()
		add_dict(self.bot.games, ctx.author.mention, game)
		embed = MyEmbed(title="2048", color=ctx.author.color)
		# ~ Envoie du jeu formatté en python ou n'importe quel autre langage
		# ~ pour colorer les chiffres et ajouter un effet visuel
		embed.add_field(name=f"Partie de {ctx.author.name}", value=f"```python\n{game}```", inline=True)
		moves = [f"{to} : {bool_reac[game.canMove(to)]}" for to in toward]
		embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
		embed.add_field(name="Score", value=game.score, inline=True)
		await ctx.respond(embed=embed, view=View2048(self.bot))

	# ~ Renvoie les stats sur les différents jeux
	@commands.slash_command(name="stats_jeux", description=cmds["stats_jeux"][0])
	@Logger.command_logger
	async def stats_jeux(self, ctx):
		await ctx.defer()
		botMember = await User2Member(ctx.guild, self.bot.user)
		embed = MyEmbed(title="Stats", description=str(self.bot.stats), color=botMember.color)
		for joueur in self.bot.stats.joueurs:
			if joueur.name == ctx.author.mention:
				embed.add_field(name="Stats Personnelles", value=str(joueur))
		await ctx.respond(embed=embed)

	@commands.slash_command(name="no_custom_messages", description=cmds["no_custom_messages"][0])
	@commands.has_permissions(administrator=True)
	@Logger.command_logger
	async def disablePR(self, ctx):
		guild = ctx.guild
		await ctx.defer(ephemeral=True)
		for pr in self.bot.PR:
			pr.Dguilds.append(guild.id)
		await self.bot.dev.send(f"Ajouter {guild.id} ({guild.name}) sur blacklist des PR à la demande de {ctx.author} ({ctx.author.id})")
		await ctx.respond(f"""Les messages de réponses customs sont désormais désactivés sur ce serveur.
Pour changer ça, envoyer un message privé au bot.""", ephemeral=True)
