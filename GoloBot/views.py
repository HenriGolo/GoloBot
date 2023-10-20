from GoloBot import *

class MyView(ui.View):
	async def on_timeout(self):
		self.disable_all_items()

# ~ Les boutons pour le jeu de 2048
class View2048(MyView):
	def __init__(self, bot):
		self.bot = bot
		super().__init__()

	# ~ Bouton "bouger vers le haut"
	@ui.button(label="Haut", style=ButtonStyle.primary, emoji='⬆️')
	@Logger.button_logger
	async def up_button(self, button, interaction):
		# ~ Récupération du joueur
		user = interaction.user
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
			game.duree = now() - game.duree
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

	# ~ Bouton "bouger vers le bas" -> idem que pour le haut
	@ui.button(label="Bas", style=ButtonStyle.primary, emoji='⬇️')
	@Logger.button_logger
	async def down_button(self, button, interaction):
		user = interaction.user
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
			game.duree = now() - game.duree
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

	# ~ Bouton "bouger vers la gauche" -> idem que pour le haut
	@ui.button(label="Gauche", style=ButtonStyle.primary, emoji='⬅️')
	@Logger.button_logger
	async def left_button(self, button, interaction):
		user = interaction.user
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
			game.duree = now() - game.duree
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

	# ~ Bouton "bouger vers la droite" -> idem que pour le haut
	@ui.button(label="Droite", style=ButtonStyle.primary, emoji='➡️')
	@Logger.button_logger
	async def right_button(self, button, interaction):
		user = interaction.user
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
			game.duree = now() - game.duree
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

	# ~ Bouton d'arrêt
	@ui.button(label="Arrêter", custom_id="stop", style=ButtonStyle.danger, emoji='❌')
	@Logger.button_logger
	async def delete_button(self, button, interaction):
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
		game.duree = now() - game.duree

		self.bot.players[user.mention] + game
		self.bot.stats + self.bot.players[user.mention]
		self.bot.stats.write(infos.stats)
		self.bot.games[user.mention] = [g for g in self.bot.games[user.mention] if g.jeu!="2048"]
		await interaction.response.edit_message(view=self)

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

	# ~ C'est pas un modal, mais c'est le même format d'arguments
	@Logger.modal_logger
	async def callback(self, interaction):
		user = interaction.user
		msg = interaction.message
		guild = interaction.guild
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

class ViewRoleReact(MyView):
	def __init__(self, roles:list[Role]=[]):
		super().__init__(timeout=None)
		self.add_item(SelectRoleReact(roles=roles))

