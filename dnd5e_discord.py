import discord, random, sqlite3, datetime, math, re, json
from discord.ext import commands
import discord_token as token
import dnd5e_interactions
import dnd5e_races
import dnd5e_classes
import dnd5e_enums as enums
import dnd5e_weaponry
import dnd5e_armor
from dnd5e_character_sheet import CharacterSheet, init_wulfgar

database = sqlite3.connect('players.db')
sql_c = database.cursor()
log_file = open('log.txt', 'w')
bot_name = 'Dungeon Master'
cooldown = 15
game = 'D&D 5.E'
activity = 'test_activity'

version = '0.0.1'
release_title = 'the pre-alpha alpha'


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


# store incomplete characters here under the username as key
incomplete_characters = {}

all_traits_set = enums.CLASS_TRAITS.Set().union(enums.TRAIT.Set())

# todo: clean this up, fix the return from  get_implemented to give the three sets without suffixes
# get the current state of implementation for races
full, partial, none = dnd5e_interactions.get_implemented_names(dnd5e_races, all_traits_set)
races_full = full
races_partial = [x[:-2] for x in partial if '-+' in x]
races_none = [x[:-2] for x in none if '--' in x]
races_all = races_full + races_partial + races_none

# get the current state of implementation for classes
full, partial, none = dnd5e_interactions.get_implemented_names(dnd5e_classes, all_traits_set)
classes_full = full
classes_partial = [x[:-2] for x in partial if '-+' in x]
classes_none = [x[:-2] for x in none if '--' in x]
classes_all = classes_full + classes_partial + classes_none

# get the current state of implementation for backgrounds
full, partial, none = dnd5e_interactions.get_implemented_names(enums.BACKGROUNDS,
                                                               enums.SKILL.Set().union(enums.TOOLS.Set()))
backgrounds_full = full
backgrounds_partial = [x[:-2] for x in partial if '-+' in x]
backgrounds_none = [x[:-2] for x in none if '--' in x]
backgrounds_all = backgrounds_full + backgrounds_partial + backgrounds_none

ages = ['Youth', 'Adolescent', 'Young_Adult', 'Mature_Adult', 'Elderly', 'Ancient']
heights = ['Very_Short', 'Short', 'Low_Average', 'High_Average', 'Tall', 'Very_Tall']
weights = ['Very_Thin', 'Thin', 'Low_Average', 'High_Average', 'Stocky', 'Very_Stocky']

default_ability_array = [15, 14, 13, 12, 10, 8]


def log(s):
    """assumes completed statements, appends a newline"""
    now = datetime.datetime.now()
    s = str(s)
    log_file.write(str(now) + ': ' + s + '\n')
    log_file.flush()
    print(str(now) + ': ' + s)


bot = commands.Bot(command_prefix='!', description='Dungeon Master')

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


@bot.event
async def on_command_completion(ctx):
    await ctx.send(ctx.message.author.mention + ' ' + ctx.message.content + ' succeeded')

@bot.event
async def on_ready():
    log('logged in as {}. Serving {} players on {} servers'.format(bot_name, len(bot.users), len(bot.guilds)))
    await bot.change_presence(status=discord.Status.idle,
                              activity=discord.Activity(name='%s people' % len(bot.users),
                                                        type=Presence.WATCHING))
    table = sql_c.execute("select count(*) from sqlite_master where type='table' and name = 'players';")
    if table.rowcount == -1:  # empty db
        sql_c.execute('create table if not exists players (' +
                      'id text, ' +
                      'name text, ' +
                      'age integer, ' +
                      'height integer, ' +
                      'weight integer, ' +
                      'level integer, ' +
                      'experience integer, ' +
                      'unspent_pts integer, ' +
                      'race text, ' +
                      'class text, ' +
                      'background text, ' +
                      'path text, ' +
                      'skills text, ' +
                      'str integer, ' +
                      'con integer, ' +
                      'dex integer, ' +
                      'int integer, ' +
                      'wis integer, ' +
                      'cha integer, ' +
                      'hp_dice integer, ' +
                      'hp_current, ' +
                      'equipment text, ' +
                      'primary key (id, name)' +
                      ');')
        sql_c.execute('create unique index if not exists idx_characters on players(id, name);')
        sql_c.execute('pragma synchronous = 1')
        sql_c.execute('pragma journal_mode = wal')
        database.commit()
        bot.get_players = lambda u: sql_c.execute('select * from players where id = ?', (int(u),)).fetchall()
        bot.get_player = lambda u, n: sql_c.execute('select * from players where id = ? and name = ?',
                                                    (int(u), n)).fetchall()
        bot.set_player = lambda p: (sql_c.execute('insert or replace into players ' +
                                                  '(id, name, age, height, weight, level, experience, ' +
                                                  'unspent_pts, race, class, background, path, skills, str, con, dex,' +
                                                  ' int, wis, cha, hp_dice, hp_current, equipment) values ' +
                                                  '(:uid, :name, :age, :height, :weight, :level, :experience, ' +
                                                  ':unspent_pts, :race, :class, :background, :path, :skills, :str, ' +
                                                  ':con, :dex, :int, :wis, :cha, :hp_dice, :hp_current, :equipment);',
                                                  p),
                                    database.commit(), print('logged',p))


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def new_user(ctx):
    await ctx.send(dnd5e_interactions.new_user(version, release_title))


