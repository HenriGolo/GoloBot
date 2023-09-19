# GoloBot

Bot Discord développé par @henrigolo.

Bot Discord toujours à jour de la dernière version [juste ici](https://discord.com/api/oauth2/authorize?client_id=1045367982060220557&permissions=8&scope=bot%20applications.commands).

Me contacter -> envoyer un message privé au bot.

# Setup

**Nécessite un environnement virtuel**

Créer le module python avec `make build` puis utiliser `import GoloBot`

`make launch` pour démarrer le bot en tâche de fond.
Attention, un fichier `infos.py` doit être créé dans `Main/`, contenant :

Nom de la variable | Description
---|---
tokenDSC | Token de connexion à [Discord](https://discord.com/developers/applications)
tokenWOWS | Token de connexion à [World of Warships](https://developers.wargaming.net/reference/all/wows/)
ownerID | Votre identifiant discord
invitation | Lien pour inviter votre bot
whitelisted_users | Liste des id des User Discord auxquels vous accordez des permissions (eventuellement vide)
stdout, stderr, dm | Chemins (en dur ou relatif) aux fichiers de log correspondants
stats | Chemins (en dur ou relatif) vers la DB des stats des joueurs
qpup | Chemins (en dur ou relatif) vers une DB de question / réponse
shipnames | Chemins (en dur ou relatif) vers la DB de tous les noms de navires dans World of Warships
pidfile, restart, bot | Chemins (en dur ou relatif) aux fichiers correspondants