# ~ QPUP (non vous n'aurez pas le lore)
class ModalQPUP(ui.Modal):
	def __init__(self, rep, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.add_item(ui.InputText(label="Votre réponse"))
		self.rep = rep

	@Logger.modal_logger
	async def callback(self, interaction):
		if correspond(self.children[0].value, self.rep):
			await interaction.response.send_message(f"{interaction.user.mention} a trouvé la bonne réponse : {self.rep}")
		else:
			await interaction.response.send_message(f"Hé non, ce n'est pas {self.children[0].value}", ephemeral=True)

class ViewQPUP(MyView):
	def __init__(self, rep):
		super().__init__()
		self.rep = rep

	@ui.button(label="Répondre")
	@Logger.button_logger
	async def button_callback(self, button, interaction):
		msg = interaction.message
		await interaction.response.send_modal(ModalQPUP(rep=self.rep, title=msg.content))

class ModalDM(ui.Modal):
	def __init__(self, bot, target=None, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.bot = bot
		self.target = target
		self.add_item(ui.InputText(label="Message", style=InputTextStyle.long))
		if target == None:
			self.add_item(ui.InputText(label="Pour"))

	@Logger.modal_logger
	async def callback(self, interaction):
		user = interaction.user
		if self.target == None:
			self.target = await self.bot.fetch_user(int(self.children[1].value))
		embed = MyEmbed(description=self.children[0].value, color=user.color)
		content = ""
		if self.target == self.bot.dev:
			content = f"Reçu de {user.mention}"
		await self.target.send(content, embed=embed)
		await interaction.response.send_message("Message envoyé :", embed=embed, ephemeral=True)

class ViewDM(MyView):
	def __init__(self, bot):
		super().__init__(timeout=None)
		self.bot = bot

	async def set_target(self, content):
		targets = await usersInStr(content, self.bot)
		return targets[0]

	@ui.button(label="Répondre", custom_id="reponse")
	@Logger.button_logger
	async def reply_button(self, button, interaction):
		self.target = await self.set_target(interaction.message.content)
		await interaction.response.send_modal(ModalDM(bot=self.bot, target=self.target, title=f"Votre Message pour {self.target.name}"))

	@ui.button(label="Supprimer", custom_id="supprimer", style=ButtonStyle.danger)
	@Logger.button_logger
	async def delete_button(self, button, interaction):
		await interaction.response.edit_message(delete_after=0)

class ModalNewEmbed(ui.Modal):
	def __init__(self, msg, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.msg = msg
		self.add_item(ui.InputText(label="Titre", required=False))
		self.add_item(ui.InputText(label="Description", style=InputTextStyle.long, required=False))
		self.add_item(ui.InputText(label="Couleur", placeholder="Couleur en Hexadécimal", value="5865F2", required=False))

	@Logger.modal_logger
	async def callback(self, interaction):
		title = self.children[0].value
		description = self.children[1].value
		color = Colour(int(self.children[2].value, 16))
		embed = MyEmbed(title=title, description=description, color=color)
		view = ViewEditEmbed([embed], embed, self.msg)
		await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ModalEditEmbed(ui.Modal):
	def __init__(self, embeds, embed, msg, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.embeds = embeds
		self.embed = embed
		self.msg = msg
		old = [embed.title, embed.description, hex(embed.color.value)]
		self.add_item(ui.InputText(label="Titre", value=old[0], required=False))
		self.add_item(ui.InputText(label="Description", value=old[1], style=InputTextStyle.long, required=False))
		self.add_item(ui.InputText(label="Couleur", value=old[2], required=False))

	@Logger.modal_logger
	async def callback(self, interaction):
		title = self.children[0].value
		description = self.children[1].value
		color = Colour(int(self.children[2].value, 16))
		self.embed.title = title
		self.embed.description = description
		self.embed.color = color
		view = ViewEditEmbed(self.embeds, self.embed, self.msg)
		await interaction.response.send_message(embeds=self.embeds, view=view, ephemeral=True)

class ModalEditEmbedFields(ui.Modal):
	def __init__(self, embeds, embed, index, msg, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.embeds = embeds
		self.embed = embed
		self.field = index
		self.msg = msg
		field = embed.fields[index]
		old_name = field.name
		old_value = field.value
		self.add_item(ui.InputText(label="Nom", value=old_name, required=False))
		self.add_item(ui.InputText(label="Contenu", value=old_value, style=InputTextStyle.long, required=False))

	@Logger.modal_logger
	async def callback(self, interaction):
		self.embed.set_field_at(self.field, name=self.children[0].value, value=self.children[1].value, inline=False)
		await interaction.response.edit_message(embeds=self.embeds, view=ViewEditEmbed(self.embeds, self.embed, self.msg))

class SelectEmbed(ui.Select):
	def __init__(self, embeds, msg):
		self.embeds = embeds
		self.msg = msg
		options = [SelectOption(label=e.title, description=f"Modifier {e.title}") for e in embeds]
		super().__init__(placeholder="Modifier un Embed", min_values=1, options=options)

	def select_embed(self, value):
		for i in range(len(self.embeds)):
			embed = self.embeds[i]
			if value == embed.title:
				return i

	@Logger.modal_logger
	async def callback(self, interaction):
		index = self.select_embed(self.values[0])
		await interaction.response.send_modal(ModalEditEmbed(self.embeds, self.embeds[index], self.msg, title="Édition de l'Embed"))

class SelectEditEmbed(ui.Select):
	def __init__(self, embeds, embed, msg):
		self.embeds = embeds
		self.embed = embed
		self.msg = msg
		# ~ Création des options du menu déroulant
		options = [SelectOption(label=e.name, description=f"Modifier {e.name}") for e in embed.fields]
		options.insert(0, SelectOption(label=embed.title, description=f"Modifier l'Embed"))
		# ~ Création du menu déroulant
		super().__init__(placeholder="Modifier un Champ", min_values=1, options=options)

	def select_field(self, value):
		for i in range(len(self.embed.fields)):
			field = self.embed.fields[i]
			if value == field.name:
				return i
		return -1

	@Logger.modal_logger
	async def callback(self, interaction):
		index = self.select_field(self.values[0])
		if index == -1:
			await interaction.response.send_modal(ModalEditEmbed(self.embeds, self.embed, self.msg, title="Édition de l'Embed"))
		else:
			await interaction.response.send_modal(ModalEditEmbedFields(self.embeds, self.embed, index, self.msg, title="Édition de Champ"))

class SelectRemoveEmbed(ui.Select):
	def __init__(self, embeds, msg):
		self.embeds = embeds
		options = [SelectOption(label=e.title, description=f"Supprimer {e.title}") for e in embeds]
		super().__init__(placeholder="Supprimer un Embed", min_values=1, options=options)

	def select_embed(self, value):
		for e in self.embeds:
			if e.title == value:
				return e

	@Logger.modal_logger
	async def callback(self, interaction):
		embed = self.select_embed(self.values[0])
		embeds = [e for e in self.embeds if e != embed]
		await interaction.response.edit_message(embeds=embeds)

class SelectRemoveFieldEmbed(ui.Select):
	def __init__(self, embeds, embed, msg):
		self.embeds = embeds
		self.embed = embed
		self.msg = msg
		options = [SelectOption(label=e.name, description=f"Supprimer {e.name}") for e in embed.fields]
		options.insert(0, SelectOption(label=embed.title, description=f"Supprimer l'Embed"))
		super().__init__(placeholder="Supprimer un Champ", min_values=1, options=options)

	def select_field(self, value):
		for i in range(len(self.embed.fields)):
			field = self.embed.fields[i]
			if value == field.name:
				return i
		return None

	@Logger.modal_logger
	async def callback(self, interaction):
		index = self.select_field(self.values[0])
		if index == None:
			embeds = [e for e in self.embeds if e != self.embed]
			view = ViewEditEmbed(embeds, embeds[0], self.msg)
			await interaction.response.edit_message(embeds=embeds, view=view)
		else:
			self.embed.remove_field(index)
			view = ViewEditEmbed(self.embeds, self.embed, self.msg)
			await interaction.response.edit_message(embeds=self.embeds, view=view)

class ViewEditEmbed(MyView):
	def __init__(self, embeds, embed, msg_id):
		super().__init__()
		self.embeds = embeds
		self.embed = embed
		self.msg = msg_id
		self.add_item(SelectEmbed(embeds, self.msg))
		self.add_item(SelectEditEmbed(embeds, embed, self.msg))
		self.add_item(SelectRemoveEmbed(embeds, self.msg))
		self.add_item(SelectRemoveFieldEmbed(embeds, embed, self.msg))

	@ui.button(label="Ajouter un Champ", style=ButtonStyle.primary)
	@Logger.button_logger
	async def button_addfield(self, button, interaction):
		self.embed.add_field(name=f"Champ {len(self.embed.fields)}", value="Nouveau", inline=False)
		view = ViewEditEmbed(self.embeds, self.embed, self.msg)
		await interaction.response.edit_message(embeds=self.embeds, view=view)

	@ui.button(label="Ajouter un Embed", style=ButtonStyle.primary)
	@Logger.button_logger
	async def button_addembed(self, button, interaction):
		color = self.embeds[-1].color.value
		self.embeds.append(MyEmbed(title=f"Embed {len(self.embeds)}", color=color))
		modal = ModalEditEmbed(self.embeds, self.embeds[-1], self.msg, title="Nouvel Embed")
		await interaction.response.send_modal(modal)

	@ui.button(label="Valider", style=ButtonStyle.success)
	@Logger.button_logger
	async def button_send(self, button, interaction):
		msg = interaction.message
		for e in self.embeds:
			e.timestamp = now()
		if self.msg == None:
			await interaction.channel.send(embeds=self.embeds)
			await interaction.response.send_message(".", ephemeral=True, delete_after=0)
		else:
			msg = await interaction.channel.fetch_message(int(self.msg))
			await msg.edit(embeds=self.embeds, view=None)
			await interaction.response.send_message(".", ephemeral=True, delete_after=0)
