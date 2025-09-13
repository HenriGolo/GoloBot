#!/usr/bin/env python3
import GBsecrets
from os import getpid
import discord
from discord.ext import tasks
from GoloBot import *  # Contient tout ce qu'il faut, imports compris
from privatebot import *  # Réponses custom à certains contenus de messages


class GoloBot(BotTemplate):
    # Récupération des tokens
    token = DictPasPareil(discord=GBsecrets.token,
                          twitch=AccessToken(GBsecrets.twitchID, GBsecrets.twitchSecret))

    # Jeux en cours
    games = dict()

    # Lettres de l'alphabet en caractères Unicode, utilisable comme emotes
    alphabet = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲',
                '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # À priori inutile, mais nécessaire pour le décorateur @logger des events
        self.bot = self

        # Ajout des commandes
        for cog in commands.Cog.__subclasses__():
            self.add_cog(cog(self))

        # Réponses personalisées
        # On cherche dans les subclass pour se laisser la possibilité d'overwrite les fonctions
        # Ce qui ne serait pas possible (ou moins intuitif / facile) avec des instances de PrivateResponse
        self.PR = [pr(self) for pr in PrivateResponse.__subclasses__()]

        # Gestion du PID pour kill proprement
        with open(GBsecrets.pidfile, 'w') as pid:
            pid.write(str(getpid()))

        # Sera défini dans on_ready
        self.startTime: datetime = None
        self.dev: discord.User = None
        self.support: discord.Guild = None
        self.emotes: dict[discord.Emoji] = None
        self.bools: dict[discord.Emoji] = None
        self.setup_fini: bool = False

    def __str__(self):
        return self.user.display_name

    @logger
    async def on_ready(self):
        # Heure de démarrage
        self.startTime = now()

        # Récupération de l'User du dev
        owner = self.owner_id
        if hasattr(GBsecrets, 'ownerID'):
            owner = GBsecrets.ownerID
        self.dev = await self.fetch_user(owner)

        # Message de statut du bot
        activity = discord.Activity(name="GitHub",
                                    state="https://github.com/HenriGolo/GoloBot",
                                    type=discord.ActivityType.watching)
        await self.change_presence(activity=activity)

        # Emojis personnalisés
        self.support = GoloBotGuild = await self.fetch_guild(1158154606124204072)
        self.emotes = {e.name: e for e in list(self.emojis) + list(GoloBotGuild.emojis)}
        self.bools = {True: self.emotes['check'], False: self.emotes['denied']}

        # View persistantes
        self.add_view(ViewRoleReact(self))
        self.add_view(ViewDM(self))

        # Clean guilds.log
        with open('logs/guilds.log', 'w'):
            pass

        for guild in self.guilds:
            await self.on_guild_join(guild)

        # c'est bon, on est prêt
        print(f"{self} connecté !")
        self.setup_fini = True

    async def on_guild_join(self, guild: discord.Guild):
        # Setup de la Musique
        await register(self, guild)

        # Enregistrement des guilds auxquelles le bot appartient
        inv = None
        try:
            invs = await guild.invites()
            dico = {i.uses: i for i in invs if i.expires_at is None}
            # On met de côté une invitation au cas où
            if dico.keys():
                inv = dico[max(dico.keys())]
        except:
            pass
        with open('logs/guilds.log', 'a') as file:
            txt = f'{guild.name} - {guild.owner.display_name} - {guild.owner.mention}'
            if isinstance(inv, discord.Invite):
                txt += f' - {inv.url}'
            file.write(f"{txt}\n")

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState,
                                    after: discord.VoiceState):
        # On ne tient pas compte des join / disconnect des bots
        if member.bot:
            return
        # On prend before pour s'intéresser au vocal dont part la personne
        if before is not None and before.channel is not None:
            # Si le vocal est composé uniquement de bots
            bots = [m.bot for m in before.channel.members]
            if not False in bots:
                for member in before.channel.members:
                    # On arrête la musique éventuelle en cours
                    if member.id == self.user.id:
                        await guild_to_audiocontroller[member.guild.id].stop_player()
                    # Déconnexion
                    await member.move_to(None)

    async def on_message(self, message: discord.Message):
        currentTime = now()
        if message.guild is not None and not message.guild.id in guild_to_settings:
            await register(self, message.guild)
        # Message d'un bot / webhook
        if message.author.bot:
            if message.guild is None:
                return
            if message.reference is None:
                if guild_to_settings[message.guild.id].config["autopublish bots"]:
                    try:
                        await message.publish()
                    except:
                        pass
            return

        # Message privé → transmission au dev
        if message.channel.type == discord.ChannelType.private:
            if not message.author == self.dev:
                embed = GBEmbed(title="Nouveau Message", description=message.content, color=message.author.color)
                # Transmission des pièces jointes
                files = [await fichier.to_file() for fichier in message.attachments]
                await self.dev.send(f"Reçu de {message.author.mention}",
                                    embed=embed,
                                    files=files,
                                    view=ViewDM(bot=self))
                if hasattr(GBsecrets, 'dm'):
                    with open(GBsecrets.dm, 'a') as fichier:
                        fichier.write(
                            f"\n{currentTime} {message.author.display_name} a envoyé un DM :\n{message.content}\n")
                await message.add_reaction(self.bools[True])
        else:
            if guild_to_settings[message.guild.id].config["reponses custom"]:
                # S'obtient avec un '@silent ' devant le message
                if not message.flags.suppress_notifications:
                    for pr in self.PR:
                        await pr.do_stuff(message)


# Création du Bot
intents = discord.Intents.all()
bot = GoloBot(intents=intents)

# Run
bot.run(token=bot.token.discord)
