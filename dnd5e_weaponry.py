import dnd5e_items as items
import dnd5e_misc as misc
from dnd5e_enums import WEAPONS, WEAPONFLAGS, DAMAGETYPE, ATTACK, EQUIP_SLOT


# weaponry base class, holds the details common to all weapons
class Weapon(items.Item):
    # cost: in copper pieces
    # damage is a 3 to 8 parameter dict.  1 handed die qty and die sides, and damage type are requisite.
    #     damage = {
    #                  '1_die': 1,  # wielded in one hand
    #                  '1_sides': 10,  # wielded in one hand
    #                  '2_die': 1,  # wielded in two hands
    #                  '2_sides': 12,  # wielded in two hands
    #                  'bonus_dmg': 0,  # flat additional damage
    #                  'bonus_die': 0,  # additional_damage_die
    #                  'bonus_sides': 0,  # additional_damage_die
    #                  'types': [DAMAGETYPE.SLASHING]  # flags is a list of relevant weaponry flags
    #              },
    #   light or heavy, finesse, etc.
    # enum_type: enum describing weapon categories.
    def __init__(self, name=None, cost=None, damage=None, hit_bonus=None, enum_type=None, atk_type=None, weight=None,
                 reach=None, ranges=None, flags=None, wield_from=None, equip_function=None, attack_function=None):
        # TODO: embed static weapon criteria in the weapon type enum?
        qty = 1
        super().__init__(name, cost, weight, qty, enum_type, equip_function)
        self.atk_type = atk_type
        self.wield_from = wield_from
        self.die1, self.die2 = None, None
        if '1_die' in damage:
            die_qty = damage['1_die']
            die_sides = damage['1_sides']
            self.die1 = misc.Die(die_qty, die_sides)
        if '2_die' in damage:
            die_qty2 = damage['2_die']
            die_sides2 = damage['2_sides']
            self.die2 = misc.Die(die_qty2, die_sides2)

        if 'bonus_die' in damage:
            self.bonus_die = misc.Die(damage['bonus_die'], damage['bonus_sides'])
        else:
            self.bonus_die = None

        self.bonus_damage = 0 if 'bonus' not in damage else damage['bonus']
        self.damage_type = damage['types']
        self.reach = reach
        self.ranges = ranges
        self.flags = flags
        self.hit_bonus = hit_bonus
        if self.hit_bonus is None:
            self.hit_bonus = 0
        self.attack_die = None  # set at runtime when equipped
        self.equip_function = equip_function
        self.attack_function = attack_function  # todo, implement attack functions

    roll = lambda self: 0 if self.attackDie is None else self.attackDie.roll()
    damage = lambda self, hand: self.roll() + self.bonus_damage + (self.bonus_die.roll() if self.bonus_die else 0)

    def __repr__(self):
        s = self.name + ': '
        s += str(self.attack_die)
        s += '' if not self.bonus_damage else (' +%d' % self.bonus_damage)
        s += '' if not self.bonus_die else (' + ' + str(self.bonus_die))
        return s

    def __str__(self): return self.__repr__()


# example definitions
greataxe = Weapon(  # todo: config limiting
                    name='GreatAxe',
                    cost=3000,
                    damage={
                            '1_die': 1,         # wielded in one hand
                            '1_sides': 10,      # wielded in one hand
                            '2_die': 1,         # wielded in two hands
                            '2_sides': 12,      # wielded in two hands
                            'types': [DAMAGETYPE.SLASHING]
                            },
                    enum_type={WEAPONS.MARTIAL.GREATAXE},
                    atk_type={ATTACK.MELEE},
                    wield_from=EQUIP_SLOT.HAND,
                    weight=7,
                    reach=0,
                    ranges=(0, 0),  # for thrown / ranged attacks, (standard, extended) - disadvantage on extended
                    flags={WEAPONFLAGS.VERSATILE},
                    equip_function=None,  # the function which executes a special effect on the  target
                    attack_function=None,
                    )

