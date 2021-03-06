import dnd5e_misc as misc
import dnd5e_functions as functions

debug = lambda *args, **kwargs: False  #dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug
# todo: find ALL default argument expressions in my code, and replace them with =None and default it inside the
#  function, see :   https://www.toptal.com/python#hiring-guide

# fuck Enum with a broken rusty pipe - if I can't have nested access, it can die in a fire


class Set:
    @classmethod
    def Set(cls):  # recursively chase it out, if its a branch, find the leaves.
        attr = (getattr(cls, i) for i in dir(cls) if not callable(i) and i.upper() == i)
#        s = {cls}  # don't include self in the
        s = set()
        for a in attr:
            if hasattr(a, 'Set'):
                s.update(a.Set())
            else:
                s.add(a)
        return s


class ABILITY(Set):
    # ATTRIBUTES
    class STR:
        def __init__(self):
            self.affectors = []

    class CON:
        def __init__(self):
            self.affectors = []

    class DEX:
        def __init__(self):
            self.affectors = []

    class INT:
        def __init__(self):
            self.affectors = []

    class WIS:
        def __init__(self):
            self.affectors = []

    class CHA:
        def __init__(self):
            self.affectors = []


class Ability:

    # ATTRIBUTES
    # STR
    # melee damage, carry limit,
    # ACTIONS: force lock/door, break bonds, hang onto, topple thing, halt thing, squeeze through
    # CON
    # health, stamina, vital force,
    # ACTIONS: hold breath, march/labour duration, sleeplessness, starvation/thirst, consumption(food/ale)
    # DEX
    # range damage,
    # ACTIONS: control heavy cart, pick lock, disable trap, bind prisoner, escape bonds,
    # play instrument, craft small/detailed object
    # INT
    # spell damage, spell resist difficulty, education, memory, logic, reasoning,
    # ACTIONS: estimate value, create disguise, forge document, recall craft/trade lore, win game of skill
    # WIS
    # read body language, feelings, notice environment, medical care.
    # CHA
    # entertain, interact with others, effects confidence and eloquence,
    # determines success of charming or commanding personalities,
    # ACTIONS: best person to meet, blend in to get a feel for things
    # STR_MOD   # USED IN STR CHECKS
    # CON_MOD   # USED IN CON CHECKS
    # DEX_MOD   # USED IN DEX CHECKS
    # INT_MOD   # USED IN INT CHECKS
    # WIS_MOD   # USED IN WIS CHECKS
    # CHA_MOD   # USED IN CHA CHECKS

    def __init__(self, strength=0, constitution=0, dexterity=0, intelligence=0, wisdom=0, charisma=0):
        """default behaviour is to assign the six values using a standard array which is [15, 14, 13, 12, 10, 8]
        generally, you will place 15 into the most important ability, 14 into the second, ... 8 into the least important

        These determine your saving throw bonus base values via (ability // 2 - 5)
        class, race, and magic can confer additional bonuses on top"""
        self._max_STR = 20
        self._max_CON = self._max_STR
        self._max_DEX = self._max_STR
        self._max_INT = self._max_STR
        self._max_WIS = self._max_STR
        self._max_CHA = self._max_STR
        self.STR, self.CON, self.DEX = strength, constitution, dexterity
        self.INT, self.WIS, self.CHA = intelligence, wisdom, charisma
        mods = self.get_mods()
        self.STR_MOD, self.CON_MOD, self.DEX_MOD = mods[:3]
        self.INT_MOD, self.WIS_MOD, self.CHA_MOD = mods[3:]

    def __setattr__(self, name, value):
        debug('abilities.__setattr__ called with', name, value)
        if name in 'STR, CON, DEX, INT, WIS, CHA':
            max_val = getattr(self, '_max_'+name)
            super().__setattr__(name, min(max_val, value))
        else:
            super().__setattr__(name, value)

    def set_max(self, **kwargs):
        for name in kwargs:
            setattr(self, '_max_' + name, kwargs[name])

    def set(self, strength=0, constitution=0, dexterity=0, intelligence=0, wisdom=0, charisma=0):
        self.STR = strength
        self.CON = constitution
        self.DEX = dexterity
        self.INT = intelligence
        self.WIS = wisdom
        self.CHA = charisma
        self.update_mods()

    def add(self, strength=0, constitution=0, dexterity=0, intelligence=0, wisdom=0, charisma=0):
        self.STR += strength
        self.CON += constitution
        self.DEX += dexterity
        self.INT += intelligence
        self.WIS += wisdom
        self.CHA += charisma
        self.update_mods()

    def get_mods(self):
        return (
                misc.ability_mod(self.STR),
                misc.ability_mod(self.CON),
                misc.ability_mod(self.DEX),
                misc.ability_mod(self.INT),
                misc.ability_mod(self.WIS),
                misc.ability_mod(self.CHA),
                )

    def update_mods(self):
        mods = self.get_mods()
        self.STR_MOD, self.CON_MOD, self.DEX_MOD = mods[:3]
        self.INT_MOD, self.WIS_MOD, self.CHA_MOD = mods[3:]

    def __repr__(self, mod=False):
        s = ' \tSTR: \t' + str(self.STR) + ('' if not mod else ('\tMOD: ' + str(self.STR_MOD))) + '\n'
        s += ' \tCON: \t' + str(self.CON) + ('' if not mod else ('\tMOD: ' + str(self.CON_MOD))) + '\n'
        s += ' \tDEX: \t' + str(self.DEX) + ('' if not mod else ('\tMOD: ' + str(self.DEX_MOD))) + '\n'
        s += ' \tINT: \t' + str(self.INT) + ('' if not mod else ('\tMOD: ' + str(self.INT_MOD))) + '\n'
        s += ' \tWIS: \t' + str(self.WIS) + ('' if not mod else ('\tMOD: ' + str(self.WIS_MOD))) + '\n'
        s += ' \tCHA: \t' + str(self.CHA) + ('' if not mod else ('\tMOD: ' + str(self.CHA_MOD))) + '\n'
        return s


