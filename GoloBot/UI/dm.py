from base_imports import *


# Transmission d'un message privé par le bot
class ModalDM(ui.Modal):
    def __init__(self, bot, target=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.target = target
        self.add_item(ui.InputText(label="Message", style=InputTextStyle.long))
        if target is None:
            self.add_item(ui.InputText(label="Pour"))

    @logger
    async def callback(self, interaction: Interaction):
        joueur = interaction.user
        if self.target is None:
            self.target = await self.bot.fetch_user(int(self.children[1].value))
        embed = GBEmbed(description=self.children[0].value, color=joueur.color)
        content = ""
        if self.target == self.bot.dev:
            content = f"Reçu de {joueur.mention}"
        await self.target.send(content, embed=embed)
        await interaction.respond("Message envoyé :", embed=embed, ephemeral=True)


class BoutonReponseDM(GButton):
    def __init__(self, bot):
        super().__init__(bot, label="Répondre", custom_id="reponse", style=ButtonStyle.success)
        self.target = None

    async def set_target(self, content):
        targets = await usersInStr(content, self.bot)
        return targets[0]

    @logger
    # Répondre au MP
    async def callback(self, interaction: Interaction):
        self.target = await self.set_target(interaction.message.content)
        modal = ModalDM(bot=self.bot, target=self.target, title=f"Votre Message pour {self.target.name}")
        await interaction.response.send_modal(modal)


class BoutonSupprimerDM(GButton):
    def __init__(self, bot):
        super().__init__(bot, label="Supprimer", style=ButtonStyle.danger)

    # Supprimer le MP
    @logger
    async def callback(self, interaction: Interaction):
        await interaction.edit(delete_after=0)


class ViewDM(GBView):
    def __init__(self, bot):
        super().__init__(bot, timeout=None)
        self.target = None
        self.add_item(BoutonReponseDM(bot))
        self.add_item(BoutonSupprimerDM(bot))
