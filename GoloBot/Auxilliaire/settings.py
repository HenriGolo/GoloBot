import json
import discord

guild_to_settings = dict()


class Settings:
    def __init__(self, guild):
        self.guild = guild
        self.json_data = None
        self.config = None
        self.path = 'logs/settings.json'
        self.settings_template = {
            "id": 0,
            "start_voice_channel": None,
            "default_volume": 100,
            "vc_timeout": 600
        }
        self.reload()
        self.upgrade()

    async def write(self, setting, value, ctx):
        response = await self.process_setting(setting, value, ctx)
        with open(self.path, 'w') as source:
            json.dump(self.json_data, source)
        self.reload()
        return response

    def reload(self):
        source = open(self.path, 'r')
        self.json_data = json.load(source)
        target = None
        for server in self.json_data:
            server = self.json_data[server]
            if server['id'] == self.guild.id:
                target = server

        if target is None:
            self.create()
            return
        self.config = target

    def upgrade(self):
        refresh = False
        for key in self.settings_template.keys():
            if key in self.config:
                continue
            self.config[key] = self.settings_template.get(key)
            refresh = True
        if refresh:
            with open(self.path, 'w') as source:
                json.dump(self.json_data, source)
            self.reload()

    def create(self):
        self.json_data[self.guild.id] = self.settings_template
        self.json_data[self.guild.id]['id'] = self.guild.id
        with open(self.path, 'w') as source:
            json.dump(self.json_data, source)
        self.reload()

    def get(self, setting):
        return self.config[setting]

    async def format(self, color=discord.Colour.blurple()):
        embed = MyEmbed(title="Settings", description=self.guild.name, color=color)
        embed.set_thumbnail(url=self.guild.icon_url)
        embed.set_footer(text="Usage: /set `setting_name` `value`")
        exclusion_keys = ['id']
        for key in self.config.keys():
            if key in exclusion_keys:
                continue

            if self.config.get(key) == "" or self.config.get(key) is None:
                embed.add_field(name=key, value="Not Set", inline=False)
                continue

            elif key == "start_voice_channel":
                if self.config.get(key) is not None:
                    found = False
                    for vc in self.guild.voice_channels:
                        if vc.id == self.config.get(key):
                            embed.add_field(
                                name=key, value=vc.name, inline=False)
                            found = True
                    if not found:
                        embed.add_field(
                            name=key, value="Invalid VChannel", inline=False)
                    continue

            embed.add_field(name=key, value=self.config.get(key), inline=False)
        return embed

    async def process_setting(self, setting, value, ctx):
        switcher = {
            'start_voice_channel': lambda: self.start_voice_channel(setting, value, ctx),
            'default_volume': lambda: self.default_volume(setting, value, ctx),
            'vc_timeout': lambda: self.vc_timeout(setting, value, ctx),
        }
        func = switcher.get(setting)
        if func is None:
            return None
        else:
            answer = await func()
            if answer is None:
                return True
            else:
                return answer

    # -----setting methods-----
    async def start_voice_channel(self, setting, value, ctx):
        if value.lower() == "unset":
            self.config[setting] = None
            return

        found = False
        for vc in self.guild.voice_channels:
            if vc.name.lower() == value.lower():
                self.config[setting] = vc.id
                self.config['vc_timeout'] = False
                found = True
        if not found:
            await ctx.respond(f"`Error: Voice channel name not found`\nUsage: /set {setting} vchannelname\nOther options: unset")
            return False

    async def default_volume(self, setting, value, ctx):
        try:
            value = int(value)
        except:
            await ctx.respond(f"`Error: Value must be a number`\nUsage: /set {set} 0-100")
            return False

        if value > 100 or value < 0:
            await ctx.respond(f"`Error: Value must be a number`\nUsage: /set {setting} 0-100")
            return False
        self.config[setting] = value

    async def vc_timeout(self, setting, value, ctx):
        if value.lower() == "true":
            self.config[setting] = True
            self.config['start_voice_channel'] = None
        elif value.lower() == "false":
            self.config[setting] = False
        else:
            await ctx.respond(
                f"`Error: Value must be True/False`\nUsage: /set {setting} True/False")
            return False