@bot.event
async def on_message(message):
    """per message event, mostly exists to stop the bot from interacting with bots and log all comms it sees"""
    # allow bot on bot for the moment, need to have a test victim for stuff
    if message.author.bot:
        return  # avoid bot on bot action
    log(f"{message.channel}: {message.author.name}: {message.content}")
    await bot.process_commands(message)


@bot.command()
async def getchar(ctx):
    print('id=', ctx.author.id)
    int(ctx.author.id)
    players = bot.get_players(ctx.author.id)
    for c in players:
        print(c)

# for creating new characters
@bot.command()
async def new(ctx, parameter=None):
    author = ctx.author  # whoever called this instance of new
    author_name = ctx.author.name
    embed = discord.Embed(title=author_name + ' : Character Creation')
    char = incomplete_characters.get(author, None)
    if char is None:
        incomplete_characters[author] = {}
        char = incomplete_characters[author]
    embed.add_field(name='Race', value=char.get('race', None))
    embed.add_field(name='Class', value=char.get('class', None))
    embed.add_field(name='Background', value=char.get('background', None))
    embed.add_field(name='Name', value=char.get('name', None))
    skills = char.get('skills', None)
    if skills is not None:
        s = ''
        for skill in skills:
            s += skill+'\n'
        embed.add_field(name='Skills', value=s)
    else:
        embed.add_field(name='Skills', value=str(None))
    embed.add_field(name='Skills Remaining', value=char.get('skills_remaining', None))
    embed.add_field(name='Age', value=char.get('age', None))
    height = char.get('height', None)
    if height:
        height = '%d\' %d"' % (height //12, height % 12)
    embed.add_field(name='Height', value=height)
    weight = char.get('weight', None)
    if weight:
        weight = '%dlbs' % weight
    embed.add_field(name='Weight', value=weight)
    embed.add_field(name='Strength', value=char.get('str', None))
    embed.add_field(name='Constitution', value=char.get('con', None))
    embed.add_field(name='Dexterity', value=char.get('dex', None))
    embed.add_field(name='Intelligence', value=char.get('int', None))
    embed.add_field(name='Wisdom', value=char.get('wis', None))
    embed.add_field(name='Charisma', value=char.get('cha', None))
    complete = char is not None and None not in [char.get('race', None), char.get('class', None), char.get('name',None),
                                                 char.get('background', None), char.get('skills', None),
                                                 char.get('skills_remaining', None), char.get('age', None),
                                                 char.get('height', None), char.get('weight', None),
                                                 char.get('str', None), char.get('con', None), char.get('dex', None),
                                                 char.get('int', None), char.get('wis', None), char.get('cha', None)] \
               and char.get('skills_remaining', None) == 0
    if parameter == 'finish':
        if complete:
            await ctx.send('finalising character')
            # test instantiation of a character here
            ability = enums.Ability(strength=char['str'],
                                  constitution=char['con'],
                                  dexterity=char['dex'],
                                  intelligence=char['int'],
                                  wisdom=char['wis'],
                                  charisma=char['cha'])
            skills = set()
            for skill in char['skills']:
                skills.add(getattr(enums.SKILL, skill.upper()))
            print(char, skills, ability)
            wulfgar = CharacterSheet(name=char['name'],
                                     age=char['age'],
                                     height=char['height'],
                                     weight=char['weight'],
                                     uid=ctx.author.id,
                                     experience=0,
                                     level=0,
                                     unspent=0,
                                     player_race=char['player_race'](),
                                     player_class=char['player_class'](lvl=0),
                                     skills=skills,
                                     background=char['player_background'],
                                     abilities=ability,
                                     hp_dice=0,
                                     hp_current=None,
                                     equipment=[dnd5e_weaponry.greataxe, dnd5e_armor.breastplate_Armor, None])
            print(wulfgar.full_str())
            w = wulfgar.to_dict()
            w['uid'] = ctx.message.author.id
            bot.set_player(wulfgar.to_dict())
            del incomplete_characters[author]
            return
        else:
            await ctx.send('Character creation is not yet complete')

    await ctx.send(embed=embed, content='Each field has a corresponding set_ command to configure it. For example, '
                                        'you can set your race with !set_race, or Age with !set_age\n\ncall !new '
                                        'again to see current progress, or finish a previous character '
                                        'build !set_new finish\n\nAll commands acknowledge the parameter \'reset\' '
                                        'which will drop your current selections.\n\nWhen you are satisfied, '
                                        'call "!new finish", and the character will be written to the database and '
                                        'persist across interactions and bot resets')


@bot.command()
async def abortnew(ctx):
    if ctx.author not in incomplete_characters:
        await ctx.send('You do not have an incomplete character to abort creating')
        raise commands.CommandInvokeError
    del incomplete_characters[ctx.author]
    await ctx.send('incomplete character creation aborted')


@bot.command()
async def setname(ctx, name=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot set a name yet, call !new first')
        return
    if name:
        incomplete_characters[ctx.author]['name'] = name
    else:
        await ctx.send('a name is required.')


@bot.command()
async def setstr(ctx, strength=None):
    await set_scdiwc(ctx, 'strength', strength)


@bot.command()
async def setcon(ctx, constitution=None):
    await set_scdiwc(ctx, 'constitution', constitution)


@bot.command()
async def setdex(ctx, dexterity=None):
    await set_scdiwc(ctx, 'dexterity', dexterity)


@bot.command()
async def setint(ctx, intelligence=None):
    await set_scdiwc(ctx, 'intelligence', intelligence)


@bot.command()
async def setwis(ctx, wisdom=None):
    await set_scdiwc(ctx, 'wisdom', wisdom)


@bot.command()
async def setcha(ctx, charisma=None):
    await set_scdiwc(ctx, 'charisma', charisma)


@bot.command()
async def setability(ctx, *args):
    #for key in ['str', 'con', 'dex', 'int', 'wis', 'cha']:
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot set an attribute yet, call !new first')
        return
    if not incomplete_characters[ctx.author].get('class', None):
        await ctx.send('You must have a Class before you can choose your attributes')
        return
    if 'reset' in args:
        for key in ['str', 'con', 'dex', 'int', 'wis', 'cha']:
            del incomplete_characters[ctx.author][key]
        return

    array = default_ability_array
    for i in range(len(args)):
        key = ['str', 'con', 'dex', 'int', 'wis', 'cha'][i]
        try:
            val = int(args[i])
        except ValueError:
            await ctx.send('That is not a valid choice')
            return
        if val not in array:
            await ctx.send('That is not a valid choice')
            return
        array.remove(val)
        incomplete_characters[ctx.author][key] = val


async def set_scdiwc(ctx, tag, parameter):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot set an attribute yet, call !new first')
        return
    if not incomplete_characters[ctx.author].get('class', None):
        await ctx.send('You must have a Class before you can choose your attributes')
        return
    if parameter == 'reset':
        del incomplete_characters[ctx.author][tag[:3]]
        return
    char = incomplete_characters[ctx.author]
    if parameter is None:
        embed = discord.Embed(title='Setting character attributes')
        embed.add_field(name='Strength', value=char.get('str', None))
        embed.add_field(name='Constitution', value=char.get('con', None))
        embed.add_field(name='Dexterity', value=char.get('dex', None))
        embed.add_field(name='Intelligence', value=char.get('int', None))
        embed.add_field(name='Wisdom', value=char.get('wis', None))
        embed.add_field(name='Charisma', value=char.get('cha', None))
        suggest = char['player_class'].ability_suggest
        s = []
        for key in suggest:
            if int(suggest[key]) > 0:
                s.append(key + ' = ' + str(suggest[key]))
        suggest = ' and '.join(s)
        content = 'You can set these attributes by calling !set_<tag> <value>, where tag is the three letter code for '\
                  'the attribute, such as dex for dexterity, or int for intelligence.  Value is an integer, ' \
                  'from the default ability array, which is [15, 14, 13, 12, 10, 8].  For a %s, %s are ' \
                  'suggested' % (char['class'], suggest)
        await ctx.send(embed=embed, content=content)
    else:
        try:
            parameter = int(parameter)
            if parameter not in default_ability_array:
                await ctx.send('That is not a valid choice')
                return
            for key in ['str', 'con', 'dex', 'int', 'wis', 'cha']:
                if key in char and char[key] == parameter:
                    del char[key]
            char[tag[:3]] = parameter
        except ValueError:
            await ctx.send('That is not a valid choice')
            return


@bot.command()
async def setskills(ctx, skill=None, *args):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select a skill yet, call !new first')
        return
    if None in [incomplete_characters[ctx.author].get('class', None),
                incomplete_characters[ctx.author].get('race', None),
                incomplete_characters[ctx.author].get('background', None)]:
        await ctx.send('You must have a Race, Class, and Background, before you can choose your additional skills')
        return
    if skill == 'reset':
        del incomplete_characters[ctx.author]['skills']
        char = incomplete_characters[ctx.author]
        char['skills_remaining'] = char['player_class'].skills_qty
        return
    if incomplete_characters[ctx.author]['skills_remaining'] == 0:
        await ctx.send('You have already chosen your full allotment of skills, call "!set_skill reset", without the '
                       'quotes, to clear your current choices and pick again')
        return

    player_class = incomplete_characters[ctx.author]['player_class']
    player_background = incomplete_characters[ctx.author]['player_background']
    skills = player_class.skills.difference(player_background.SKILLS)
    skills = set([x.__name__.capitalize() for x in skills])
    skills = skills.difference(incomplete_characters[ctx.author].get('skills', set()))
    skills = sorted(list(skills))
    if skill is not None:
        for skill in [skill] + list(args):
            try:
                skill = int(skill)
                if not 0 <= skill <= len(skills):
                    await ctx.send(str(skill) + ' is not a valid choice')
                    return
                skill = skills[skill]
            except ValueError:
                match = re.search(skill, ' '.join(skills), re.IGNORECASE)
                if not match:
                    await ctx.send(skill + ' is not a valid choice')
                    return
                skill = match.group()
            try:
                incomplete_characters[ctx.author]['skills'].add(skill)
            except KeyError:
                incomplete_characters[ctx.author]['skills'] = set()
                incomplete_characters[ctx.author]['skills'].add(skill)
            incomplete_characters[ctx.author]['skills_remaining'] -= 1
    else:
        embed = discord.Embed(title='Skills',
                              description='Available skills not already provided by choice or backgrounds')
        number = -1
        for skill in skills:
            number += 1
            embed.add_field(name=str(number), value=skill)

        await ctx.send(embed=embed)
        await ctx.send(content='You may select a skill with the command !set_skill <choice>, where choice is either '
                               'the number, or name of the skill you want, it is not case sensitive')


@bot.command()
async def setage(ctx, age=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select an age yet, call !new first')
        return
    if not incomplete_characters[ctx.author].get('race', None):
        await ctx.send('You must have a Race before you can set your age')
        return
    if age == 'reset':
        del incomplete_characters[ctx.author]['age']
        return
    low, high = incomplete_characters[ctx.author]['player_race'].age
    if age is not None:
        try:
            age = int(age)
            if not 0 <= age <= len(ages) and not low <= age <= high:
                await ctx.send('That is not a valid choice, the valid range is %d - %d' % (low, high))
                return
        except ValueError:
            match = re.search(age, ' '.join(ages), re.IGNORECASE)
            if not match:
                await ctx.send('That is not a valid choice')
                return
            age = match.group()
            age = ages.index(age)
        if age < low:
            low, high = incomplete_characters[ctx.author]['player_race'].age
            incomplete_characters[ctx.author]['age'] = dnd5e_interactions.get_value_from_curve(age, low, high)
        else:
            incomplete_characters[ctx.author]['age'] = age
        return
    else:
        embed = discord.Embed(title='Age categories',
                              description='You can set your age directly within the range of %d - %d.  Or you '
                                          'can select a category and an age will be randomly chosen from there' %
                                          (low, high))
        number = -1
        for age in ages:
            number += 1
            embed.add_field(name=str(number), value=age)

        await ctx.send(embed=embed)
        await ctx.send(content='You may select an age range with the command !set_age <choice>, where choice is either '
                               'the age you want, or the number or name of the age range you want - not case sensitive')


@bot.command()
async def setheight(ctx, height=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select an height yet, call !new first')
        return
    if not incomplete_characters[ctx.author].get('race', None):
        await ctx.send('You must have a Race before you can choose your height range')
        return
    if height == 'reset':
        del incomplete_characters[ctx.author]['height']
        return
    low, high = incomplete_characters[ctx.author]['player_race'].height
    if height is not None:
        try:
            height = int(height)
            if not 0 <= height <= len(heights) and not low <= height <= high:
                await ctx.send('That is not a valid choice, the valid range is %d - %d' % (low, high))
                return
        except ValueError:
            match = re.search(height, ' '.join(heights), re.IGNORECASE)
            if not match:
                await ctx.send('That is not a valid choice')
                return
            height = match.group()
            height = heights.index(height)
        if height < low:
            low, high = incomplete_characters[ctx.author]['player_race'].height
            incomplete_characters[ctx.author]['height'] = dnd5e_interactions.get_value_from_curve(height, low, high)
        else:
            incomplete_characters[ctx.author]['height'] = height
        return
    else:
        embed = discord.Embed(title='Height categories',
                              description='You can set your height directly within the range of %d - %d.  Or you '
                                          'can select a category and an height will be randomly chosen from there' %
                                          (low, high))
        number = -1
        for height in heights:
            number += 1
            embed.add_field(name=str(number), value=height)

        await ctx.send(embed=embed)
        await ctx.send(content='You may select a height range with the command !set_height <choice>, where choice is '
                               'the height you want, or the number or name of the height range you want - not case '
                               'sensitive')

@bot.command()
async def setweight(ctx, weight=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select an height yet, call !new first')
        return
    if not incomplete_characters[ctx.author].get('race', None):
        await ctx.send('You must have a Race before you can choose your height range')
        return
    if weight == 'reset':
        del incomplete_characters[ctx.author]['weight']
        return
    low, high = incomplete_characters[ctx.author]['player_race'].weight
    if weight is not None:
        try:
            weight = int(weight)
            if not 0 <= weight <= len(weights) and not low <= weight <= high:
                await ctx.send('That is not a valid choice, the valid range is %d - %d' % (low, high))
                return
        except ValueError:
            match = re.search(weight, ' '.join(weights), re.IGNORECASE)
            if not match:
                await ctx.send('That is not a valid choice')
                return
            weight = match.group()
            weight = weights.index(weight)
        if weight < low:
            low, high = incomplete_characters[ctx.author]['player_race'].weight
            incomplete_characters[ctx.author]['weight'] = dnd5e_interactions.get_value_from_curve(weight, low, high)
        else:
            incomplete_characters[ctx.author]['weight'] = weight
        return
    else:
        embed = discord.Embed(title='Weight categories',
                              description='You can set your weight directly within the range of %d - %d.  Or you '
                                          'can select a category and a weight will be randomly chosen from there' %
                                          (low, high))
        number = -1
        for weight in weights:
            number += 1
            embed.add_field(name=str(number), value=weight)

        await ctx.send(embed=embed)
        await ctx.send(content='You may select a weight range with the command !set_weight <choice>, where choice is '
                               'the weight you want, or the number or name of the weight range you want - not case '
                               'sensitive')


# used for one line character creation
@bot.command()
async def setnew(ctx, race=None, klass=None, background=None):
    if ctx.author not in incomplete_characters:
        incomplete_characters[ctx.author] = {}
    if race:
        match = re.search(race, ' '.join(races_all), re.IGNORECASE)
        if not match:
            await ctx.send(race + ' is not a valid choice')
            return
        race = match.group()
        incomplete_characters[ctx.author]['race'] = race
        incomplete_characters[ctx.author]['player_race'] = getattr(dnd5e_races, race.replace(' ', ''))
    if background:
        match = re.search(background, ' '.join(backgrounds_all), re.IGNORECASE)
        if not match:
            await ctx.send(background + ' is not a valid choice')
            return
        background = match.group()
        incomplete_characters[ctx.author]['background'] = background.capitalize()
        incomplete_characters[ctx.author]['player_background'] = getattr(enums.BACKGROUNDS, background.upper())
    if klass:
        match = re.search(klass, ' '.join(classes_all), re.IGNORECASE)
        if not match:
            await ctx.send(klass + ' is not a valid choice')
            return
        klass = match.group()
        incomplete_characters[ctx.author]['class'] = klass
        player_class = getattr(dnd5e_classes, klass)
        incomplete_characters[ctx.author]['skills_remaining'] = player_class.skills_qty
        incomplete_characters[ctx.author]['player_class'] = player_class


@bot.command()
async def setbackground(ctx, background=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select a background yet, call !new first')
        return
    if background == 'reset':
        del incomplete_characters[ctx.author]['background']
        return
    if background is not None:
        try:
            background = int(background)
            if not 0 <= background <= len(backgrounds_all):
                await ctx.send('That is not a valid choice')
                return
            background = backgrounds_all[background]
        except ValueError:
            match = re.search(background, ' '.join(backgrounds_all), re.IGNORECASE)
            if not match:
                await ctx.send('That is not a valid choice')
                return
            background = match.group()
        incomplete_characters[ctx.author]['background'] = background.capitalize()
        incomplete_characters[ctx.author]['player_background'] = getattr(enums.BACKGROUNDS, background.upper())
        return
    else:
        embed_full = discord.Embed(title='Fully Implemented Backgrounds',
                                   description='all referenced functions are implemented for these backgrounds')
        number = -1
        for background in backgrounds_full:
            number += 1
            embed_full.add_field(name=str(number), value=background)

        content = ''
        embed_partial = None
        embed_none = None
        if partial or none:
            content = 'Choosing an incomplete or non-implemented backgrounds should be harmless, but currently ' \
                      'provides little to no benefit beyond cosmetic differences'
            if backgrounds_partial:
                embed_partial = discord.Embed(title='Partially Implemented backgrounds',
                                              description='Some of the referenced functions for these backgrounds have '
                                                          'been implemented')
                for background in backgrounds_partial:
                    number += 1
                    embed_partial.add_field(name=str(number), value=background)
            if backgrounds_none:
                embed_none = discord.Embed(title='Not-Implemented Backgrounds',
                                           description='None of the functions referenced by these backgrounds are '
                                                       'currently implemented')
                for background in backgrounds_none:
                    number += 1
                    embed_none.add_field(name=str(number), value=background)

        await ctx.send(embed=embed_full)
        if backgrounds_partial:
            await ctx.send(content=content, embed=embed_partial)
        if backgrounds_none:
            await ctx.send(content=content, embed=embed_none)
        await ctx.send(content='You may select a race with the command !set_background <choice>, where choice is '
                               'either the number, or name of the background you want, it is not case sensitive')


@bot.command()
async def setrace(ctx, race=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select a race yet, call !new first')
        return
    if race == 'reset':
        del incomplete_characters[ctx.author]['race']
        return
    if race is not None:
        try:
            race = int(race)
            if not 0 <= race <= len(races_all):
                await ctx.send('That is not a valid choice')
                return
            race = races_all[race]
        except ValueError:
            match = re.search(race, ' '.join(races_all), re.IGNORECASE)
            if not match:
                await ctx.send('That is not a valid choice')
                return
            race = match.group()
        incomplete_characters[ctx.author]['race'] = race
        race = getattr(dnd5e_races, race.replace(' ', ''))
        incomplete_characters[ctx.author]['player_race'] = race
        if 'age' in incomplete_characters[ctx.author] and \
            not race.age[0] <= incomplete_characters[ctx.author]['age'] <= race.age[1]:
            await ctx.send(str(incomplete_characters[ctx.author]['age']) + ' is out of range for a ' + race.name +
                           ' age, clearing the value')
            del incomplete_characters[ctx.author]['age']
        if 'height' in incomplete_characters[ctx.author] and \
            not race.height[0] <= incomplete_characters[ctx.author]['height'] <= race.height[1]:
            await ctx.send(str(incomplete_characters[ctx.author]['height']) + ' is out of range for a ' + race.name +
                           ' height, clearing the value')
            del incomplete_characters[ctx.author]['height']
        if 'weight' in incomplete_characters[ctx.author] and \
            not race.weight[0] <= incomplete_characters[ctx.author]['weight'] <= race.weight[1]:
            await ctx.send(str(incomplete_characters[ctx.author]['weight']) + ' is out of range for a ' + race.name +
                           ' weight, clearing the value')
            del incomplete_characters[ctx.author]['weight']

        return
    else:
        embed_full = discord.Embed(title='Fully Implemented Races',
                                   description='all referenced functions are implemented for these races')
        number = -1
        for race in races_full:
            number += 1
            embed_full.add_field(name=str(number), value=race)

        content = ''
        embed_partial = None
        embed_none = None
        if partial or none:
            content = 'Choosing an incomplete or non-implemented race should be harmless, but currently provides ' \
                     'little to no benefit beyond cosmetic differences'
            if races_partial:
                embed_partial = discord.Embed(title='Partially Implemented Races',
                                              description='Some of the referenced functions for these races have been '
                                                          'implemented')
                for race in races_partial:
                    number += 1
                    embed_partial.add_field(name=str(number), value=race)
            if races_none:
                embed_none = discord.Embed(title='Not-Implemented Races',
                                           description='None of the functions referenced by these races are currently '
                                                       'implemented')
                for race in races_none:
                    number += 1
                    embed_none.add_field(name=str(number), value=race)

        await ctx.send(embed=embed_full)
        if races_partial:
            await ctx.send(content=content, embed=embed_partial)
        if races_none:
            await ctx.send(content=content, embed=embed_none)
        await ctx.send(content='You may select a race with the command !set_race <choice>, where choice is either the '
                               'number, or name of the race you want, it is not case sensitive')


@bot.command()
async def setclass(ctx, klass=None):
    if ctx.author not in incomplete_characters:
        await ctx.send('You cannot select a class yet, call !new first')
        return
    if klass == 'reset':
        del incomplete_characters[ctx.author]['class']
        return
    if klass is not None:
        try:
            klass = int(klass)
            if not 0 <= klass <= len(classes_all):
                await ctx.send('That is not a valid choice')
                return
            klass = classes_all[klass]
        except ValueError:
            match = re.search(klass, ' '.join(classes_all), re.IGNORECASE)
            if not match:
                await ctx.send('That is not a valid choice')
                return
            klass = match.group()
        incomplete_characters[ctx.author]['class'] = klass
        player_class = getattr(dnd5e_classes, klass)
        incomplete_characters[ctx.author]['skills_remaining'] = player_class.skills_qty
        incomplete_characters[ctx.author]['player_class'] = player_class
        return
    else:
        embed_full = discord.Embed(title='Fully Implemented Classes',
                                   description='all referenced functions are implemented for these classes')
        number = -1
        for klass in classes_full:
            number += 1
            embed_full.add_field(name=str(number), value=klass)

        content = ''
        embed_partial = None
        embed_none = None
        if partial or none:
            content = 'Choosing an incomplete or non-implemented race should be harmless, but currently provides ' \
                     'little to no benefit beyond cosmetic differences'
            if classes_partial:
                embed_partial = discord.Embed(title='Partially Implemented Classes',
                                              description='Some of the referenced functions for these classes have '
                                                          'been implemented')
                for klass in classes_partial:
                    number += 1
                    embed_partial.add_field(name=str(number), value=klass)
            if classes_none:
                embed_none = discord.Embed(title='Not-Implemented Classes',
                                           description='None of the functions referenced by these classes are '
                                                       'currently implemented')
                for klass in classes_none:
                    number += 1
                    embed_none.add_field(name=str(number), value=klass)

        await ctx.send(embed=embed_full)
        if classes_partial:
            await ctx.send(content=content, embed=embed_partial)
        if classes_none:
            await ctx.send(content=content, embed=embed_none)
        await ctx.send(content='You may select a race with the command !set_class <choice>, where choice is either the '
                               'number, or name of the race you want, it is not case sensitive')


bot.run(token.token())


