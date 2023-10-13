# GoloBot

Bot Discord développé par @henrigolo.

Inviter le Bot Discord toujours à jour de la dernière version [juste ici](https://discord.com/api/oauth2/authorize?client_id=1045367982060220557&permissions=8&scope=bot%20applications.commands).

Me contacter -> envoyer un message privé au bot ou rejoindre le [Serveur de Support](https://discord.gg/V2spkxSp8N).

---

## Setup

**Nécessite un environnement virtuel**

Créer le module python avec `make build`.
`import GoloBot` pour l'utiliser dans vos scripts python.

`make launch` pour démarrer le bot en tâche de fond.
Attention, vous devez définir les variables suivantes dans votre environnement virtuel.

Nom de la variable | Description | Format | Vide
---|---
tokenDSC | Token de connexion à [Discord](https://discord.com/developers/applications) | string | nécessaire
tokenWOWS | Token de connexion à [World of Warships](https://developers.wargaming.net/reference/all/wows/) | string | `""`
ownerID | Votre identifiant discord | int | nécessaire
invite_bot | Lien pour inviter votre bot | string | `""`
invite_server | Lien vers votre serveur de support | string | `""`
stdout, stderr, dm | Chemins (en dur ou relatif) aux fichiers de log correspondants | string | nécessaire
stats | Chemins (en dur ou relatif) vers la DB des stats des joueurs | string | nécessaire
qpup | Chemins (en dur ou relatif) vers une DB de question / réponse | string | nécessaire
shipnames | Chemins (en dur ou relatif) vers la DB de tous les noms de navires dans World of Warships | string | nécessaire
pidfile, restart, bot_path | Chemins (en dur ou relatif) aux fichiers correspondants | string | nécessaire
error_msg | Message a envoyé en cas d'erreur | string | tout sauf `""`