class SKILL(Set):
    class ATHLETICS:
        def __init__(self):
            self.affectors = []

    class ACROBATICS:
        def __init__(self):
            self.affectors = []

    class SLEIGHT:
        def __init__(self):
            self.affectors = []

    class STEALTH:
        def __init__(self):
            self.affectors = []

    class ARCANA:
        def __init__(self):
            self.affectors = []

    class HISTORY:
        def __init__(self):
            self.affectors = []

    class INVESTIGATION:
        def __init__(self):
            self.affectors = []

    class NATURE:
        def __init__(self):
            self.affectors = []

    class RELIGION:
        def __init__(self):
            self.affectors = []

    class ANIMAL_HANDLING:
        def __init__(self):
            self.affectors = []

    class INSIGHT:
        def __init__(self):
            self.affectors = []

    class MEDICINE:
        def __init__(self):
            self.affectors = []

    class PERCEPTION:
        def __init__(self):
            self.affectors = []

    class SURVIVAL:
        def __init__(self):
            self.affectors = []

    class DECEPTION:
        def __init__(self):
            self.affectors = []

    class INTIMIDATION:
        def __init__(self):
            self.affectors = []

    class PERFORMANCE:
        def __init__(self):
            self.affectors = []

    class PERSUASION:
        def __init__(self):
            self.affectors = []


class Skill:
    def __init__(self, ability_set=None):
        self.__abilities__ = ability_set  # used TO clearing bonuses or temporary values, to restore original XXX_MOD
        self.ATHLETICS = self.__abilities__.STR_MOD  # SWIMMING, JUMPING, CLIMBING
        self.ACROBATICS = self.__abilities__.DEX_MOD  # dives/rolls/flips - evasion
        self.SLEIGHT = self.__abilities__.DEX_MOD  # theft
        self.STEALTH = self.__abilities__.DEX_MOD  # conceal, sneak upon/away
        self.ARCANA = self.__abilities__.INT_MOD
        # spell lore, magic items, eldritch symbols, arcane traditions, planes of existence and their inhabitants
        self.HISTORY = self.__abilities__.INT_MOD
        # historical lore, legendary people, ancient kingdoms, past disputes, recent wars, lost civilisations
        self.INVESTIGATION = self.__abilities__.INT_MOD
        # locate objects, discern type of wound, determine weak points, reading ancient scrolls/texts
        self.NATURE = self.__abilities__.INT_MOD  # lore about terrain, animals, plants, weather, etc
        self.RELIGION = self.__abilities__.INT_MOD
        # recall religious lore, deities, rites/prayers, hierarchies, holy symbols, cults and their practice
        self.ANIMAL_HANDLING = self.__abilities__.WIS_MOD
        # calm animal, avoid spooked mount, discern animal's intentions, control mount through risky maneuver
        self.INSIGHT = self.__abilities__.WIS_MOD  # determine creature intentions(detect lie, predict move)
        self.MEDICINE = self.__abilities__.WIS_MOD  # diagnose injury/illness, tend injury/illness
        self.PERCEPTION = self.__abilities__.WIS_MOD
        # spot/hear/detect presence of something.  hear conversation, eavesdrop, hear stealthy creatures sneaking
        # detect traps or ambushes, detect undead
        self.SURVIVAL = self.__abilities__.WIS_MOD
        # follow tracks, hunt game, navigate wastelands, identify signs of habitation(wild or civilised), predict
        # weather, avoid natural hazards(quicksand)
        self.DECEPTION = self.__abilities__.CHA_MOD
        # deceive via words or action, from ambiguity to lies.  fast talk guard, con merchant, hustle gamblers, wear
        # disguise, dull suspicions with assurances
        self.INTIMIDATION = self.__abilities__.CHA_MOD  # influence via overt threats, hostile actions, and
        # violence, obtaining information, convincing threats to back down, coercion
        self.PERFORMANCE = self.__abilities__.CHA_MOD  # music, dance, acting, storytelling, showmanship
        self.PERSUASION = self.__abilities__.CHA_MOD  # acting in good faith, foster trust, requests, etiquette.
        self.update_mods()

    def update_mods(self):
        self.ATHLETICS = self.__abilities__.STR_MOD
        self.ACROBATICS = self.__abilities__.DEX_MOD
        self.SLEIGHT = self.__abilities__.DEX_MOD
        self.STEALTH = self.__abilities__.DEX_MOD
        self.ARCANA = self.__abilities__.INT_MOD
        self.HISTORY = self.__abilities__.INT_MOD
        self.INVESTIGATION = self.__abilities__.INT_MOD
        self.NATURE = self.__abilities__.INT_MOD
        self.RELIGION = self.__abilities__.INT_MOD
        self.ANIMAL_HANDLING = self.__abilities__.WIS_MOD
        self.INSIGHT = self.__abilities__.WIS_MOD
        self.MEDICINE = self.__abilities__.WIS_MOD
        self.PERCEPTION = self.__abilities__.WIS_MOD
        self.SURVIVAL = self.__abilities__.WIS_MOD
        self.DECEPTION = self.__abilities__.CHA_MOD
        self.INTIMIDATION = self.__abilities__.CHA_MOD
        self.PERFORMANCE = self.__abilities__.CHA_MOD
        self.PERSUASION = self.__abilities__.CHA_MOD

    def add(self, **kwargs):
        for k, v in kwargs:
            self.__dict__[k] = v

    def __repr__(self):
        s = 'Proficiencies'

        for a in dir(self):
            if a == a.upper():
                s += '\n\t' + a + '=' + str(getattr(self, a))


#    def proficiencies(self, bonus, proficiencies):
#        for proficiency in proficiencies:  #list of enums


#    def add(self, skills):  #used for combining proficiencies.

class VISION(Set):
    DARK = None
    DIM = None
    BRIGHT = None

    def __init__(self, dark=0, dim=300, bright=3000):
        #  how far away you can normally see in open terrain
        self.DARK = dark
        self.DIM = dim
        self.BRIGHT = bright


class SIZE(Set):
    # control is reach of creature for 'touching' aspects.
    # occupy is space creature needs in oder to be present somewhere
    class S:
        def __init__(self, carry, hitdie, control, occupy):
            self.CARRY = carry
            self.HITDIE = hitdie
            self.CONTROL = control
            self.OCCUPY = occupy

    class TINY(S):
        def __init__(self): super().__init__(3.75, 4, 2.5, 1)

    class SMALL(S):
        def __init__(self): super().__init__(7.5, 6, 4, 2)

    class MEDIUM(S):
        def __init__(self): super().__init__(15, 8, 5, 3)

    class LARGE(S):
        def __init__(self): super().__init__(30, 10, 10, 5)

    class HUGE(S):
        def __init__(self): super().__init__(60, 12, 15, 8)

    class GARGANTUAN(S):
        def __init__(self): super().__init__(120, 20, 20, 10)


class ATTACK(Set):
    class MELEE:
        def __init__(self):
            self.affectors = []

    class RANGED:
        def __init__(self):
            self.affectors = []

    class ARCANE:
        def __init__(self):
            self.affectors = []


