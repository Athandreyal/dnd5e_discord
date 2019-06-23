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

    @commands.command(pass_context=True)
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

# irrelevant now that I'm passing discord.Member objects
    # async def get_player_name_from_id(self, uid: discord.Member):
    #     debug(uid.display_name)
    #     return uid.display_name
    #     player = [u.name for u in self.bot.users if u.id == uid]
    #     if player:
    #         return player
    #     else:
    #         return None

# irrelevant now that I'm passing discord.Member objects
    # async def get_player_id_by_name(self, ctx, name):
    #     player = [u.id for u in self.bot.users if u.name == name]
    #     print(player)
    #     if player:
    #         player_id = int(player[0])
    #         return player_id
    #     else:
    #         await ctx.send('I don\'t know who %s is' % name)
    #         return None

    @commands.command(pass_context=True)
    async def characters(self, ctx, player: discord.Member = None):
        """printout of a player's characters, short form"""
        # noinspection PyUnresolvedReferences
        player_id = player.mention if player else ctx.author.mention
        player = player.display_name.split('#')[0] if player else ctx.author.name
        if not player_id:
            await ctx.send('something went wrong, I don\'t have a player_id to look up in the database')
            return
        await self.print_characters_short_form(ctx, player, player_id)


def setup(bot):
    bot.add_cog(general(bot))
