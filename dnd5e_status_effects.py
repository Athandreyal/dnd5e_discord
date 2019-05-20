import random
import dnd5e_enums as enums
import dnd5e_misc

# melee attack
#   add str modifier to attack roll and damage roll
# ranged/finesse attack
#   add dex modifier to attack roll and damage roll

# armor class
#   depending on armor, might add dex value to armor class

# initiative
#   uses dexterity to determine movement order

# hiding
#   uses dexterity(stealth) to hide
#   uses wis(perception) to search for

# spell casting
#   sets spell DC for setting spell saving throw to resist
#

# saving throws
#   attempts to resist spell, trap, poison, disease, etc.
#   standard 1d20 roll with ability_mod
#   situationally modified with bonus/penalty
#   (dis)advantage bonus/penalty

# difficulty class (DC)
#   determines by effect that causes it, spells are determined via spellcasting and proficiency bonus


class Effect:
    def __init__(self):
        self.name = None
        self.range = None
        self.dice = None
        self.sides = None
        self.range = None
        self.range_throw = None
        self.duration_turns = None
        self.duration_time = None
        self.on_turn_start = False
        self.on_turn_end = False
        self.immediate = False
        self.attack_type = None

    def on_turn(self):
        if not self.on_turn_start:
            return


class Acid(Effect):
    def __init__(self):
        super().__init__()
        self.name = 'Acid'
        self.range = 5
        self.range_throw = 20
        self.dice = 2
        self.sides = 6
        self.attack_type = enums.ATTACK.RANGED
        self.immediate = True
        self.duration_turns = 0  # will be applied on init, and then removed.


class AlchemistFire(Effect):
    def __init__(self):
        super().__init__()
        self.name = "Alchemist's Fire"
        self.range_throw = 20
        self.dice = 1
        self.sides = 4
        self.on_turn_start = True
        self.duration_turns = float('inf')  # every turn until it is stopped by some action
        self.attack_type = enums.ATTACK.RANGED

    
class Antitoxin(Effect):
    def __init__(self):
        super().__init__()
        self.name('Antitoxin')
