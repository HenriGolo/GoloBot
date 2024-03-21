from .base_imports import *
from discord import Permissions


class BoutonInfos(GButton):
    def __init__(self, bot):
        super().__init__(bot, label="Permissions", style=ButtonStyle.primary)

    @logger
    async def callback(self, interaction: Interaction):
        embed = interaction.message.embeds[0]
        [member_id] = [f.value for f in embed.fields if f.name.lower() == "identifiant"]
        member = await interaction.guild.fetch_member(member_id)
        embed.add_field(name="Permissions", value=color_permissions(member.guild_permissions), inline=False)
        await interaction.edit(embed=embed, view=None)


class ViewUserInfo(GBView):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(bot, *args, **kwargs)
        self.add_item(BoutonInfos(bot))
