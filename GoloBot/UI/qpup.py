from .base_imports import *


# QPUP (non, vous n'aurez pas le lore)
class ModalQPUP(ui.Modal):
    def __init__(self, bot, rep, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.add_item(ui.InputText(label="Votre réponse"))
        self.rep = rep

    @logger
    async def callback(self, interaction: Interaction):
        if correspond(self.children[0].value, self.rep):
            await interaction.respond(
                f"{interaction.user.mention} a trouvé la bonne réponse : {self.rep}")
        else:
            await interaction.respond(f"Hé non, ce n'est pas {self.children[0].value}", ephemeral=True)


class BoutonReponseQPUP(GButton):
    def __init__(self, bot, rep):
        super().__init__(bot, label="Répondre", style=ButtonStyle.success)
        self.rep = rep

    @logger
    async def callback(self, interaction: Interaction):
        msg = interaction.message
        await interaction.response.send_modal(ModalQPUP(self.bot, rep=self.rep, title=msg.content))


class ViewQPUP(GBView):
    def __init__(self, bot, rep):
        super().__init__(bot)
        self.bot = bot
        self.add_item(BoutonReponseQPUP(bot, rep))
