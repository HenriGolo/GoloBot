from discord import ui, Interaction, SelectOption, Role
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.decorators import *
from GoloBot.Auxilliaire.converters import ANSI


# Menu déroulant pour le role react
class SelectRoleReact(ui.Select):
    def __init__(self, roles: list[Role]):
        self.roles = roles
        # Création des options du menu déroulant
        choix = [SelectOption(label=f"Récupérer / Enlever {e.name}") for e in roles]
        if not choix:
            choix = [SelectOption(label="Actualiser")]
        # Création du menu déroulant
        super().__init__(placeholder="Choisir un rôle", min_values=1, options=choix, custom_id="role_react")

    # Ce n'est pas un modal, mais c'est le même format d'arguments
    @select_logger
    async def callback(self, interaction: Interaction):
        user = interaction.user
        msg = interaction.message
        guild = interaction.guild
        if self.values[0] == "Actualiser":
            await interaction.response.edit_message(view=ViewRoleReact(rolesInStr(msg.content, guild)))
            return

        for role in self.roles:
            if self.values[0] == role.name:
                if role in user.roles:
                    await user.remove_roles(role)
                    await interaction.response.send_message(content=f"Rôle supprimé : {role.mention}", ephemeral=True)
                else:
                    await user.add_roles(role)
                    await interaction.response.send_message(content=f"Rôle ajouté : {role.mention}", ephemeral=True)
        await msg.edit(view=ViewRoleReact(self.roles))


class ViewRoleReact(MyView):
    def __init__(self, roles: list[Role] = ()):
        super().__init__(timeout=None)
        self.add_item(SelectRoleReact(roles=roles))
