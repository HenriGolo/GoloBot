from GoloBot.UI.base_imports import *


class BoutonListeCommandes(GButton):
    def __init__(self, bot):
        super().__init__(bot, label="Liste des commandes", style=ButtonStyle.success)

    @logger
    async def callback(self, interaction: Interaction):
        names = [name for name in cmds]
        names.sort()
        embed = interaction.message.embeds[0]
        liste = "\n".join(names)
        embed.add_field(name="Liste des commandes", value=ANSI.converter("<green>"+liste))
        await interaction.edit(embed=embed, view=None)


class ViewAide(GBView):
    def __init__(self, bot):
        super().__init__(bot)
        self.bot = bot
        self.add_item(BoutonListeCommandes(bot))
        self.add_item(ui.Button(label="Serveur de Support", url="https://discord.gg/V2spkxSp8N"))
