# from enum import Enum
import dnd5e_misc as misc
import sys

# todo: find ALL default argument expressions in my code, and replace them with =None and default it inside the
#  function, see :   https://www.toptal.com/python#hiring-guide

# fuck Enum with a broken rusty pipe - if I can't have nested access, it can die in a fire


class Set:
    @classmethod
    def Set(cls):  # recursively chase it out, if its a branch, find the leaves.
        attr = (getattr(cls, i) for i in dir(cls) if not callable(i) and i.upper() == i)
        s = {cls}
        for a in attr:
            if hasattr(a, 'Set'):
                s.update(a.Set())
            else:
                s.add(a)
        return s


class ABILITY(Set):
    # ATTRIBUTES
    class STR: pass
    class CON: pass
    class DEX: pass
    class INT: pass
    class WIS: pass
    class CHA: pass


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
        self.STR, self.CON, self.DEX = strength, constitution, dexterity
        self.INT, self.WIS, self.CHA = intelligence, wisdom, charisma
        mods = self.get_mods()
        self.STR_MOD, self.CON_MOD, self.DEX_MOD = mods[:3]
        self.INT_MOD, self.WIS_MOD, self.CHA_MOD = mods[3:]

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
    class ATHLETICS: pass
    class ACROBATICS: pass
    class SLEIGHT: pass
    class STEALTH: pass
    class ARCANA: pass
    class HISTORY: pass
    class INVESTIGATION: pass
    class NATURE: pass
    class RELIGION: pass
    class ANIMAL_HANDLING: pass
    class INSIGHT: pass
    class MEDICINE: pass
    class PERCEPTION: pass
    class SURVIVAL: pass
    class DECEPTION: pass
    class INTIMIDATION: pass
    class PERFORMANCE: pass
    class PERSUASION: pass


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
    class MELEE: pass
    class RANGED: pass
    class ARCANE: pass


