import dnd5e_enums as enums
import dnd5e_misc as misc
import dnd5e_races as RACE
import dnd5e_classes as CLASS
import dnd5e_weaponry as weaponry
import dnd5e_armor as armor
import json
import re
import sys


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


class Equipped:
    # todo: equip events - curses, attunement bonuses, etc
    def __init__(self):
        self.left_hand = None
        self.right_hand = None
        self.armor = None
        self.shield = None

    def equip(self, equipment):
        if not isinstance(equipment, list):
            equipment = [equipment]
        for e in equipment:
            if isinstance(e, weaponry.Weapon):
                self.equip_weapon(e)
            elif isinstance(e, armor.Armor):
                self.equip_armor(e)
            elif isinstance(e, armor.Shield):
                self.equip_shield(e)

    def equip_weapon(self, weapon):
        self.right_hand = weapon
        # un-equip shield if equipping a two-hander
        if enums.WEAPONFLAGS.TWO_HANDED in weapon.flags:
            self.left_hand = None

        if enums.WEAPONFLAGS.VERSATILE in weapon.flags and self.shield is None:
            self.right_hand.attackDie = self.right_hand.die2
        else:
            self.right_hand.attackDie = self.right_hand.die1

    def equip_armor(self, armor):
        self.armor = armor

    def equip_shield(self, shield):
        self.shield = shield
        # un-equip two-hander if equipping a shield
        if self.right_hand is not None and enums.WEAPONFLAGS.TWO_HANDED in self.right_hand.flags:
            self.right_hand = None

        if enums.WEAPONFLAGS.VERSATILE in self.right_hand.flags:
            self.right_hand.attackDie = self.right_hand.die1
        else:
            self.right_hand.attackDie = self.right_hand.die2


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
        self.experience = experience

        self.player_race = race
        self.player_class = player_class
        self.abilities = abilities

        if level == 0:  # fresh character init
            self.level = 1
            self.hp_max = hp_dice + self.abilities.CON_MOD
            self.hp = self.hp_max
        else:
            self.level = level
            self.hp_max = hp_dice + (level - 1) * self.abilities.CON_MOD
            self.hp = hp_current

        self.proficiency_skills = skills
        self.proficiency_bonus = self.player_class.get_proficiency_bonus(self.level)
        sys.stdout.flush()
        self.proficiency_weapons = self.player_class.proficiencies.intersection(enums.WEAPONS.Set())
        self.proficiency_armor = self.player_class.proficiencies.intersection(enums.ARMOR.Set())
                            # todo: apply proficiencies from class/race to character
        self.proficiency_tools = set()  # todo: apply proficiencies from class/race to character
        self.saving_throws = self.set_saving_throws()
        self.initiative = self.abilities.DEX_MOD  # todo: proper initiative
        self.temporary_hitpoints = 0  # magical shielding, and such
        self.background = background
        self.equipment = Equipped()
        self.equipment.equip(equipment)  # todo: implement weapons/shields/armor
        self.traits = self.player_race.traits
        self.traits.update(self.player_class.traits)
        self.effects = self.Effect()  # use for trait/status effects - re-apply whenever character refreshes
        self.advantage = enums.ADVANTAGE
        self.disadvantage = enums.ADVANTAGE

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

    def __repr__(self):
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
        s += 'Hitpoints: \t\t\t\t' + '{:,}'.format(self.hp) + '/' +'{:,}'.format(self.hp_max)+'\n'
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

    def get_armor_class(self, atype):  # todo: apply modifiers from various traits, statuses, and spell effects
        # DETERMINE WHAT AC FORMULAS CAN BE USED FOR CHARACTER
        #   CLASSES CAN HAVE DEFENSIVE ARMOR CALCULATIONS(BARBARIAN UNARMORED DEFENCE FOR EXAMPLE)
        # DETERMINE WHICH YIELDS HIGHEST RESULT
        #   THEY DO NOT STACK, SO USE THE BEST ONE
        # TACK ON ANY BONUSES TO AC
        #   SHIELDS TO NOT HAVE A CALCULATION, THEY SIMPLY ADD 2 TO AC, AS AN EXAMPLE
        # RETURN RESULT

        # atype is type of attack, melee, ranged, arcane, etc.
        # todo: ensure atype is obeyed
        if atype: pass  # simply using it to silence the unused error for now.
        # todo: throw defence event related to specific attack type, modify ac if necessary - may need to return
        #  statuses from here for thorns like effects

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

    def right_hand_weapon_attack(self, target):
        # todo: deal with multiple damage types
        self.effects.attack(self, target=target)  # call attack event handler - trigger any registered attack
        advantage = enums.ADVANTAGE.ATTACK in self.advantage
        disadvantage = enums.ADVANTAGE.ATTACK in self.disadvantage
        lucky = enums.TRAIT.LUCKY in self.traits
        attack_roll, critical = misc.attack_roll(advantage, disadvantage, lucky=lucky)


    def check_attack(self, target):
        # todo: deal with multiple damage types
        self.effects.attack(self, target=target)  # call attack event handler - trigger any registered attack
        attack, damage = self.get_attack()
        return 0, None if attack < target.get_armor_class() else damage, self.equipment.right_hand.damage_types[0]

    def take_damage(self, damage):
        # todo: handle death, incapacitation, etc.
        self.hp -= damage

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
        return attack,

    class Effect:
        # todo: complete the event system for player characters
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

        class Event(set):   # minimalist event handler abusing the set class
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

        before_battle = Event(set())    # applies on battle start
        before_turn = Event(set())      # applies on start of each turn
        after_turn = Event(set())       # applies after each turn
        action = Event(set())           # applies whenever a character acts
        attack = Event(set())           # applies whenever a character attacks
        defend = Event(set())           # applies whenever a character defends
        after_battle = Event(set())     # applies whenever a battle ends
        init = Event(set())             # applies on character creation - including loading
        level_up = Event(set())         # applies on levelup
        # class When:
        #     def __init__(self):
        #         self.status = []
        #         self.temporary = []
        #         self.permanent = []
        #
        # def __init__(self):
        #     self.always = self.When()
        #     self.before_turn = self.When()
        #     self.on_action = self.When()
        #     self.after_turn = self.When()


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
#     def calculate_hp_max(self, old_con_mod=None):
#         if old_con_mod is None:
#             old_con_mod = self.con['mod']
#         new_con_mod = functions.ability_mod(self.con['base']+self.con['bonus'])
#         if new_con_mod != old_con_mod:   #if constitution changes, recalculate HP max
#             self.base_hp += self.level * (old_con_mod - new_con_mod)  #base HP max changes by levels times changes in constitution
#         self.hp['base']+=functions.roll(1,20,new_con_mod)  #roll 1d20 +con_mod
#
#     def armor_class(self):
#         return 10+functions.ability_mod(self.dex['current'])  #no armor or shield applied!  chapter 5
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


#wulfgar = init_wulfgar()
#print(wulfgar)

