from dnd5e_enums import *
import dnd5e_misc as misc

# don't have to save everything about their class, just what decisions they've taken, and what it was.
# for example, keep knowledge of any unspent points, or unspent spell slots, etc.
# have class code present options that reflect their current level, rather than read the character to see what options
# it has.

# does mean more complex runtime code, but far less complex character code.

# reference and save character functions to handle decisions that were made, if undefined, decision not yet made.
# collect all bonuses, proficiencies, and damage rolls to be laid over-top of the basic character data here though.


# need to flesh out the attack/defence code before I can fully realise things here,
# because the class/character effects influence it, and I would prefer not to need to constantly reread this later

# should inherit a class with the base functions common to all, such as getter functions, which handle the math
# behind various attributes.  if a class modifies the result away from standard, call the parent function,
# then apply the class specific modification to the result - this way there is one source for bugs, instead of many


class CommonFunctions:
    @staticmethod
    def get_proficiency_bonus(level):
        if level >= 17:
            return 6
        elif level >= 13:
            return 5
        elif level >= 9:
            return 4
        elif level >= 5:
            return 3
        else:
            return 2


class Barbarian(CommonFunctions):
    name = 'Barbarian'
    hitDie = 12
    #Ability(strength=0, constitution=0, dexterity=0, intelligence=0, wisdom=0, charisma=0)
    # unassigned [13,12,10,8]
    proficiencies = {PROFICIENCY.ARMOR.LIGHT, PROFICIENCY.ARMOR.MEDIUM, PROFICIENCY.SHIELDS,
                     PROFICIENCY.WEAPONS.SIMPLE, PROFICIENCY.WEAPONS.MARTIAL}
    saving_throws = {ABILITY.STR, ABILITY.CON}
    skills = {SKILL.ANIMAL_HANDLING, SKILL.ATHLETICS, SKILL.INTIMIDATION, SKILL.NATURE, SKILL.PERCEPTION,
              SKILL.SURVIVAL}  # TODO : CHOOSE 2
    skills_qty = 2

    traits = {CLASS_TRAITS.RAGE, CLASS_TRAITS.UNARMORED_DEFENCE, CLASS_TRAITS.RECKLESS_ATTACK,
              CLASS_TRAITS.DANGER_SENSE, CLASS_TRAITS.EXTRA_ATTACK, CLASS_TRAITS.FAST_MOVEMENT,
              CLASS_TRAITS.FERAL_INSTINCT, CLASS_TRAITS.RELENTLESS_RAGE, CLASS_TRAITS.PERSISTENT_RAGE,
              CLASS_TRAITS.INDOMITABLE_MIGHT, CLASS_TRAITS.PRIMAL_CHAMPION, CLASS_TRAITS.FRENZY,
              CLASS_TRAITS.MINDLESS_RAGE, CLASS_TRAITS.INTIMIDATING_PRESENCE, CLASS_TRAITS.RETALIATION,
              CLASS_TRAITS.SPIRIT_SEEKER, CLASS_TRAITS.BEAR_TOTEM, CLASS_TRAITS.ASPECT_OF_THE_BEAR,
              CLASS_TRAITS.SPIRIT_WALKER, CLASS_TRAITS.BEAR_ATTUNEMENT, CLASS_TRAITS.EAGLE_TOTEM,
              CLASS_TRAITS.ASPECT_OF_THE_EAGLE, CLASS_TRAITS.EAGLE_ATTUNEMENT, CLASS_TRAITS.WOLF_TOTEM,
              CLASS_TRAITS.ASPECT_OF_THE_WOLF, CLASS_TRAITS.WOLF_ATTUNEMENT}
    ability_suggest = {'Strength': 15,
                       'Constitution': 14,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 0,
                       'Charisma': 0
                       }

    def __init__(self, lvl, ability=None, skills=None, background=None, path=None):
        self.class_ability = ability
        if self.class_ability is None:
            self.class_ability = Ability(strength=0, constitution=0, dexterity=0, intelligence=0, wisdom=0, charisma=0)

        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(2, 4).roll()
        self.skills = skills
        if self.skills is None:
            # TODO: MAKE THIS A PLAYER CHOICE, PICK TWO FROM ABOVE.
            self.skills = {SKILL.NATURE, SKILL.INTIMIDATION}
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)

        self.background = background
        if self.background is None:
            self.background = BACKGROUNDS.OUTLANDER  # TODO : make this player chosen
            self.skills.update(self.background.SKILLS)

        # RAGE IS A BARBARIAN BONUS ACTION WITH FOLLOWING ADVANTAGES:
        #       ADV IN STR CHECKS AND SAVING THROWS
        #       BONUS DAMAGE ON MELEE ATTACK
        #       RESIST BLUDGEONING, PIERCING, SLASHING DAMAGE.
        self.rages = 2 + (1 if lvl >= 3 else 0) + (1 if lvl >= 6 else 0) + (1 if lvl >= 12 else 0) \
            + (1 if lvl >= 17 else 0) + (1000000 if lvl >= 20 else 0)
        self.rage_damage = 2 + (1 if lvl >= 9 else 0) + (1 if lvl >= 16 else 0)
        self.brutal_crit_die = (1 if lvl >= 9 else 0) + (1 if lvl >= 13 else 0) + (1 if lvl >= 17 else 0)
        #       ADDITIONAL WEAPON DAMAGE ROLLS ON CRITICAL MELEE ATTACK
        # self.traits = {CLASS_TRAITS.RAGE, CLASS_TRAITS.UNARMORED_DEFENCE, TRAIT.LUCKY}  #lucky added for testing
        self.traits = {CLASS_TRAITS.RAGE, CLASS_TRAITS.UNARMORED_DEFENCE}
        # todo: remove lucky from barbarian, just here for testing
        if lvl >= 2:
            self.traits.update({CLASS_TRAITS.RECKLESS_ATTACK, CLASS_TRAITS.DANGER_SENSE})
        if lvl >= 5:
            self.traits.update({CLASS_TRAITS.EXTRA_ATTACK, CLASS_TRAITS.FAST_MOVEMENT})
        if lvl >= 7:
            self.traits.update({CLASS_TRAITS.FERAL_INSTINCT})
        if lvl >= 11:
            self.traits.remove(CLASS_TRAITS.RAGE)
            self.traits.update({CLASS_TRAITS.RELENTLESS_RAGE})
        if lvl >= 15:
            self.traits.remove(CLASS_TRAITS.RELENTLESS_RAGE)
            self.traits.update({CLASS_TRAITS.PERSISTENT_RAGE})
        if lvl >= 18:
            self.traits.update({CLASS_TRAITS.INDOMITABLE_MIGHT})
        if lvl >= 20:
            self.traits.update({CLASS_TRAITS.PRIMAL_CHAMPION})

        # TODO: PERMIT CHOICE OF PATHS: BERSERKER, OR TOTEM WARRIOR
        self.path = path
        if self.path is None and lvl >= 3:
            self.path = 'Berserker'
        if self.path == 'Berserker':
            self.traits.update({CLASS_TRAITS.FRENZY})
            if lvl >= 6:
                self.traits.update({CLASS_TRAITS.MINDLESS_RAGE})
            if lvl >= 10:
                self.traits.update({CLASS_TRAITS.INTIMIDATING_PRESENCE})
            if lvl >= 14:
                self.traits.update({CLASS_TRAITS.RETALIATION})
        elif self.path == 'Bear_Totem_Warrior':
            self.traits.update({CLASS_TRAITS.SPIRIT_SEEKER, CLASS_TRAITS.BEAR_TOTEM})
            if lvl >= 6:
                self.traits.update({CLASS_TRAITS.ASPECT_OF_THE_BEAR})
            if lvl >= 10:
                self.traits.update({CLASS_TRAITS.SPIRIT_WALKER})
            if lvl >= 14:
                self.traits.update({CLASS_TRAITS.BEAR_ATTUNEMENT})
        elif self.path == 'Eagle_Totem_Warrior':
            self.traits.update({CLASS_TRAITS.SPIRIT_SEEKER, CLASS_TRAITS.EAGLE_TOTEM})
            if lvl >= 6:
                self.traits.update({CLASS_TRAITS.ASPECT_OF_THE_EAGLE})
            if lvl >= 10:
                self.traits.update({CLASS_TRAITS.SPIRIT_WALKER})
            if lvl >= 14:
                self.traits.update({CLASS_TRAITS.EAGLE_ATTUNEMENT})
        elif self.path == 'Wolf_Totem_Warrior':
            self.traits.update({CLASS_TRAITS.SPIRIT_SEEKER, CLASS_TRAITS.WOLF_TOTEM})
            if lvl >= 6:
                self.traits.update({CLASS_TRAITS.ASPECT_OF_THE_WOLF})
            if lvl >= 10:
                self.traits.update({CLASS_TRAITS.SPIRIT_WALKER})
            if lvl >= 14:
                self.traits.update({CLASS_TRAITS.WOLF_ATTUNEMENT})

        
