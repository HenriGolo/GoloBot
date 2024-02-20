from .base_imports import *
from discord import Permissions


class BoutonInfos(ui.Button):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

    @logger
    async def callback(self, interaction: Interaction):
        embed = interaction.message.embeds[0]
        [member_id] = [f.value for f in embed.fields if f.name.lower() == "identifiant"]
        user = await interaction.guild.fetch_member(member_id)
        perms = list()
        perm_list = [k for k, v in Permissions.__dict__.items() if isinstance(v, discord.flags.flag_value)]
        perm_list.sort()
        for key in perm_list:
            if getattr(user.guild_permissions, key):
                color = "{}"
                if getattr(Permissions.advanced(), key):
                    color = "<red>{}<reset>"
                elif getattr(Permissions.general(), key):
                    color = "<yellow>{}<reset>"
                elif getattr(Permissions.membership(), key):
                    color = "<cyan>{}<reset>"
                perms.append(color.format(key))
        embed.add_field(name="Permissions", value=ANSI.converter('\n'.join(perms)), inline=False)
        await interaction.response.edit_message(embed=embed, view=None)


class ViewUserInfo(GBView):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(bot, *args, **kwargs)
        self.add_item(BoutonInfos(bot, label="Permissions", style=ButtonStyle.primary))
