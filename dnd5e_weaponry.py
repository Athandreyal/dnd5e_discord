import dnd5e_items as items
import dnd5e_misc as misc
import dnd5e_enums as enums
#from dnd5e_enums import WEAPONS, WEAPONFLAGS, DAMAGETYPE, ATTACK, EQUIP_SLOT
import dnd5e_functions as functions
import json


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
        super().__init__(name=name, cost=cost, weight=weight, qty=qty, enum_type=enum_type, equip_to=wield_from,
                         function=attack_function)
        self.atk_type = atk_type
#        self.wield_from = wield_from
        self.die1, self.die2 = None, None
        if '1_die' in damage:
            die_qty = damage['1_die']
            die_sides = damage['1_sides']
            self.die1 = misc.Die(die_qty, die_sides)
        if '2_die' in damage:
            die_qty2 = damage['2_die']
            die_sides2 = damage['2_sides']
            self.die2 = misc.Die(die_qty2, die_sides2)

        if 'bonus_die' in damage and damage['bonus_die'] is not None:
            print(damage)
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

    roll = lambda self: None if self.attack_die is None else self.attack_die.roll()
    damage = lambda self, hand: self.roll() + self.bonus_damage + (self.bonus_die.roll() if self.bonus_die else 0)

    def __repr__(self):
        s = self.name + ': '
        s += str(self.attack_die)
        s += '' if not self.bonus_damage else (' +%d' % self.bonus_damage)
        s += '' if not self.bonus_die else (' + ' + str(self.bonus_die))
        return s

    def __str__(self): return self.__repr__()

    @staticmethod
    def from_dict(d):
        return Weapon(  # todo: config limiting
                      name=d['name'],
                      cost=d['cost'],
                      damage={
                          '1_die': d.get('1_die', None),
                          '1_sides': d.get('1_sides', None),
                          '2_die': d.get('2_die', None),
                          '2_sides': d.get('2_sides', None),
                          'bonus_die': d.get('b_sides', None),
                          'bonus_sides': d.get('b_sides', None),
                          'bonus': d.get('bonus_damage', None),
                          'types': misc.get_sets_of_attribs_from_sets_of_qualnames(enums,
                                                                                   json.loads(d['damage_types'])),
                      },
                      hit_bonus=d.get('hit_bonus', None),
                      enum_type=misc.get_sets_of_attribs_from_sets_of_qualnames(enums, json.loads(d['type'])),
                      atk_type=misc.get_sets_of_attribs_from_sets_of_qualnames(enums, json.loads(d['atk_type'])),
                      wield_from=misc.get_attrib_from_qualname(enums, d['equip_to']),
                      weight=d['weight'],
                      reach=d['reach'],
                      ranges=json.loads(d['ranges']),
                      flags=misc.get_sets_of_attribs_from_sets_of_qualnames(enums, json.loads(d['flags'])),
                      equip_function=getattr(functions, d['function']) if d['function'] else None,
                      attack_function=getattr(functions, d['attack_function']) if d['attack_function'] else None,
                  )
    # todo: confirm the values for damage are not harmed by not being explicitly integers

    def to_dict(self):
        d = super().to_dict()

        def wrap(obj):
            if type(obj) != type(""):
                return json.dumps(obj)
            return obj
        d['1_die'] = self.die1.qty if self.die1 else None
        d['1_sides'] = self.die1.sides if self.die1 else None
        d['2_die'] = self.die2.qty if self.die2 else None
        d['2_sides'] = self.die2.sides if self.die2 else None
        d['b_die'] = self.bonus_die.qty if self.bonus_die else None
        d['b_sides'] = self.bonus_die.sides if self.bonus_die else None
        d['hit_bonus'] = self.hit_bonus
        d['bonus_damage'] = self.bonus_damage
        d['damage_types'] = wrap([misc.get_full_qualname(x) for x in self.damage_type])
        d['atk_type'] = wrap([misc.get_full_qualname(x) for x in self.atk_type])
        d['weight'] = self.weight
        d['reach'] = self.reach
        d['ranges'] = wrap(self.ranges)
        d['flags'] = wrap([misc.get_full_qualname(x) for x in self.flags])
        d['attack_function'] = self.equip_function.__name__ if self.equip_function else None
        return d


# example definitions
greataxe = Weapon(  # todo: config limiting
                    name='GreatAxe',
                    cost=3000,
                    damage={
                            '1_die': 1,         # wielded in one hand
                            '1_sides': 10,      # wielded in one hand
                            '2_die': 1,         # wielded in two hands
                            '2_sides': 12,      # wielded in two hands
                            'types': [enums.DAMAGETYPE.SLASHING]
                            },
                    enum_type={enums.WEAPONS.MARTIAL.GREATAXE},
                    atk_type={enums.ATTACK.MELEE},
                    wield_from=enums.EQUIP_SLOT.HAND,
                    weight=7,
                    reach=0,
                    ranges=(0, 0),  # for thrown / ranged attacks, (standard, extended) - disadvantage on extended
                    flags={enums.WEAPONFLAGS.VERSATILE},
                    equip_function=None,  # the function which executes a special effect on the  target
                    attack_function=None,
                    )

GSTQ2H = Weapon(  # todo: config limiting
                    name='God Save The Queen',
                    cost=50000,
                    damage={
                            '2_die': 2,         # wielded in two hands
                            '2_sides': 6,      # wielded in two hands
                            'types': [enums.DAMAGETYPE.SLASHING]
                            },
                    enum_type={enums.WEAPONS.MARTIAL.GREATSWORD},
                    atk_type={enums.ATTACK.MELEE},
                    wield_from=enums.EQUIP_SLOT.HAND,
                    weight=6,
                    reach=0,
                    ranges=(0, 0),  # for thrown / ranged attacks, (standard, extended) - disadvantage on extended
                    flags={enums.WEAPONFLAGS.HEAVY, enums.WEAPONFLAGS.TWO_HANDED},
                    equip_function=functions.WeaponEffectGSTQ2H,
                    #               the function which executes a special effect on the  target
                    attack_function=None,
                    )

if __name__ == '__main__':
    print(greataxe)
    g = greataxe.to_dict()
    print(g)
    g2 = Weapon.from_dict(g)
    print(g2)
    g2 = g2.to_dict()
    print(g2)
