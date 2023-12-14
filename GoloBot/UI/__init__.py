from GoloBot.UI.buttons import *
from GoloBot.UI.modals import *
from GoloBot.UI.selects import *


class MyView(ui.View):
    async def on_timeout(self):
        self.disable_all_items()


# Les boutons pour le jeu de 2048
class View2048(MyView):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        self.add_item(BoutonDirectionnel2048(bot, self, Directions.Haut))
        self.add_item(BoutonDirectionnel2048(bot, self, Directions.Bas))
        self.add_item(BoutonDirectionnel2048(bot, self, Directions.Gauche))
        self.add_item(BoutonDirectionnel2048(bot, self, Directions.Droite))
        self.add_item(BoutonStop2048(bot, self))


class ViewRoleReact(MyView):
    def __init__(self, roles: list[Role] = ()):
        super().__init__(timeout=None)
        self.add_item(SelectRoleReact(roles=roles))


class ViewQPUP(MyView):
    def __init__(self, rep):
        super().__init__()
        self.add_item(BoutonReponseQPUP(bot, rep))


class ViewDM(MyView):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.target = None
        self.add_item(BoutonReponseDM(bot))
        self.add_item(BoutonSupprimerDM())


# View finale de la création / modification des Embeds
class ViewEditEmbed(MyView):
    def __init__(self, embeds, embed, msg_id):
        super().__init__()
        self.add_item(BoutonAjouterEmbed(embeds, embed))
        self.add_item(BoutonAjouterChampEmbed(embeds, embed))
        self.add_item(BoutonEnvoyerEmbed(msg_id))
        if len(embeds) > 1:
            self.add_item(SelectEmbed(embeds, self.msg))
        self.add_item(SelectFieldEmbed(embeds, embed, self.msg))
        if len(embeds) > 1:
            self.add_item(SelectRemoveEmbed(embeds, self.msg))
        self.add_item(SelectRemoveFieldEmbed(embeds, embed, self.msg))


class ViewAide(MyView):
    def __init__(self):
        super().__init__()
        self.add_item(BoutonListeCommandes())
