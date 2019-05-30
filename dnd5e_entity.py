# parent class to both Character Sheet and creature, has things relevant to encounters.
from dnd5e_enums import TRAIT, ABILITY, Ability, SKILL
import dnd5e_weaponry as weaponry
from dnd5e_events import Event
from dnd5e_inventory import Equipped
from dnd5e_misc import Attack, Die


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
        self.advantage = Event().none()
        self.disadvantage = Event().none()
        self.atk_bonus = 0
        self.damage_vulnerable = Event().none()  # todo: implement damage vulnerabilities
        self.damage_resist = Event().none()  # todo: implement damage resistances
        self.abilities = abilities
        if self.abilities is None:
            self.abilities = Ability()
        self.proficiency_skills = skills
        if self.proficiency_skills is None:
            self.proficiency_skills = Event().none()
        self.proficiency_bonus = proficiency_bonus
        if self.proficiency_bonus is None:
            self.proficiency_bonus = 0
        self.saving_throws = self.set_saving_throws(saving_throws)
        if self.saving_throws is None:
            self.saving_throws = Ability()
        self.temporary_hitpoints = 0
        self.actions = Event().none()
        self.status = Event().none()
        self.unspent_ability = unspent_ability
        if self.unspent_ability is None:
            self.unspent_ability = 0

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

    def is_lucky(self):
        return TRAIT.LUCKY in self.traits

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
        attacks = Attack(num=1)

#        if CLASS_TRAITS.EXTRA_ATTACK in self.traits:
#            attacks['num'] += 1

        # is storing two of the same reference
#        attacks['effects'] = effects
        attacks.calculation = self._wpn
        attacks.weapons = self.equipment.right_hand, self.equipment.left_hand, \
                          self.equipment.jaw, self.equipment.fingers
        return attacks

    def _wpn(self, hand: weaponry.Weapon = None):
        while True:
            if hand is None:
                yield 0
            damage = hand.roll()
            if damage == 1 and self.is_lucky():
                damage = hand.attack_die.roll()
            damage += hand.bonus_die.roll() if hand.bonus_die is not None else 0
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

    def save_roll(self, roll_type, roll_difficulty):
        die = Die(1, 20)
        proficiency = 0
        if roll_type in self.proficiency_skills:
            proficiency = self.proficiency_bonus
        return die.roll() + proficiency > roll_difficulty
