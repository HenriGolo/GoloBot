from discord import ui, Interaction
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.decorators import *
from GoloBot.Auxilliaire.converters import ANSI


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


class ViewAide(MyView):
    def __init__(self):
        super().__init__()
        self.add_item(BoutonListeCommandes())
