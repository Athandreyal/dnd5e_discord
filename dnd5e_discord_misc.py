from discord.ext import commands
import dnd5e_database
import datetime
import discord
from dnd5e_character_sheet import CharacterSheet
import dnd5e_interactions


debug = lambda *args, **kwargs: True  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug

log_file = open('log.txt', 'w')
version = '0.0.1'
release_title = 'the pre-alpha alpha'


def log(s):
    """assumes completed statements, appends a newline"""
    now = datetime.datetime.now()
    s = str(s)
    log_file.write(str(now) + ': ' + s + '\n')
    log_file.flush()
    print(str(now) + ': ' + s)


class general(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ping(self, ctx):
        """A basic ping command"""
        await ctx.send(f"Pong! :ping_pong:\nTook {round(self.bot.latency * 1000, 2)} ms.")

    @commands.command(pass_context=True, hidden=True)
    async def getchar(self, ctx):
        """temporary testing function"""
        int(ctx.author.mention)
        # noinspection PyUnresolvedReferences
        players = self.bot.get_players(ctx.author.mention)
        embed = discord.Embed(title=ctx.author.name + '\'s characters')
        if not players:
            embed.description = 'You have no characters yet, call !new to get started!'
            await ctx.send(embed=embed)
        else:
            for c in players:
                d = CharacterSheet.from_dict(dnd5e_database.database_char_tuple_to_dict(c))
                while d.level < 20:
                    d.experience += 200
                print(d.full_str())
                d = d.dict_short()
                embed.add_field(name=d['name'],
                                value=d['race']+', '+d['class'] + '\nLevel: %2s  HP: %7s' % (d['level'], d['hp']))
            await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def new_user(self, ctx):
        """new user greeting"""
        await ctx.send(dnd5e_interactions.new_user(version, release_title))

    @staticmethod
    async def print_characters_short_form(ctx, player, player_id, chars=None, title=None, desc=None, number=False):
        if not chars:
            chars = dnd5e_database.get_players(player_id)
        player_name = player
        embed = discord.Embed(title=title if title else player + '\'s characters')
        if not chars:
            if player_id == ctx.author.mention:
                prefix = 'You'
                suffix = ', call !new to get started!'
            else:
                prefix = 'They'
                suffix = '.'
            embed.description = desc if desc else prefix + ' have no characters yet' + suffix
            await ctx.send(embed=embed)
        else:
            for i, c in enumerate(chars):
                d = CharacterSheet.from_dict(dnd5e_database.database_char_tuple_to_dict(c)).dict_short()
                embed.add_field(name=('%d) ' % i if number else '') + d['name'],
                                value=d['race']+', '+d['class'] + '\nLevel: %2s  HP: %7s' % (d['level'], d['hp']))
                if desc:
                    embed.description = desc
            await ctx.send(embed=embed)


    @commands.command(pass_context=True)
    async def characters(self, ctx, player: discord.Member = None):
        """printout of a player's characters, short form
        !characters <player_mention>
        if no player_mention is given, it prints out your characters
        if a player mention is given, it prints their characters
        """
        # noinspection PyUnresolvedReferences
        player_id = player.mention if player else ctx.author.mention
        player = player.display_name.split('#')[0] if player else ctx.author.name
        if not player_id:
            await ctx.send('something went wrong, I don\'t have a player_id to look up in the database')
            return
        await self.print_characters_short_form(ctx, player, player_id)


def setup(bot):
    bot.add_cog(general(bot))
