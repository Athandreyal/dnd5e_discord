import discord
from discord.ext import commands
import dnd5e_enums as enums
import dnd5e_interactions
import dnd5e_races
import dnd5e_classes
from dnd5e_character_sheet import CharacterSheet
import dnd5e_weaponry
import dnd5e_armor
import re
import dnd5e_database

debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug

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


class character_creation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # for creating new characters
    @commands.command(pass_context=True)
    async def new(self, ctx, parameter=None):
        """Starts the character creation process
        prints the temporary player data,
            empty for freshly initialised characters
            populated with data as the user configures their new character
        !new <parameter>
        with no parameter, it inits a new character, or prints out the current progress
        with parameter,
          if parameter is finish
              it finalises the character if it is complete, prints state if not complete
          if parameter is reset
              not implemented, going ato absorb the abortnew function here in time
        """
        author = ctx.author.mention  # whoever called this instance of new
        author_name = ctx.author.name
        embed = discord.Embed(title=author_name + ' : Character Creation')
        char = incomplete_characters.get(author, None)
        if char is None:
            incomplete_characters[author] = {}
            char = incomplete_characters[author]
            char['array'] = default_ability_array.copy()
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
            height = '%d\' %d"' % (height // 12, height % 12)
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
        complete = char is not None and None not in [char.get('race', None), char.get('class', None),
                                                     char.get('name', None), char.get('background', None),
                                                     char.get('skills', None), char.get('skills_remaining', None),
                                                     char.get('age', None), char.get('height', None),
                                                     char.get('weight', None), char.get('str', None),
                                                     char.get('con', None), char.get('dex', None),
                                                     char.get('int', None), char.get('wis', None),
                                                     char.get('cha', None)] and char.get('skills_remaining', None) == 0
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
                char = CharacterSheet(name=char['name'],
                                      age=char['age'],
                                      height=char['height'],
                                      weight=char['weight'],
                                      uid=ctx.author.mention,
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
                dnd5e_database.set_player(char.to_dict())
                del incomplete_characters[author]
                return
            else:
                await ctx.send('Character creation is not yet complete')

        await ctx.send(embed=embed, content='Each field has a corresponding set command to configure it. For example, '
                                            'you can set your race with !setrace, or Age with !setage\n\ncall !new '
                                            'again to see current progress, or finish a previous character '
                                            'build !setnew finish\n\nAll commands acknowledge the parameter \'reset\' '
                                            'which will drop your current selections.\n\nWhen you are satisfied, '
                                            'call "!new finish", and the character will be written to the database and '
                                            'persist across interactions and bot resets')

    @commands.command(pass_context=True)
    async def abortnew(self, ctx):
        """used to cancel creating a new character
        !abortnew
        wipes out the temporary data for an in progress character
        planned to be absorbed by '!new reset' in the relatively near future """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You do not have an incomplete character to abort creating')
        del incomplete_characters[ctx.author.mention]
        await ctx.send('incomplete character creation aborted')

    @commands.command(pass_context=True)
    async def setname(self, ctx, name=None):
        """sets the new character's name
        !setname <name>
        if the name has spaces, wrap it in double quotes, ie
            !setname "two names"
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot set a name yet, call !new first')
            return
        if name:
            incomplete_characters[ctx.author.mention]['name'] = name
        else:
            await ctx.send('a name is required.')

    @commands.command(pass_context=True)
    async def setstr(self, ctx, strength=None):
        """sets the new character's strength
        requires that you have set a class before it accepts input
        !setstr <val>
        assigns a character initialisation value from the default character array (15 14 13 12 10 8) which is
        currently unassigned to another stat to Strength
        """
        await self.set_scdiwc(ctx, 'strength', strength)

    @commands.command(pass_context=True)
    async def setcon(self, ctx, constitution=None):
        """sets the new character's constitution
        requires that you have set a class before it accepts input
        !setcon <val>
        assigns a character initialisation value from the default character array (15 14 13 12 10 8) which is
        currently unassigned to another stat to Constitution
        """
        await self.set_scdiwc(ctx, 'constitution', constitution)

    @commands.command(pass_context=True)
    async def setdex(self, ctx, dexterity=None):
        """sets the new character's dexterity
        requires that you have set a class before it accepts input
        !setdex <val>
        assigns a character initialisation value from the default character array (15 14 13 12 10 8) which is
        currently unassigned to another stat to Dexterity
        """
        await self.set_scdiwc(ctx, 'dexterity', dexterity)

    @commands.command(pass_context=True)
    async def setint(self, ctx, intelligence=None):
        """sets the new character's intelligence
        requires that you have set a class before it accepts input
        !setint <val>
        assigns a character initialisation value from the default character array (15 14 13 12 10 8) which is
        currently unassigned to another stat to intelligence
        """
        await self.set_scdiwc(ctx, 'intelligence', intelligence)

    @commands.command(pass_context=True)
    async def setwis(self, ctx, wisdom=None):
        """sets the new character's wisdom
        requires that you have set a class before it accepts input
        !setwis <val>
        assigns a character initialisation value from the default character array (15 14 13 12 10 8) which is
        currently unassigned to another stat to wisdom
        """
        await self.set_scdiwc(ctx, 'wisdom', wisdom)

    @commands.command(pass_context=True)
    async def setcha(self, ctx, charisma=None):
        """sets the new character's charisma
        requires that you have set a class before it accepts input
        !setcha <val>
        assigns a character initialisation value from the default character array (15 14 13 12 10 8) which is
        currently unassigned to another stat to charisma
        """
        await self.set_scdiwc(ctx, 'charisma', charisma)

    @commands.command(pass_context=True)
    async def setability(self, ctx, *args):
        """sets the new character's ability scores en-masse
        requires that you have set a class before it accepts input
        !setability <str> <con> <dex> <int> <wis> <cha>
        assigns up to 6 character initialisation values from the default character array
        (15 14 13 12 10 8) which is currently unassigned to another stat to charisma

        If a value is used for a second time, the first is dropped, and the second is applied.
        """
        # for key in ['str', 'con', 'dex', 'int', 'wis', 'cha']:
        fields = ['str', 'con', 'dex', 'int', 'wis', 'cha']
        char = incomplete_characters[ctx.author.mention]
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot set an attribute yet, call !new first')
            return
        if not char.get('class', None):
            await ctx.send('You must have a Class before you can choose your attributes')
            return
        if 'reset' in args:
            for key in fields:
                del incomplete_characters[ctx.author.mention][key]
                char['array'] = default_ability_array.copy()
            return

#        array = incomplete_characters[ctx.author.mention]['array']
        for i in range(len(args)):
            key = fields[i]
            try:
                for j in range(len(fields)):
                    print(fields[j], fields[j] in char, args[i],
                          None if not fields[j] in char else char[fields[j]],
                          None if not fields[j] in char else char[fields[j]] == int(args[i]))
                    if fields[j] in char and char[fields[j]] and int(args[i]) == char[fields[j]]:
                        del incomplete_characters[ctx.author.mention][fields[j]]
                        char['array'].append(int(args[i]))
                val = int(args[i])
            except ValueError:
                await ctx.send('%s is not a valid choice' % args[i])
                debug('args[i] is not int')
                return
            if val not in char['array']:
                await ctx.send('%s is not a valid choice' % args[i])
                debug('args[i] not in array')
                return
            char['array'].remove(val)
            char[key] = val

    @staticmethod
    async def set_scdiwc(ctx, tag, parameter):
        """the set<tag> methods that set abilities individually call this method to do their work"""
        char = incomplete_characters[ctx.author.mention]
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot set an attribute yet, call !new first')
            return
        if not char.get('class', None):
            await ctx.send('You must have a Class before you can choose your attributes')
            return
        if parameter == 'reset':
            char['array'] = char[tag[:3]]
            del incomplete_characters[ctx.author.mention][tag[:3]]
            return
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
            content = 'You can set these attributes by calling !set<tag> <value>, where tag is the three letter code '\
                      'for the attribute, such as dex for dexterity, or int for intelligence.  Value is an integer, ' \
                      'from the default ability array, which is [15, 14, 13, 12, 10, 8].  For a %s, %s are ' \
                      'suggested' % (char['class'], suggest)
            await ctx.send(embed=embed, content=content)
        else:
            try:
                parameter = int(parameter)
                if parameter not in incomplete_characters[ctx.author.mention]['array']:
                    await ctx.send('That is not a valid choice')
                    return
                for key in ['str', 'con', 'dex', 'int', 'wis', 'cha']:
                    if key in char and char[key] == parameter:
                        incomplete_characters[ctx.author.mention]['array'].append(int(char[key]))
                        del char[key]
                char[tag[:3]] = parameter
            except ValueError:
                await ctx.send('That is not a valid choice')
                return

    @commands.command(pass_context=True)
    async def setskills(self, ctx, skill=None, *args):
        """sets the new character's proficiency skills.
        requires that you have set a race, class, and background before it accepts input
        !setskills <skill1>, <skill2>, ... <skilln>
        accepts from 0 to n skills, case-insensitive
        with no skills given,
            it will print off the list of available skills, both named and numbered
        for each skill given:
            if the name, or number is one of those in the set provided, it will be assigned
            note, if using numbers, list them in descending order( 3,2,1)
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select a skill yet, call !new first')
            return
        if None in [incomplete_characters[ctx.author.mention].get('class', None),
                    incomplete_characters[ctx.author.mention].get('race', None),
                    incomplete_characters[ctx.author.mention].get('background', None)]:
            await ctx.send('You must have a Race, Class, and Background, before you can choose your additional skills')
            return
        if skill == 'reset':
            del incomplete_characters[ctx.author.mention]['skills']
            char = incomplete_characters[ctx.author.mention]
            char['skills_remaining'] = char['player_class'].skills_qty
            return
        if incomplete_characters[ctx.author.mention]['skills_remaining'] == 0:
            await ctx.send('You have already chosen your full allotment of skills, call "!setskill reset", without '
                           'the quotes, to clear your current choices and pick again')
            return

        player_class = incomplete_characters[ctx.author.mention]['player_class']
        player_background = incomplete_characters[ctx.author.mention]['player_background']
        skills = player_class.skills.difference(player_background.SKILLS)
        skills = set([x.__name__.capitalize() for x in skills])
        skills = skills.difference(incomplete_characters[ctx.author.mention].get('skills', set()))
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
                        # noinspection PyTypeChecker
                        await ctx.send(skill + ' is not a valid choice')
                        return
                    skill = match.group()
                try:
                    incomplete_characters[ctx.author.mention]['skills'].add(skill)
                except KeyError:
                    incomplete_characters[ctx.author.mention]['skills'] = set()
                    incomplete_characters[ctx.author.mention]['skills'].add(skill)
                incomplete_characters[ctx.author.mention]['skills_remaining'] -= 1
        else:
            embed = discord.Embed(title='Skills',
                                  description='Available skills not already provided by choice or backgrounds')
            number = -1
            for skill in skills:
                number += 1
                embed.add_field(name=str(number), value=skill)

            await ctx.send(embed=embed)
            await ctx.send(content='You may select a skill with the command !setskill <choice>, where choice is '
                                   'either the number, or name of the skill you want, it is not case sensitive')

    @commands.command(pass_context=True)
    async def setage(self, ctx, age=None):
        """sets the new character's age
        requires that you have set a race before it accepts input
        !setage <parameter>
        parameter can be one of a category value, category name, or direct age value.
        ages are bound to those value for the given race, categories adjust accordingly
        for <parameter>
            integers with value 0-5 are considered to be categorical age assignments
            text is considered to be categorical and must match on of those given, case-insensitive
            integers with value where min <= value <= max, the age is assigned as given
        if no parameter is given, the categories will be printed, and the valid range shown as well
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select an age yet, call !new first')
            return
        if not incomplete_characters[ctx.author.mention].get('race', None):
            await ctx.send('You must have a Race before you can set your age')
            return
        if age == 'reset':
            del incomplete_characters[ctx.author.mention]['age']
            return
        low, high = incomplete_characters[ctx.author.mention]['player_race'].age
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
                low, high = incomplete_characters[ctx.author.mention]['player_race'].age
                incomplete_characters[ctx.author.mention]['age'] = dnd5e_interactions.get_value_from_curve(age, low, high)
            else:
                incomplete_characters[ctx.author.mention]['age'] = age
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
            await ctx.send(content='You may select an age range with the command !setage <choice>, where choice is '
                                   'either the age you want, or the number or name of the age range you want - not '
                                   'case sensitive')

    @commands.command(pass_context=True)
    async def setheight(self, ctx, height=None):
        """sets the new character's height
        requires that you have set a race before it accepts input
        !setheight <parameter>
        parameter can be one of a category value, category name, or direct height value, in inches.
        heights are bound to those value for the given race, categories adjust accordingly
        for <parameter>
            integers with value 0-5 are considered to be categorical height assignments
            text is considered to be categorical and must match on of those given, case-insensitive
            integers with value where min <= value <= max, the height is assigned as given
        if no parameter is given, the categories will be printed, and the valid range shown as well
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select an height yet, call !new first')
            return
        if not incomplete_characters[ctx.author.mention].get('race', None):
            await ctx.send('You must have a Race before you can choose your height range')
            return
        if height == 'reset':
            del incomplete_characters[ctx.author.mention]['height']
            return
        low, high = incomplete_characters[ctx.author.mention]['player_race'].height
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
                low, high = incomplete_characters[ctx.author.mention]['player_race'].height
                incomplete_characters[ctx.author.mention]['height'] = dnd5e_interactions.get_value_from_curve(height, low, high)
            else:
                incomplete_characters[ctx.author.mention]['height'] = height
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
            await ctx.send(content='You may select a height range with the command !setheight <choice>, where choice '
                                   'is the height you want, or the number or name of the height range you want - not '
                                   'case sensitive')

    @commands.command(pass_context=True)
    async def setweight(self, ctx, weight=None):
        """sets the new character's weight
        requires that you have set a race before it accepts input
        !setweight <parameter>
        parameter can be one of a category value, category name, or direct weight value, in lbs.
        weights are bound to those value for the given race, categories adjust accordingly
        for <parameter>
            integers with value 0-5 are considered to be categorical weight assignments
            text is considered to be categorical and must match on of those given, case-insensitive
            integers with value where min <= value <= max, the weight is assigned as given
        if no parameter is given, the categories will be printed, and the valid range shown as well
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select an height yet, call !new first')
            return
        if not incomplete_characters[ctx.author.mention].get('race', None):
            await ctx.send('You must have a Race before you can choose your height range')
            return
        if weight == 'reset':
            del incomplete_characters[ctx.author.mention]['weight']
            return
        low, high = incomplete_characters[ctx.author.mention]['player_race'].weight
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
                low, high = incomplete_characters[ctx.author.mention]['player_race'].weight
                incomplete_characters[ctx.author.mention]['weight'] = dnd5e_interactions.get_value_from_curve(weight, low, high)
            else:
                incomplete_characters[ctx.author.mention]['weight'] = weight
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
            await ctx.send(content='You may select a weight range with the command !setweight <choice>, where choice '
                                   'is the weight you want, or the number or name of the weight range you want - not '
                                   'case sensitive')

    # used for one line character creation
    @commands.command(pass_context=True)
    async def setnew(self, ctx, race=None, klass=None, background=None):
        """shortcut for creating new characters.
        !setnew <race> <class> <background>
        accepts from 0 to 3 arguments, doing nothing if no arguments are given
        expects the text label for each of race, class, and background, case insensitive.
        It will assign those parameters which match valid options, and note which ones do not
        """
        if ctx.author.mention not in incomplete_characters:
            incomplete_characters[ctx.author.mention] = {}
            incomplete_characters[ctx.author.mention]['array'] = default_ability_array.copy()
        if race:
            match = re.search(race, ' '.join(races_all), re.IGNORECASE)
            if not match:
                await ctx.send(race + ' is not a valid choice')
            else:
                race = match.group()
                incomplete_characters[ctx.author.mention]['race'] = race
                incomplete_characters[ctx.author.mention]['player_race'] = getattr(dnd5e_races, race.replace(' ', ''))
        if klass:
            match = re.search(klass, ' '.join(classes_all), re.IGNORECASE)
            if not match:
                await ctx.send(klass + ' is not a valid choice')
            else:
                klass = match.group()
                incomplete_characters[ctx.author.mention]['class'] = klass
                player_class = getattr(dnd5e_classes, klass)
                incomplete_characters[ctx.author.mention]['skills_remaining'] = player_class.skills_qty
                incomplete_characters[ctx.author.mention]['player_class'] = player_class
        if background:
            match = re.search(background, ' '.join(backgrounds_all), re.IGNORECASE)
            if not match:
                await ctx.send(background + ' is not a valid choice')
            else:
                background = match.group()
                incomplete_characters[ctx.author.mention]['background'] = background.capitalize()
                incomplete_characters[ctx.author.mention]['player_background'] = getattr(enums.BACKGROUNDS, background.upper())

    @commands.command(pass_context=True)
    async def setbackground(self, ctx, background=None):
        """sets the new character's background
        !setbackground <background>
        if no background is given, it prints off the valid choices, both text and numerical labels
        if background is given
            if numerical, it must be an integer, and it must be one of the options given
            if text, it is case insensitive, it must be one of the options given, use quotes if it has spaces
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select a background yet, call !new first')
            return
        if background == 'reset':
            del incomplete_characters[ctx.author.mention]['background']
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
            incomplete_characters[ctx.author.mention]['background'] = background.capitalize()
            incomplete_characters[ctx.author.mention]['player_background'] = getattr(enums.BACKGROUNDS, background.upper())
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
                                                  description='Some of the referenced functions for these backgrounds '
                                                              'have been implemented')
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
            await ctx.send(content='You may select a background with the command !setbackground <choice>, where choice '
                                   'is either the number, or name of the background you want, it is not case sensitive')

    @commands.command(pass_context=True)
    async def setrace(self, ctx, race=None):
        """sets the new character's race
        !setrace <race>
        if no race is given, it prints off the valid choices, both text and numerical labels
        if race is given
            if numerical, it must be an integer, and it must be one of the options given
            if text, it is case insensitive, it must be one of the options given, use quotes if it has spaces
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select a race yet, call !new first')
            return
        if race == 'reset':
            del incomplete_characters[ctx.author.mention]['race']
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
            incomplete_characters[ctx.author.mention]['race'] = race
            race = getattr(dnd5e_races, race.replace(' ', ''))
            incomplete_characters[ctx.author.mention]['player_race'] = race
            if 'age' in incomplete_characters[ctx.author.mention] and \
                    not race.age[0] <= incomplete_characters[ctx.author.mention]['age'] <= race.age[1]:
                await ctx.send(str(incomplete_characters[ctx.author.mention]['age']) + ' is out of range for a ' +
                               race.name + ' age, clearing the value')
                del incomplete_characters[ctx.author.mention]['age']
            if 'height' in incomplete_characters[ctx.author.mention] and \
                    not race.height[0] <= incomplete_characters[ctx.author.mention]['height'] <= race.height[1]:
                await ctx.send(str(incomplete_characters[ctx.author.mention]['height']) + ' is out of range for a ' +
                               race.name + ' height, clearing the value')
                del incomplete_characters[ctx.author.mention]['height']
            if 'weight' in incomplete_characters[ctx.author.mention] and \
                    not race.weight[0] <= incomplete_characters[ctx.author.mention]['weight'] <= race.weight[1]:
                await ctx.send(str(incomplete_characters[ctx.author.mention]['weight']) + ' is out of range for a ' +
                               race.name + ' weight, clearing the value')
                del incomplete_characters[ctx.author.mention]['weight']

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
                                                  description='Some of the referenced functions for these races have '
                                                              'been implemented')
                    for race in races_partial:
                        number += 1
                        embed_partial.add_field(name=str(number), value=race)
                if races_none:
                    embed_none = discord.Embed(title='Not-Implemented Races',
                                               description='None of the functions referenced by these races are '
                                                           'currently implemented')
                    for race in races_none:
                        number += 1
                        embed_none.add_field(name=str(number), value=race)

            await ctx.send(embed=embed_full)
            if races_partial:
                await ctx.send(content=content, embed=embed_partial)
            if races_none:
                await ctx.send(content=content, embed=embed_none)
            await ctx.send(content='You may select a race with the command !setrace <choice>, where choice is either '
                                   'the number, or name of the race you want, it is not case sensitive')

    @commands.command(pass_context=True)
    async def setclass(self, ctx, klass=None):
        """sets the new character's class
        !setclass <class>
        if no class is given, it prints off the valid choices, both text and numerical labels
        if class is given
            if numerical, it must be an integer, and it must be one of the options given
            if text, it is case insensitive, it must be one of the options given, use quotes if it has spaces
        """
        if ctx.author.mention not in incomplete_characters:
            await ctx.send('You cannot select a class yet, call !new first')
            return
        if klass == 'reset':
            del incomplete_characters[ctx.author.mention]['class']
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
            incomplete_characters[ctx.author.mention]['class'] = klass
            player_class = getattr(dnd5e_classes, klass)
            incomplete_characters[ctx.author.mention]['skills_remaining'] = player_class.skills_qty
            incomplete_characters[ctx.author.mention]['player_class'] = player_class
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
            await ctx.send(content='You may select a race with the command !setclass <choice>, where choice is either'
                                   ' the number, or name of the race you want, it is not case sensitive')


def setup(bot):
    bot.add_cog(character_creation(bot))
