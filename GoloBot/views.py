from GoloBot import *

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
		currentTime = now()
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
				self.bot.players[user.mention] + game
				self.bot.stats + self.bot.players[user.mention]
				self.bot.stats.write(infos.stats)

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
		currentTime = now()
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
				self.bot.players[user.mention] + game
				self.bot.stats + self.bot.players[user.mention]
				self.bot.stats.write(infos.stats)

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
		currentTime = now()
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
				self.bot.players[user.mention] + game
				self.bot.stats + self.bot.players[user.mention]
				self.bot.stats.write(infos.stats)

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
		currentTime = now()
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
				self.bot.players[user.mention] + game
				self.bot.stats + self.bot.players[user.mention]
				self.bot.stats.write(infos.stats)

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
		currentTime = now()
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

			self.bot.players[user.mention] + game
			self.bot.stats + self.bot.players[user.mention]
			self.bot.stats.write(infos.stats)
			self.bot.games[user.mention] = [g for g in self.bot.games[user.mention] if g.jeu!="2048"]
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
		currentTime = now()
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
	def __init__(self, roles:list[Role]=[]):
		super().__init__(timeout=None)
		self.add_item(SelectRoleReact(roles=roles))

# ~ QPUP (non vous n'aurez pas le lore)
class ModalQPUP(ui.Modal):
	def __init__(self, rep, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_item(ui.InputText(label="Votre réponse"))
		self.rep = rep

	async def callback(self, interaction):
		if correspond(self.children[0].value, self.rep):
			await interaction.response.send_message(f"{interaction.user.mention} a trouvé la bonne réponse : {self.rep}")
		else:
			await interaction.response.send_message(f"Hé non, ce n'est pas {self.children[0].value}", ephemeral=True)

class ViewQPUP(ui.View):
	def __init__(self, rep):
		self.rep = rep
		super().__init__()

	@ui.button(label="Répondre")
	async def button_callback(self, button, interaction):
		msg = interaction.message
		await interaction.response.send_modal(ModalQPUP(rep=self.rep, title=msg.content))
