# parent class to both Character Sheet and creature, has things relevant to encounters.
from dnd5e_enums import ABILITY, Ability  # , SKILL, TRAIT
import dnd5e_weaponry as weaponry
from dnd5e_events import Event
from dnd5e_inventory import Equipped
from dnd5e_misc import Attack, Die, NamedTuple, Location

debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


class Entity:
    def __init__(self, name=None, traits=None, hp=None, hp_max=None, effects=None, equipment=None, abilities=None,
                 skills=None, saving_throws=None, speed=None, proficiency_bonus=None, unspent_ability=None):
        self.name = name
        self.speed = speed
        if self.speed is None:
            self.speed = 0  # todo, replace with full range of speeds, flight, swimming, etc.

        if self.name is None:
            self.name = 'an Entity is No One'
        self.traits = traits
        if self.traits is None:
            self.traits = set()
        # combat actions
        import dnd5e_functions as functions
        self.traits.update({functions.ActionCombatAssist, functions.ActionCombatAttack, functions.ActionCombatDash,
                            functions.ActionCombatDisengage, functions.ActionCombatDodge, functions.ActionCombatHide,
                            functions.ActionCombatReady, functions.ActionCombatSearch, functions.ActionCombatUse})
        self.hp_max = hp_max
        self.hp = hp
        if self.hp is None:
            self.hp = self.hp_max
        self.effects = effects
        if self.effects is None:
            self.effects = Event()  # use for trait/status effects - re-apply whenever character refreshes
            self.effects_persist = Event()  # use for things which must persist across states initialisations
        self.equipment = equipment
        if isinstance(equipment, Equipped):
            self.equipment = equipment
        elif equipment is None:
            self.equipment = Equipped()
        elif isinstance(equipment, list):
            self.equipment = Equipped()
            self.equipment.equip(equipment)  # todo: implement weapons/shields/armor
        self.atk_bonus = 0
        self.abilities = abilities
        if self.abilities is None:
            self.abilities = Ability()
        self.proficiency_bonus = proficiency_bonus
        if self.proficiency_bonus is None:
            self.proficiency_bonus = 0
        self.saving_throws = self.set_saving_throws(saving_throws)
        if self.saving_throws is None:
            self.saving_throws = Ability()
        self.unspent_ability = unspent_ability
        if self.unspent_ability is None:
            self.unspent_ability = 0

        self.temporary_hitpoints = 0
        self._advantage = Event()
        self._disadvantage = Event()
        self._damage_vulnerable = Event()  # todo: implement damage vulnerabilities
        self._damage_resist = Event()  # todo: implement damage resistances
        self._proficiency_skills = Event()
        self._status = Event()
        self._immunity = Event()
        self.proficiency_skills = skills
        self.d20 = Die(1, 20)
        self.location = Location()
        self.party = None   # reference to our party, so anywhere we have the entity object, we have the party too


    @property
    def advantage(self):
        return self._advantage.none

    @property
    def disadvantage(self):
        return self._disadvantage.none

    @property
    def immunity(self):
        return self._immunity.none

    @property
    def damage_vulnerable(self):
        return self._damage_vulnerable.none

    @property
    def damage_resist(self):
        return self._damage_resist.none

    @property
    def proficiency_skills(self):
        return self._proficiency_skills.none

    @property
    def status(self):
        return self._status.none

    @advantage.setter
    def advantage(self, value):
        if not isinstance(value, Event):
            self._advantage = Event()
        else:
            self._advantage.none.clear()
        self._advantage.none.update(value)

    @immunity.setter
    def immunity(self, value):
        if not isinstance(value, Event):
            self._immunity = Event()
        else:
            self._immunity.none.clear()
        self._immunity.none.update(value)

    @disadvantage.setter
    def disadvantage(self, value):
        if not isinstance(value, Event):
            self._disadvantage = Event()
        else:
            self._disadvantage.none.clear()
        self._disadvantage.none.update(value)

    @damage_vulnerable.setter
    def damage_vulnerable(self, value):
        if not isinstance(value, Event):
            self._damage_vulnerable = Event()
        else:
            self._damage_vulnerable.none.clear()
        self._damage_vulnerable.none.update(value)

    @damage_resist.setter
    def damage_resist(self, value):
        if not isinstance(value, Event):
            self._damage_resist = Event()
        else:
            self._damage_resist.none.clear()
        self._damage_resist.none.update(value)

    @proficiency_skills.setter
    def proficiency_skills(self, value):
        if not isinstance(value, Event):
            self._proficiency_skills = Event()
        else:
            self._proficiency_skills.none.clear()
        self._proficiency_skills.none.update(value)

    @status.setter
    def status(self, value):
        if not isinstance(value, Event):
            self._status = Event()
        else:
            self._status.none.clear()
        self._status.none.update(value)

    def equip(self, gear):
        if self.equipment is None:
            self.equipment = Equipped()
        if gear is None:
            return
        if isinstance(gear, Equipped):
            gear = gear.get_equipped()
        elif not isinstance(gear, list):
            gear = [gear]

        # todo: call the individual gear equip functions. - test for cursed
        self.equipment.equip(gear)  # todo: implement weapons/shields/armor
        self.effects.equip()

    def unequip(self, slot=None, gear=None):
        # todo: check for cursed - unable to remove item
        self.equipment.unequip(slot, gear)
        self.effects.unequip()

    def receive_damage(self, damage):
        # todo: handle death, incapacitation, etc.
        # todo: trigger defence events, return any that apply to attacker
        self.hp -= int(max(damage))
        return int(max(damage)), None  # todo: return actual damage taken and any counter effects
        # todo: cross check damage types against vulnerability/resist, and modify accordingly - take highest effect

    def melee_attack(self):
        #
        #     return any effects which require a target - like poison effects.
        #        advantage = enums.ADVANTAGE.ATTACK in self.advantage
        #        disadvantage = enums.ADVANTAGE.ATTACK in self.disadvantage
        #        lucky = enums.TRAIT.LUCKY in self.traits
        #        attack_roll, critical = misc.attack_roll(advantage, disadvantage, lucky=lucky)
        # todo: implement usage of reach value
        attacks = Attack()

