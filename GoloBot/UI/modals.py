from discord import ui, Interaction, InputTextStyle
from GoloBot.Auxilliaire import *
from GoloBot.Auxilliaire.converters import ANSI
from GoloBot.Auxilliaire.decorators import *
from GoloBot.UI import *


# QPUP (non, vous n'aurez pas le lore)
class ModalQPUP(ui.Modal):
    def __init__(self, rep, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_item(ui.InputText(label="Votre réponse"))
        self.rep = rep

    @modal_logger
    async def callback(self, interaction: Interaction):
        if correspond(self.children[0].value, self.rep):
            await interaction.response.send_message(
                f"{interaction.user.mention} a trouvé la bonne réponse : {self.rep}")
        else:
            await interaction.response.send_message(f"Hé non, ce n'est pas {self.children[0].value}", ephemeral=True)


# Transmission d'un message privé par le bot
class ModalDM(ui.Modal):
    def __init__(self, bot, target=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.target = target
        self.add_item(ui.InputText(label="Message", style=InputTextStyle.long))
        if target is None:
            self.add_item(ui.InputText(label="Pour"))

    @modal_logger
    async def callback(self, interaction: Interaction):
        joueur = interaction.user
        if self.target is None:
            self.target = await self.bot.fetch_user(int(self.children[1].value))
        embed = MyEmbed(description=self.children[0].value, color=joueur.color)
        content = ""
        if self.target == self.bot.dev:
            content = f"Reçu de {joueur.mention}"
        await self.target.send(content, embed=embed)
        await interaction.response.send_message("Message envoyé :", embed=embed, ephemeral=True)


# Création d'Embed
class ModalNewEmbed(ui.Modal):
    def __init__(self, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg = msg
        self.add_item(ui.InputText(label="Titre", required=False))
        self.add_item(ui.InputText(label="Description", style=InputTextStyle.long, required=False))
        self.add_item(
            ui.InputText(label="Couleur", placeholder="Couleur en Hexadécimal", value="5865F2", required=False))

    @modal_logger
    async def callback(self, interaction: Interaction):
        title = self.children[0].value
        description = ANSI().converter(self.children[1].value)
        color = Colour(int(self.children[2].value, 16))
        embed = MyEmbed(title=title, description=description, color=color)
        view = ViewEditEmbed([embed], embed, self.msg)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Modification d'un Embed déjà existant
class ModalEditEmbed(ui.Modal):
    def __init__(self, embeds, embed, msg, send_new=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.embed = embed
        self.msg = msg
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
        view = ViewEditEmbed(self.embeds, self.embed, self.msg)
        if self.send:
            await interaction.response.send_message(embeds=self.embeds, view=view, ephemeral=True)
        else:
            await interaction.response.edit_message(embeds=self.embeds, view=view)


# Modification des champs d'un Embed
class ModalEditEmbedFields(ui.Modal):
    def __init__(self, embeds, embed, index, msg, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.embeds = embeds
        self.embed = embed
        self.field = index
        self.msg = msg
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
        view = ViewEditEmbed(self.embeds, self.embed, self.msg)
        await interaction.response.edit_message(embeds=self.embeds, view=view)