class TRAIT(Set):
    # todo: replace the ints with functions references expecting source and target objects
    class ABILITY_VERSATILITY: pass  # INCREASE TWO ABILITY SCORES OF YOUR CHOICE, OTHER THAN CHARISMA, BY 1

    class ARTIFICERS_LORE: pass  # DOUBLE PROFICIENCY BONUS ON INTELLIGENCE CHECKS RELATING TO ARCANE,
    # ALCHEMICAL, OR MECHANICAL DEVICES.

    class BRAVE: pass  # ADVANTAGE RESISTING FRIGHTENED

    class CANTRIP: pass  # KNOW ONE SPELL FROM THE WIZARD SPELL SET, USES INTELLIGENCE TO CAST

    class COMMON_PERCEPTION: pass  # PASSIVE PERCEPTION OF 10

    class DARKVISION: pass  # CAN SEE IN DIM AS IF BRIGHT LIGHT TO 60FT

    class DRACONIC_ANCESTRY_BLACK: pass  # ACID      DAMAGE TYPE, 5X30FT,  DC(DEX), 50% ACID      RESIST

    class DRACONIC_ANCESTRY_BLUE: pass  # LIGHTING  DAMAGE TYPE, 5X30FT,  DC(DEX), 50% LIGHTNING RESIST

    class DRACONIC_ANCESTRY_BRASS: pass  # FIRE      DAMAGE TYPE, 5X30FT,  DC(DEX), 50% FIRE      RESIST

    class DRACONIC_ANCESTRY_BRONZE: pass  # LIGHTNING DAMAGE TYPE, 5X30FT,  DC(DEX), 50% LIGHTNING RESIST

    class DRACONIC_ANCESTRY_COPPER: pass  # ACID      DAMAGE TYPE, 5X30FT,  DC(DEX), 50% ACID      RESIST

    class DRACONIC_ANCESTRY_GOLD: pass  # FIRE      DAMAGE TYPE, 15X15FT, DC(DEX), 50% FIRE      RESIST

    class DRACONIC_ANCESTRY_GREEN: pass  # POISON    DAMAGE TYPE, 15X15FT, DC(CON), 50% POISON    RESIST

    class DRACONIC_ANCESTRY_RED: pass  # FIRE      DAMAGE TYPE, 15X15FT, DC(DEX), 50% FIRE      RESIST

    class DRACONIC_ANCESTRY_SILVER: pass  # COLD      DAMAGE TYPE, 15X15FT, DC(CON), 50% COLD      RESIST

    class DRACONIC_ANCESTRY_WHITE: pass  # COLD      DAMAGE TYPE, 15X15FT, DC(CON), 50% COLD      RESIST

    class DRACONIC_BREATH_WEAPON: pass
    # ANCESTRAL DAMAGE TYPE ATTACK, DC8+CON_MOD+PROFICIENCY.  HALF DAMAGE FOR SUCCESSFUL RESIST.  2D6 UNTIL LVL6, 3D6
    # UNTIL 11, 4D6 UNTIL 16, AND 5D6 16+

    class DRACONIC_DAMAGE_RESISTANCE: pass  # RECEIVE ONLY 50% DAMAGE AGAINST ANCESTRAL TYPE

    class DROW_MAGIC: pass
    # DANCING LIGHTS AT LVL 1, FAERIE FIRE AT LVL 3, DARKNESS AT LVL 5, ONCE EACH PER DAY, USES CHARISMA TO CAST.

    class DROW_WEAPON_TRAINING: pass  # PROFICIENCY WITH RAPIERS, SHORTSWORDS, HAND CROSSBOWS

    class DWARVEN_ARMOR_TRAINING: pass  # PROFICIENCY IN LIGHT AND MEDIUM ARMOR

    class DWARVEN_COMBAT_TRAINING: pass  # PROFICIENCY WITH BATTLEAXE, HANDAXE, THROWING HAMMER, AND WARHAMMER

    class DWARVEN_RESILIENCE: pass  # ADVANTAGE ON SAVING THROWS VS POISON, RESISTS POISON TAKING ONLY 50% DAMAGE

    class DWARVEN_TOUGHNESS: pass  # MAXIMUM HP INCREASED BY LEVEL

    class ELVEN_WEAPON_TRAINING: pass  # PROFICIENCY WITH LONGSWORD, SHORTSWORD, SHORTBOW, AND LONGBOW

    class FEY_ANCESTRY: pass  # ADVANTAGE IN SAVING THROWS AGAINST CHARM, IMMUNE TO ARCANE SLEEP

    class FLEET_OF_FOOT: pass  # BASE WALKING SPEED IS 35FT

    class GNOME_CUNNING: pass  # ADVANTAGE ON ALL INTELLIGENCE, WISDOM, AND CHARISMA SAVING THROWS VS MAGIC

    class HALFLING_NIMBLENESS: pass  # CAN MOVE THROUGH THE SPACE OF ANY CREATURE AT LEAST ONE SIZE LARGER.

    class HELLISH_RESISTANCE: pass  # RESISTANCE AGAINST FIRE DAMAGE, TAKING ONLY 50% DAMAGE

    class INFERNAL_LEGACY: pass
    # KNOW THE THAUMATURGY CANTRIP, CAST ONCE PER DAY, HELLISH REBUKE AT LVL3 ONCE PER DAY AT 2ND LEVEL,
    # DARKNESS AT LVL 5 ONCE PER DAY. USING CHARISMA FOR SPELL CASTING

    class KEEN_SENSES: pass  # PROFICIENCY IN THE PERCEPTION SKILL

    class LUCKY: pass
    # WHEN YOU ROLL A 1 ON AN ATTACK ROLL, ABILITY CHECK, OR SAVING THROW, ROLL AGAIN AND USE THE SECOND ROLL

    class MASK_OF_THE_WILD: pass
    # CAN HIDE WHENEVER PARTIAL OBSCUREMENT OCCURS, SUCH AS SMOKE, RAIN, SNOW, FOLIAGE, ETC

    class MENACING: pass  # PROFICIENCY IN THE INTIMIDATION SKILL

    class NATURAL_ILLUSIONIST: pass  # KNOW THE MINOR ILLUSION CANTRIP, USES INTELLIGENCE FOR CASTING

    class NATURALLY_STEALTHY: pass  # CAN ATTEMPT TO HIDE WHEN OBSCURED BY A CREATURE AT LEAST ONE SIZE LARGER

    class RELENTLESS_ENDURANCE: pass
    # WHEN REDUCED TO 0 HITPOINTS BUT NOT KILLED, WILL DROP TO 1 HP INSTEAD, RESETS VIA LONG REST

    class SAVAGE_ATTACKS: pass  # CAN ROLL ANOTHER ATTACK DIE ON CRITICAL HITS, ADDING ON MORE DAMAGE

    class SKILL_VERSATILITY: pass  # GAIN PROFICIENCY IN TWO SKILL SOF YOUR CHOOSING AT CHARACTER CREATION

    class SPEAK_WITH_SMALL_BEASTS: pass  # CAN CONVEY SIMPLE IDEAS TO SMALL/TINY BEASTS.

    class STONE_CUNNING: pass  # DOUBLE PROFICIENCY BONUS FOR HISTORY/LORE RELATING TO STONE

    class STOUT_RESILIENCE: pass  # ADVANTAGE ON SAVING THROWS VS POISON, RESISTS POISON TAKING ONLY 50% DAMAGE

    class SUNLIGHT_SENSITIVITY: pass
    # DISADVANTAGE IN ATTACK ROLLS AND PERCEPTION CHECKS THAT RELY ON SIGHT IF YOU OR TARGET ARE IN DIRECT SUNLIGHT

    class SUPERIOR_DARKVISION: pass  # RADIUS OF 120FT DIM LIGHT LIKE BRIGHT LIGHT

    class TOOL_BREWER_PROFICIENCY: pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_MASON_PROFICIENCY: pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_SMITH_PROFICIENCY: pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_SUPPLIES_PROFICIENCY: pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TOOL_TINKER_PROFICIENCY: pass  # PROFICIENCY WITH THE ARTISAN'S TOOLS FOR WORK IN THE PROFESSION

    class TRANCE: pass  # ELVEN MEDITATION, REPLACES SLEEP FOR REST, 2X AS EFFECTIVE,
    # SHORT REST IN 1HR, LONG REST IN 4HR


