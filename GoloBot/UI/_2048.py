from base_imports import *
from ..Auxilliaire.games import *


class BoutonDirectionnel2048(GButton):
    def __init__(self, bot, direction):
        super().__init__(bot, label=direction.name, style=ButtonStyle.primary)
        self.direction = direction

    @logger
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
            for child in self.view.children:
                child.label = "Partie Terminée"
                # On désactive le bouton
                child.disabled = True
            game.termine = True

        # On itère sur les boutons de la View
        for child in self.view.children:
            direcs = [d for d in list(Directions) if d.name.lower() == child.label.lower()]
            if len(direcs) > 0:
                child.disabled = not game.canMove(direcs[0])

        embed = GBEmbed(title="2048", color=joueur.color)
        # On envoie le jeu formatté pour du python (ou n'importe quel autre langage)
        # pour colorer les chiffres et ajouter un effet visuel
        embed.add_field(name=f"Partie de {joueur.name}", value=str(game), inline=True)
        moves = [f"{to} : {self.bot.bools[game.canMove(to)]}" for to in list()]
        embed.add_field(name="Mouvements", value="\n".join(moves), inline=True)
        embed.add_field(name="Score", value=game.score, inline=True)
        await interaction.edit(embed=embed, view=self.view)


class BoutonStop2048(GButton):
    def __init__(self, bot):
        super().__init__(bot, label="Arrêter", style=ButtonStyle.danger, emoji=bot.bools[False])

    @logger
    async def callback(self, interaction: Interaction):
        # On désactive tous les boutons
        for child in self.view.children:
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
        await interaction.edit(view=self.view)


# Les boutons pour le jeu de 2048
class View2048(GBView):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        super().__init__(bot, *args, **kwargs)
        for direction in list(Directions):
            self.add_item(BoutonDirectionnel2048(bot, direction))
        self.add_item(BoutonStop2048(bot))
