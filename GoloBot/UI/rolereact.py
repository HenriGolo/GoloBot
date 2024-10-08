import discord

from .base_imports import *
from discord import Role


# Menu déroulant pour le role react
class SelectRoleReact(ui.Select):
    def __init__(self, bot, roles: list[Role]):
        self.roles = roles
        # Création des options du menu déroulant
        choix = [SelectOption(label=f"Récupérer / Enlever {e.name}") for e in roles]
        if not choix:
            choix = [SelectOption(label="Actualiser")]
        # Création du menu déroulant
        super().__init__(placeholder="Choisir un rôle", min_values=1, options=choix, custom_id="role_react")
        self.bot = bot

    @logger
    async def callback(self, interaction: Interaction):
        member = interaction.user
        msg = interaction.message
        guild = interaction.guild
        if self.values[0] == "Actualiser":
            await interaction.edit(view=ViewRoleReact(self.bot, rolesInStr(msg.content, guild)))
            return

        for role in self.roles:
            if self.values[0].endswith(role.name):
                if role.id in [r.id for r in member.roles]:
                    await member.remove_roles(role)
                    await interaction.respond(content=f"Rôle supprimé : {role.mention}", ephemeral=True)
                else:
                    await member.add_roles(role)
                    await interaction.respond(content=f"Rôle ajouté : {role.mention}", ephemeral=True)
        await msg.edit(view=ViewRoleReact(self.bot, self.roles))


class ViewRoleReact(GBView):
    def __init__(self, bot, roles: list[Role] = ()):
        super().__init__(bot, timeout=None)
        self.bot = bot
        self.add_item(SelectRoleReact(bot, roles=roles))