class DEFENCE(Set):
    class MELEE:
        def __init__(self):
            self.affectors = []

    class RANGED:
        def __init__(self):
            self.affectors = []

    class ARCANE:
        def __init__(self):
            self.affectors = []


class TRAIT(Set):
    # todo: replace the ints with functions references expecting source and target objects
    class ABILITY_VERSATILITY:
        def __init__(self, *args, **kwargs): pass  # INCREASE TWO ABILITY SCORES OF YOUR CHOICE, OTHER THAN CHARISMA, BY 1

    class ARTIFICERS_LORE:
        def __init__(self, *args, **kwargs): pass  # DOUBLE PROFICIENCY BONUS ON INTELLIGENCE CHECKS RELATING TO ARCANE,
    # ALCHEMICAL, OR MECHANICAL DEVICES.

    BRAVE = functions.RaceTraitBrave  # ADVANTAGE RESISTING FRIGHTENED

    class CANTRIP:
        def __init__(self, *args, **kwargs): pass  # KNOW ONE SPELL FROM THE WIZARD SPELL SET, USES INTELLIGENCE TO CAST

    class COMMON_PERCEPTION:
        def __init__(self, *args, **kwargs): pass  # PASSIVE PERCEPTION OF 10

    class DARKVISION:
        def __init__(self, *args, **kwargs): pass  # CAN SEE IN DIM AS IF BRIGHT LIGHT TO 60FT

    class DRACONIC_ANCESTRY_BLACK:
        def __init__(self, *args, **kwargs): pass  # ACID      DAMAGE TYPE, 5X30FT,  DC(DEX), 50% ACID      RESIST

    class DRACONIC_ANCESTRY_BLUE:
        def __init__(self, *args, **kwargs): pass  # LIGHTING  DAMAGE TYPE, 5X30FT,  DC(DEX), 50% LIGHTNING RESIST

    class DRACONIC_ANCESTRY_BRASS:
        def __init__(self, *args, **kwargs): pass  # FIRE      DAMAGE TYPE, 5X30FT,  DC(DEX), 50% FIRE      RESIST

    class DRACONIC_ANCESTRY_BRONZE:
        def __init__(self, *args, **kwargs): pass  # LIGHTNING DAMAGE TYPE, 5X30FT,  DC(DEX), 50% LIGHTNING RESIST

    class DRACONIC_ANCESTRY_COPPER:
        def __init__(self, *args, **kwargs): pass  # ACID      DAMAGE TYPE, 5X30FT,  DC(DEX), 50% ACID      RESIST

    class DRACONIC_ANCESTRY_GOLD:
        def __init__(self, *args, **kwargs): pass  # FIRE      DAMAGE TYPE, 15X15FT, DC(DEX), 50% FIRE      RESIST

    class DRACONIC_ANCESTRY_GREEN:
        def __init__(self, *args, **kwargs): pass  # POISON    DAMAGE TYPE, 15X15FT, DC(CON), 50% POISON    RESIST

    class DRACONIC_ANCESTRY_RED:
        def __init__(self, *args, **kwargs): pass  # FIRE      DAMAGE TYPE, 15X15FT, DC(DEX), 50% FIRE      RESIST

    class DRACONIC_ANCESTRY_SILVER:
        def __init__(self, *args, **kwargs): pass  # COLD      DAMAGE TYPE, 15X15FT, DC(CON), 50% COLD      RESIST

    class DRACONIC_ANCESTRY_WHITE:
        def __init__(self, *args, **kwargs): pass  # COLD      DAMAGE TYPE, 15X15FT, DC(CON), 50% COLD      RESIST

    class DRACONIC_BREATH_WEAPON:
        def __init__(self, *args, **kwargs): pass
    # ANCESTRAL DAMAGE TYPE ATTACK, DC8+CON_MOD+PROFICIENCY.  HALF DAMAGE FOR SUCCESSFUL RESIST.  2D6 UNTIL LVL6, 3D6
    # UNTIL 11, 4D6 UNTIL 16, AND 5D6 16+

    class DRACONIC_DAMAGE_RESISTANCE:
        def __init__(self, *args, **kwargs): pass  # RECEIVE ONLY 50% DAMAGE AGAINST ANCESTRAL TYPE

    class DROW_MAGIC:
        def __init__(self, *args, **kwargs): pass
    # DANCING LIGHTS AT LVL 1, FAERIE FIRE AT LVL 3, DARKNESS AT LVL 5, ONCE EACH PER DAY, USES CHARISMA TO CAST.

    class DROW_WEAPON_TRAINING:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH RAPIERS, SHORTSWORDS, HAND CROSSBOWS

    class DWARVEN_ARMOR_TRAINING:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY IN LIGHT AND MEDIUM ARMOR

    class DWARVEN_COMBAT_TRAINING:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH BATTLEAXE, HANDAXE, THROWING HAMMER, AND WARHAMMER

    class DWARVEN_RESILIENCE:
        def __init__(self, *args, **kwargs): pass  # ADVANTAGE ON SAVING THROWS VS POISON, RESISTS POISON TAKING ONLY 50% DAMAGE

    class DWARVEN_TOUGHNESS:
        def __init__(self, *args, **kwargs): pass  # MAXIMUM HP INCREASED BY LEVEL

    class ELVEN_WEAPON_TRAINING:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH LONGSWORD, SHORTSWORD, SHORTBOW, AND LONGBOW

    class FEY_ANCESTRY:
        def __init__(self, *args, **kwargs): pass  # ADVANTAGE IN SAVING THROWS AGAINST CHARM, IMMUNE TO ARCANE SLEEP

    class FLEET_OF_FOOT:
        def __init__(self, *args, **kwargs): pass  # BASE WALKING SPEED IS 35FT

    class GNOME_CUNNING:
        def __init__(self, *args, **kwargs): pass  # ADVANTAGE ON ALL INTELLIGENCE, WISDOM, AND CHARISMA SAVING THROWS VS MAGIC

    class HALFLING_NIMBLENESS:
        def __init__(self, *args, **kwargs): pass  # CAN MOVE THROUGH THE SPACE OF ANY CREATURE AT LEAST ONE SIZE LARGER.

    class HELLISH_RESISTANCE:
        def __init__(self, *args, **kwargs): pass  # RESISTANCE AGAINST FIRE DAMAGE, TAKING ONLY 50% DAMAGE

    class INFERNAL_LEGACY:
        def __init__(self, *args, **kwargs): pass
    # KNOW THE THAUMATURGY CANTRIP, CAST ONCE PER DAY, HELLISH REBUKE AT LVL3 ONCE PER DAY AT 2ND LEVEL,
    # DARKNESS AT LVL 5 ONCE PER DAY. USING CHARISMA FOR SPELL CASTING

    class KEEN_SENSES:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY IN THE PERCEPTION SKILL

    LUCKY = functions.RaceTraitLucky
    # WHEN YOU ROLL A 1 ON AN ATTACK ROLL, ABILITY CHECK, OR SAVING THROW, ROLL AGAIN AND USE THE SECOND ROLL

    class MASK_OF_THE_WILD:
        def __init__(self, *args, **kwargs): pass
    # CAN HIDE WHENEVER PARTIAL OBSCUREMENT OCCURS, SUCH AS SMOKE, RAIN, SNOW, FOLIAGE, ETC

    class MENACING:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY IN THE INTIMIDATION SKILL

    class NATURAL_ILLUSIONIST:
        def __init__(self, *args, **kwargs): pass  # KNOW THE MINOR ILLUSION CANTRIP, USES INTELLIGENCE FOR CASTING

    class NATURALLY_STEALTHY:
        def __init__(self, *args, **kwargs): pass  # CAN ATTEMPT TO HIDE WHEN OBSCURED BY A CREATURE AT LEAST ONE SIZE LARGER

    class RELENTLESS_ENDURANCE:
        def __init__(self, *args, **kwargs): pass
    # WHEN REDUCED TO 0 HITPOINTS BUT NOT KILLED, WILL DROP TO 1 HP INSTEAD, RESETS VIA LONG REST

    class SAVAGE_ATTACKS:
        def __init__(self, *args, **kwargs): pass  # CAN ROLL ANOTHER ATTACK DIE ON CRITICAL HITS, ADDING ON MORE DAMAGE

    class SKILL_VERSATILITY:
        def __init__(self, *args, **kwargs): pass  # GAIN PROFICIENCY IN TWO SKILL SOF YOUR CHOOSING AT CHARACTER CREATION

    class SPEAK_WITH_SMALL_BEASTS:
        def __init__(self, *args, **kwargs): pass  # CAN CONVEY SIMPLE IDEAS TO SMALL/TINY BEASTS.

    class STONE_CUNNING:
        def __init__(self, *args, **kwargs): pass  # DOUBLE PROFICIENCY BONUS FOR HISTORY/LORE RELATING TO STONE

    class STOUT_RESILIENCE:
        def __init__(self, *args, **kwargs): pass  # ADVANTAGE ON SAVING THROWS VS POISON, RESISTS POISON TAKING ONLY 50% DAMAGE

    class SUNLIGHT_SENSITIVITY:
        def __init__(self, *args, **kwargs): pass
    # DISADVANTAGE IN ATTACK ROLLS AND PERCEPTION CHECKS THAT RELY ON SIGHT IF YOU OR TARGET ARE IN DIRECT SUNLIGHT

    class SUPERIOR_DARKVISION:
        def __init__(self, *args, **kwargs): pass  # RADIUS OF 120FT DIM LIGHT LIKE BRIGHT LIGHT

    class TOOL_BREWER_PROFICIENCY:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_MASON_PROFICIENCY:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_SMITH_PROFICIENCY:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_SUPPLIES_PROFICIENCY:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_TINKER_PROFICIENCY:
        def __init__(self, *args, **kwargs): pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TRANCE:
        def __init__(self, *args, **kwargs): pass  # ELVEN MEDITATION, REPLACES SLEEP FOR REST, 2X AS EFFECTIVE,
    # SHORT REST IN 1HR, LONG REST IN 4HR

    # unarmored default defence of 10 + dex_mod
    NATURAL_DEFENCE = functions.TraitNaturalDefence


