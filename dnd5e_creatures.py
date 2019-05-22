import dnd5e_enums as enums
import dnd5e_weaponry as weaponry
import dnd5e_misc as misc
from dnd5e_enums import DAMAGETYPE, ATTACK, EQUIP_SLOT, WEAPONS
from dnd5e_inventory import Equipped
from dnd5e_events import Event


class Creature:
    # hp_dice is a 3 element tuple, or perhaps a dictionary for naming purposes.
    #    number of die, sides per, initial hp.
    # transfer some stuff to the subclasses - challenge was needed at the subclass level already for inspection
    # before instantiation of an instance.
    def __init__(self, name, creature_type, size, armor_class, hp_dice, speed, abilities, saving_throws, skills,
                 traits, actions):  # todo: senses
        self.name = name
        self.creature_type = creature_type
        self.size = size
        self.armor_class = armor_class
        hp_die = misc.Die(hp_dice['die_qty'], hp_dice['die_sides'])
        self.hp_max = hp_die.roll(bonus=hp_dice['bonus'])
        self.hp = self.hp_max
        self.speed = speed
        self.abilities = abilities
        self.saving_throws = self.set_saving_throws(saving_throws)
        self.skills = skills
#        self.senses = senses
        self.traits = traits
        self.actions = actions
        self.equipment = Equipped()  # creatures technically have the full set of gear players do
        for action in self.actions:
            self.equipment.equip(self.actions[action])  # todo, confirm this doesn't break anything
        self.initiative = self.abilities.DEX_MOD   # todo: proper initiative
        self.gold = None
        self.gems = None
        self.items = None  # could be potions, maps, equipment, mounts, etc
#        self.temporary_hitpoints = 0  # magical shielding, and such
#        self.effects = self.Effect()  # use for trait/status effects - re-apply whenever character refreshes
        self.advantage = set()
        self.disadvantage = set()
        self.atk_bonus = 0
        self.effects = Event()  # use for trait/status effects - re-apply whenever character refreshes

    def dict_short(self):
        return {
                'name': self.name,
                'type': self.creature_type.__name__.capitalize(),
                'hp': '{:,}'.format(self.hp) + '/' + '{:,}'.format(self.hp_max),
                }

    def set_saving_throws(self, saving_throws):
        # todo: confirm if saving throws are modified by any races and include if so
        # base values
        STR = self.abilities.STR_MOD
        CON = self.abilities.CON_MOD
        DEX = self.abilities.DEX_MOD
        INT = self.abilities.INT_MOD
        WIS = self.abilities.WIS_MOD
        CHA = self.abilities.CHA_MOD
        # proficiency boosted
        STR += saving_throws.STR
        CON += saving_throws.CON
        DEX += saving_throws.DEX
        INT += saving_throws.INT
        WIS += saving_throws.WIS
        CHA += saving_throws.CHA
        return enums.Ability(STR, CON, DEX, INT, WIS, CHA)

    def is_lucky(self):
        return enums.TRAIT.LUCKY in self.traits

    def receive_damage(self, damage):
        # todo: handle death, incapacitation, etc.
        # todo: trigger defence events, return any that apply to attacker
        self.hp -= int(max(damage))
        return int(max(damage)), None  # todo: return actual damage taken and any counter effects
        # todo: cross check damage types against vulnerability/resist, and modify accordingly - take highest effect

    def melee_attack(self):
        # todo: deal with multiple damage types
        # todo: make effects.attack return the effects for the target to apply to itself.
        effects = self.effects.attack(self)  # call attack event handler - trigger any registered attack
        #     return any effects which require a target - like poison effects.
        #        advantage = enums.ADVANTAGE.ATTACK in self.advantage
        #        disadvantage = enums.ADVANTAGE.ATTACK in self.disadvantage
        #        lucky = enums.TRAIT.LUCKY in self.traits
        #        attack_roll, critical = misc.attack_roll(advantage, disadvantage, lucky=lucky)
        # todo: implement usage of reach value
        #        damage = weapon.attack_die.roll() + weapon.bonus_die.roll() if weapon.bonus_die else 0 + weapon.bonus_damage
        attacks = {'num': 1}
        if enums.CLASS_TRAITS.EXTRA_ATTACK in self.traits:
            attacks['num'] += 1

        # is storing two of the same reference
        attacks['effects'] = effects
        attacks['calculation'] = self._wpn

        attacks['weapons'] = self.equipment.right_hand, self.equipment.left_hand, \
            self.equipment.jaw, self.equipment.fingers
        return attacks

    def _wpn(self, hand: weaponry.Weapon = None):
        while True:
            if hand is None:
                yield 0
            damage = hand.attack_die.roll()
            if damage == 1 and enums.TRAIT.LUCKY in self.traits:
                damage = hand.attack_die.roll()
            damage += hand.bonus_die.roll() if hand.bonus_die is not None else 0
            damage += hand.bonus_damage
            yield [d(damage) for d in hand.damage_type], hand.attack_function

    def get_armor_class(self):
        # todo: throw defence event related to specific attack type, modify ac if necessary - may need to return
        #  statuses from here for thorns like effects

        # todo: poll all gear(not just armor), and sum the AC values.
        # todo: run racial/class defence functions, keep best AC value.
        return self.armor_class


