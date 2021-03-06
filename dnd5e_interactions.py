from dnd5e_misc import getint as getint
from dnd5e_misc import getstr as getstr
from dnd5e_misc import Die as Die
import dnd5e_enums as enums
import inspect
import dnd5e_races
import dnd5e_classes
import dnd5e_enums
import dnd5e_weaponry as weaponry
import dnd5e_armor as armor

# todo: database table: player UID and character names, and their specific UIDs
# todo: database table: character UID and their specific init data, equipment UID, and inventory UID
# todo: database table: equipment, with equipment UID, gear slots, and item UID's and data to regenerate any given item
# todo: database table: inventory, with inventory UID, and item references and data to regenerate any given item

debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


def new_user(ver, release_title):
    s = '''
    Welcome to the D&D 5.e Discord Bot ver ''' + ver + ''' ''' + release_title + '''
    
    You'll have to forgive the sparse content, the critical systems much of that depends on do not yet exist.
    
    Progress is ongoing, and not exactly predictable, this developer is prone to valve time, which is to say, 
    releases happen then they're 'ready', which could be in a few moments, or a few weeks, roll the dice, 
    its guess is as good as yours or mine.
    
    The code has been written to try and indicate what is flagged as not yet ready, and if I've done my job right, 
    will indicate that before you choose, though choosing them should not be an issue.  Failure to flag items as 
    incomplete is a thing, so bugs and outright crashes will be a thing for some time to come.
    
    You will need a willingness to accept that you have to just ignore the in-progress state of things until they 
    start to clean up more and more and I can remove this message in favour of more isolated remarks where relevant.
    
    Traits were written to trigger automatically initially, so there may be some un-noticed flakyness in allowing 
    the player to intercede in the process. 
    
    The command '!new' will get you started with creating a character.
    '''
    return s


def get_value_from_curve(segment, minimum, maximum):
    # todo: put this on a normal distribution curve at some point
    segments = [(0, 0.023), (0.023, 0.159), (0.159, 0.5), (0.5, 0.841), (0.841, 0.977), (0.977, 1)]
    segment = segments[segment]
    _range = maximum - minimum
    _min, _max = int(_range*segment[0]+0.5), int(_range*segment[1]+0.5)
    die = Die(1, _max-_min)
    result = minimum + _min + die.roll()
    return result


def getAbility(player_class):
    default = [15, 14, 13, 12, 10, 8]
    print('you will need to choose your ability stats from the default set of', default)
    print('These are to be assigned into the abilities Strength, Constitution, Dexterity, Intelligence, Wisdom, '
          'Charisma')
    print('for the', player_class.name, 'class, it is suggested to have ', end='')
    suggest = [(k, player_class.ability_suggest[k]) for k in player_class.ability_suggest.keys() if
               player_class.ability_suggest[k] is not 0]
    for ability in suggest:
        print(ability[0], '=', ability[1], end=', ')
    print('')
    abilities = enums.Ability()
    ability_list = [abilities.STR, abilities.CON, abilities.DEX, abilities.INT, abilities.WIS, abilities.CHA]
    while 0 in ability_list:
        choice = print_choices(list(player_class.ability_suggest.keys()), [], [], no_sort=True)
        debug(ability_list)
        choice = choice[getint('choose an ability to set: ', 0, len(choice) - 1)]
        debug(choice[:3].upper())
        values = [x for x in default if x not in ability_list]
        value = getint('choose a value from %s: ' % values, 0, 0, list=values)
        abilities.__setattr__(choice[:3].upper(), value)
        ability_list = [abilities.STR, abilities.CON, abilities.DEX, abilities.INT, abilities.WIS, abilities.CHA]
    abilities.update_mods()
    return abilities