# noinspection PyPep8Naming
# ^^be silent damn you
class CLASS_TRAITS(Set):
    # ADVANTAGE TO DC(STR) AND SAVE(STR), BONUS DAMAGE
    RAGE = functions.ClassTraitRage

    # WHILE NOT WEARING ARMOR, DEFENCE IS 10+CON_MOD, PLUS SHIELD IF EQUIPPED.
    UNARMORED_DEFENCE = functions.ClassTraitUnarmoredDefence

    # FIRST ATTACK OF TURN HAS ADVANTAGE, BUT ATTACKS AGAINST YOU HAVE ADVANTAGE
    RECKLESS_ATTACK = functions.ClassTraitRecklessAttack

    # ADVANTAGE DC(DEX) ON PERCEPTION, INEFFECTIVE IF BLINDED, DEAFENED, INCAPACITATED
    DANGER_SENSE = functions.ClassTraitDangerSense

    # MAY ATTACK ADDITIONAL TIMES PER TURN, SEE CLASS STATS FOR NUMBER OF ATTACKS
    EXTRA_ATTACK = functions.ClassTraitExtraAttack

    # GAIN 10FT/SEC IF NOT WEARING ARMOR
    FAST_MOVEMENT = functions.ClassTraitFastMovement

    # ADVANTAGE ON INITIATIVE, CAN RAGE AND THEN ACT NORMALLY IF SURPRISED
    FERAL_INSTINCT = functions.ClassTraitFeralInstinct

    # ADDS ADDITION ATTACK ROLLS ON CRITICAL, 1 AT LVL9, 2 AT LVL13, 3 AT LVL17
    BRUTAL_CRITICAL = functions.ClassTraitBrutalCritical

    # IF 0HP, +1 IF PASS DC10(CON), +DC5 EVERY TIME THIS IS USED UNTIL REST
    RELENTLESS_RAGE = functions.ClassTraitRelentlessRage

    # RAGE ENDS ONLY IF UNCONSCIOUS, OR CHOSEN TO END
    PERSISTENT_RAGE = functions.ClassTraitPersistentRage

    # IF ROLL(STR) < STR, USE STR INSTEAD.
    INDOMITABLE_MIGHT = functions.ClassTraitIndomitableMight

    # MAXIMUM STR AND CON +4, MAXIMUM POSSIBLE +4 TO 24
    PRIMAL_CHAMPION = functions.ClassTraitPrimalChampion

    # CAN MAKE BONUS ATTACK AT END OF EACH TURN, SUFFER EXHAUSTION +1 AT END OF RAGE
    FRENZY = functions.ClassTraitFrenzy

    # IMMUNE TO CHARM AND FRIGHTEN WHILE RAGING, SUSPENDS EFFECT WHILE RAGING
    MINDLESS_RAGE = functions.ClassTraitMindlessRage

    # CAN USE AN ACTION TO FRIGHTEN VISIBLE TARGET WITHIN 30 FT,
    # CHA_MOD UNTIL END OF YOUR NEXT TURN. ENDS IF 60FT AWAY, OR LOSES SIGHT OF YOU
    INTIMIDATING_PRESENCE = functions.ClassTraitIntimidatingPresence

    # CAN USE REACTION TO MELEE ATTACK A CREATURE WITHIN 5FT WHICH HARMS YOU
    RETALIATION = functions.ClassTraitRetaliation

    # MAY CAST BEAST SENSE, AND SPEAK WITH ANIMALS, AS RITUALS
    SPIRIT_SEEKER = functions.ClassTraitSpiritSeeker

    # CAST COMMUNE WITH NATURE AS RITUAL - SUMMONS SPIRIT ANIMAL TO CONVEY THE INFO YOU SEEK
    SPIRIT_WALKER = functions.ClassTraitSpiritWalker

    # WHILE RAGING, RESIST ALL DAMAGE EXCEPT PSYCHIC
    BEAR_TOTEM = functions.ClassTraitTotemBear

    # WHILE RAGING, IF NOT WEARING HEAVY ARMOR OTHER CREATURES HAVE DISADVANTAGE ON
    # OPPORTUNITY ATTACK ROLLS, CAN USE DASH AS BONUS ACTION
    EAGLE_TOTEM = functions.ClassTraitTotemEagle

    # WHILE RAGING, PARTY HAS ADVANTAGE ON MELEE VS ANY HOSTILE WITHIN 5FT OF YOU
    WOLF_TOTEM = functions.ClassTraitTotemWolf

    # CARRYING CAPACITY DOUBLES, ADVANTAGE STR TO PUSH, PULL, LIFT, BREAK
    ASPECT_OF_THE_BEAR = functions.ClassTraitAspectBear

    # SEE 1 MILE AWAY AS IF 100FT AWAY. NO PERCEPTION DISADVANTAGE IN DIM LIGHT
    ASPECT_OF_THE_EAGLE = functions.ClassTraitAspectEagle

    # CAN TRACK CREATURES WHILE AT FAST PACE, CAN MOVE STEALTHILY AT NORMAL
    ASPECT_OF_THE_WOLF = functions.ClassTraitAspectWolf

    # WHILE RAGING, CREATURES 5FT AWAY HAVE DISADVANTAGE AGAINST TARGETS OTHER THAN YOU,
    # IMMUNE IF IT CANT SEE YOU OR IS IMMUNE TO FRIGHTEN
    BEAR_ATTUNEMENT = functions.ClassTraitAttuneBear

    # WHILE RAGING, CAN 'FLY' AT WALKING PACE, END TURN ON GROUND OR FALL
    EAGLE_ATTUNEMENT = functions.ClassTraitAttuneEagle

    # WHILE RAGING, CAN KNOCK A CREATURE UP TO SIZE.LARGE PRONE
    WOLF_ATTUNEMENT = functions.ClassTraitAttuneWolf

    # HALF OF DEX_MOD(ROUNDED DOWN) ADDED TO ALL ABILITY CHECKS WITHOUT PROFICIENCY
    JACK_OF_ALL_TRADES = None


