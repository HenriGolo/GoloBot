from GoloBot.Auxilliaire import *


# Signature de la classe du bot
class BotTemplate(AutoAddBot):
    token: DictPasPareil
    games: dict
    alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
                '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
    PR: list[PrivateResponse]
    startTime: datetime
    dev: discord.User
    support: discord.Guild
    emotes: dict[str, discord.Emoji]
    bools: dict[bool, discord.Emoji]
    setup_fini: bool