#        if CLASS_TRAITS.EXTRA_ATTACK in self.traits:
#            attacks['num'] += 1

        # is storing two of the same reference
#        attacks['effects'] = effects
        attacks.calculation = self._wpn
        attacks.weapons = [self.equipment.right_hand, self.equipment.left_hand,
                           self.equipment.jaw, self.equipment.fingers]
        return attacks

    def _wpn(self, hand: weaponry.Weapon = None):
        while True:
            if hand is None:
                yield 0
            rolls = NamedTuple(roll1=hand.attack_die.roll(), roll2=None, die=hand.attack_die)
            self.effects.roll_damage(rolls=rolls)
            # noinspection PyUnresolvedReferences
            damage = rolls.roll1
            if hand.bonus_die is not None:
                debug('weapon rolling for bonus die')
                rolls = NamedTuple(roll1=hand.bonus_die.roll(), roll2=None, die=hand.bonus_die)
                self.effects.roll_damage(rolls)
                # noinspection PyUnresolvedReferences
                damage += rolls.roll1
            damage += hand.bonus_damage
            yield [d(damage) for d in hand.damage_type], hand.attack_function

    def set_saving_throws(self, throws):
        # todo: confirm if saving throws are modified by any races and include if so
        # base values
        STR = self.abilities.STR_MOD
        CON = self.abilities.CON_MOD
        DEX = self.abilities.DEX_MOD
        INT = self.abilities.INT_MOD
        WIS = self.abilities.WIS_MOD
        CHA = self.abilities.CHA_MOD
        # proficiency boosted
        if self.proficiency_bonus == 0:  # is creature
            STR += throws.STR
            CON += throws.CON
            DEX += throws.DEX
            INT += throws.INT
            WIS += throws.WIS
            CHA += throws.CHA
        else:
            STR += self.proficiency_bonus if ABILITY.STR in throws else 0
            CON += self.proficiency_bonus if ABILITY.CON in throws else 0
            DEX += self.proficiency_bonus if ABILITY.DEX in throws else 0
            INT += self.proficiency_bonus if ABILITY.INT in throws else 0
            WIS += self.proficiency_bonus if ABILITY.WIS in throws else 0
            CHA += self.proficiency_bonus if ABILITY.CHA in throws else 0
        return Ability(STR, CON, DEX, INT, WIS, CHA)

    def roll_hp(self):
        self.effects.roll_hp()

    def roll_attack(self, attack):
        rolls = NamedTuple(roll1=self.d20.roll(), roll2=self.d20.roll(), die=self.d20)
        self.effects.roll_attack(rolls=rolls)
        attack.set_rolls(rolls)
        return attack

    def roll_dc(self, roll_type, roll_difficulty):
        proficiency = 0
        debug(roll_type)
        debug(self.proficiency_skills)
        if roll_type in ABILITY.Set():
            debug('isinstance ability')
            debug(roll_type, getattr(self.saving_throws, roll_type.__name__))
            proficiency = self.proficiency_bonus
        if roll_type in self.proficiency_skills:
            proficiency = self.proficiency_bonus
        debug(type(self.proficiency_skills))
        debug(self.proficiency_skills.get(roll_type))

        debug(self.saving_throws)
        roll1 = self.d20.roll()
        roll2 = None
        advantage = roll_type in self.advantage
        disadvantage = roll_type in self.disadvantage

        if advantage or disadvantage:
            roll2 = self.d20.roll()
        rolls = NamedTuple(roll1=roll1, roll2=roll2, die=self.d20, type=roll_type)
        self.effects.roll_dc(rolls=rolls)
        if advantage and not disadvantage:
            # noinspection PyUnresolvedReferences
            roll = max(rolls.roll1, rolls.roll1)
        elif disadvantage and not advantage:
            # noinspection PyUnresolvedReferences
            roll = min(rolls.roll1, rolls.roll1)
        else:
            # noinspection PyUnresolvedReferences
            roll = rolls.roll1

        debug('roll', roll, 'prof', proficiency, 'diff', roll_difficulty)
        return roll + proficiency > roll_difficulty