class STATUS(Set):
    # todo: provide __call__ methods, which will call the appropriate function in dnd5e_functions
    class Call:
        def __init__(self):
            self.func = getattr(functions, 'Status' + self.__class__.__name__.capitalize())
            self.affectors = []

        def __call__(self, *args, **kwargs):
            self.func(*args, **kwargs)

    class BLINDED(Call):
        def __init__(self):
            super().__init__()

    class CHARMED(Call):
        def __init__(self):
            super().__init__()

    class DEAD(Call):
        def __init__(self):
            super().__init__()

    class DEAFENED(Call):
        def __init__(self):
            super().__init__()

    class EXHAUSTED(Call):  #use this and remove the tiered statuses?
        def __init__(self):
            super().__init__()

    class EXHAUSTED1(Call):
        def __init__(self):
            super().__init__()

    class EXHAUSTED2(Call):
        def __init__(self):
            super().__init__()

    class EXHAUSTED3(Call):
        def __init__(self):
            super().__init__()

    class EXHAUSTED4(Call):
        def __init__(self):
            super().__init__()

    class EXHAUSTED5(Call):
        def __init__(self):
            super().__init__()

    class EXHAUSTED6(Call):
        def __init__(self):
            super().__init__()

    class FRIGHTENED(Call):
        def __init__(self):
            super().__init__()

    class GRAPPLED(Call):
        def __init__(self):
            super().__init__()

    class INCAPACITATED(Call):
        def __init__(self):
            super().__init__()

    class INVISIBLE(Call):
        def __init__(self):
            super().__init__()

    class PARALYZED(Call):
        def __init__(self):
            super().__init__()

    class PETRIFIED(Call):
        def __init__(self):
            super().__init__()

    class POISONED(Call):
        def __init__(self):
            super().__init__()

    class PRONE(Call):
        def __init__(self):
            super().__init__()

    class RESTRAINED(Call):
        def __init__(self):
            super().__init__()

    class STUNNED(Call):
        def __init__(self):
            super().__init__()

    class UNCONSCIOUS(Call):
        def __init__(self):
            super().__init__()

    class ENRAGED(Call):
        def __init__(self):
            super().__init__()

    class FRENZIED(Call):
        def __init__(self):
            super().__init__()


class ADVANTAGE(ABILITY, Set):
    ATTACK = ATTACK
    DEFENCE = DEFENCE

    class SOCIAL(Set): pass
    ABILITY = ABILITY
    # todo: add additional entries as needed for more and more advantage checks to work.


class PACE(Set):  # travelling pace, not burst speed for combat rules
    # FEET, MILES, MILES
    # 1MIN, 1HOUR, 1DAY
    FASTMIN = lambda self: 400  # 400 FT/MIN
    FASTHR = lambda self: 4 * 5160  # 4 MILES/HR
    FASTDAY = lambda self: 30 * 5160  # 30 MILES/DAY
    NORMALMIN = lambda self: 300
    NORMALHR = lambda self: 3 * 5160
    NORMALDAY = lambda self: 24 * 5160
    SLOWMIN = lambda self: 200
    SLOWHR = lambda self: 2 * 5160
    SLOWDAY = lambda self: 18 * 5160
    DIFFICULT = lambda self, x: x * 0.5
    SWIM = lambda self, x: x * 0.5
    CLIMB = lambda self, x: x * 0.5
    CRAWL = lambda self, x: x * 0.5
    FLY = lambda self, x: x * 2


class LIGHTING(Set):
    class DARK: pass
    class DIM: pass
    class BRIGHT: pass


# class SENSES:


