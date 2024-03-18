from .Auxilliaire import *


# Signature de la classe du bot
class BotTemplate(discord.AutoShardedBot):
    token: str
    session: GBSession
    games: dict
    words: dict[str: set]
    synonyms: dict[str: set[str]]
    commands_names: Completer
    alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
                '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']
    bot: BotTemplate
    PR: list[PrivateResponse]
    startTime: datetime
    dev: discord.User
    support: discord.Guild
    emotes: dict[str: discord.Emoji]
    bools: dict[bool: discord.Emoji]
