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
Attention, un fichier `infos.py` doit être créé dans `Main/`.
Vous pouvez y mettre toutes les infos que vous voulez uitliser de façon privée.
Mais doit obligatoirement contenir :

Nom de la variable | Description | Format | Vide
---|---
tokenDSC | Token de connexion à [Discord](https://discord.com/developers/applications) | string | nécessaire
tokenWOWS | Token de connexion à [World of Warships](https://developers.wargaming.net/reference/all/wows/) | string | `""`
ownerID | Votre identifiant discord | int | nécessaire
invitation | Lien pour inviter votre bot | string | nécessaire
whitelisted_users | Liste des id des User Discord auxquels vous accordez des permissions | list[int] | `[]`
stdout, stderr, dm | Chemins (en dur ou relatif) aux fichiers de log correspondants | string | nécessaire
stats | Chemins (en dur ou relatif) vers la DB des stats des joueurs | string | nécessaire
qpup | Chemins (en dur ou relatif) vers une DB de question / réponse | string | nécessaire
shipnames | Chemins (en dur ou relatif) vers la DB de tous les noms de navires dans World of Warships | string | nécessaire
pidfile, restart, bot | Chemins (en dur ou relatif) aux fichiers correspondants | string | nécessaire
