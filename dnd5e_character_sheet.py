import dnd5e_enums as enums
import dnd5e_misc as misc
import dnd5e_races as RACE
import dnd5e_classes as CLASS
import dnd5e_weaponry as weaponry
import dnd5e_armor as armor
from dnd5e_inventory import Equipped
import json
from dnd5e_events import Event


class CharacterSheet:
    # todo: embed senses relevant to hostile detection for when it comes time to do battles  darkness is irrelevant
    #  if no one can see anyway and everyone knows where everyone is by default as a consequence.

    def __init__(self, name, age, height, weight, uid, experience, level, race, player_class, skills, background,
                 abilities, hp_dice, hp_current, equipment):
        self.name = name
        self.age = age
        self.height = height
        self.weight = weight
        self.uid = uid

        self._experience = experience

        self.player_race = race
        self.player_class = player_class
        self.abilities = abilities

        if level == 0:  # fresh character init
            self.level = 1
            self.hp_max = self.abilities.CON_MOD + self.player_class.hitDie
            self.hp = self.hp_max
            self.hp_dice = self.hp_max

        else:
            self.level = level
            self.hp_max = hp_dice + (level - 1) * self.abilities.CON_MOD
            self.hp = hp_current
            if self.hp is None:
                self.hp = self.hp_max
            self.hp_dice = hp_dice

        self.nextLevel = self.get_next_level_xp()
        self.proficiency_skills = skills
        self.proficiency_bonus = self.player_class.get_proficiency_bonus(self.level)
        self.proficiency_weapons = self.player_class.proficiencies.intersection(enums.WEAPONS.Set())
        self.proficiency_armor = self.player_class.proficiencies.intersection(enums.ARMOR.Set())
                            # todo: apply proficiencies from class/race to character
        self.proficiency_tools = set()  # todo: apply proficiencies from class/race to character
        self.saving_throws = self.set_saving_throws()
        self.initiative = self.abilities.DEX_MOD  # todo: proper initiative
        self.temporary_hitpoints = 0  # magical shielding, and such
        self.background = background
        if isinstance(equipment, Equipped):
            self.equipment = equipment
        elif equipment is None:
            self.equipment = Equipped()
        elif isinstance(equipment, list):
            self.equipment = Equipped()
            self.equipment.equip(equipment)  # todo: implement weapons/shields/armor
        self.traits = self.player_race.traits.union(self.player_class.traits)
