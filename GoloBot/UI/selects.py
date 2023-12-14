from discord import ui, Interaction, SelectOption, Role
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.decorators import *
from GoloBot.UI import *
from GoloBot.UI.modals import *


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


# Sélection de l'Embed à modifier
class SelectEmbed(ui.Select):
    def __init__(self, embeds, msg):
        self.embeds = embeds
        self.msg = msg
        choix = [SelectOption(label=f"Modifier {e.title}") for e in embeds]
        super().__init__(placeholder="Modifier un Embed", min_values=1, options=choix)

    def select_embed(self, value):
        for i in range(len(self.embeds)):
            embed = self.embeds[i]
            if value == embed.title:
                return i

    @select_logger
    async def callback(self, interaction: Interaction):
        index = self.select_embed(self.values[0])
        modal = ModalEditEmbed(self.embeds, self.embeds[index], self.msg, title="Édition de l'Embed")
        await interaction.response.send_modal(modal)


# Sélection du champ à modifier
class SelectFieldEmbed(ui.Select):
    def __init__(self, embeds, embed, msg):
        self.embeds = embeds
        self.embed = embed
        self.msg = msg
        # Création des options du menu déroulant
        options = [SelectOption(label=f"Modifier {e.name}") for e in embed.fields]
        options.insert(0, SelectOption(label=f"Modifier {embed.title}"))
        # Création du menu déroulant
        super().__init__(placeholder="Modifier un Champ", min_values=1, options=options)

    def select_field(self, value):
        for i in range(len(self.embed.fields)):
            field = self.embed.fields[i]
            if value == field.name:
                return i

    @select_logger
    async def callback(self, interaction: Interaction):
        index = self.select_field(self.values[0])
        if index is None:
            modal = ModalEditEmbed(self.embeds, self.embed, self.msg, title="Édition de l'Embed")
        else:
            modal = ModalEditEmbedFields(self.embeds, self.embed, index, self.msg, title="Édition de Champ")
        await interaction.response.send_modal(modal)


# Sélection de l'Embed à supprimer
class SelectRemoveEmbed(ui.Select):
    def __init__(self, embeds, msg):
        self.embeds = embeds
        self.msg = msg
        choix = [SelectOption(label=f"Supprimer {e.title}") for e in embeds]
        super().__init__(placeholder="Supprimer un Embed", min_values=1, options=choix)

    def select_embed(self, value):
        for e in self.embeds:
            if e.title == value:
                return e

    @select_logger
    async def callback(self, interaction: Interaction):
        embed = self.select_embed(self.values[0])
        embeds = [e for e in self.embeds if e != embed]
        view = ViewEditEmbed(embeds, embeds[0], self.msg)
        await interaction.response.edit_message(embeds=embeds, view=view)


# Sélection du champ à supprimer
class SelectRemoveFieldEmbed(ui.Select):
    def __init__(self, embeds, embed, msg):
        self.embeds = embeds
        self.embed = embed
        self.msg = msg
        options = [SelectOption(label=f"Supprimer {e.name}") for e in embed.fields]
        options.insert(0, SelectOption(label=f"Supprimer {embed.title}"))
        super().__init__(placeholder="Supprimer un Champ", min_values=1, options=options)

    def select_field(self, value):
        for i in range(len(self.embed.fields)):
            field = self.embed.fields[i]
            if value == field.name:
                return i
        return None

    @select_logger
    async def callback(self, interaction: Interaction):
        index = self.select_field(self.values[0])
        if index is None:
            self.embeds = [e for e in self.embeds if e != self.embed]
            if len(self.embeds) == 0:
                await interaction.response.edit_message(delete_after=0)
                return
            view = ViewEditEmbed(self.embeds, self.embeds[0], self.msg)
        else:
            self.embed.remove_field(index)
            view = ViewEditEmbed(self.embeds, self.embed, self.msg)
        await interaction.response.edit_message(embeds=self.embeds, view=view)