def new():
    s = '''
    Character creation 101.  You will be given the chance to choose a name, age range, height range, weight range, 
    race, class, background, and starting gear.
    
    Name and age range are essentially just flavour at current.
    
    Height and weight ranges are planned to be used for such things as roof height, difficulty scaling platforms with no 
    gear, occupancy in carts/wagons, etc - distant future, for now, they are merely flavour.  
    
    Race determines your size class, base speed, some of your default traits and default proficiencies.
    
    Class determines your leveling path, the traits you will acquire along the way, as well as your rate of gaining 
    hitpoints.
    
    Backgrounds provide a couple more proficiencies, and traits.
    
    Starting gear allows you to choose from a limited set of starting options for your character's race, class, 
    and background.  
    
    As things stand currently, there is no real choice to be had that differentiates characters.  That is to come in 
    due time as I complete more and more of the systems those elements rely on.  The systems used for applying traits is 
    not yet at full functionality, so implementation of traits is an ongoing task.   
    
    As traits are completed, races, classes, and backgrounds will be opened up for selection.
    '''
    print(s)
    name = getstr('Input your character name: ')

    age = getint('0) Youth\t1) Adolescent\t2) Young Adult\t3) Mature Adult\t4) Elderly\t5) Ancient : ', 0, 5)
    height = getint('0) Very Short\t1) Short\t2) Low Average\t3) High Average\t4) Tall\t5) Very Tall : ', 0, 5)
    weight = getint('0) Very Thin\t1) Thin\t2) Low Average\t3) High Average\t4) Stocky\t5) Very Stocky : ', 0, 5)

    uid = 1
    #    experience = 85001  # lvl 11
    experience = 1  # lvl 11
    level = 0
    unspent_pts = 0

    # noinspection PyTypeChecker
    full, partial, none = get_implemented_names(dnd5e_races, enums.CLASS_TRAITS.Set().union(enums.TRAIT.Set()))
    races = print_choices(full, partial, none)
    print('Choose a race from: ')
    race = races[getint('choose your race: ', 0, len(races)-1)].replace('-', '').replace('+', '').replace(' ', '')
#    debug(race.__class__.__name__)
    player_race = getattr(dnd5e_races, race)()
#    debug(player_race.name)
    age = get_value_from_curve(age, player_race.age[0], player_race.age[1])
    height = get_value_from_curve(height, player_race.height[0], player_race.height[1])
    weight = get_value_from_curve(weight, player_race.weight[0], player_race.weight[1])

    # noinspection PyTypeChecker
    full, partial, none = get_implemented_names(dnd5e_classes, enums.CLASS_TRAITS.Set().union(enums.TRAIT.Set()))
    print('Choose a class from: ')
    classes = print_choices(full, partial, none)
    klass = classes[getint('choose your class: ', 0, len(classes)-1)].replace('-', '').replace('+', '').replace(' ', '')
#    debug(klass)
    player_class = getattr(dnd5e_classes, klass)

    full, partial, none = get_implemented_names(dnd5e_enums.BACKGROUNDS,
                                                enums.SKILL.Set().union(enums.TOOLS.Set()))
#    full, partial, none = get_background_names()
    print('Choose a background from: ')
    backs = print_choices(full, partial, none)
    back = backs[getint('choose your background: ', 0, len(backs) - 1)]\
        .replace('-', '').replace('+', '').replace(' ', '')
    debug(back)
    background = getattr(dnd5e_enums.BACKGROUNDS, back.upper())
    debug(background.SKILLS)
    debug(background.TOOLS)

#    skill_choices = [x.__name__ for x in player_class.skills]
    print('the background skills are', [x.__name__ for x in background.SKILLS])
    print('the %s class provides %d from: ' % (player_class.name, player_class.skills_qty))
    skills = set()

