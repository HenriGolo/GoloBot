from GoloBot.UI.base_imports import *
from GoloBot.Auxilliaire.settings import *


class ModalDashboard(ui.Modal):
    def __init__(self, bot, guild, setting, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.guild = guild
        self.setting = setting
        self.message = msg
        self.sett = guild_to_settings[guild]
        self.add_item(ui.InputText(label=f"Nouvelle valeur pour {setting}",
                                   value=str(self.sett[setting].value),
                                   style=InputTextStyle.long))

    @logger
    async def callback(self, interaction: Interaction):
        value = self.children[0].value
        value = GBDecoder().decode(value)  # oui c'est overkill de load du json pour ça
        update = self.sett.write(self.setting, value)
        if update == Exit.Success:
            msg = f"Paramètre <cyan>{self.setting}<reset> modifié avec <green>succès"
            await interaction.response.send_message(ANSI.converter(msg), ephemeral=True)
            view = GBView(self.bot)
            view.add_item(SelectDashboard(self.bot, self.guild))
            await self.message.edit(embed=self.sett.to_embed(), view=view)
        elif update == Exit.Fail:
            raise Exception(f"Échec de mise à jour de {self.setting} dans {self.guild}")


class SelectDashboard(ui.Select):
    def __init__(self, bot, guild):
        self.bot = bot
        self.guild = guild
        options = [SelectOption(label=sett) for sett in guild_to_settings[guild].config if not sett in Settings.excluded]
        super().__init__(placeholder="Modifier un paramètre", min_values=1, options=options)

    @logger
    async def callback(self, interaction: Interaction):
        setting = self.values[0]
        await interaction.response.send_modal(
            ModalDashboard(self.bot, self.guild, setting, interaction.message,
                           title=f"Modification de {setting}"))