class Crab(Creature):
    challenge = (0, 10)

    def __init__(self):
        super().__init__(name='Crab',
                         creature_type=enums.CREATURE_TYPES.BEAST,
                         size=enums.SIZE.TINY,
                         armor_class=11,
                         hp_dice={'die_qty': 1,
                                  'die_sides': 4,
                                  'bonus': 0},
                         speed=20,  # todo, swim speed, and fly, and...etc
                         abilities=enums.Ability(strength=2,
                                                 dexterity=11,
                                                 constitution=10,
                                                 intelligence=1,
                                                 wisdom=8,
                                                 charisma=2),
                         saving_throws=enums.Ability(),  # no bonuses to throws
                         skills={'STEALTH': 2},
                         traits={enums.TRAIT.COMMON_PERCEPTION},
                         actions={'melee': weaponry.Weapon(name='Claw',
                                                           damage={
                                                              '1_die': 1,  # wielded in two hands
                                                              '1_sides': 1,  # wielded in two hands
                                                              'types': [DAMAGETYPE.BLUNT],
                                                              'bonus_dmg': 0,  # flat additional damage
                                                          },
                                                           enum_type={WEAPONS.GENERIC},
                                                           hit_bonus=0,
                                                           reach=5,
                                                           atk_type={ATTACK.MELEE},
                                                           wield_from=EQUIP_SLOT.FINGERS,
                                                           ranges=(0, 0),  # (standard, extended w/disadvantage)
                                                           equip_function=None,
                                                           # the function which executes a special effect on the  target
                                                           attack_function=None,
                                                           ),
                                  }  # todo: remaining orc actions, MM page 246
                         )


class GiantWeasel(Creature):
    challenge = (0.12, 25)

    def __init__(self):
        super().__init__(name='Giant Weasel',
                         creature_type=enums.CREATURE_TYPES.BEAST,
                         size=enums.SIZE.MEDIUM,
                         armor_class=13,
                         hp_dice={'die_qty': 2,
                                  'die_sides': 8,
                                  'bonus': 0},
                         speed=40,
                         abilities=enums.Ability(strength=11,
                                                 dexterity=16,
                                                 constitution=10,
                                                 intelligence=4,
                                                 wisdom=12,
                                                 charisma=5),
                         saving_throws=enums.Ability(),  # no bonuses to throws
                         skills={'PERCEPTION': 2, 'STEALTH': 5},
                         traits={enums.TRAIT.DARKVISION, enums.TRAIT.COMMON_PERCEPTION},
                         actions={'melee': weaponry.Weapon(name='Bite',
                                                           damage={
                                                              '1_die': 1,  # wielded in two hands
                                                              '1_sides': 4,  # wielded in two hands
                                                              'types': [DAMAGETYPE.PIERCING],
                                                              'bonus_dmg': 3,  # flat additional damage
                                                          },
                                                           enum_type={WEAPONS.GENERIC},
                                                           hit_bonus=5,
                                                           reach=0,
                                                           atk_type={ATTACK.MELEE},
                                                           wield_from=EQUIP_SLOT.JAW,
                                                           ranges=(0, 0),  # (standard, extended w/disadvantage)
                                                           equip_function=None,
                                                           # the function which executes a special effect on the  target
                                                           attack_function=None,
                                                           ),
                                  }  # todo: remaining orc actions, MM page 246
                         )


class Orc(Creature):
    challenge = (0.5, 100)

    def __init__(self):
        super().__init__(name='Orc',
                         creature_type=enums.CREATURE_TYPES.HUMANOID,
                         size=enums.SIZE.MEDIUM,
                         armor_class=13,
                         hp_dice={'die_qty': 2,
                                  'die_sides': 8,
                                  'bonus': 6},
                         speed=30,
                         abilities=enums.Ability(strength=16,
                                                 dexterity=12,
                                                 constitution=16,
                                                 intelligence=7,
                                                 wisdom=11,
                                                 charisma=10),
                         saving_throws=enums.Ability(),  # no bonuses to throws
                         skills={'INTIMIDATION': 2},
                         traits={enums.TRAIT.DARKVISION, enums.TRAIT.COMMON_PERCEPTION},
                         actions={'melee': weaponry.Weapon(name='GreatAxe',
                                                           damage={
                                                              '2_die': 1,  # wielded in two hands
                                                              '2_sides': 12,  # wielded in two hands
                                                              'types': [DAMAGETYPE.SLASHING],
                                                          },
                                                           reach=0,
                                                           atk_type={ATTACK.MELEE},
                                                           wield_from=EQUIP_SLOT.HAND,
                                                           ranges=(0, 0),  # (standard, extended w/disadvantage)
                                                           equip_function=None,
                                                           attack_function=None,
                                                           ),
                                  }  # todo: remaining orc actions, MM page 246
                         )


