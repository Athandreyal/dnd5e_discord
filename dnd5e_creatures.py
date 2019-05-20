import dnd5e_enums as enums
import dnd5e_weaponry as weapons
import dnd5e_misc as misc
from dnd5e_enums import WEAPONS, WEAPONFLAGS, DAMAGETYPE
import sys


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

        self.initiative = self.abilities.DEX_MOD   # todo: proper initiative
        self.gold = None
        self.gems = None
        self.items = None  # could be potions, maps, equipment, mounts, etc
#        self.temporary_hitpoints = 0  # magical shielding, and such
#        self.effects = self.Effect()  # use for trait/status effects - re-apply whenever character refreshes
        self.advantage = None
        self.disadvantage = None

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

    def check_attack(self, target):
        # self.effects.attack(self, target=target)  # call attack event handler - trigger any registered attack


    def get_attack(self):
        # todo: events handler for attack
        # todo: replace with individual attack functions?
        #self.effects.attack(self, Target=None)  # call attack event handler - trigger any registered attack
        advantage = enums.ADVANTAGE.ATTACK in self.advantage
        disadvantage = enums.ADVANTAGE.ATTACK in self.disadvantage
        # actions
        # determine modifiers
        #   target ahs cover?
        #   do you have advantage or disadvantage?
        #   any relevant self.effects?
        # resolve attack
        #   attack roll 1d20 to determine miss, hit_minor, hit_major, critical
        #   roll weapon attack_die
        attack_die = misc.Die(1, 20)
        roll1 = attack_die.roll()
        roll2 = attack_die.roll()
        if roll1 == 1 or roll2 == 1 and enums.TRAIT.LUCKY in self.traits:
            if roll1 == 1:
                roll1 = attack_die.roll()
            else:
                roll2 = attack_die.roll()

        if advantage or disadvantage:
            if advantage:
                attack_roll = max(roll1, roll2)
            else:
                attack_roll = min(roll1, roll2)
        else:
            attack_roll = roll1
        critical = attack_roll == 20




        attack = attack_roll + ability + weapon_bonus
        print('attack =', attack, '(', attack_roll, '+', proficiency, '+', ability, ')')
        print('damage =', damage, 'critical =', critical)
        return attack, damage * (2 if critical else 1)

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
                         actions={'melee': weapons.Weapon(name='Bite',
                                                          damage={
                                                              '1_die': 1,  # wielded in two hands
                                                              '1_sides': 4,  # wielded in two hands
                                                              'types': [DAMAGETYPE.PIERCING],
                                                              'bonus_dmg': 3,  # flat additional damage
                                                          },
                                                          hit_bonus=5,
                                                          reach=0,
                                                          ranges=(0, 0),  # (standard, extended w/disadvantage)
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
                         actions={'melee': weapons.Weapon(name='GreatAxe',
                                                          damage={
                                                              '2_die': 1,  # wielded in two hands
                                                              '2_sides': 12,  # wielded in two hands
                                                              'types': [DAMAGETYPE.SLASHING],
                                                          },
                                                          reach=0,
                                                          ranges=(0, 0),  # (standard, extended w/disadvantage)
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
                         actions={'melee': weapons.Weapon(name='GreatAxe',
                                                          damage={
                                                              '2_die': 1,  # wielded in two hands
                                                              '2_sides': 12,  # wielded in two hands
                                                              'types': [DAMAGETYPE.SLASHING],
                                                          },
                                                          reach=0,
                                                          ranges=(0, 0),  # (standard, extended w/disadvantage)
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
                         actions={'melee': weapons.Weapon(name='GreatAxe',
                                                          damage={
                                                             '2_die': 1,  # wielded in two hands
                                                             '2_sides': 12,  # wielded in two hands
                                                             'types': [DAMAGETYPE.SLASHING],
                                                             'bonus_dmg': 4,  # flat additional damage
                                                             'bonus_die': 1,  # additional_damage_die
                                                             'bonus_sides': 8,  # additional_damage_die
                                                          },
                                                          reach=0,
                                                          ranges=(0, 0),  # (standard, extended w/disadvantage)
                                                          attack_function=None,
                                                          ),
                                  }  # todo: remaining orc actions, MM page 246
                         )


#print(Orc().dict_short())
#print(Orc_Chieftan().dict_short())
#print(Orog().dict_short())

creatures = []
local_values = list(locals().values())
for local in local_values:
    try:
        if issubclass(local, Creature) and local is not Creature:
            creatures.append(local)
    except TypeError:
        pass


