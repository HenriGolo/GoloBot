from discord import Permissions
from discord.commands import option
from varname import nameof
from GoloBot.Auxilliaire.converters import ANSI

docs = {"pycord": "https://docs.pycord.dev/en/stable/",
        "discord developpers": "https://discord.com/developers/applications",
        "crontab": "https://www.man7.org/linux/man-pages/man5/crontab.5.html",
        "cron": "https://www.man7.org/linux/man-pages/man8/cron.8.html",
        "ansi": "https://gist.github.com/kkrypt0nn/a02506f3712ff2d1c8ca7c9e0aed7c06"}

# Valeur par défaut des arguments
base_value = ""
# Utilisé pour dire qu'un argument n'est pas optionel
assert base_value is not None


class Arg:
    def __init__(self, name, description, **kwargs):
        self.name = name
        self.desc = description
        # Vive le sucre syntaxique
        self.default = kwargs["default"] = kwargs.get("default", None)
        self.required = kwargs["required"] = kwargs.get("required", self.default is None)

        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.option = option(name=self.name, description=self.desc, **kwargs)

    def __str__(self):
        name = self.name
        if not self.required:
            name += " (optionnel)"
        affichage = f"""- <cyan>{name}<reset>
    {self.desc}"""
        if self.default is not None and self.default != base_value:
            affichage += "\n\tValeur par défaut : "
            affichage += f"<yellow>{self.default}<reset>"
        return ANSI.converter(affichage)

    def __eq__(self, other):  # self == other
        if isinstance(other, self.__class__):
            return self.name == other.name and self.desc == other.desc
        return False

    def __lt__(self, other):  # self < other
        if isinstance(other, self.__class__):
            if self.required == other.required:
                return self.name < other.name
            return self.required
        return False

    def __gt__(self, other):  # self > other
        if isinstance(other, self.__class__):
            if self.required == other.required:
                return self.name > other.name
            return self.required
        return False


class DocCommand:
    instances = list()

    def __init__(self, name: str, desc: str, perms, aide: str, args: list[Arg]):
        self.options = None
        self.name = name
        self.desc = desc
        if isinstance(perms, Permissions):
            self.perms = nameof(perms)
            if perms == Permissions.none():
                self.perms = "Aucune"
        else:
            self.perms = "Développeur"
        self.aide = aide
        args.sort()
        self.args = {a.name: a for a in args}
        self.__class__.instances.append(self)

    def set_options(self):
        self.options = [self.args[arg].option for arg in self.args]
        return self

    def __str__(self):
        return "\n".join([str(self.args[e]) for e in self.args])

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            name = self.name == other.name
            desc = self.desc == other.desc
            args = self.args == other.args
            return name and desc and args
        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.name < other.name
        return False

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            if self == other:
                return self.value > other.value
            return self.name > other.name
        return False


DocCommand("aide",
           "Affiche la liste des commandes.",
           Permissions.none(),
           "",
           [Arg("commande", "Une commande en particulier.", default="aide"),
            Arg("visible", "Affiche la fenêtre d'aide à tout le monde.", default=False)])

DocCommand("dm",
           "Envoie un MP",
           "dev",
           "",
           [])

DocCommand("logout",
           "Déconnecte le bot.",
           "dev",
           "",
           [])

DocCommand("ping",
           "Ping et autres infos",
           Permissions.none(),
           "Informations : latence du bot, running time ... ce genre de trucs.",
           [])

DocCommand("poll",
           "Crée un sondage, séparer les réponses par un point virgule.",
           Permissions.none(),
           "",
           [Arg("question", "Question à poser dans le sondage."),
            Arg("reponses", "Réponses possibles dans le sondage, séparer par un point virgule."),
            Arg("salon", "Salon où envoyer le sondage.", default=base_value)])

DocCommand("role_react",
           "Ajoute un menu déroulant à un message pour choisir des rôles.",
           Permissions.manage_roles,
           """`roles` et `message` n'ont pas besoin d'être renseignés tous les 2.
Dans le cas où `message` est renseigné, un nouveau message avec le même contenu sera envoyé et l'original sera supprimé.
Si échec suivi d'une possibilité `Actualiser`, choisir `Actualiser` et continuer normalement.""",
           [Arg("roles", "Mentions des rôles à attribuer, avec ou sans séparation.", default=base_value),
            Arg("texte", "Toutes les mentions des rôles à attribuer, contenues dans un texte custom.",
                default=base_value),
            Arg(name="message", default=base_value,
                description="Identifiant d'un message à utiliser. ⚠ le message sera supprimé puis envoyé par le bot.")])

