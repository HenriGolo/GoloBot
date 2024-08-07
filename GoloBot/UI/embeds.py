from .base_imports import *
from ..Auxilliaire.doc import base_value
from discord import Color, Colour


# Création d'Embed
class ModalNewEmbed(ui.Modal):
    def __init__(self, bot, msg_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.msg_id = msg_id
        self.add_item(ui.InputText(label="Titre", required=False))
        self.add_item(ui.InputText(label="Description", style=InputTextStyle.long, required=False))
        self.add_item(
            ui.InputText(label="Couleur", placeholder="Couleur en Hexadécimal", value="5865F2", required=False))

    @logger
    async def callback(self, interaction: Interaction):
        title = self.children[0].value
        description = ANSI.converter(self.children[1].value)
        color = Colour(int(self.children[2].value, 16))
        embed = GBEmbed(title=title, description=description, color=color)
        view = ViewEditEmbed(self.bot, [embed], embed, self.msg_id)
        await interaction.respond(embed=embed, view=view, ephemeral=True)


# Modification d'un Embed déjà existant
class ModalEditEmbed(ui.Modal):
    def __init__(self, bot, embeds, embed, msg_id, send_new=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id
        self.send = send_new
        if not embed.color:
            embed.color = Color(0xffffff)
        old = [embed.title, embed.description, hex(embed.color.value)]
        self.add_item(ui.InputText(label="Titre", value=old[0], required=False))
        self.add_item(ui.InputText(label="Description", value=old[1], style=InputTextStyle.long, required=False))
        self.add_item(ui.InputText(label="Couleur", value=old[2], required=False))

    @logger
    async def callback(self, interaction: Interaction):
        title = self.children[0].value
        description = ANSI.converter(self.children[1].value)
        color = Colour(int(self.children[2].value, 16))
        self.embed.title = title
        self.embed.description = description
        self.embed.color = color
        view = ViewEditEmbed(self.bot, self.embeds, self.embed, self.msg_id)
        if self.send:
            await interaction.respond(embeds=self.embeds, view=view, ephemeral=True)
        else:
            await interaction.edit(embeds=self.embeds, view=view)


# Modification des champs d'un Embed
class ModalEditEmbedFields(ui.Modal):
    def __init__(self, bot, embeds, embed, index, msg_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.embeds = embeds
        self.embed = embed
        self.field = index
        self.msg_id = msg_id
        field = embed.fields[index]
        old_name = field.name
        old_value = field.value
        self.add_item(ui.InputText(label="Nom", value=old_name, required=False))
        self.add_item(ui.InputText(label="Contenu", value=old_value, style=InputTextStyle.long, required=False))

    @logger
    async def callback(self, interaction: Interaction):
        name = self.children[0].value
        value = ANSI.converter(self.children[1].value)
        self.embed.set_field_at(self.field, name=name, value=value, inline=False)
        view = ViewEditEmbed(self.bot, self.embeds, self.embed, self.msg_id)
        await interaction.edit(embeds=self.embeds, view=view)


class ModalSetAuthor(ui.Modal):
    def __init__(self, bot, embeds, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.embeds = embeds
        self.add_item(ui.InputText(label="Nom", placeholder="par défaut : toi", required=False))
        self.add_item(ui.InputText(label="Avatar (url)", placeholder="par défaut : toi", required=False))
        self.add_item(ui.InputText(label="Ne modifier que les N premiers", value="Tous"))

    @logger
    async def callback(self, interaction: Interaction):
        name = self.children[0].value
        avatar = self.children[1].value
        try:
            n = int(self.children[2].value)
        except ValueError:
            n = None

        for embed in self.embeds[:n]:
            if not name:
                name = embed.author.display_name
                if not name:
                    name = interaction.user.display_name

            if not avatar:
                avatar = embed.author.icon_url
                if not avatar:
                    avatar = interaction.user.avatar.url

            embed.set_author(name=name, icon_url=avatar)
        await interaction.edit(embeds=self.embeds)


# Sélection de l'Embed à modifier
class SelectEmbed(ui.Select):
    def __init__(self, bot, embeds, msg_id):
        self.bot = bot
        self.embeds = embeds
        self.msg_id = msg_id
        choix = [SelectOption(label=f"Modifier {e.title}") for e in embeds]
        super().__init__(placeholder="Modifier un Embed", min_values=1, options=choix)

    def select_embed(self, value):
        for i in range(len(self.embeds)):
            embed = self.embeds[i]
            if value.endswith(embed.title):
                return i

    @logger
    async def callback(self, interaction: Interaction):
        index = self.select_embed(self.values[0])
        modal = ModalEditEmbed(self.bot, self.embeds, self.embeds[index], self.msg_id, title="Édition de l'Embed")
        await interaction.response.send_modal(modal)


# Sélection du champ à modifier
class SelectFieldEmbed(ui.Select):
    def __init__(self, bot, embeds, embed, msg_id):
        self.bot = bot
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

    @logger
    async def callback(self, interaction: Interaction):
        index = self.select_field(self.values[0])
        if index is None:
            modal = ModalEditEmbed(self.bot, self.embeds, self.embed, self.msg_id, title="Édition de l'Embed")
        else:
            modal = ModalEditEmbedFields(self.bot, self.embeds, self.embed, index, self.msg_id, title="Édition de Champ")
        await interaction.response.send_modal(modal)


# Sélection de l'Embed à supprimer
class SelectRemoveEmbed(ui.Select):
    def __init__(self, bot, embeds, msg_id):
        self.bot = bot
        self.embeds = embeds
        self.msg_id = msg_id
        choix = [SelectOption(label=f"Supprimer {e.title}") for e in embeds]
        super().__init__(placeholder="Supprimer un Embed", min_values=1, options=choix)

    def select_embed(self, value):
        for e in self.embeds:
            if value.endswith(e.title):
                return e

    @logger
    async def callback(self, interaction: Interaction):
        embed = self.select_embed(self.values[0])
        embeds = [e for e in self.embeds if e != embed]
        view = ViewEditEmbed(self.bot, embeds, embeds[0], self.msg_id)
        await interaction.edit(embeds=embeds, view=view)


# Sélection du champ à supprimer
class SelectRemoveFieldEmbed(ui.Select):
    def __init__(self, bot, embeds, embed, msg_id):
        self.bot = bot
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

    @logger
    async def callback(self, interaction: Interaction):
        index = self.select_field(self.values[0])
        if index is None:
            self.embeds = [e for e in self.embeds if e != self.embed]
            if len(self.embeds) == 0:
                return await interaction.edit(delete_after=0)
            view = ViewEditEmbed(self.bot, self.embeds, self.embeds[0], self.msg_id)
        else:
            self.embed.remove_field(index)
            view = ViewEditEmbed(self.bot, self.embeds, self.embed, self.msg_id)
        await interaction.edit(embeds=self.embeds, view=view)


class BoutonAjouterChampEmbed(GButton):
    def __init__(self, bot, embeds, embed, msg_id):
        super().__init__(bot, label="Ajouter un Champ", style=ButtonStyle.primary)
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id

    @logger
    # Ajouter un Champ
    async def callback(self, interaction: Interaction):
        self.embed.add_field(name=f"Champ {len(self.embed.fields)}", value="Nouveau", inline=False)
        view = ViewEditEmbed(self.bot, self.embeds, self.embed, self.msg_id)
        await interaction.edit(embeds=self.embeds, view=view)


class BoutonAjouterEmbed(GButton):
    def __init__(self, bot, embeds, embed, msg_id):
        super().__init__(bot, label="Ajouter un Embed", style=ButtonStyle.primary)
        self.embeds = embeds
        self.embed = embed
        self.msg_id = msg_id

    @logger
    # Ajouter un Embed
    async def callback(self, interaction: Interaction):
        color = self.embeds[-1].color
        if not color:
            color = Color(0xffffff)
        color = color.value
        self.embeds.append(GBEmbed(title=f"Embed {len(self.embeds)}", color=color))
        modal = ModalEditEmbed(self.bot, self.embeds, self.embeds[-1], self.msg_id, title="Nouvel Embed")
        await interaction.response.send_modal(modal)


class BoutonEnvoyerEmbed(GButton):
    def __init__(self, bot, embeds, msg_id):
        super().__init__(bot, label="Valider", style=ButtonStyle.success)
        self.embeds = embeds
        self.msg_id = msg_id

    @logger
    # Envoyer les Embeds
    async def callback(self, interaction: Interaction):
        for e in self.embeds:
            e.timestamp = now()
        if self.msg_id == base_value:
            await interaction.channel.send(embeds=self.embeds)
        else:
            msg_id = await interaction.channel.fetch_message(int(self.msg_id))
            await msg_id.edit(embeds=self.embeds)
        await interaction.edit(delete_after=0)


class BoutonSetAuthor(GButton):
    def __init__(self, bot, embeds):
        super().__init__(bot, label="Définir Auteur", style=ButtonStyle.primary)
        self.embeds = embeds

    @logger
    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(ModalSetAuthor(self.bot, self.embeds, title="Modifier l'auteur"))


# View finale de la création / modification des Embeds
class ViewEditEmbed(GBView):
    def __init__(self, bot, embeds, embed, msg_id):
        super().__init__(bot)
        self.bot = bot
        self.add_item(BoutonAjouterEmbed(bot, embeds, embed, msg_id))
        self.add_item(BoutonAjouterChampEmbed(bot, embeds, embed, msg_id))
        self.add_item(BoutonSetAuthor(bot, embeds))
        self.add_item(BoutonEnvoyerEmbed(bot, embeds, msg_id))
        if len(embeds) > 1:
            self.add_item(SelectEmbed(bot, embeds, msg_id))
        self.add_item(SelectFieldEmbed(bot, embeds, embed, msg_id))
        if len(embeds) > 1:
            self.add_item(SelectRemoveEmbed(bot, embeds, msg_id))
        self.add_item(SelectRemoveFieldEmbed(bot, embeds, embed, msg_id))
