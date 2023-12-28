from discord import ui, Interaction, ButtonStyle
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.decorators import *


class ShowFullError(ui.Button):
    def __init__(self, full_embed):
        super().__init__(*args, **kwargs)
        self.full = full_embed

    async def callback(self, interaction: Interaction):
        await interaction.response.edit_message(embed=self.full, view=None)


class ViewError(MyView):
    def __init__(self, full_embed):
        super().__init__()
        self.add_item(ShowFullError(full_embed))