# noinspection PyPep8Naming
# ^^be silent damn you
class CLASS_TRAITS(Set):
    # todo: replace the ints with functions references expecting source and target objects
    class RAGE: pass  # ADVANTAGE TO DC(STR) AND SAVE(STR), BONUS DAMAGE
    class UNARMORED_DEFENCE: pass  # WHILE NOT WEARING ARMOR, DEFENCE IS 10+CON_MOD, PLUS SHIELD IF EQUIPPED.
    class RECKLESS_ATTACK: pass  # FIRST ATTACK OF TURN HAS ADVANTAGE, BUT ATTACKS AGAINST YOU HAVE ADVANTAGE
    class DANGER_SENSE: pass  # ADVANTAGE DC(DEX) ON PERCEption, INEFFECTIVE IF BLINDED, DEAFENED, INCAPACITATED
    class EXTRA_ATTACK: pass  # MAY ATTACK ADDITIONAL TIMES PER TURN, SEE CLASS STATS FOR NUMBER OF ATTACKS
    class FAST_MOVEMENT: pass  # GAIN 10FT/SEC IF NOT WEARING ARMOR
    class FERAL_INSTINCT: pass  # ADVANTAGE ON INITIATIVE, CAN RAGE AND THEN ACT NORMALLY IF SURPRISED
    class BRUTAL_CRITICAL: pass  # ADDS ADDITION ATTACK ROLLS ON CRITICAL, 1 AT LVL9, 2 AT LVL13, 3 AT LVL17
    class RELENTLESS_RAGE: pass  # IF 0HP, +1 IF PASS DC10(CON), +DC5 EVERY TIME THIS IS USED UNTIL REST
    class PERSISTENT_RAGE: pass  # RAGE ENDS ONLY IF UNCONSCIOUS, OR CHOSEN TO END
    class INDOMITABLE_MIGHT: pass  # IF ROLL(STR) < STR, USE STR INSTEAD.
    class PRIMAL_CHAMPION: pass  # MAXIMUM STR AND CON +4, MAXIMUM POSSIBLE +4 TO 24
    class FRENZY: pass  # CAN MAKE BONUS ATTACK AT END OF EACH TURN, SUFFER EXHAUSTION +1 AT END OF RAGE
    class MINDLESS_RAGE: pass  # IMMUNE TO CHARM AND FRIGHTEN WHILE RAGING, SUSPENDS EFFECT WHILE RAGING
    class INTIMIDATING_PRESENCE: pass  # CAN USE AN ACTION TO FRIGHTEN VISIBLE TARGET WITHIN 30 FT,
    # CHA_MOD UNTIL END OF YOUR NEXT TURN. ENDS IF 60FT AWAY, OR LOSES SIGHT OF YOU
    class RETALIATION: pass  # CAN USE REACTION TO MELEE ATTACK A CREATURE WITHIN 5FT WHICH HARMS YOU
    class SPIRIT_SEEKER: pass  # MAY CAST BEAST SENSE, AND SPEAK WITH ANIMALS, AS RITUALS
    class SPIRIT_WALKER: pass  # CAST COMMUNE WITH NATURE AS RITUAL - SUMMONS SPIRIT ANIMAL TO CONVEY THE INFO YOU SEEK
    class BEAR_TOTEM: pass  # WHILE RAGING, RESIST ALL DAMAGE EXCEPT PSYCHIC
    class EAGLE_TOTEM: pass  # WHILE RAGING, IF NOT WEARING HEAVY ARMOR OTHER CREATURES HAVE DISADVANTAGE ON
    # OPPORTUNITY ATTACK ROLLS, CAN USE DASH AS BONUS ACTION
    class WOLF_TOTEM: pass  # WHILE RAGING, PARTY HAS ADVANTAGE ON MELEE VS ANY HOSTILE WITHIN 5FT OF YOU
    class ASPECT_OF_THE_BEAR: pass  # CARRYING CAPACITY DOUBLES, ADVANTAGE STR TO PUSH, PULL, LIFT, BREAK
    class ASPECT_OF_THE_EAGLE: pass  # SEE 1 MILE AWAY AS IF 100FT AWAY. NO PERCEPTION DISADVANTAGE IN DIM LIGHT
    class ASPECT_OF_THE_WOLF: pass  # CAN TRACK CREATURES WHILE AT FAST PACE, CAN MOVE STEALTHILY AT NORMAL
    class BEAR_ATTUNEMENT: pass  # WHILE RAGING, CREATURES 5FT AWAY HAVE DISADVANTAGE AGAINST TARGETS OTHER THAN YOU,
    # IMMUNE IF IT CANT SEE YOU OR IS IMMUNE TO FRIGHTEN
    class EAGLE_ATTUNEMENT: pass  # WHILE RAGING, CAN 'FLY' AT WALKING PACE, END TURN ON GROUND OR FALL
    class WOLF_ATTUNEMENT: pass  # WHILE RAGING, CAN KNOCK A CREATURE UP TO SIZE.LARGE PRONE
    class JACK_OF_ALL_TRADES: pass  # HALF OF DEX_MOD(ROUNDED DOWN) ADDED TO ALL ABILITY CHECKS WITHOUT PROFICIENCY


