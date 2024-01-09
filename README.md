# GoloBot

Bot Discord développé par @henrigolo.

Inviter le Bot Discord toujours à jour de la dernière version [juste ici](https://discord.com/api/oauth2/authorize?client_id=1045367982060220557&permissions=8&scope=bot%20applications.commands).

Me contacter → envoyer un message privé au bot ou rejoindre le [Serveur de Support](https://discord.gg/V2spkxSp8N).

---

## Setup

**Nécessite un environnement virtuel**

*Makefile* : ne pas exécuter avec `make -j`

Créer le module python avec `make build`.
`import GoloBot` pour l'utiliser dans vos scripts python.

`make update` ou simplement `make` pour démarrer le bot en tâche de fond.
Attention, vous devez définir les variables suivantes dans votre environnement virtuel.
Certaines ne vont pas causer d'erreurs si non renseignées, mais risque de rendre un affichage moins aggréable

| Nom de la variable         | Description                                                                 | Format |
|----------------------------|-----------------------------------------------------------------------------|--------|
| token                      | Token de connexion à [Discord](https://discord.com/developers/applications) | string |
| ownerID                    | Votre identifiant discord                                                   | int    |
| invite_bot                 | Lien pour inviter votre bot                                                 | string |
| github                     | Lien vers le repository [GitHub](https://github.com)                        | string |
| invite_server              | Lien vers votre serveur de support                                          | string |
| support_qr                 | Pareil mais un lien avec un QR Code                                         | string |
| stdout, stderr, dm         | Chemins (en dur ou relatif) aux fichiers de log correspondants              | string |
| qpup                       | Chemins (en dur ou relatif) vers une DB de question / réponse               | string |
| pidfile, restart, bot_path | Chemins (en dur ou relatif) aux fichiers correspondants                     | string |
| error_msg                  | Message à envoyer en cas d'erreur                                           | string |