#    player_class.skills.difference(skills)
    while len(skills) < player_class.skills_qty:
        skill_choices = print_choices([x.__name__ for x in
                                       player_class.skills.difference(skills).difference(background.SKILLS)], [], [])
        chosen = skill_choices[getint('choose a skill: ', 0, len(skill_choices) - 1)]\
            .replace('-', '').replace('+', '').replace(' ', '')
        skill = [x for x in player_class.skills if x.__name__ == chosen]
        skills.add(skill[0])
        print('you have', [x.__name__ for x in skills])
        print('you have', player_class.skills_qty - len(skills), 'left')

    debug('chosen skills', skills)
    abilities = getAbility(player_class)
    # abilities = enums.Ability(15, 13, 14, 8, 12, 10)

    hp_dice = 0
    hp_current = None
    weapon = weaponry.greataxe  # todo: implement weapons/shields/armor
    _armor = armor.breastplate_Armor  # todo: implement weapons/shields/armor
    shield = None  # todo: implement weapons/shields/armor

    # re-roll the player class
    player_class = player_class(0, ability=abilities, skills=skills, background=background)

    from dnd5e_character_sheet import CharacterSheet
    return CharacterSheet(name, age, height, weight, uid, experience, level, unspent_pts, player_race, player_class,
                          skills, background, abilities, hp_dice, hp_current, [weapon, _armor, shield], False)


async def ActionHelp(*args, **kwargs):

    choices = kwargs['choices']
    s = 'Help:\n'
    for choice in choices:
        debug(choice, choices[choice])
        try:
            h = choices[choice][2]
        except IndexError:
            h = 'No help available'
        s += '\t\t' + choice + '\n' + h + '\n'
    debug(len(s), s)
    if kwargs.get('dialogue_message', None):
        kwargs['dialogue_message'] = await kwargs['dialogue_message'].edit(content=s +
                                                                           kwargs['dialogue_message'].content +
                                                                           '\n send any message to clear the help')
        await kwargs['bot'].wait_for('message', check=kwargs['pred'])
    else:
        print(s)
    return False


async def ActionEndTurn(*args, **kwargs):
    kwargs['choices'] = dict()


# noinspection PyDefaultArgument
async def print_choices(full, partial=[], none=[], **kwargs):
    choices, s, w1, w2 = get_choices(full, partial, none, kwargs.get('no_sort', False))
    s = '\n' + s
    if w1:
        s += '\n' + w1
    if w2:
        s += '\n' + w2
    if kwargs.get('dialogue_message', None):
        kwargs['dialogue_message'] = await kwargs['dialogue_message'].edit(content=s)
    else:
        if debug() is not False:
            debug(s)
        else:
            print(s)
    return choices


# noinspection PyDefaultArgument
def get_choices(full, partial=[], none=[], no_sort=False):
    s = ''
    s2 = ''
    if no_sort:
        choices = full + partial + none
    else:
        choices = sorted(full + partial + none)
    for i, name in enumerate(choices):
        n_str = '\t%d)  %s' % (i, name)
        if len(s2 + n_str) > 80:
            s += s2 + '\n'
            s2 = ''
        s2 += n_str
    s += s2
    warn1 = ''
    warn2 = ''
    if partial:
        warn1 = 'options with the suffix -+ are partially implemented, and will not provide their full benefits'
    if none:
        warn2 = 'options with the suffix -- are not implemented at all, and will provide little to no benefits'
    return choices, s, warn1, warn2


