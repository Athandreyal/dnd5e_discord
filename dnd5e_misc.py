import random
import re
import json
import dnd5e_enums as enums
# miscellaneous errata used in many places, but not large enough to warrant their own file


class Effect:
    # todo: complete the event system
    # re-organise?
    #   register within appropriate event window for when to apply effect
    #      event windows are:
    #        combat events: before_battle, before_turn, after_turn, action, attack, defend, after_battle
    #        standard events: before_battle, before_turn, after_turn, action, after_battle, init, levelup
    #   before/after battle: init/end triggers for combat,
    #                        used to convert ongoing timed events to iterative battle triggers, or battle to timed
    #   before/after turn: in battle, these occur every 6 seconds.  Out of battle, these occur every time the bot
    #                      decides you need to be contacted for clarification of an important decision.  If
    #                      someone dies, the bot will contact you about retreating, or pressing on, for example.
    #   action: events which trigger when you do things.  Flight for example - if an item grants you the power
    #           to fly, then the flight effect would exist in the action trigger - you have to try to fly for it
    #           to do anything
    #   attack/defend:  these occur as part of battle.  attack events occur when you launch an attack,
    #                   defend triggers when you are attacked

    class Event(set):  # minimalist event handler abusing the set class
        #     >>> e = Event({foo, bar})
        #     >>> e('a', 'b')
        #     foo(a b)
        #     bar(a b)
        #     >>> e
        #     Event(foo, bar)
        #     >>> e.add(baz)
        #     >>> e
        #     Event(foo, baz, bar)
        #     >>> e('a', 'b')
        #     foo(a b)
        #     baz(a b)
        #     bar(a b)
        #     >>> e.remove(foo)
        #     >>> e('a', 'b')
        #     baz(a b)
        #     bar(a b)

        def __call__(self, *args, **kwargs):
            for f in self:
                f(*args, **kwargs)

        def __repr__(self):
            return 'Event(%s)' % re.sub('["[\]]', '', json.dumps([x.__name__ for x in self]))


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
        iterations = 1 if not average else 10000
        while iterations > 0:
            n_dice = self.qty
            while n_dice > 0:
                result += 1 if self.sides == 1 else self.random(self.sides).__next__()
                n_dice -= 1
            iterations -= 1
            result += bonus
        return result if not average else result // 100 / 100

    def __repr__(self):
        return str(self.qty)+'d'+str(self.sides)

    def __str__(self):
        return self.__repr__()


def ability_mod(ability):
    return ability // 2 - 5


# def ability_check_pass(ability):
#     return ability+ability_mod(ability) > roll(1, 20, 0)


def attack_roll(advantage=False, disadvantage=False, lucky=False):
    attack_die = Die(1, 20)
    roll1 = attack_die.roll()
    roll2 = attack_die.roll()
    if lucky:
        if roll1 == 1 or roll2 == 1:
            if roll1 == 1:
                roll1 = attack_die.roll()
            else:
                roll2 = attack_die.roll()
    if advantage or disadvantage and not advantage and disadvantage:
        # exclusive or, one or the other, but not both
        if advantage:
            roll = max(roll1, roll2)
        else:
            roll = min(roll1, roll2)
    else:
        roll = roll1
    critical = roll == 20
    return roll, critical


# noinspection SpellCheckingInspection
def getAdvantage(a, b):
    # does A have advantage against B?
    a_adv = enums.ADVANTAGE.ATTACK in a.advantage
    a_dadv = enums.ADVANTAGE.ATTACK in a.disadvantage
    b_adv = enums.ADVANTAGE.ATTACK in b.advantage
    b_dadv = enums.ADVANTAGE.ATTACK in b.disadvantage
    adv = (a_adv or b_dadv)
    dadv = (a_dadv or b_adv)
    if adv == dadv:
        return False, False
    else:
        return adv, dadv


if __name__ == '__main__':
    die = Die(1, 20)
    print(die, die.roll(), die.roll(), die.roll())
