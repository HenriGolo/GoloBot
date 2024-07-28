# Chemin
path = __file__.split('GoloBot')[0] + 'GoloBot/'

# Tokens
# Discord
token = ''  # Indispensable
# Twitch
twitchID = ''  # Indispensable
twitchSecret = ''  # Indispensable

# Discord
ownerID = 0  # Pas nécessaire
appID = 0  # Pas nécessaire
clientID = 0  # Pas nécessaire
public_key = ''  # Pas nécessaire

# Inviter le bot
invite_bot = ''  # Nécessite d'adapter des parties du code
# Inviter sur le serveur de support
invite_server = ''  # Nécessite d'adapter des parties du code
support_qr = ''  # Nécessite d'adapter des parties du code
# GitHub
github = 'https://github.com/HenriGolo/GoloBot/'

# Logs
stdout = path + 'logs/dev.log'
stderr = path + 'logs/error.log'
dm = path + 'logs/dm.log'

# Lancement du bot
bot_path = path + 'Main/main.py'
# PID pour kill facilement
pidfile = path + 'discord.pid'

# Fichiers .json
# Settings
settings = path + 'Data/settings.json'
# Annonces Streams
annonces_streams = path + 'Data/annonces_streams.json'
# QPUP, aucune info du lore
qpup = path + 'Data/qpup.json'

# Message d'erreur
error_msg = "<a:error:1162123651232051200> Hmm ... Embêtant ça ..."