def get_implemented_names(source, dest):
    module = source.__name__
    try:
        module = source.__module__
    except AttributeError:
        pass

    def is_implemented(obj):
        if not hasattr(obj, 'traits'):
            return False, False
        objs = obj.traits.intersection(dest)
        implemented = []
        for trait in objs:
            trait_attribs = [x for x in dir(trait)
                             if '__' not in x and x not in ['_install', '_uninstall', 'add_affector', 'remove_affector']
                             ]
            implemented.append(len(trait_attribs) > 0)
        return any(implemented), all(implemented)

    def get_implemented():
        objs = [[m[0], m[1]] for m in inspect.getmembers(source, inspect.isclass)
                if m[1].__module__ == module]
        has_no_inheritors = []
        for o in objs:
            o = o[0]
            not_inherited = True
            for o2 in objs:
                o2 = o2[0]
                if o is not o2:
                    if not_inherited:
                        not_inherited = o is not o2 \
                                        and not issubclass(getattr(source, o2), getattr(source, o))
            if not_inherited:
                has_no_inheritors.append(getattr(source, o))
        implemented_classes = []
        fully_implemented_classes = []
        not_started = []
        for obj in has_no_inheritors:
            _partial, fully = is_implemented(obj)
            if fully:
                fully_implemented_classes.append(obj)
            elif _partial:
                implemented_classes.append(obj)
            else:
                not_started.append(obj)
        return not_started, implemented_classes, fully_implemented_classes

    def split_names(names, suffix):
        new_names = []
        for name in names:
            name = name.__name__
            if name != name.upper():
                capital = 0
                for i, c in enumerate(name):
                    if c.upper() == c and i > 0:
                        capital = i
                        break
                if capital > 0:
                    name = name[:capital] + ' ' + name[capital:]
            new_names.append(name + suffix)
        return new_names

    none, partial, full = get_implemented()
    none = split_names(none, '--')
    partial = split_names(partial, '-+')
    full = split_names(full, '')
    return full, partial, none


async def get_assist_target(self, party, **kwargs):
    touching = True  # todo: confirm they are within 5ft or not
    names = [x.name for x in party if x.name is not self.name]
    await print_choices(names, **kwargs)
    if kwargs.get('dialogue_message', None):
        kwargs['dialogue_message'] = kwargs['dialogue_message'].edit(content=kwargs['dialogue_message'].content +
                                                                     'Which party member would you like to assist: ')
        choice = -1
        while choice < 0:
            choice = await kwargs['bot'].wait_for('message', check=kwargs['pred'])
            try:
                choice = int(choice.content)
                if not choice < len(party):
                    choice = -1
            except ValueError:
                pass
    else:
        choice = getint('Which party member would you like to assist: ', 0, len(party)-1)
    return [touching, party[choice]]


