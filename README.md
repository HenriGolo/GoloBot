# GoloBot

Bot Discord développé par @henrigolo.

Inviter le Bot Discord toujours à jour de la dernière version [juste ici](https://discord.com/api/oauth2/authorize?client_id=1045367982060220557&permissions=8&scope=bot%20applications.commands).

Me contacter → envoyer un message privé au bot ou rejoindre le [Serveur de Support](https://discord.gg/V2spkxSp8N).

---

## Setup

**Nécessite un environnement virtuel**

`make setup` la première fois pour créer tous les fichiers.

Créer le module python avec `make build`.
`import GoloBot` pour l'utiliser dans vos scripts python.

`make update` ou simplement `make` pour démarrer le bot en tâche de fond.

Certains variables sont à définir dans un fichier `secrets.py`. 
Un fichier d'exemple `secrets_template.py` est fourni.
