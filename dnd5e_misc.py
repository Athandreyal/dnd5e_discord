import random
import math
import dnd5e_enums as enums
# miscellaneous errata used in many places, but not large enough to warrant their own file

debug = lambda *args, **kwargs: False  #dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


class NamedTuple:
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])


class Location:
    # used for entity positions on both the world map, and their position on battle maps
    # use a node like travel system for world map movement
    # give it control over movement?

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z  # caves, castles, etc, multiple floors.
        self.speed = enums.MOVE

    def range_to(self, other_pos):
        dx = abs(self.x - other_pos.x)
        dy = abs(self.y - other_pos.y)
        dz = abs(self.z - other_pos.z)
        dx2 = dx * dx
        dy2 = dy * dy
        dz2 = dz * dz
        distance = math.sqrt(dx2+dy2+dz2)
        return distance

    def set_pos(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z


class Die:  # ....dice, not death...
    # qty is number of dice to roll
    # sides is ...erm... the number of sides the die has...
    #   minimum of 2 because a 1 sided die is a constant, not a die
    def __init__(self, qty, sides):
        if qty is None or sides is None:
            return
        self.qty = qty
        self.sides = sides

    def random(self, upper):
        while True:
            yield int(random.random() * (self.sides - 1) + 0.5) + 1

    # n is number of dice to roll
    # d is number of sides for the die, minimum 2
    # bonus is roll bonus, added to sum after rolls, default 0
    # average is for determining roll average - 10,000 rolls.
    def roll(self, bonus=0, average=False):
        """n=# dice, d=sides per die"""
        result = 0
        iterations = 1 if not average else 1000000
        while iterations > 0:
            n_dice = self.qty
            while n_dice > 0:
                result += 1 if self.sides == 1 else self.random(self.sides).__next__()
                n_dice -= 1
            iterations -= 1
            result += bonus
        return result if not average else result // 10000 / 100

    def __repr__(self):
        return str(self.qty)+'d'+str(self.sides)

    def __str__(self):
        return self.__repr__()


def ability_mod(ability):
    return ability // 2 - 5


# def ability_check_pass(ability):
#     return ability+ability_mod(ability) > roll(1, 20, 0)


# defence object, use for determining which defence to use, and storing the related defence values, and selecting the
#  best from here to use in actually defending on self
class Defend:
    def __init__(self):
        self.armor_classes = []

    def get_armor_class(self):
        # todo: make this consider arcane attacks
        return max(self.armor_classes)


class Attack:
    attack_die = Die(1, 20)

    def get(self, attr, default):
        if hasattr(self, attr):
            return getattr(self, attr)
        return default

    def __init__(self, advantage=False, disadvantage=False, num=1):
        self.advantage = advantage
        self.disadvantage = disadvantage
        self.num = num
        self.calculation = None
        self.weapons = []
        self.bonus_damage = 0
        self.bonus_attack = 0
        self.extra_attacks = 0
        self.effects = set()  # used to track modifiers applied to the attack
        self.critical_multi = 2
        self.roll1 = None
        self.roll2 = None

    def set_rolls(self, rolls):
        debug('attack.set_rolls called')
        self.roll1 = rolls.roll1
        self.roll2 = rolls.roll2

    def result(self):
        if self.advantage or self.disadvantage and not self.advantage and self.disadvantage:
            # exclusive or, one or the other, but not both
            debug('attacker has disadvantage?', self.disadvantage)
            roll = max(self.roll1, self.roll2) if self.advantage else min(self.roll1, self.roll2)
        else:
            roll = self.roll1
        return roll, roll == 20

# noinspection SpellCheckingInspection
def getAdvantage(a, b):
    # todo: make this account for melee, ranges, and arcane
    # does A have attack advantage?
    a_adv = any(isinstance(adv, enums.ATTACK.MELEE) for adv in a.advantage)
    # does B have attack advantage?
    b_adv = any(isinstance(adv, enums.ATTACK.MELEE) for adv in b.advantage)
    a_dadv = any(isinstance(adv, enums.DEFENCE.MELEE) for adv in a.disadvantage)
    b_dadv = any(isinstance(adv, enums.DEFENCE.MELEE) for adv in b.disadvantage)
    #    a_adv = enums.ADVANTAGE.ATTACK.Set().intersection(a.advantage)
    #    a_dadv = enums.ADVANTAGE.ATTACK.Set().intersection(a.disadvantage)
    #    b_adv = enums.ADVANTAGE.ATTACK.Set().intersection(b.advantage)
    #    b_dadv = enums.ADVANTAGE.ATTACK.Set().intersection(b.disadvantage)
    adv = (a_adv or b_dadv)
    dadv = (a_dadv or b_adv)
    if adv == dadv:
        return False, False
    else:
        return adv, dadv


# base is the object where you expect to find it, like dnd5e_enums.
# qualname is the full path to that item, like dnd5e_enums._WEAPONS_MARTIAL.GREATAXE, as a string
# returns the actual dnd5e_enums._WEAPONS_MARTIAL.GREATAXE attribute.
def get_attrib_from_qualname(base, qualname):
    qualname = qualname.split('.')[1:]
    for name in qualname:
        base = getattr(base, name)
    return base


def get_sets_of_attribs_from_sets_of_qualnames(base, qualnames):
    return_set = set()
    if qualnames:
        for qualname in qualnames:
            return_set.add(get_attrib_from_qualname(base, qualname))
    else:
        return_set.add(get_attrib_from_qualname(base, qualnames))
    return return_set


def get_full_qualname(object):
    try:
        ans = []
        for obj in object:
            ans.append(obj.__module__ + '.' + obj.__qualname__)
        return ans
    except TypeError:
        return object.__module__ + '.' + object.__qualname__


def getint(text, minimum, maximum, list=None):
    incomplete = True
    choice2 = -1
    while incomplete:
        choice = input(text)
        choice2 = ''.join(x for x in choice if 48 <= ord(x) <= 57)
        if choice != choice2:
            print ("        Rejecting characters which are not numbers...")
        try:
            choice2 = int(choice2)
            if list and choice2 in list:
                incomplete = False
            elif minimum <= choice2 <= maximum:
                incomplete = False
            else:
                print ("        Please choose one of the options given, %s wasn't an option." % choice2)
        except ValueError:
            choice2 = None
            print ("        Please choose one of the options given, %s wasn't an option..." % choice2)
    return choice2


def getstr(text):
    incomplete = True
    choice2 = ''
    while incomplete:
        choice = input(text)
        choice2 = ''.join(x for x in choice if ord(x) < 128)
        if choice != choice2:
            print ('        Rejecting invalid characters...')
        if choice2 != '':
            incomplete = False
    return choice2


def add_affector(token, host, what, where):
    if debug() is not False:
        printout = {}
        debug('attempting to add', what, 'in ', 'self.host.' + where)
    where_set = getattr(host, where)
    for effect in what:
        where_set = getattr(host, where)
        if effect in where_set:
            debug('found', effect, ', with affectors:', effect.affectors)
            affected = where_set.get(effect)
            affected.affectors.append(token)
        else:
            debug('didn\'t find', effect, ', instantiating it with affector', token)
            affected = effect()
            affected.affectors.append(token)
            where_set.add(affected)
        debug(affected, 'affectors is now', affected.affectors)
    debug('final self.host.' + where, 'is', where_set)


def remove_affector(token, host, what, where):
    remove = []
    if debug() is not False:
        debug('attempting to remove', what, 'in ', 'self.host.' + where)
    where_set = getattr(host, where)
    for w in what:
        effect = where_set.get(w)
        if debug() is not False:
            debug('found', what, ', with affectors:', effect.affectors)
            try:
                # I know its potentially unbound....thats why its in the try except,
                # common pycharm, its better to ask forgiveness than permission, you should know this....
                # noinspection PyUnboundLocalVariable
                printout[effect] = effect.affectors.copy()
            except TypeError:
                printout = {effect: effect.affectors.copy()}
        effect.affectors.remove(token)
        if not effect.affectors:
            debug('removing', token, 'from', effect.affectors)
            remove.append(effect)
    for r in remove:
        debug('trying to remove', r, ', from', where, 'due to no affectors')
        where_set.discard(r)
        debug(where_set)


if __name__ == '__main__':
    die = Die(1, 20)
    print(die, '\navg =', die.roll(average=True),'\nroll 1, 2, 3 =', die.roll(), die.roll(), die.roll())