DocCommand("spam_emote",
           "Spamme une emote.",
           Permissions.none(),
           "",
           [Arg("emote",
                "Une emote qui va être spam pour atteindre la limite de 2000 caractères.",
                default="<:pepe_fuck:943761805703020614>"),
            Arg("user", "Mentionne un utilisateur en particulier.", default=base_value)])

DocCommand("clear",
           "Nettoie un salon.",
           Permissions.manage_messages,
           "Préciser le nombre de messages et le salon (par défaut : le salon actuel), éventuellement l'auteur.",
           [Arg("nombre", "Nombre de messages à chercher dans l'historique."),
            Arg("salon", "Salon où supprimer les messages.", default=base_value),
            Arg("user", "Ne supprimer que les messages de l'utilisateur en question.",
                default=base_value)])

DocCommand("ban",
           "Si tu sais pas ce que c'est, t'es pas concerné.",
           Permissions.ban_members,
           "",
           [Arg("user", "Utilisateur à bannir."),
            Arg("raison", "Motif du ban.", default=" ")])

DocCommand("mute",
           "Mute une personne.",
           Permissions.moderate_members,
           """Durée sous forme d'un nombre et `d` ou `j` (jour), `h` (heure), `m` (minute), `s` (secondes).
Ne pas combiner, par exemple `3m30s` est invalide, utiliser `210s` à la place.""",
           [Arg("user", "Utilisateur à mute."),
            Arg("duree", "Durée du mute.", default="30m"),
            Arg("raison", "Motif du mute.", default=" ")])

DocCommand("invite",
           "Affiche un lien pour inviter le bot.",
           Permissions.none(),
           "",
           [])

DocCommand("github",
           "Lien vers GitHub pour accéder aux fichiers du bot.",
           Permissions.none(),
           f"""Doc Pycord : [ici]({docs['pycord']}).
Portail des Développeurs : [ici]({docs['discord developpers']}).
Doc Cron : [ici]({docs['crontab']}) et [là]({docs['cron']}).""",
           [])

DocCommand("get_logs",
           "Envoie les logs des erreurs.",
           "dev",
           "",
           [Arg("last_x_lines", "Les X dernières lignes de stderr.", default=50)])

DocCommand("get_history",
           "Envoie les logs de stdout.",
           "dev",
           "",
           [Arg("last_x_lines", "Les X dernières lignes de stdout.", default=50)])

DocCommand("qpup",
           "Lance le quiz Questions Pour Un Poulet !",
           Permissions.none(),
           "Tellement de lore derrière ce nom ... Même avec le nom vous devinerez pas ...",
           [Arg("nbquestions", "Nombre de questions désirées.", default=1)])

DocCommand("user_info",
           "Donne des informations sur la personne demandée.",
           Permissions.none(),
           "Nom, date de création du compte, membre du serveur depuis <date>, rôles (si permission `Gérer les Rôles`))",
           [Arg("user", "Utilisateur ciblé.")])

DocCommand("2048",
           "Démarre une partie de 2048.",
           Permissions.none(),
           "",
           [Arg("size", "Taille de la grille.", default=4)])

DocCommand("suggestions",
           "Envoie un MP au dev à propos d'une suggestion que vous avez.",
           Permissions.none(),
           "Vous pouvze aussi passer par le Serveur de Support",
           [])

DocCommand("droprates",
           "Indique le nombre de lootbox attendu pour une certaine probabilité de drop.",
           Permissions.none(),
           "Renseigner le nom de la lootbox **et** l'item voulu va afficher la fenêtre de résultats à tout le monde.",
           [Arg("pourcentage", "Pourcentage de drop de l'item désiré."),
            Arg("nom", "Nom de la lootbox.", default=base_value),
            Arg("item", "Item désiré.", default=base_value)])

