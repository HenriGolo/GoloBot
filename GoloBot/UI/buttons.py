from discord import *
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.games import *
from GoloBot.Auxilliaire.decorators import *
from GoloBot.UI.modals import *


class BoutonDirectionnel2048(ui.Button):
    def __init__(self, bot, view, direction):
        super().__init__(label=direction.name, style=ButtonStyle.primary)
        self.bot = bot
        self.gameview = view
        self.direction = direction

    @button_logger
    async def callback(self, interaction: Interaction):
        # Récupération du joueur
        joueur = interaction.user
        # Récupération de la dernière partie de 2048 du joueur
        game = [g for g in self.bot.games[joueur.mention] if g.jeu == "2048"][-1]
        # Voir board_bot.games.py
        game.moveAll(self.direction)
        if not game.gagne:
            # Détecte la présence d'un 2048 sur le plateau
            game.gagne = "2048" in str(game)

        # Partie perdue
        if not game.canMoveAll():
            # On itère sur tous les boutons de la View
            for child in self.gameview.children:
                child.label = "Partie Terminée"
                # On désactive le bouton
                child.disabled = True
            game.termine = True

        # On itère sur les boutons de la View
        for child in self.gameview.children:
            direcs = [d for d in list(Directions) if d.name.lower() == child.label.lower()]
            if len(direcs) > 0:
                child.disabled = not game.canMove(direcs[0])

        embed = MyEmbed(title="2048", color=joueur.color)
        # On envoie le jeu formatté pour du python (ou n'importe quel autre langage)
        # pour colorer les chiffres et ajouter un effet visuel
        embed.add_field(name=f"Partie de {joueur.name}", value=str(game), inline=True)
        moves = [f"{to} : {self.bot.bools[game.canMove(to)]}" for to in list()]
        embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
        embed.add_field(name="Score", value=game.score, inline=True)
        await interaction.response.edit_message(embed=embed, view=self.gameview)


class BoutonStop2048(ui.Button):
    def __init__(self, bot, view):
        super().__init__(label="Arrêter", style=ButtonStyle.danger, emoji=bot.bools[False])
        self.bot = bot
        self.gameview = view

    @button_logger
    async def callback(self, interaction: Interaction):
        # On désactive tous les boutons
        for child in self.gameview.children:
            child.disabled = True
            child.label = "Partie Arrêtée"

        joueur = interaction.user
        # On supprime la partie de la liste des parties en cours
        game = [g for g in self.bot.games[joueur.mention] if g.jeu == "2048"][-1]
        game.termine = not game.canMoveAll()
        # Détection de victoire
        game.gagne = "2048" in str(game)
        game.duree = now() - game.duree

        self.bot.games[joueur.mention] = [g for g in self.bot.games[joueur.mention] if g.jeu != "2048"]
        await interaction.response.edit_message(view=self.gameview)


class BoutonReponseQPUP(ui.Button):
    def __init__(self, bot, rep):
        super().__init__(label="Répondre", style=ButtonStyle.success)
        self.rep = rep

    @button_logger
    async def callback(self, interaction: Interaction):
        msg = interaction.message
        await interaction.response.send_modal(ModalQPUP(rep=self.rep, title=msg.content))


class BoutonReponseDM(ui.Button):
    def __init__(self, bot):
        super().__init__(label="Répondre", custom_id="reponse", style=ButtonStyle.success)
        self.bot = bot
        self.target = None

    async def set_target(self, content):
        targets = await usersInStr(content, self.bot)
        return targets[0]

    @button_logger
    # Répondre au MP
    async def callback(self, interaction: Interaction):
        self.target = await self.set_target(interaction.message.content)
        modal = ModalDM(bot=self.bot, target=self.target, title=f"Votre Message pour {self.target.name}")
        await interaction.response.send_modal(modal)


class BoutonSupprimerDM(ui.Button):
    def __init__(self):
        super().__init__(label="Supprimer", custom_id="supprimer", style=ButtonStyle.danger)

    @button_logger
    # Supprimer le MP
    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(delete_after=0)


class BoutonAjouterChampEmbed(ui.Button):
    def __init__(self, embeds, embed):
        super().__init__(label="Ajouter un Champ", style=ButtonStyle.primary)
        self.embeds = embeds
        self.embed = embed

    @button_logger
    # Ajouter un Champ
    async def callback(self, interaction: Interaction):
        self.embed.add_field(name=f"Champ {len(self.embed.fields)}", value="Nouveau", inline=False)
        view = ViewEditEmbed(self.embeds, self.embed, self.msg)
        await interaction.response.edit_message(embeds=self.embeds, view=view)


class BoutonAjouterEmbed(ui.Button):
    def __init__(self, embeds, embed):
        super().__init__(label="Ajouter un Embed", style=ButtonStyle.primary)
        self.embeds = embeds
        self.embed = embed

    @button_logger
    # Ajouter un Embed
    async def callback(self, interaction: Interaction):
        color = self.embeds[-1].color.value
        self.embeds.append(MyEmbed(title=f"Embed {len(self.embeds)}", color=color))
        modal = ModalEditEmbed(self.embeds, self.embeds[-1], self.msg, title="Nouvel Embed")
        await interaction.response.send_modal(modal)


class BoutonEnvoyerEmbed(ui.Button):
    def __init__(self, embeds, msg_id):
        super().__init__(label="Valider", style=ButtonStyle.success)
        self.msg_id = msg_id

    @button_logger
    # Envoyer les Embeds
    async def callback(self, interaction: Interaction):
        msg = interaction.message
        for e in self.embeds:
            e.timestamp = now()
        if self.msg_id == base_value:
            await interaction.channel.send(embeds=self.embeds)
        else:
            msg = await interaction.channel.fetch_message(int(self.msg_id))
            await msg.edit(embeds=self.embeds, view=None)
        await interaction.response.edit_message(delete_after=0)


class BoutonListeCommandes(ui.Button):
    def __init__(self):
        super().__init__(label="Liste des commandes", style=ButtonStyle.success)

    @button_logger
    async def callback(self, interaction: Interaction):
        names = [name for name in cmds]
        names.sort()
        embed = MyEmbed(title="Liste des commandes", color=interaction.user.color)
        description = "<reset>, <green>".join(names)
        embed.description = ANSI().converter("<green>"+description)
        await interaction.response.send_message(embed=embed, ephemeral=True)