#        self.traits.update(self.player_class.traits)
        self.effects = Event()  # use for trait/status effects - re-apply whenever character refreshes
        self.advantage = set()
        self.disadvantage = set()
        self.atk_bonus = 0
        self.damage_vulnerable = set()  # todo: implement damage vulnerabilities
        self.damage_resist = set()  # todo: implement damage resistances
        # todo: execute init event - the always event

    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, xp):
        self._experience = xp
        if self.experience > self.get_next_level_xp():
            self.level_up()

    def level_up(self):
        # todo: run all statuses/traits to get their combined additional effects
        #  subtract those effects from the character, re-init() the character, re-apply all the statuses/traits
        print('Level up!')
        self.level += 1
        self.hp_dice += misc.Die(1, self.player_class.hitDie).roll()
        self.__init__(name=self.name, age=self.age, height=self.height, weight=self.weight, uid=self.uid,
                      experience=self.experience, level=self.level, race=self.player_race,
                      player_class=self.player_class, skills=self.proficiency_skills, background=self.background,
                      abilities=self.abilities, hp_dice=self.hp_dice, hp_current=None, equipment=self.equipment)

    def set_saving_throws(self):  # todo: confirm if saving throws are modified by any races and include if so
        throws = self.player_class.saving_throws
        # base values
        STR = self.abilities.STR_MOD
        CON = self.abilities.CON_MOD
        DEX = self.abilities.DEX_MOD
        INT = self.abilities.INT_MOD
        WIS = self.abilities.WIS_MOD
        CHA = self.abilities.CHA_MOD
        # proficiency boosted
        STR += self.proficiency_bonus if enums.ABILITY.STR in throws else 0
        CON += self.proficiency_bonus if enums.ABILITY.CON in throws else 0
        DEX += self.proficiency_bonus if enums.ABILITY.DEX in throws else 0
        INT += self.proficiency_bonus if enums.ABILITY.INT in throws else 0
        WIS += self.proficiency_bonus if enums.ABILITY.WIS in throws else 0
        CHA += self.proficiency_bonus if enums.ABILITY.CHA in throws else 0
        return enums.Ability(STR, CON, DEX, INT, WIS, CHA)

    def get_next_level_xp(self):
        xp = {2:     300,
              3:     900,
              4:    2700,
              5:    6500,
              6:   14000,
              7:   23000,
              8:   34000,
              9:   48000,
              10:  64000,
              11:  85000,
              12: 100000,
              13: 120000,
              14: 140000,
              15: 165000,
              16: 195000,
              17: 225000,
              18: 265000,
              19: 305000,
              20: 355000}
        return xp.get(self.level, -1)

    def full_str(self):
        s = '\n'
        s += 'Name: \t\t\t\t\t' + self.name + '\n'
        s += 'Age: \t\t\t\t\t' + '{:,}'.format(self.age) + ' yrs\n'
        s += 'Height: \t\t\t\t' + str(self.height//12) + 'ft ' + \
             ('' if self.height % 12 == 0 else str(self.height % 12) + 'in') + '\n'
        s += 'Weight: \t\t\t\t' + '{:,}'.format(self.weight) + 'lbs\n'
        s += 'Level: \t\t\t\t\t' + str(self.level) + '\n'
        s += 'Experience: \t\t\t' + '{:,}'.format(self.experience) + '\n'
        s += 'Race: \t\t\t\t\t' + self.player_race.name + '\n'
        s += 'Class: \t\t\t\t\t' + self.player_class.name + '\n'
        s += 'Abilities: \n' + self.abilities.__repr__(mod=True)
        s += 'Racial Ability Proficiencies: '
        ab = json.dumps([x.__name__ for x in self.player_class.saving_throws])
        ab = ab.replace('"', '').replace('[', '').replace(']', '')
        s += ab + '\n'
        s += 'Saving Throws: \n' + self.saving_throws.__repr__()
        s += 'Proficiency: Bonus: \t' + str(self.proficiency_bonus) + '\n'
        s += 'Proficiency: Skills: \t'
        skills = '' if self.proficiency_skills is None else \
            json.dumps([x.__name__ for x in self.proficiency_skills]) + '\n'
        skills = skills.replace('"', '').replace('[', '').replace(']', '')
        s += skills
        s += 'Proficiency: Weapons: \t' + str(self.proficiency_weapons) + '\n'
        s += 'Proficiency: Armor: \t' + str(self.proficiency_armor) + '\n'
        s += 'Proficiency: Tools: \t' + str(self.proficiency_tools) + '\n'
        s += 'Hitpoints: \t\t\t\t' + '{:,}'.format(self.hp) + '/' + '{:,}'.format(self.hp_max)+'\n'
        s += 'HitDice: \t\t\t\t' + str(self.level) + ' d' + str(self.player_class.hitDie) + '\n'
        s += 'Initiative: \t\t\t' + str(self.initiative) + '\n'
        s += 'Speed: \t\t\t\t\t' + str(self.player_race.speed) + 'ft/round\n'
        s += 'Armor Class: \t\t\t' + str(self.get_armor_class()) + '\n'
        s += 'Weapon: \t\t\t\t' + str(self.equipment.right_hand) + '\n'
        s += 'Armor: \t\t\t\t\t' + str(self.equipment.armor.name) + '\n'
        s += 'Shield: \t\t\t\t' + str(self.equipment.shield) + '\n'
        s += 'Traits: \t\t\t\t'
        traits = json.dumps([x.__name__ for x in self.traits]) + '\n'
        traits = traits.replace('"', '').replace('[', '').replace(']', '')
        s += traits
        return s

    def dict_short(self):
        return {
                'name': self.name,
                'race': self.player_race.name,
                'class': self.player_class.name,
                'hp': '{:,}'.format(self.hp) + '/' + '{:,}'.format(self.hp_max),
                }

    def is_lucky(self):
        return enums.TRAIT.LUCKY in self.traits

    def get_armor_class(self):  # todo: apply modifiers from various traits, statuses, and spell effects
        # DETERMINE WHAT AC FORMULAS CAN BE USED FOR CHARACTER
        #   CLASSES CAN HAVE DEFENSIVE ARMOR CALCULATIONS(BARBARIAN UNARMORED DEFENCE FOR EXAMPLE)
        # DETERMINE WHICH YIELDS HIGHEST RESULT
        #   THEY DO NOT STACK, SO USE THE BEST ONE
        # TACK ON ANY BONUSES TO AC
        #   SHIELDS TO NOT HAVE A CALCULATION, THEY SIMPLY ADD 2 TO AC, AS AN EXAMPLE
        # RETURN RESULT

        # todo: throw defence event related to specific attack type, modify ac if necessary - may need to return
        #  statuses from here for thorns like effects

        # todo: poll all gear(not just armor), and sum the AC values.
        # todo: run racial/class defence functions, keep best AC value.
        # CURRENTLY NO EQUIPMENT IN USE, SO ALWAYS RETURNS BASIC ARMOR FOR NOW.
        if self.equipment.armor is None:
            return 10 + self.abilities.DEX_MOD
        else:  # have armor, calculate it.
            base_armor_class = self.equipment.armor.armor_class
            dex_bonus = min(self.abilities.DEX_MOD, self.equipment.armor.dex_limit)
            proficiency = self.equipment.armor.flags.intersection(self.proficiency_armor)
            if proficiency:
                proficiency_bonus = self.proficiency_bonus
            else:
                proficiency_bonus = 0

            armor_class = base_armor_class + dex_bonus + proficiency_bonus

            return armor_class

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
            damage = hand.roll()
            if damage == 1 and enums.TRAIT.LUCKY in self.traits:
                damage = hand.attack_die.roll()
            damage += hand.bonus_die.roll() if hand.bonus_die is not None else 0
            damage += hand.bonus_damage
            yield [d(damage) for d in hand.damage_type], hand.attack_function

    def receive_damage(self, damage):
        # todo: handle death, incapacitation, etc.
        # todo: trigger defence events, return any that apply to attacker
        self.hp -= int(max(damage))
        return int(max(damage)), None  # todo: return actual damage taken and any counter effects
        # todo: cross check damage types against vulnerability/resist, and modify accordingly - take highest effect

    def get_attack(self):
        # todo: should re-tag to get_weapon_attack and use the weapon's attack function
        self.effects.attack(self, Target=None)  # call attack event handler - trigger any registered attack
        advantage = enums.ADVANTAGE.ATTACK in self.advantage
        disadvantage = enums.ADVANTAGE.ATTACK in self.disadvantage
        lucky = enums.TRAIT.LUCKY in self.traits
        attack_roll, critical = misc.attack_roll(advantage, disadvantage, lucky=lucky)

        proficiency = self.proficiency_bonus if self.equipment.right_hand.type in self.proficiency_weapons else 0
        if enums.WEAPONFLAGS.FINESSE in self.equipment.right_hand.flags:
            ability = max(self.abilities.STR_MOD, self.abilities.DEX_MOD)
        else:
            ability = self.abilities.STR_MOD
        attack = attack_roll + proficiency + ability
        print('attack =', attack, '(', attack_roll, '+', proficiency, '+', ability, ')')
        damage = self.equipment.right_hand.roll() + ability
        damage = damage * (2 if critical else 1)

        print('damage =', damage, 'critical =', critical)
        return attack, critical

# class Character():  #rebuilt this already, lol
#     pace=enums.PACE.NORMAL
#
#     #strength factors
#     carry_capacity  = lambda self:self.str * self.carry_multi       #carrying limit
#     push_mass       = lambda self:self.str * 2 * self.carry_multi   #limit for pushing/lifting/dragging
#     lift_mass = push_mass
#     drag_mass = push_mass
#
#     def push_speed(self,mass):
#         multiple = carry_capacity()/mass
#         low = min(12,max(0,multiple-5))*(0.33/12)
#         med = min(12,max(0,multiple-17))*((0.67-0.25)/12)
#         hi = max(multiple-25,0)*.05
#         mod = 1 - low-med-hi
#         return max(1,int(self.speed*mod)) if mod < 1 else 0
#     carry_speed = push_speed
#     drag_speed = carry_speed
#
#     def levelup(self):  #replace this with class specific.
#         old_con_mod = functions.ability_mod(self.con['current'])
#         self.str['base']+=self.str['level']
#         self.con['base']+=self.con['level']
#         self.dex['base']+=self.dex['level']
#         self.wis['base']+=self.wis['level']
#         self.int['base']+=self.int['level']
#         self.cha['base']+=self.cha['level']
#         calculate_hp_max(self,old_con_mod)
#         self.level+=1
#
# melee attack
#   add str modifier to attack roll and damage roll unless weapon has finesse, then _can_ use dex instead
# ranged/finesse attack
#   add dex modifier to attack roll and damage roll unless has thrown property, then _can_ use strength
#
# armor class
#   depending on armor, might add dex value to armor class
#
# initiative
#   uses dexterity to determine movement order
#
# hiding
#   uses dexterity(stealth) to hide
#   uses wis(perception) to search for
#
# spell casting
#   sets spell DC for setting spell saving throw to resist
#
#
# saving throws
#   attempts to resist spell, trap, poison, disease, etc.
#   standard 1d20 roll with ability_mod
#   situationally modified with bonus/penalty
#   (dis)advantage bonus/penalty
#
# difficulty class (DC)
#   determines by effect that causes it, spells are determined via spellcasting and proficiency bonus


def init_wulfgar():
    # THESE ARE WHAT WE NEED TO KNOW IN ORDER TO LOAD A CHARACTER
    # INVENTORY IS GONNA BE AN EXPANSIVE MESS...PERHAPS JUST A DATABASE TABLE ID - LOAD EVERYTHING WE FIND THERE?
    #
    name = 'Wulfgar, son of Beornegar'
    age = 21
    height = 7 * 12 + 1  # 7` 1"
    weight = 223
    uid = 1
    experience = 0
    level = 0
    player_race = RACE.Human()
    player_class = CLASS.Barbarian(level)
    class_skills = {enums.SKILL.ATHLETICS, enums.SKILL.PERCEPTION}
    background = enums.BACKGROUNDS.OUTLANDER
    #    abilities = enums.Ability(24, 16, 22, 9, 14, 11)
    abilities = enums.Ability(15, 13, 14, 8, 12, 10)
    #    hp_dice = 179  # sum total of all hp rolls to date - needs to be kept for recalculating hp on con_mod change
    hp_dice = 0
    #    hp_current = 236
    hp_current = 0
    weapon = weaponry.greataxe  # todo: implement weapons/shields/armor
    _armor = armor.plate_Armor  # todo: implement weapons/shields/armor
    shield = None  # todo: implement weapons/shields/armor
    return CharacterSheet(name, age, height, weight, uid, experience, level, player_race, player_class,
                          class_skills, background, abilities, hp_dice, hp_current, [weapon, _armor, shield])


if __name__ == '__main__':
    from trace import __LINE__
    import sys

    wulfgar = init_wulfgar()
    print(wulfgar, '\n\n', wulfgar.dict_short(), '\n', wulfgar.full_str())

    print('\n\n\t\t****************************')
    print('\t\t***   get attack debug   ***')
    print('\t\t****************************\n\n')
    print(__LINE__(), wulfgar.melee_attack())

    attack = wulfgar.melee_attack()
    print(__LINE__(), attack)
    sys.stdout.flush()

    results = [None, None]
    calculation = attack['calculation']
    for n in range(attack['num']):
        results[n] = calculation(attack['weapons'][n])
    print(__LINE__(), results)
    results2 = []
    for d in attack['weapons'][0].damage_type:
        print(__LINE__(), d)
    for n in range(len(results)):
        for a in range(attack['num']):
            print(__LINE__(), str(n)+'_'+str(a), attack['weapons'][n], attack['weapons'][n] is not None)
            if attack['weapons'][n] is not None:
                print(__LINE__(), attack['weapons'][n].damage_type)
                damage = results[n].__next__()[0]
                print(__LINE__(), damage)
                [results2.append(damage) for x in attack['weapons'][n].damage_type]
                print(__LINE__(), results2)
    print(__LINE__(), 'attacks and damage types:', results2)


