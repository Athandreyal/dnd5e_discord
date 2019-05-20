import random
import dnd5e_enums, dnd5e_misc


# top level code file, currently empty other than aborted old ideas because I've reworked the structure repeatedly
# will be used for the outermost scope of the program.  a problem for future me.
# todo: complain that past me hasn't done this yet.

# class character():
#     def __init__(self):
#         self.level = 1
#         self.exp=0
#         #physical power
#         self.base_str=0
#         #agility
#         self.base_dex=0
#         #endurance
#         self.base_con=0
#         #reasoning and memory
#         self.base_int=0
#         #perception and insight
#         self.base_wis=0
#         #force of personality
#         self.base_cha=0
#         self.str=0
#         self.con=0
#         self.dex=0
#         self.wis=0
#         self.int=0
#         self.cha=0
#         self.str_mod=0
#         self.con_mod=0
#         self.dex_mod=0
#         self.wis_mod=0
#         self.int_mod=0
#         self.cha_mod=0
#
#         self.base_hp=0
#         self.hp=0
#         self.hitDie=None
#         self.carry_multi=15
#         self.size=MEDIUM
#
#
#     #strength factors
#     carry_capacity  = lambda self:self.str * self.carry_multi       #carrying limit
#     push_mass       = lambda self:self.str * 2 * self.carry_multi   #limit for pushing/lifting/dragging
#     lift_mass = push_mass
#     drag_mass = push_mass
#
#     def push_speed(self,mass):
#         multiple = carry_capacity()/mass
#         low = min(12,max(0,multiple-5))*(0.33/12))
#         med = min(12,max(0,multiple-17))*((0.67-0.25)/12)
#         hi = max(multiple-25,0)*.05
#         mod = 1 - low-med-hi
#         return max(1,int(self.speed*mod)) if mod < 1 else 0
#
#     def levelup(self):
#         self.str+=1
#         self.con+=1
#         self.dex+=1
#         self.wis+=1
#         self.int+=1
#         self.cha+=1
#         new_con_mod = ability_mod(self.constitution)
#         if new_con_mod != self.con_mod:   #if constitution changes, recalculate HP max
#             self.base_hp += self.level * (self.con_mod - new_con_mod)  #base HP max changes by levels times changes in constitution
#             self.con_mod = new_con_mod      #adjust con_mod to new value
#         self.base_hp+=roll(1,20,new_con_mod)  #roll 1d20 +con_mod
        

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


