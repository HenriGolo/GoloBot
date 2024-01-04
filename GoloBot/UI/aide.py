from GoloBot.UI.base_imports import *


class BoutonListeCommandes(ui.Button):
    def __init__(self, bot):
        super().__init__(label="Liste des commandes", style=ButtonStyle.success)
        self.bot = bot

    @button_logger
    async def callback(self, interaction: Interaction):
        names = [name for name in cmds]
        names.sort()
        embed = interaction.message.embeds[0]
        liste = "\n".join(names)
        embed.add_field(name="Liste des commandes", value=ANSI().converter("<green>"+liste))
        await interaction.response.edit_message(embed=embed, view=None)


class ViewAide(GBView):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        self.add_item(BoutonListeCommandes(bot))
