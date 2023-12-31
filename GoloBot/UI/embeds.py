from GoloBot.UI.base_imports import *
from discord import Colour


# Création d'Embed
class ModalNewEmbed(ui.Modal):
    def __init__(self, msg_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg_id = msg_id
        self.add_item(ui.InputText(label="Titre", required=False))
        self.add_item(ui.InputText(label="Description", style=InputTextStyle.long, required=False))
        self.add_item(
            ui.InputText(label="Couleur", placeholder="Couleur en Hexadécimal", value="5865F2", required=False))

    @modal_logger
    async def callback(self, interaction: Interaction):
        title = self.children[0].value
        description = ANSI().converter(self.children[1].value)
        color = Colour(int(self.children[2].value, 16))
        embed = GBEmbed(title=title, description=description, color=color)
        view = ViewEditEmbed([embed], embed, self.msg_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Modification d'un Embed déjà existant
class ModalEditEmbed(ui.Modal):
    def __init__(self, embeds, embed, msg_id, send_new=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id
        self.send = send_new
        old = [embed.title, embed.description, hex(embed.color.value)]
        self.add_item(ui.InputText(label="Titre", value=old[0], required=False))
        self.add_item(ui.InputText(label="Description", value=old[1], style=InputTextStyle.long, required=False))
        self.add_item(ui.InputText(label="Couleur", value=old[2], required=False))

    @modal_logger
    async def callback(self, interaction: Interaction):
        title = self.children[0].value
        description = ANSI().converter(self.children[1].value)
        color = Colour(int(self.children[2].value, 16))
        self.embed.title = title
        self.embed.description = description
        self.embed.color = color
        view = ViewEditEmbed(self.embeds, self.embed, self.msg_id)
        if self.send:
            await interaction.response.send_message(embeds=self.embeds, view=view, ephemeral=True)
        else:
            await interaction.response.edit_message(embeds=self.embeds, view=view)


# Modification des champs d'un Embed
class ModalEditEmbedFields(ui.Modal):
    def __init__(self, embeds, embed, index, msg_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.embed = embed
        self.field = index
        self.msg_id = msg_id
        field = embed.fields[index]
        old_name = field.name
        old_value = field.value
        self.add_item(ui.InputText(label="Nom", value=old_name, required=False))
        self.add_item(ui.InputText(label="Contenu", value=old_value, style=InputTextStyle.long, required=False))

    @modal_logger
    async def callback(self, interaction: Interaction):
        name = self.children[0].value
        value = ANSI().converter(self.children[1].value)
        self.embed.set_field_at(self.field, name=name, value=value, inline=False)
        view = ViewEditEmbed(self.embeds, self.embed, self.msg_id)
        await interaction.response.edit_message(embeds=self.embeds, view=view)


# Sélection de l'Embed à modifier
class SelectEmbed(ui.Select):
    def __init__(self, embeds, msg_id):
        self.embeds = embeds
        self.msg_id = msg_id
        choix = [SelectOption(label=f"Modifier {e.title}") for e in embeds]
        super().__init__(placeholder="Modifier un Embed", min_values=1, options=choix)

    def select_embed(self, value):
        for i in range(len(self.embeds)):
            embed = self.embeds[i]
            if value.endswith(embed.title):
                return i

    @select_logger
    async def callback(self, interaction: Interaction):
        index = self.select_embed(self.values[0])
        modal = ModalEditEmbed(self.embeds, self.embeds[index], self.msg_id, title="Édition de l'Embed")
        await interaction.response.send_modal(modal)


# Sélection du champ à modifier
class SelectFieldEmbed(ui.Select):
    def __init__(self, embeds, embed, msg_id):
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id
        # Création des options du menu déroulant
        options = [SelectOption(label=f"Modifier {e.name}") for e in embed.fields]
        options.insert(0, SelectOption(label=f"Modifier {embed.title}"))
        # Création du menu déroulant
        super().__init__(placeholder="Modifier un Champ", min_values=1, options=options)

    def select_field(self, value):
        for i in range(len(self.embed.fields)):
            field = self.embed.fields[i]
            if value.endswith(field.name):
                return i

    @select_logger
    async def callback(self, interaction: Interaction):
        index = self.select_field(self.values[0])
        if index is None:
            modal = ModalEditEmbed(self.embeds, self.embed, self.msg_id, title="Édition de l'Embed")
        else:
            modal = ModalEditEmbedFields(self.embeds, self.embed, index, self.msg_id, title="Édition de Champ")
        await interaction.response.send_modal(modal)


# Sélection de l'Embed à supprimer
class SelectRemoveEmbed(ui.Select):
    def __init__(self, embeds, msg_id):
        self.embeds = embeds
        self.msg_id = msg_id
        choix = [SelectOption(label=f"Supprimer {e.title}") for e in embeds]
        super().__init__(placeholder="Supprimer un Embed", min_values=1, options=choix)

    def select_embed(self, value):
        for e in self.embeds:
            if value.endswith(e.title):
                return e

    @select_logger
    async def callback(self, interaction: Interaction):
        embed = self.select_embed(self.values[0])
        embeds = [e for e in self.embeds if e != embed]
        view = ViewEditEmbed(embeds, embeds[0], self.msg_id)
        await interaction.response.edit_message(embeds=embeds, view=view)


# Sélection du champ à supprimer
class SelectRemoveFieldEmbed(ui.Select):
    def __init__(self, embeds, embed, msg_id):
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id
        options = [SelectOption(label=f"Supprimer {e.name}") for e in embed.fields]
        options.insert(0, SelectOption(label=f"Supprimer {embed.title}"))
        super().__init__(placeholder="Supprimer un Champ", min_values=1, options=options)

    def select_field(self, value):
        for i in range(len(self.embed.fields)):
            field = self.embed.fields[i]
            if value.endswith(field.name):
                return i
        return None

    @select_logger
    async def callback(self, interaction: Interaction):
        index = self.select_field(self.values[0])
        if index is None:
            self.embeds = [e for e in self.embeds if e != self.embed]
            if len(self.embeds) == 0:
                return await interaction.response.edit_message(delete_after=0)
            view = ViewEditEmbed(self.embeds, self.embeds[0], self.msg_id)
        else:
            self.embed.remove_field(index)
            view = ViewEditEmbed(self.embeds, self.embed, self.msg_id)
        await interaction.response.edit_message(embeds=self.embeds, view=view)


class BoutonAjouterChampEmbed(ui.Button):
    def __init__(self, embeds, embed, msg_id):
        super().__init__(label="Ajouter un Champ", style=ButtonStyle.primary)
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id

    @button_logger
    # Ajouter un Champ
    async def callback(self, interaction: Interaction):
        self.embed.add_field(name=f"Champ {len(self.embed.fields)}", value="Nouveau", inline=False)
        view = ViewEditEmbed(self.embeds, self.embed, self.msg_id)
        await interaction.response.edit_message(embeds=self.embeds, view=view)


class BoutonAjouterEmbed(ui.Button):
    def __init__(self, embeds, embed, msg_id):
        super().__init__(label="Ajouter un Embed", style=ButtonStyle.primary)
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id

    @button_logger
    # Ajouter un Embed
    async def callback(self, interaction: Interaction):
        color = self.embeds[-1].color.value
        self.embeds.append(GBEmbed(title=f"Embed {len(self.embeds)}", color=color))
        modal = ModalEditEmbed(self.embeds, self.embeds[-1], self.msg_id, title="Nouvel Embed")
        await interaction.response.send_modal(modal)


class BoutonEnvoyerEmbed(ui.Button):
    def __init__(self, embeds, msg_id):
        super().__init__(label="Valider", style=ButtonStyle.success)
        self.embeds = embeds
        self.msg_id = msg_id

    @button_logger
    # Envoyer les Embeds
    async def callback(self, interaction: Interaction):
        for e in self.embeds:
            e.timestamp = now()
        if self.msg_id == base_value:
            await interaction.channel.send(embeds=self.embeds)
        else:
            msg_id = await interaction.channel.fetch_message(int(self.msg_id))
            await msg_id.edit(embeds=self.embeds, view=None)
        await interaction.response.edit_message(delete_after=0)


# View finale de la création / modification des Embeds
class ViewEditEmbed(GBView):
    def __init__(self, embeds, embed, msg_id):
        super().__init__()
        self.add_item(BoutonAjouterEmbed(embeds, embed, msg_id))
        self.add_item(BoutonAjouterChampEmbed(embeds, embed, msg_id))
        self.add_item(BoutonEnvoyerEmbed(embeds, msg_id))
        if len(embeds) > 1:
            self.add_item(SelectEmbed(embeds, msg_id))
        self.add_item(SelectFieldEmbed(embeds, embed, msg_id))
        if len(embeds) > 1:
            self.add_item(SelectRemoveEmbed(embeds, msg_id))
        self.add_item(SelectRemoveFieldEmbed(embeds, embed, msg_id))
