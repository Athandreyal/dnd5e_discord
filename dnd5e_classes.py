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
            self.skills = {SKILL.SURVIVAL, SKILL.NATURE}
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
        # todo: run all of the trait and status functions, so any bonuses are conferred immediately

        
class Bard(CommonFunctions):
    name = 'Bard'
    hitDie = 8
    class_ability = Ability(strength=0, constitution=0, dexterity=14, intelligence=0, wisdom=0, charisma=15)
    #                       unassigned [13,12,10,8]
    proficiencies = {PROFICIENCY.ARMOR.LIGHT, PROFICIENCY.WEAPONS.SIMPLE, PROFICIENCY.WEAPONS.MARTIAL.CROSSBOW_HAND,
                     PROFICIENCY.WEAPONS.MARTIAL.LONGSWORD, PROFICIENCY.WEAPONS.MARTIAL.RAPIER, PROFICIENCY.WEAPONS.MARTIAL.SHORTSWORD}
    saving_throws = {ABILITY.STR, ABILITY.CON}
    skills = {SKILL.ATHLETICS, SKILL.ACROBATICS, SKILL.SLEIGHT, SKILL.STEALTH, SKILL.ARCANA, SKILL.HISTORY,
              SKILL.INVESTIGATION, SKILL.NATURE, SKILL.RELIGION, SKILL.ANIMAL_HANDLING, SKILL.INSIGHT, SKILL.MEDICINE,
              SKILL.PERCEPTION, SKILL.SURVIVAL, SKILL.DECEPTION, SKILL.INTIMIDATION, SKILL.PERFORMANCE,
              SKILL.PERSUASION}  # TODO : choose ANY 3
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
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Druid(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Druid'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(2, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Fighter(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Fighter'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Monk(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Monk'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 100 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Paladin(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Paladin'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Ranger(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Ranger'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(5, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Rogue(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Rogue'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(4, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Sorcerer(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Sorcerer'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(3, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Warlock(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Warlock'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(4, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)


class Wizard(CommonFunctions):  # TODO: COMPLETE CLASS, LOL
    name = 'Wizard'
    hitDie = 12

    def __init__(self, lvl):
        if lvl == 0:
            self.lvl = 1
            self.wealth = 1000 * misc.Die(4, 4).roll()
        self.proficiency_bonus = 2 + self.get_proficiency_bonus(lvl)