DocCommand("embed",
           "Crée un nouvel embed, entièrement customisable.",
           Permissions.none(),
           f"""Si modification d'un Embed existant : aucune modification n'est effective avant de valider à la toute fin.
Documention sur les [couleurs ANSI]({docs['ansi']}).
Utilisation avec le bot : <couleur>, <bgcouleur> ou <reset>.""",
           [Arg("edit", "ID du message à modifier.", default=base_value)])

DocCommand("play",
           "Joue une musiqe / playlist à partir d'une recherche / url.",
           Permissions.none(),
           "Sources supportées : YouTube, Twitter, SoundCloud, BandCamp",
           [Arg("search", "Mots clé ou URL de la vidéo / playlist à jouer.")])

DocCommand("playlist",
           "Affiche la playlist en cours.",
           Permissions.none(),
           "",
           [])

DocCommand("stop",
           "Arrête la musique et déconnecte le bot du vocal.",
           Permissions.none(),
           "",
           [])

DocCommand("skip",
           "Joue la prochaine musique de la playlist.",
           Permissions.none(),
           "",
           [])

DocCommand("songinfo",
           "Des informations sur la musique en cours.",
           Permissions.none(),
           "Provenance et durée de la musique.",
           [])

DocCommand("historique",
           "Affiche l'historique des musiques jouées.",
           Permissions.none(),
           "",
           [])

DocCommand("volume",
           "Change le volume de la musique.",
           Permissions.none(),
           "",
           [Arg("volume", "Compris entre 1 et 100 (inclus).")])

DocCommand("loop",
           "(Dés)active la boucle de la PlayList.",
           Permissions.none(),
           "",
           [])

DocCommand("write_emote",
           "Écrit un mot avec des réactions sous un message",
           Permissions.none(),
           "",
           [Arg("mot", "Mot à écrire."),
            Arg("message", "Identifiant du message.")])

DocCommand("dashboard",
           "Affiche un menu de configuration des paramètres locaux du serveur.",
           Permissions.manage_guild,
           "",
           [])

DocCommand("wows_setup_autorole",
           "Configure l'attribution automatique des rôles discord en fonction des rôles World of Warships",
           Permissions.administrator,
           """Supprimer le message pour annuler l'autorole.
Pour modifier un rôle, supprimer le message puis en refaire un.
:warning: cela nécessite que chaque personne utilise le nouveau bouton""",
           [Arg("clans", "Tag de clan auquel limiter. Laisser vide pour tous les clans", default=base_value),
            Arg("commandant", "Rôle à attribuer au Commandant du clan.", default=base_value),
            Arg("commandant_second", "Rôle à attribuer aux Commandants en Second.", default=base_value),
            Arg("recruteur", "Rôle à attribuer aux Recruteurs.", default=base_value),
            Arg("officier_commissionne", "Rôle à attribuer aux Officiers Commissionnés.", default=base_value),
            Arg("officier_superieur", "Rôle à attribuer aux Officiers Supérieurs.", default=base_value),
            Arg("aspirant", "Rôle à attribuer aux Aspirants.", default=base_value)])

DocCommand("disable",
           "(Dés)Active une commande sur ce serveur.",
           Permissions.administrator,
           "",
           [Arg("commande", "nom de la commande à (dés)activer")])

DocCommand("roles",
           "Donne un ou plusieurs rôles à une ou plusieurs personnes en même temps",
           Permissions.manage_roles,
           "",
           [Arg("mode", "Ajouter ou retirer les rôles en question", choices=["ajouter", "enlever"]),
            Arg("users", "Mentions de toutes les personnes (sans séparateur spécifique)"),
            Arg("roles", "Mentions de tous les rôles (sans séparateur spécifique)")])

DocCommand("move",
           "Déplace un ou plusieurs users vers un même salon vocal.",
           Permissions.move_members,
           "*users* et *depuis_salon* ne sont pas mutuellement exclusifs.",
           [Arg("users", "Mentions des users à déplacer", default=base_value),
            Arg("depuis_salon", "Déplace tous les users du salon en question", default=base_value),
            Arg("vers_salon", "Déplace les users sélectionnés vers ce salon. Laisser vide pour les déconnecter.", default=base_value)])

DocCommand.instances.sort()
cmds = {d.name: d.set_options() for d in DocCommand.instances}
