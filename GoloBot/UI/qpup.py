from discord import ui, Interaction, ButtonStyle
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.decorators import *
from GoloBot.Auxilliaire.converters import ANSI


# QPUP (non, vous n'aurez pas le lore)
class ModalQPUP(ui.Modal):
    def __init__(self, rep, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(ui.InputText(label="Votre réponse"))
        self.rep = rep

    @modal_logger
    async def callback(self, interaction: Interaction):
        if correspond(self.children[0].value, self.rep):
            await interaction.response.send_message(
                f"{interaction.user.mention} a trouvé la bonne réponse : {self.rep}")
        else:
            await interaction.response.send_message(f"Hé non, ce n'est pas {self.children[0].value}", ephemeral=True)


class BoutonReponseQPUP(ui.Button):
    def __init__(self, rep):
        super().__init__(label="Répondre", style=ButtonStyle.success)
        self.rep = rep

    @button_logger
    async def callback(self, interaction: Interaction):
        msg = interaction.message
        await interaction.response.send_modal(ModalQPUP(rep=self.rep, title=msg.content))


class ViewQPUP(MyView):
    def __init__(self, rep):
        super().__init__()
        self.add_item(BoutonReponseQPUP(bot, rep))