class STATUS(Set):
    # todo: replace the ints with functions references expecting source and target objects
    class BLINDED: pass
    class CHARMED: pass
    class DEAFENED: pass
    class EXHAUSTED1: pass
    class EXHAUSTED2: pass
    class EXHAUSTED3: pass
    class EXHAUSTED4: pass
    class EXHAUSTED5: pass
    class EXHAUSTED6: pass
    class FRIGHTENED: pass
    class GRAPPLED: pass
    class INCAPACITATED: pass
    class INVISIBLE: pass
    class PARALYZED: pass
    class PETRIFIED: pass
    class POISONED: pass
    class PRONE: pass
    class RESTRAINED: pass
    class STUNNED: pass
    class UNCONSCIOUS: pass


class ADVANTAGE(ABILITY):
    class ATTACK: pass
    class DEFENCE: pass
    class SOCIAL: pass
    class ABILITY: pass  # all abilities.
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

        def __call__(self):
            return self.speed

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
        def __init__(self, damage):
            self.damage = damage

        def __call__(self, damage=None):
            if damage:  # use to set, or get the damage
                self.damage = damage
            else:
                return self.damage

        def __int__(self):
            return int(self.damage)

        def __str__(self):
            return self.__repr__()# str(self.damage)# + ' ' + self.__class__.__name__

        def __repr__(self):
            return str(self.damage) + ' ' + self.__class__.__name__

        def __imul__(self, other):
            self.damage *= other
            return self

        def __mul__(self, other):
            self.damage *= other
            return self

        def __rmul__(self, other):
            self.damage *= other
            return self

    class ACID(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class BLUNT(__Damage):
        def __init__(self, damage): super().__init__(damage)    # blunt force attack, punches, hammers, falling, crushing, etc

    class COLD(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class FIRE(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class FORCE(__Damage):
        def __init__(self, damage): super().__init__(damage)  # pure magical energy

    class LIGHTNING(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class NECROTIC(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class PIERCING(__Damage):
        def __init__(self, damage): super().__init__(damage)  # puncturing/impaling - spears, bites, arrows, etc.

    class POISON(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class PSYCHIC(__Damage):
        def __init__(self, damage): super().__init__(damage)  # attacks on the mind

    class RADIANT(__Damage):
        def __init__(self, damage): super().__init__(damage)

    class SLASHING(__Damage):
        def __init__(self, damage): super().__init__(damage)  # cutting attacks, swords, axes, claws

    class THUNDER(__Damage):
        def __init__(self, damage): super().__init__(damage)  # concussive effects, a shock wave of sorts.


class ARMOR(Set):
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


class _SHIELDS(Set):
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
    ARMOR = _ARMOR
    SHIELDS = _SHIELDS
    WEAPONS = WEAPONS


class BACKGROUNDS(Set):  # todo: ADD EQUIPMENT FOR BACKGROUNDS, ADD SUPPORT FOR TOOLS
    class ACOLYTE:
        SKILLS = {SKILL.INSIGHT, SKILL.RELIGION}

    class CHARLATAN:
        SKILLS = {SKILL.DECEPTION, SKILL.SLEIGHT}

    class CRIMINAL:
        SKILLS = {SKILL.DECEPTION, SKILL.STEALTH}

    class FOLK_HERO:
        SKILLS = {SKILL.ANIMAL_HANDLING, SKILL.SURVIVAL}

    class GUILD_ARTISAN:
        SKILLS = {SKILL.INSIGHT, SKILL.PERSUASION}

    class HERMIT:
        SKILLS = {SKILL.MEDICINE, SKILL.RELIGION}

    class NOBLE:
        SKILLS = {SKILL.HISTORY, SKILL.PERSUASION}

    class OUTLANDER:
        SKILLS = {SKILL.ATHLETICS, SKILL.SURVIVAL}

    class PERFORMER:
        SKILLS = {SKILL.ACROBATICS, SKILL.PERFORMANCE}

    class SAGE:
        SKILLS = {SKILL.ARCANA, SKILL.HISTORY}

    class SAILOR:
        SKILLS = {SKILL.ATHLETICS, SKILL.PERCEPTION}

    class SOLDIER:
        SKILLS = {SKILL.ATHLETICS, SKILL.INTIMIDATION}

    class URCHIN:
        SKILLS = {SKILL.SLEIGHT, SKILL.STEALTH}


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