class MOVE(Set):    # todo: replace enum values with basic movement modifiers
    class _:
        def __init__(self, speed=None):
            self.speed = 0 if speed is None else speed

        def __call__(self, speed=False):
            # conditionally assigns to self, or returns from self.
            if not speed:
                return self.speed
            self.speed = speed

    class SWIM(_):
        def __init__(self, speed=None):
            super().__init__(speed)

    class PRONE(_):
        def __init__(self, speed=None):
            super().__init__(speed)

    class CRAWL(_):
        def __init__(self, speed=None):
            super().__init__(speed)

    class WALK(_):
        def __init__(self, speed=None):
            super().__init__(speed)

    class RUN(_):
        def __init__(self, speed=None):
            super().__init__(speed)

    class CLIMB(_):
        def __init__(self, speed=None):
            super().__init__(speed)

    class FLY(_):
        def __init__(self, speed=None):
            super().__init__(speed)


class WEAPONFLAGS(Set):
    class LIGHT: pass
    class HEAVY: pass
    class FINESSE: pass
    class THROWN: pass
    class TWO_HANDED: pass
    class VERSATILE: pass
    class AMMUNITION: pass
    class LOADING: pass
    class SILVERED: pass


class __WEAPON(Set):  # todo: replace the ints with functions references expecting source and target objects
    class CLUB: pass
    class DAGGER: pass
    class GREATCLUB: pass
    class HANDAXE: pass
    class JAVELIN: pass
    class LIGHT_HAMMER: pass
    class MACE: pass
    class QUATERSTAFF: pass
    class SICKLE: pass
    class SPEAR: pass
    class LIGHT_CROSSBOW: pass
    class DART: pass
    class SHORTBOW: pass
    class SLING: pass
    class BATTLEAXE: pass
    class FLAIL: pass
    class GLAIVE: pass
    class GREATAXE: pass
    class GREATSWORD: pass
    class HALBERD: pass
    class LANCE: pass
    class LONGSWORD: pass
    class MAUL: pass
    class MORNINGSTAR: pass
    class PIKE: pass
    class RAPIER: pass
    class SCIMITAR: pass
    class SHORTSWORD: pass
    class TRIDENT: pass
    class WAR_PICK: pass
    class WARHAMMER: pass
    class WHIP: pass
    class BLOWGUN: pass
    class HAND_CROSSBOW: pass
    class HEAVY_CROSSBOW: pass
    class LONGBOW: pass