async def choose_weapon(weapons, auto, **kwargs):
    if not auto:
        weapons = [x for x in weapons if x is not None]
        await print_choices(weapons, **kwargs)
        debug('choose_weapon entry not auto')
        debug("kwargs['dialogue_message']", kwargs['dialogue_message'])
        if kwargs.get('dialogue_message', None):
            msg = kwargs['dialogue_message']
            kwargs['dialogue_message'] = await msg.edit(content=msg.content + '\nYour chosen weapon is? : ')
            choice = -1
            while choice < 0:
                choice = (await kwargs['bot'].wait_for('message', check=kwargs['pred'])).content
                try:
                    choice = int(choice)
                    if not choice < len(weapons):
                        debug('choice larger than weapons', choice, len(weapons))
                        choice = -1
                except ValueError:
                    debug('choice not int', choice, type(choice))
                    choice = -1
        else:
            choice = getint('Your chosen weapon is? ', 0, len(weapons)-1)
        debug('exiting choose_weapon')
        return weapons[choice]
    else:
        # find the highest damage output, and run with it.
        weapons = [x for x in weapons if x is not None]
        # todo: improve the auto weapon selection to actually consider factors, not just what is most damaging
        sorted(weapons, key=lambda x: (x.attack_die.sides//2 + 1) * x.attack_die.qty + x.bonus_damage +
                                      (x.bonus_die.sides//2 + 1 if x.bonus_die else 1) *
                                      (x.bonus_die.qty if x.bonus_die else 0), reverse=True)
        return weapons[0]


async def get_target(targets, **kwargs):
    target_list = [x.name + ' %dhp' % x.hp for x in targets]
    await print_choices(target_list, no_sort=True, **kwargs)
    if kwargs.get('dialogue_message', None):
        msg = kwargs['dialogue_message']
        kwargs['dialogue_message'] = await msg.edit(content=msg.content + '\nChoose a target: ')
        choice = -1
        while choice < 0:
            choice = await kwargs['bot'].wait_for('message', check=kwargs['pred'])
            try:
                choice = int(choice.content)
                if not choice < len(target_list):
                    choice = -1
            except ValueError:
                pass
    else:
        choice = getint('Choose a target: ', 0, len(targets)-1)
    target = targets[choice]
    return target


def verify_can_attack(choices, attack, party1, party2):
    debug(attack.num < 1, not(party1.is_able() and party2.is_able()))
    if attack.num < 1 or not (party1.is_able() and party2.is_able()):
        try:
            del choices['Attack']
        except KeyError:
            pass  # already removed...


async def ChooseCombatAction(*args, **kwargs):
    entity = kwargs['entity']
    if entity.status.get(enums.STATUS.INCAPACITATED):
        debug(entity.status, entity.name, 'is incapacitated, actions are not possible at this time')
        return
    choices = kwargs['choices']
    attack = kwargs['attack']
    party1 = kwargs['party1']
    party2 = kwargs['party2']
    choices['Help'] = [False, ActionHelp, 'Your lookin at it...']
    choices['End Turn'] = [True, ActionEndTurn, 'Ends the current turn']
    entity.effects.before_action()

    debug(choices)
    verify_can_attack(choices, attack, party1, party2)

    entity.effects.is_action(choices)  # get trait enabled choices
    keys = sorted(choices.keys())

    if not entity.auto:
        s = '\n' + entity.name + ', what is your choice of action?'
        debug('choose action not auto')
        debug("kwargs['dialogue_message']", kwargs['dialogue_message'])
        if kwargs['ctx']:
            debug('print_choices called')
            await print_choices(keys, dialogue_message=kwargs['dialogue_message'])
            debug('print_choices returned')
            debug('edit message called')
            await kwargs['dialogue_message'].edit(content=kwargs['dialogue_message'].content+s)
            debug('edit message awaited')
            choice = -1
            while choice < 0:
                choice = (await kwargs['bot'].wait_for('message', check=kwargs['pred'])).content
                debug(choice, type(choice))
                try:
                    choice = int(choice)
                    if not choice < len(keys):
                        debug(choice, ' not less than len(keys):', len(keys))
                        choice = -1
                except ValueError:
                    debug('valueerror,', choice, type(choice))
                    choice = -1
        else:
            print(s)
            await print_choices(keys)
            choice = getint('%s, what is your choice?(number): ' % entity.name, 0, len(keys)-1)
    else:
        debug(choices)
        choice = 'Attack' if 'Attack' in choices else 'Dodge'
        choice = keys.index(choice)
    function = choices.get(keys[choice], None)

    consume_turn, function, h = function
    debug(consume_turn, function)
    debug(function)
    await function(*args, **kwargs)
    debug(choices)
    debug('attack num:', attack.num)
    debug('consume turn? ', consume_turn)
    if consume_turn:  # eliminate all the choices that consume the turn once the first action does so.
        remove = []
        for action in choices.keys():
            if choices[action][0]:
                remove.append(action)
        for action in remove:
            if action == 'Attack' and keys[choice] == 'Attack':
                if attack.num < 1:
                    debug('removing ' + action)
                    del choices[action]
            else:
                debug('removing ' + action)
                del choices[action]
    del choices['Help']

    return function


if __name__ == '__main__':
    from dnd5e_character_sheet import init_wulfgar
    from dnd5e_encounter import Party
    w = init_wulfgar()
    w2 = init_wulfgar()
    w2.name += ' 2'
    e1 = w.effects
    e2 = w2.effects
    e1.before_battle()
    e1.before_turn()
    e1.before_action()
    e2.before_battle()
    e2.before_turn()
    e2.before_action()
    a1 = {}
    e1.is_action(actions=a1)
    debug(a1)
    a2 = {}
    e2.is_action(actions=a2)
    debug(a2)
    party = Party(w, w2)
