import random
import re
import json
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
            roll = max(self.roll1, self.roll2) if self.advantage else min(self.roll1, self.roll2)
        else:
            roll = self.roll1
        return roll, roll == 20


# def attack_roll(advantage=False, disadvantage=False, lucky=False):
#     attack_die = Die(1, 20)
#     roll1 = attack_die.roll()
#     roll2 = attack_die.roll()
#     if lucky:
#         if roll1 == 1 or roll2 == 1:
#             if roll1 == 1:
#                 roll1 = attack_die.roll()
#             else:
#                 roll2 = attack_die.roll()
#     if advantage or disadvantage and not advantage and disadvantage:
#         # exclusive or, one or the other, but not both
#         if advantage:
#             roll = max(roll1, roll2)
#         else:
#             roll = min(roll1, roll2)
#     else:
#         roll = roll1
#     critical = roll == 20
#     return roll, critical

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


if __name__ == '__main__':
    die = Die(1, 20)
    print(die, '\navg =', die.roll(average=True),'\nroll 1, 2, 3 =', die.roll(), die.roll(), die.roll())