class Bard(CommonFunctions):
    name = 'Bard'
    hitDie = 8
    proficiencies = PROFICIENCY.ARMOR.LIGHT.Set()\
        .union(PROFICIENCY.WEAPONS.SIMPLE.Set())\
        .union({PROFICIENCY.WEAPONS.MARTIAL.CROSSBOW_HAND, PROFICIENCY.WEAPONS.MARTIAL.LONGSWORD,
                PROFICIENCY.WEAPONS.MARTIAL.RAPIER, PROFICIENCY.WEAPONS.MARTIAL.SHORTSWORD})
    saving_throws = {ABILITY.DEX, ABILITY.CHA}
    skills = SKILL.Set()  # TODO: choose any 3
    skills_qty = 3
    ability_suggest = {'Strength': 0,
                       'Constitution': 0,
                       'Dexterity': 14,
                       'Intelligence': 0,
                       'Wisdom': 0,
                       'Charisma': 15
                       }
    background = BACKGROUNDS.PERFORMER  # TODO : make this player chosen
    # TODO: FINISH THE BARD....
    
    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)

    def get_proficiency_bonus(self, level):  # todo: apply the bardic trait jack of all trades.
        base = super().get_proficiency_bonus(level)
        return base

        
class Cleric(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Cleric'
    hitDie = 8
    skills = {SKILL.HISTORY, SKILL.INSIGHT, SKILL.MEDICINE, SKILL.PERSUASION, SKILL.RELIGION}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 14,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 15,
                       'Charisma': 0
                       }
    saving_throws = {ABILITY.WIS, ABILITY.CHA}
    proficiencies = PROFICIENCY.ARMOR.LIGHT.Set() \
        .union(PROFICIENCY.ARMOR.MEDIUM.Set()) \
        .union(PROFICIENCY.SHIELDS.Set()) \
        .union(PROFICIENCY.WEAPONS.SIMPLE.Set())

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Druid(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Druid'
    hitDie = 8
    skills = {SKILL.ARCANA, SKILL.ANIMAL_HANDLING, SKILL.INSIGHT, SKILL.MEDICINE, SKILL.NATURE, SKILL.PERCEPTION,
              SKILL.RELIGION, SKILL.SURVIVAL}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 14,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 15,
                       'Charisma': 0
                       }
    saving_throws = {ABILITY.INT, ABILITY.WIS}
    proficiencies = PROFICIENCY.ARMOR.LIGHT.Set() \
        .union(PROFICIENCY.ARMOR.MEDIUM.Set()) \
        .union(PROFICIENCY.ARMOR.LIGHT.Set()) \
        .union(PROFICIENCY.SHIELDS.Set()) \
        .union(PROFICIENCY.WEAPONS.SIMPLE.Set()).difference({PROFICIENCY.WEAPONS.SIMPLE.CROSSBOW,
                                                             PROFICIENCY.WEAPONS.SIMPLE.CROSSBOW_LIGHT,
                                                             PROFICIENCY.WEAPONS.SIMPLE.GREATCLUB,
                                                             PROFICIENCY.WEAPONS.SIMPLE.HANDAXE,
                                                             PROFICIENCY.WEAPONS.SIMPLE.LIGHT_HAMMER,
                                                             PROFICIENCY.WEAPONS.SIMPLE.SHORTBOW})


    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(2, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Fighter(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Fighter'
    hitDie = 10
    skills = {SKILL.ACROBATICS, SKILL.ANIMAL_HANDLING, SKILL.ATHLETICS, SKILL.HISTORY, SKILL.INSIGHT,
              SKILL.INTIMIDATION, SKILL.PERCEPTION, SKILL.SURVIVAL}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 14,
                       'Dexterity': 15,
                       'Intelligence': 0,
                       'Wisdom': 0,
                       'Charisma': 0
                       }
    saving_throws = {ABILITY.STR, ABILITY.CON}
    proficiencies = PROFICIENCY.ARMOR.Set() \
        .union(PROFICIENCY.SHIELDS.Set()) \
        .union(PROFICIENCY.WEAPONS.Set().difference({PROFICIENCY.WEAPONS.GENERIC}))
    # todo, exclude PROFICIENCY.WEAPONS.GENERIT.Set() when generis has a Set()

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Monk(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Monk'
    hitDie = 8
    skills = {SKILL.ACROBATICS, SKILL.ATHLETICS, SKILL.HISTORY, SKILL.INSIGHT, SKILL.RELIGION, SKILL.STEALTH}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 15,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 14,
                       'Charisma': 0
                       }
    saving_throws = {ABILITY.STR, ABILITY.DEX}
    proficiencies = PROFICIENCY.WEAPONS.SIMPLE.Set().union({PROFICIENCY.WEAPONS.MARTIAL.SHORTSWORD})
    # todo: enable picking a tool proficiency


    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 100 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Paladin(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Paladin'
    hitDie = 10
    SKILLS = {SKILL.ATHLETICS, SKILL.INSIGHT, SKILL.INTIMIDATION, SKILL.MEDICINE, SKILL.PERSUASION, SKILL.RELIGION}
    skills_qty = 2
    ability_suggest = {'Strength': 15,
                       'Constitution': 0,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 0,
                       'Charisma': 14
                       }
    saving_throws = {ABILITY.WIS, ABILITY.CHA}
    proficiencies = PROFICIENCY.ARMOR.Set().union(PROFICIENCY.SHIELDS.Set()) \
        .union(PROFICIENCY.WEAPONS.Set().difference({PROFICIENCY.WEAPONS.GENERIC}))
    # todo, exclude PROFICIENCY.WEAPONS.GENERIT.Set() when generis has a Set()

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Ranger(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Ranger'
    hitDie = 10
    skills = {SKILL.ANIMAL_HANDLING, SKILL.ATHLETICS, SKILL.INSIGHT, SKILL.INVESTIGATION, SKILL.NATURE,
              SKILL.PERCEPTION, SKILL.STEALTH, SKILL.SURVIVAL}
    skills_qty = 3
    ability_suggest = {'Strength': 0,
                       'Constitution': 0,
                       'Dexterity': 15,
                       'Intelligence': 0,
                       'Wisdom': 14,
                       'Charisma': 0
                       }
    saving_throws = {ABILITY.STR, ABILITY.DEX}
    proficiencies = PROFICIENCY.ARMOR.Set().difference(PROFICIENCY.ARMOR.HEAVY.Set()) \
        .union(PROFICIENCY.SHIELDS.Set()) \
        .union(PROFICIENCY.WEAPONS.Set().difference({PROFICIENCY.WEAPONS.GENERIC}))

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Rogue(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Rogue'
    hitDie = 8
    skills = {SKILL.ACROBATICS, SKILL.ATHLETICS, SKILL.DECEPTION, SKILL.INSIGHT, SKILL.INTIMIDATION,
              SKILL.INVESTIGATION, SKILL.PERCEPTION, SKILL.PERFORMANCE, SKILL.PERSUASION, SKILL.SLEIGHT, SKILL.STEALTH}
    skills_qty = 4
    ability_suggest = {'Strength': 0,
                       'Constitution': 0,
                       'Dexterity': 15,
                       'Intelligence': 14,
                       'Wisdom': 0,
                       'Charisma': 0
                       }
    saving_throws = {ABILITY.DEX, ABILITY.INT}
    proficiencies = PROFICIENCY.ARMOR.LIGHT.Set().union(PROFICIENCY.WEAPONS.SIMPLE.Set()) \
        .union({PROFICIENCY.WEAPONS.MARTIAL.CROSSBOW_HAND, PROFICIENCY.WEAPONS.MARTIAL.LONGSWORD,
                PROFICIENCY.WEAPONS.MARTIAL.RAPIER, PROFICIENCY.WEAPONS.MARTIAL.SHORTSWORD})

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(4, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Sorcerer(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Sorcerer'
    hitDie = 6
    skills = {SKILL.ARCANA, SKILL.DECEPTION, SKILL.INSIGHT, SKILL.INTIMIDATION, SKILL.PERSUASION, SKILL.RELIGION}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 14,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 0,
                       'Charisma': 15
                       }
    saving_throws = {ABILITY.CHA, ABILITY.CON}
    proficiencies = {PROFICIENCY.WEAPONS.SIMPLE.DAGGER,PROFICIENCY.WEAPONS.SIMPLE.DART,
                     PROFICIENCY.WEAPONS.SIMPLE.SLING, PROFICIENCY.WEAPONS.SIMPLE.QUARTERSTAFF,
                     PROFICIENCY.WEAPONS.SIMPLE.CROSSBOW_LIGHT}

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(3, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Warlock(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Warlock'
    hitDie = 8
    skills = {SKILL.ARCANA, SKILL.DECEPTION, SKILL.HISTORY, SKILL.INTIMIDATION, SKILL.INVESTIGATION, SKILL.NATURE,
              SKILL.RELIGION}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 14,
                       'Dexterity': 0,
                       'Intelligence': 0,
                       'Wisdom': 0,
                       'Charisma': 15
                       }
    saving_throws = {ABILITY.WIS, ABILITY.CHA}
    proficiencies = PROFICIENCY.ARMOR.LIGHT.Set().union(PROFICIENCY.WEAPONS.SIMPLE.Set())


    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(4, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Wizard(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Wizard'
    hitDie = 6
    skills = {SKILL.ARCANA, SKILL.HISTORY, SKILL.INSIGHT, SKILL.INVESTIGATION, SKILL.MEDICINE, SKILL.RELIGION}
    skills_qty = 2
    ability_suggest = {'Strength': 0,
                       'Constitution': 0,
                       'Dexterity': 0,
                       'Intelligence': 15,
                       'Wisdom': 0,
                       'Charisma': 14
                       }
    saving_throws = {ABILITY.INT, ABILITY.WIS}
    proficiencies = {PROFICIENCY.WEAPONS.SIMPLE.DAGGER,PROFICIENCY.WEAPONS.SIMPLE.DART,
                     PROFICIENCY.WEAPONS.SIMPLE.SLING, PROFICIENCY.WEAPONS.SIMPLE.QUARTERSTAFF,
                     PROFICIENCY.WEAPONS.SIMPLE.CROSSBOW_LIGHT}

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(4, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)
