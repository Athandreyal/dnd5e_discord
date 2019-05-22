import dnd5e_enums as enums
import dnd5e_weaponry as weaponry
import dnd5e_misc as misc
from dnd5e_enums import DAMAGETYPE, ATTACK, EQUIP_SLOT, WEAPONS
from dnd5e_entity import Entity
from trace import print


class Creature(Entity):
    # hp_dice is a 3 element tuple, or perhaps a dictionary for naming purposes.
    #    number of die, sides per, initial hp.
    # transfer some stuff to the subclasses - challenge was needed at the subclass level already for inspection
    # before instantiation of an instance.
    def __init__(self, name, creature_type, size, armor_class, hp_dice, speed, abilities, saving_throws, skills,
                 traits, actions):  # todo: senses

        hp_die = misc.Die(hp_dice['die_qty'], hp_dice['die_sides'])
        hp_max = hp_die.roll(bonus=hp_dice['bonus'])
        hp_current = hp_max
        super().__init__(name=name, traits=traits, abilities=abilities, hp=hp_current, hp_max=hp_max, skills=skills,
                         saving_throws=saving_throws, equipment=None, speed=speed, proficiency_bonus=None)
        self.creature_type = creature_type
        self.size = size
        self.armor_class = armor_class
        self.skills = skills
        self.actions = actions
        for action in self.actions:
            self.equipment.equip(self.actions[action])  # todo, confirm this doesn't break anything
        self.initiative = self.abilities.DEX_MOD   # todo: proper initiative
        self.gold = None
        self.gems = None
        self.items = None  # could be potions, maps, equipment, mounts, etc

    def dict_short(self):
        return {
                'name': self.name,
                'type': self.creature_type.__name__.capitalize(),
                'hp': '{:,}'.format(self.hp) + '/' + '{:,}'.format(self.hp_max),
                }


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
                         saving_throws=enums.Ability(strength=6,  # BONUS TO STR THROWS
                                                     constitution=6,  # BONUS TO CON THROWS
                                                     wisdom=2,),  # BONUS TO WIS THROWS
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
    print(Orc().dict_short())
    print(Orc_Chieftan().dict_short())
    orog = Orog()
    print(orog.dict_short())
    print('orog jaw:', orog.equipment.jaw)
    print('orog fingers:', orog.equipment.fingers)
    print('orog left hand:', orog.equipment.left_hand)
    print('orog right hand:', orog.equipment.right_hand)
    print(GiantWeasel().dict_short())
    weasel = GiantWeasel()
    print('weasel jaw:', weasel.equipment.jaw)
    print('weasel fingers:', weasel.equipment.fingers)
    print('weasel left hand:', weasel.equipment.left_hand)
    print('weasel right hand:', weasel.equipment.right_hand)

# todo: add this same capability to items, weaponry, armors, shields, and any other listable object.
creatures = []
local_values = list(locals().values())
for local in local_values:
    try:
        if issubclass(local, Creature) and local is not Creature:
            creatures.append(local)
    except TypeError:
        pass