class Orog(Creature):
    challenge = (2, 450)

    def __init__(self):
        super().__init__(name='Orog',
                         creature_type=enums.CREATURE_TYPES.HUMANOID,
                         size=enums.SIZE.MEDIUM,
                         armor_class=18,
                         hp_dice={'die_qty': 5,
                                  'die_sides': 8,
                                  'bonus': 20},
                         speed=30,
                         abilities=enums.Ability(strength=18,
                                                 dexterity=12,
                                                 constitution=18,
                                                 intelligence=12,
                                                 wisdom=11,
                                                 charisma=12),
                         saving_throws=enums.Ability(),  # no bonuses to throws
                         skills={'INTIMIDATION': 5, 'SURVIVAL': 2},
                         traits={enums.TRAIT.DARKVISION, enums.TRAIT.COMMON_PERCEPTION},
                         actions={'melee': weaponry.Weapon(name='GreatAxe',
                                                           damage={
                                                              '2_die': 1,  # wielded in two hands
                                                              '2_sides': 12,  # wielded in two hands
                                                              'types': [DAMAGETYPE.SLASHING],
                                                          },
                                                           reach=0,
                                                           wield_from=EQUIP_SLOT.HAND,
                                                           atk_type={ATTACK.MELEE},
                                                           ranges=(0, 0),  # (standard, extended w/disadvantage)
                                                           equip_function=None,
                                                           attack_function=None,
                                                           ),
                                  }  # todo: remaining orc actions, MM page 246
                         )


class Orc_Chieftan(Creature):
    challenge = (4, 1100)

    def __init__(self):
        super().__init__(name='Orc War Chief',
                         creature_type=enums.CREATURE_TYPES.HUMANOID,
                         size=enums.SIZE.MEDIUM,
                         armor_class=16,
                         hp_dice={'die_qty': 11,
                                  'die_sides': 8,
                                  'bonus': 44},
                         speed=30,
                         abilities=enums.Ability(strength=18,
                                                 dexterity=12,
                                                 constitution=18,
                                                 intelligence=11,
                                                 wisdom=11,
                                                 charisma=16),
                         saving_throws=enums.Ability(strength=6,
                                                     dexterity=0,
                                                     constitution=6,
                                                     intelligence=0,
                                                     wisdom=2,
                                                     charisma=0),
                         skills={'INTIMIDATION': 5},
                         traits={enums.TRAIT.DARKVISION, enums.TRAIT.COMMON_PERCEPTION},
                         actions={'melee': weaponry.Weapon(name='GreatAxe',
                                                           damage={
                                                             '2_die': 1,  # wielded in two hands
                                                             '2_sides': 12,  # wielded in two hands
                                                             'types': [DAMAGETYPE.SLASHING],
                                                             'bonus_dmg': 4,  # flat additional damage
                                                             'bonus_die': 1,  # additional_damage_die
                                                             'bonus_sides': 8,  # additional_damage_die
                                                          },
                                                           reach=0,
                                                           atk_type={ATTACK.MELEE},
                                                           wield_from=EQUIP_SLOT.HAND,
                                                           ranges=(0, 0),  # (standard, extended w/disadvantage)
                                                           equip_function=None,
                                                           attack_function=None,
                                                           ),
                                  }  # todo: remaining orc actions, MM page 246
                         )


if __name__ == '__main__':
    #print(Orc().dict_short())
    #print(Orc_Chieftan().dict_short())
    #print(Orog().dict_short())
    orog = Orog()
    print(orog.equipment.jaw)
    print(orog.equipment.fingers)
    print(orog.equipment.left_hand)
    print(orog.equipment.right_hand)
    print(GiantWeasel().dict_short())
    weasel = GiantWeasel()
    print(weasel.equipment.jaw)
    print(weasel.equipment.fingers)
    print(weasel.equipment.left_hand)
    print(weasel.equipment.right_hand)

# todo: add this same capability to items, weaponry, armors, shields, and any other listable object.
creatures = []
local_values = list(locals().values())
for local in local_values:
    try:
        if issubclass(local, Creature) and local is not Creature:
            creatures.append(local)
    except TypeError:
        pass


