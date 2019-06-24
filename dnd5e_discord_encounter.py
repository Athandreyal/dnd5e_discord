from discord.ext import commands
import dnd5e_database
import datetime
import discord

# intended for discord actions relating to encounters

debug = lambda *args, **kwargs: True  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


class encounter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(encounter(bot))
