import discord
from discord.ext import commands
import discord_token as token
import dnd5e_database
import dnd5e_discord_misc

debug = lambda *args, **kwargs: True  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


log_file = open('log.txt', 'w')
bot_name = 'Dungeon Master'
cooldown = 15
game = 'D&D 5.E'
activity = 'test_activity'

# this file is intended now to be used for bot specific code.


# very useful embed visualiser
# https://leovoel.github.io/embed-visualizer/

# store character data under a table with UID-GID as key


# presence_types
class Presence:
    PLAYING = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    UNKNOWN = 4


bot = commands.Bot(command_prefix='!', description='Dungeon Master')
command_extensions = ['dnd5e_discord_misc', 'dnd5e_discord_party_actions', 'dnd5e_discord_character_creation']
for extension in command_extensions:
    bot.load_extension(extension)

# @bot.event
# async def on_command_error(ctx, error):
#     log(ctx.message.author.mention + ' ' + error.__class__.__name__ + ' ' + ctx.message.content)
#     # noinspection PyTypeChecker
#     if isinstance(error, commands.CommandInvokeError):
#         log(error.args)
#         log(error.original)
#         log(error.with_traceback(error.__traceback__))
#         return
#     await ctx.send(ctx.message.author.mention)
#     if isinstance(error, commands.CommandNotFound):
#         await ctx.send_help()
#     elif isinstance(error, commands.MissingRequiredArgument):
#         await ctx.send_help(str(ctx.command))
#     elif isinstance(error, commands.CommandOnCooldown):
#         answer = 'The ' + str(ctx.command) + ' command is on cool-down, try again in ' + \
#                  str(int(error.retry_after*10) * .1) + ' seconds'
#         await ctx.send(answer)


# @bot.event
# async def on_command_completion(ctx):
#     await ctx.send(ctx.message.author.mention + ' ' + ctx.message.content + ' succeeded')

@bot.event
async def on_ready():
    dnd5e_database.database_init()
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Activity(name='%s people' % len(bot.users),
                                                        type=Presence.WATCHING))
    dnd5e_discord_misc.log('logged in as {}. Serving {} players on {} servers'.format(bot_name,
                                                                                      len(bot.users),
                                                                                      len(bot.guilds)))


@bot.event
async def on_message(message):
    """per message event, mostly exists to stop the bot from interacting with bots and log all comms it sees"""
    # allow bot on bot for the moment, need to have a test victim for stuff
    if message.author.bot:
        return  # avoid bot on bot action
    dnd5e_discord_misc.log(f"{message.channel}: {message.author.name}: {message.content}")
    await bot.process_commands(message)

bot.run(token.token())


