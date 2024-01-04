from GoloBot.UI.base_imports import *


# QPUP (non, vous n'aurez pas le lore)
class ModalQPUP(ui.Modal):
    def __init__(self, bot, rep, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
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
    def __init__(self, bot, rep):
        super().__init__(label="Répondre", style=ButtonStyle.success)
        self.bot = bot
        self.rep = rep

    @button_logger
    async def callback(self, interaction: Interaction):
        msg = interaction.message
        await interaction.response.send_modal(ModalQPUP(self.bot, rep=self.rep, title=msg.content))


class ViewQPUP(GBView):
    def __init__(self, bot, rep):
        super().__init__(bot)
        self.bot = bot
        self.add_item(BoutonReponseQPUP(bot, rep))