class DAMAGETYPE(Set):
    class __Damage:
        def __init__(self, damage=None):
            if damage is not None:
                self.damage = damage
            self.affectors = []

        def __call__(self, damage=None):
            if damage:  # use to set, or get the damage
                self.damage = damage
            else:
                return self.damage

        def __int__(self):
            return int(self.damage)

        def __str__(self):
            return self.__repr__()  # str(self.damage)# + ' ' + self.__class__.__name__

        def __repr__(self):
            return (str(self.damage) + ' ' if hasattr(self, 'damage') else '') + self.__class__.__name__

        def __imul__(self, other):
            self.damage *= other
            return self

        def __mul__(self, other):
            self.damage *= other
            return self

        def __rmul__(self, other):
            self.damage *= other
            return self

        def __iadd__(self, other):
            self.damage += other
            return self

        def __add__(self, other):
            self.damage += other
            return self

        def __radd__(self, other):
            self.damage += other
            return self

        def __isub__(self, other):
            self.damage -= other
            return self

        def __sub__(self, other):
            self.damage -= other
            return self

        def __rsub__(self, other):
            self.damage -= other
            return self

        def __itruediv__(self, other):
            self.damage //= other
            return self

        def __truediv__(self, other):
            self.damage //= other
            return self

        def __ifloordiv__(self, other):
            self.damage //= other
            return self

    class ACID(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class BLUNT(__Damage):
        def __init__(self, damage=None): super().__init__(damage)
        # blunt force attack, punches, hammers, falling, crushing, etc

    class COLD(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class FIRE(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class FORCE(__Damage):
        def __init__(self, damage=None): super().__init__(damage)  # pure magical energy

    class LIGHTNING(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class NECROTIC(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class PIERCING(__Damage):
        def __init__(self, damage=None): super().__init__(damage)  # puncturing/impaling - spears, bites, arrows, etc.

    class POISON(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class PSYCHIC(__Damage):
        def __init__(self, damage=None): super().__init__(damage)  # attacks on the mind

    class RADIANT(__Damage):
        def __init__(self, damage=None): super().__init__(damage)

    class SLASHING(__Damage):
        def __init__(self, damage=None): super().__init__(damage)  # cutting attacks, swords, axes, claws

    class THUNDER(__Damage):
        def __init__(self, damage=None): super().__init__(damage)  # concussive effects, a shock wave of sorts.


class ARMOR(Set):
    class LIGHT(Set):
        class PADDED(Set):
            class METAL: pass
            class NONMETAL: pass

        class LEATHER(Set):
            class METAL: pass
            class NONMETAL: pass

        class STUDDED(Set):
            class METAL: pass
            class NONMETAL: pass

    class MEDIUM(Set):
        class HIDE(Set):
            class METAL: pass
            class NONMETAL: pass

        class CHAIN_SHIRT(Set):
            class METAL: pass
            class NONMETAL: pass

        class SCALE_MAIL(Set):
            class METAL: pass
            class NONMETAL: pass

        class BREASTPLATE(Set):
            class METAL: pass
            class NONMETAL: pass

        class HALF_PLATE(Set):
            class METAL: pass
            class NONMETAL: pass

    class HEAVY(Set):
        class RING_MAIL(Set):
            class METAL: pass
            class NONMETAL: pass

        class CHAIN_MAIL(Set):
            class METAL: pass
            class NONMETAL: pass

        class SPLINT(Set):
            class METAL: pass
            class NONMETAL: pass

        class PLATE(Set):
            class METAL: pass
            class NONMETAL: pass


class _ARMOR(Set):
    class LIGHT: pass
    class MEDIUM: pass
    class HEAVY: pass
    class METAL: pass
    class NONMETAL: pass
    class PADDED: pass
    class LEATHER: pass
    class STUDDED: pass
    class HIDE: pass
    class CHAIN_SHIRT: pass
    class SCALE_MAIL: pass
    class BREASTPLATE: pass
    class HALF_PLATE: pass
    class RING_MAIL: pass
    class CHAIN_MAIL: pass
    class SPLINT: pass
    class PLATE: pass


class SHIELDS(Set):
    class TARGE: pass
    class KITE: pass
    class TOWER: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _WEAPONS_SIMPLE(Set):
    class CLUB: pass
    class CROSSBOW: pass
    class CROSSBOW_LIGHT: pass
    class DAGGER: pass
    class DART: pass
    class GREATCLUB: pass
    class HANDAXE: pass
    class JAVELIN: pass
    class LIGHT_HAMMER: pass
    class MACE: pass
    class QUARTERSTAFF: pass
    class SHORTBOW: pass
    class SICKLE: pass
    class SLING: pass
    class SPEAR: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _WEAPONS_MARTIAL(Set):
    class BATTLEAXE: pass
    class BLOWGUN: pass
    class CROSSBOW_HAND: pass
    class CROSSBOW_HEAVY: pass
    class FLAIL: pass
    class GLAIVE: pass
    class GREATAXE: pass
    class GREATSWORD: pass
    class HALBERD: pass
    class LANCE: pass
    class LONGBOW: pass
    class LONGSWORD: pass
    class MAUL: pass
    class MORNINGSTAR: pass
    class PIKE: pass
    class RAPIER: pass
    class SCIMITAR: pass
    class SHORTSWORD: pass
    class TRIDENT: pass
    class WAR_PICK: pass
    class WARHAMMER: pass
    class WHIP: pass


class WEAPONS(Set):
    SIMPLE = _WEAPONS_SIMPLE
    MARTIAL = _WEAPONS_MARTIAL
    class GENERIC: pass


class PROFICIENCY(Set):
    ARMOR = ARMOR
    SHIELDS = SHIELDS
    WEAPONS = WEAPONS


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _TOOLS_ARTISAN(Set):
    class ALCHEMIST: pass
    class BREWER: pass
    class CALIGRAPHER: pass
    class CARPENTER: pass
    class CARTOGRAPHER: pass
    class COBBLER: pass
    class COOK: pass
    class GLASSBLOWER: pass
    class JEWELER: pass
    class LEATHER_WORK: pass
    class MASON: pass
    class PAINTER: pass
    class POTTER: pass
    class SMITH: pass
    class TINKER: pass
    class WEAVER: pass
    class WOODCARVER: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _TOOLS_GAMING(Set):
    class DICE: pass
    class DRAGON_CHESS: pass
    class CARDS: pass
    class THREE_DRAGON_ANTE: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _TOOLS_INSTRUMENT(Set):
    class BAGPIPES: pass
    class DRUM: pass
    class DULCIMER: pass
    class FLUTE: pass
    class LUTE: pass
    class LYRE: pass
    class HORN: pass
    class PAN_FLUTE: pass
    class SHAWM: pass
    class VIOL: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _VEHICLES_WATER(Set):
    class GALLEY: pass
    class KEELBOAT: pass
    class LONGSHIP: pass
    class ROWBOAT: pass
    class SAILING_SHIP: pass
    class WARSHIP: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _VEHICLES_LAND(Set):
    class CARRIAGE: pass
    class CART: pass
    class CHARIOT_LIGHT: pass
    class CHARIOT_MEDIUM: pass
    class CHARIOT_HEAVY: pass
    class DOG_SLED: pass
    class STEAM_GIANT: pass
    class WAGON_LIGHT: pass
    class WAGON_MEDIUM: pass
    class WAGON_HEAVY: pass


# noinspection PyPep8Naming
# ^^be silent damn you, I know its not camel case
class _TOOLS_VEHICLES(Set):
    LAND = _VEHICLES_LAND
    WATER = _VEHICLES_WATER


class TOOLS(Set):
    # todo: end the tools enums with a description of what those tool sets contain?
    ARTISAN = _TOOLS_ARTISAN
    GAMING = _TOOLS_GAMING
    INSTRUMENT = _TOOLS_INSTRUMENT

    class DISGUISE: pass

    class FORGERY: pass

    class THIEVES: pass

    class HERBALIST: pass

    class NAVIGATOR: pass

    class POISONER: pass

    VEHICLES = _TOOLS_VEHICLES


class BACKGROUNDS(Set):  # todo: ADD EQUIPMENT FOR BACKGROUNDS, ADD SUPPORT FOR TOOLS
    class ACOLYTE:
        SKILLS = {SKILL.INSIGHT, SKILL.RELIGION}
        TOOLS = set()

    class CHARLATAN:
        SKILLS = {SKILL.DECEPTION, SKILL.SLEIGHT}
        TOOLS = {TOOLS.DISGUISE, TOOLS.FORGERY}

    class CRIMINAL:
        SKILLS = {SKILL.DECEPTION, SKILL.STEALTH}
        TOOLS = {TOOLS.THIEVES}.union(TOOLS.GAMING.Set())

    class FOLK_HERO:
        SKILLS = {SKILL.ANIMAL_HANDLING, SKILL.SURVIVAL}

    class GUILD_ARTISAN:
        SKILLS = {SKILL.INSIGHT, SKILL.PERSUASION}
        TOOLS = TOOLS.ARTISAN.Set()

    class HERMIT:
        SKILLS = {SKILL.MEDICINE, SKILL.RELIGION}
        TOOLS = {TOOLS.HERBALIST}

    class NOBLE:
        SKILLS = {SKILL.HISTORY, SKILL.PERSUASION}
        TOOLS = TOOLS.GAMING.Set()

    class OUTLANDER:
        SKILLS = {SKILL.ATHLETICS, SKILL.SURVIVAL}
        TOOLS = TOOLS.INSTRUMENT.Set()

    class PERFORMER:
        SKILLS = {SKILL.ACROBATICS, SKILL.PERFORMANCE}
        TOOLS = {TOOLS.DISGUISE}.union(TOOLS.INSTRUMENT.Set())

    class SAGE:
        SKILLS = {SKILL.ARCANA, SKILL.HISTORY}
        TOOLS = set()

    class SAILOR:
        SKILLS = {SKILL.ATHLETICS, SKILL.PERCEPTION}
        TOOLS = {TOOLS.NAVIGATOR}.union(TOOLS.VEHICLES.WATER.Set())

    class SOLDIER:
        SKILLS = {SKILL.ATHLETICS, SKILL.INTIMIDATION}
        TOOLS = TOOLS.GAMING.Set().union(TOOLS.VEHICLES.LAND.Set())

    class URCHIN:
        SKILLS = {SKILL.SLEIGHT, SKILL.STEALTH}
        TOOLS = {TOOLS.DISGUISE, TOOLS.THIEVES}
#
# # noinspection PyPep8Naming
# # ^^be silent damn you, I know its not camel case
# class VEHICLES:
#     # todo decision:  not sure I want an enum and class for vehicles, or if I can simply embed the class in the enum
#     #  Enums have no instances, just static members - so cannot have a unique vehicle instance to manipulate
#     #    - could implement a getter than copies out an instance and render the separate class irrelevant?
#     #       - can drawn carriages with speed determined at runtime even exist in an enum determined at compile time?
#     #    - does it even matter?  Do we need this freedom at all?
#     class Across:
#         AIR = 0
#         LAND = 1
#         WATER = 2
#
#     class Characteristics:
#         # cost is in gold coins
#         # speed is given in miles/hr, converted to feet internally
#         # cargo is in tons, converted to lbs internally
#         # DT is damage threshold, damage less than this is ignored entirely.
#         def __init__(self, cost, speed, crew, passengers, cargo, ac, hp, dt, medium, _type, pulled_speed=False):
#             self.COST = cost
#             if pulled_speed:  # carts, chariots, etc.
#                 self.speed = pulled_speed
#             else:
#                 self.SPEED = speed * 5160
#             self.CREW = crew
#             self.PASSENGERS = passengers
#             self.CARGO = cargo * 2200
#             self.ARMOR_CLASS = ac
#             self.HIT_POINTS = hp
#             self.DAMAGE_THRESHOLD = dt
#             self.MEDIUM_OF_TRAVEL = medium
#             self.TYPE = _type
#             self.take_damage = lambda dmg: max(0, dmg - self.DAMAGE_THRESHOLD)
#
#     # TODO: FINISH  - below data is NOT complete, much of these are simply copies, not unique to each.
#     # https://www.d20pfsrd.com/equipment/vehicles/ SEEMS USEFUL FOR THIS
#
#     GALLEY = [20000, 8, 10, 20, 1, 13, 300, 0, TOOLS.VEHICLES.WATER, TOOLS.VEHICLES.WATER.GALLEY]
#     KEELBOAT = [30000, 4, 80, 0, 150, 15, 500, 20, TOOLS.VEHICLES.WATER, TOOLS.VEHICLES.WATER.GALLEY]
#     LONGSHIP = [3000, 1, 1, 6, .5, 15, 100, 10, TOOLS.VEHICLES.WATER, TOOLS.VEHICLES.WATER.GALLEY]
#     ROWBOAT = [50, 1.5, 1, 3, 0, 11, 50, 0, TOOLS.VEHICLES.WATER, TOOLS.VEHICLES.WATER.GALLEY]
#     SAILING_SHIP = [10000, 2, 20, 20, 100, 15, 300, 15, TOOLS.VEHICLES.WATER, TOOLS.VEHICLES.WATER.GALLEY]
#     WARSHIP = [25000, 2.5, 60, 60, 200, 15, 500, 20, TOOLS.VEHICLES.WATER, TOOLS.VEHICLES.WATER.GALLEY]
#     CARRIAGE = lambda x: [100, -1, 2, 4, .2, 9, 90, 5, TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]
#     CART = lambda x: [15, -1, 1, 0, 300, 9, 30, 5, TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CART, x-10]
#     CHARIOT_LIGHT = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                                TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CHARIOT_LIGHT, x]
#     CHARIOT_MEDIUM = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                                 TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]
#     CHARIOT_HEAVY = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                                TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]
#     DOG_SLED = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                           TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]
#     STEAM_GIANT = lambda x: [100, 60, 60, 60, 200, 15, 500, 20, TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE]
#     WAGON_LIGHT = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                              TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]
#     WAGON_MEDIUM = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                               TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]
#     WAGON_HEAVY = lambda x: [100, -1, 60, 60, 200, 15, 500, 20,
#                              TOOLS.VEHICLES.LAND, TOOLS.VEHICLES.LAND.CARRIAGE, x]


class CREATURE_TYPES(Set):
    class ABERATION: pass
    class BEAST: pass
    class CELESTIAL: pass
    class CONSTRUCT: pass
    class DRAGON: pass
    class ELEMENTAL: pass
    class FEY: pass
    class FIEND: pass
    class GIANT: pass
    class HUMANOID: pass
    class MONSTROSITY: pass
    class OOZE: pass
    class PLANT: pass
    class UNDEAD: pass


class EQUIP_SLOT(Set):
    # todo: implement a get_qty, get_weight, get_etc functions
    # todo: implement equipped, wielded, carried subvars for each
    class __E(Set):
        # todo: implement variable carriage of items
        # todo: change equip process to use this rather than internal vars
        class WIELDED:
            def __init__(self):
                self.items = set()

        class EQUIPPED:
            def __init__(self):
                self.items = set()

        class CARRIED:
            def __init__(self):
                self.items = set()

    class HAND(__E): pass  # current weapon(s) and/or shield
    class JAW(__E): pass  # creature bite/spit attacks
    class ARMOR(__E): pass  # self explanatory?
    class SHIELD(__E): pass  # self explanatory?
    class BACK(__E): pass  # equipped but carried weapons, inventory, backpacks
    class COLLAR(__E): pass  # neck slot, collars, single
    class NECK(__E): pass  # neck slot, amulets, necklaces, multiple
    class GLOVES(__E): pass  # for worn gloves, around the hands, not in them.
    class FINGERS(__E): pass  # rings, creature talon/claw attacks
    class BELT(__E): pass  # for belts, weapon sheaths/loops, and pouches, multiple
    class SHOULDER(__E): pass  # for sling type gear, such as quivers, smaller sword sheaths
    class INVENTORY(__E): pass  # for general inventory items, not actionable


class EVENT(Set):
    class INIT: pass
    class EQUIP: pass
    class UNEQUIP: pass
    class BEFORE_BATTLE: pass
    class AFTER_BATTLE: pass
    class BEFORE_TURN: pass
    class AFTER_TURN: pass
    class BEFORE_ACTION: pass
    class AFTER_ACTION: pass
    class ATTACK: pass
    class DEFEND: pass
    class CRITICAL: pass
    class LEVEL_UP: pass
    class REST_LONG: pass
    class REST_SHORT: pass
    class ROLL_ATTACK: pass
    class ROLL_DAMAGE: pass
    class ROLL_DC: pass
    class ROLL_HP: pass
    class DEATH: pass
    class HEAL: pass


if __name__ == '__main__':
    from trace import print
    print(ARMOR)
    print(ARMOR.MEDIUM)
    print(ARMOR.MEDIUM.HIDE)
    print(ARMOR.Set())
    print(ARMOR.MEDIUM.Set())
    for f in CLASS_TRAITS.Set():
        try:
            print(f, f(host=None))
        except:
            pass
    test1 = ABILITY.CON
    test2 = ABILITY
    print(test1 in test2.Set())
