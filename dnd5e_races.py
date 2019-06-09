from dnd5e_enums import *


class Race:
    size = SIZE.MEDIUM
    speed = 25

    def __call__(self):
        self.__repr__()

    def __repr__(self):
        print('size =', self.size.__name__)
        print('speed =', self.speed, 'ft/sec')
        print('racial bonus =\n', end='')
        print(self.racial_ability.__repr__())
        print('traits = ', end='')
        for trait in self.traits:
            print(trait.__name__ + '\n\t', end='')
        print('')


class Dwarf(Race):
    racial_ability = Ability(constitution=2)
    traits = {TRAIT.DWARVEN_RESILIENCE, TRAIT.DWARVEN_COMBAT_TRAINING, TRAIT.STONE_CUNNING,
              TRAIT.TOOL_BREWER_PROFICIENCY, TRAIT.TOOL_MASON_PROFICIENCY, TRAIT.TOOL_SMITH_PROFICIENCY,
              TRAIT.TOOL_SUPPLIES_PROFICIENCY, TRAIT.DARKVISION
              }
    size = SIZE.MEDIUM
    speed = 25
    name = 'Dwarf'
    age = (50, 350)
    height = (4*12, 5*12)
    weight = (int(150*5/6+0.5), int(150*4/3+0.5))  #5/6 to 4/3 average


class HillDwarf(Dwarf):
    name = 'Hill Dwarf'

    #    def __init__(self, name='Kathra Torunn', age=175, height=51, weight=135):
    def __init__(self):
        self.traits.update({TRAIT.DWARVEN_TOUGHNESS})
        self.racial_ability.add(wisdom=1)


class MountainDwarf(Dwarf):
    name = 'Mountain Dwarf'

    #    def __init__(self, name='Bruenor Battlehammer', age=157, height=59, weight=150):
    def __init__(self):
        self.traits.update({TRAIT.DWARVEN_ARMOR_TRAINING})
        self.racial_ability.add(strength=2)


class Elf(Race):
    name = 'Elf'
    racial_ability = Ability(dexterity=2)
    traits = {TRAIT.DARKVISION, TRAIT.KEEN_SENSES, TRAIT.FEY_ANCESTRY, TRAIT.TRANCE}
    size = SIZE.MEDIUM
    speed = 30
    age = (80, 750)
    height = (4*12+6, 6*12+6)
    weight = (int(140*5/6+0.5), int(140*4/3+0.5))  #5/6 to 4/3 average


class HighElf(Elf):
    name = 'High Elf'

    #    def __init__(self, name='Gilmirie Sopek', age=375, height=63, weight=110):
    def __init__(self):
        self.traits.update({TRAIT.ELVEN_WEAPON_TRAINING, TRAIT.CANTRIP})
        self.racial_ability.add(intelligence=1)


class WoodElf(Elf):
    name = 'Wood Elf'

    #    def __init__(self, name='Daene Letell', age=196, height=57, weight=130):
    def __init__(self):
        self.traits.update({TRAIT.ELVEN_WEAPON_TRAINING, TRAIT.FLEET_OF_FOOT, TRAIT.MASK_OF_THE_WILD})
        self.racial_ability.add(wisdom=1)


class DarkElf(Elf):
    name = 'Dark Elf'

    #    def __init__(self, name='Elurgor of House Kokek', age=276, height=62, weight=102):
    def __init__(self):
        self.racial_ability.add(charisma=1)
        self.traits.update({TRAIT.DROW_WEAPON_TRAINING, TRAIT.SUNLIGHT_SENSITIVITY, TRAIT.DROW_MAGIC,
                            TRAIT.SUPERIOR_DARKVISION})


class Halfling(Race):
    name = 'Halfling'
    traits = {TRAIT.BRAVE, TRAIT.LUCKY, TRAIT.HALFLING_NIMBLENESS}
    size = SIZE.SMALL
    racial_ability = Ability(dexterity=2)
    speed = 25
    age = (20, 250)
    height = (2*12+8, 3*12+4)
    weight = (int(42.5*5/6+0.5), int(42.5*4/3+0.5))  #40-45 in book


class LightfootHalfling(Halfling):
    name = 'Lightfoot Halfling'

    #    def __init__(self, name='Rooso Wull', age=66, height=34, weight=38):
    def __init__(self):
        self.racial_ability.add(charisma=1)
        self.traits.update({TRAIT.NATURALLY_STEALTHY})


class StoutHalfling(Halfling):
    name = 'Stout Halfling'

    #    def __init__(self, name='Rivon Bonnot', age=68, height=37, weight=46):
    def __init__(self):
        self.racial_ability.add(constitution=1)
        self.traits.update({TRAIT.STOUT_RESILIENCE})


class Human(Race):
    name = 'Human'

    traits = set()
    size = SIZE.MEDIUM
    racial_ability = Ability(strength=1, constitution=1, dexterity=1, intelligence=1, wisdom=1, charisma=1)
    age = (20, 100)
    height = (4*12+6, 7*12)
    weight = (int(140*5/6+0.5), int(180*4/3+0.5))  #book doesn't say, taking 5/6 of 140, and 4/3 of 180


class DragonBorn(Race):
    traits = {TRAIT.DRACONIC_BREATH_WEAPON, TRAIT.DRACONIC_DAMAGE_RESISTANCE}
    size = SIZE.MEDIUM
    racial_ability = Ability(strength=2, charisma=1)
    speed = 30
    age = (15, 80)
    height = (5*12+6, 7*12+6)
    weight = (int(250*5/6+0.5), int(250*4/3+0.5))  #5/6 to 4/3 average


class BlackDragonBorn(DragonBorn):
    name = 'Black Dragonborn'

    #    def __init__(self, name='Ethinclaw the Victorious', age=35, height=69, weight=181):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_BLACK})


class BlueDragonBorn(DragonBorn):
    name = 'Blue Dragonborn'

    #    def __init__(self, name='Tynludor the Dreadful', age=40, height=75, weight=247):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_BLUE})


class BrassDragonBorn(DragonBorn):
    name = 'Brass Dragonborn'

    #    def __init__(self, name='Ammantyr', age=36, height=76, weight=245):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_BRASS})


class BronzeDragonBorn(DragonBorn):
    name = 'Bronze Dragonborn'

    #    def __init__(self, name='Reghetyr the Eminent', age=33, height=76, weight=235):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_BRONZE})


class CopperDragonBorn(DragonBorn):
    name = 'Copper Dragonborn'

    #    def __init__(self, name='Shaggaust', age=45, height=79, weight=201):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_COPPER})


class GoldDragonBorn(DragonBorn):
    name = 'Gold Dragonborn'

    #    def __init__(self, name='Rhymenztyr', age=28, height=71, weight=190):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_GOLD})


class GreenDragonBorn(DragonBorn):
    name = 'Green Dragonborn'

    #    def __init__(self, name='Rynnastor the Awesome', age=37, height=72, weight=217):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_GREEN})


class RedDragonBorn(DragonBorn):
    name = 'Red Dragonborn'

    #    def __init__(self, name='Chethetor the Terrible', age=33, height=79, weight=305):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_RED})


class SilverDragonBorn(DragonBorn):
    name = 'Silver Dragonborn'

    #    def __init__(self, name='Cheluwyrm', age=36, height=74, weight=215):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_SILVER})


class WhiteDragonBorn(DragonBorn):
    name = 'White Dragonborn'

    #    def __init__(self, name='Lenastor', age=15, height=80, weight=301):
    def __init__(self):
        self.traits.update({TRAIT.DRACONIC_ANCESTRY_WHITE})


class Gnome(Race):
    name = 'Gnome'

    traits = {TRAIT.DARKVISION, TRAIT.GNOME_CUNNING}
    size = SIZE.SMALL
    racial_ability = Ability(intelligence=2)
    speed = 25
    age = (30, 500)
    height = (2*12+8, 4*12+4)
    weight = (int(40*5/6+0.5), int(40*4/3+0.5))  #5/6 to 4/3 average


class ForestGnome(Gnome):  # akaly the smart, 55,38,38
    name = 'Forest Gnome'

    #    def __init__(self, name='Akaly the Smart', age=55, height=38, weight=38):
    def __init__(self):
        self.racial_ability.add(dexterity=1)
        self.traits.update({TRAIT.NATURAL_ILLUSIONIST, TRAIT.SPEAK_WITH_SMALL_BEASTS})


class RockGnome(Gnome):  # avadu the lucky, 63,40,40
    name = 'Rock Gnome'

    #    def __init__(self, name='Avadu the lucky', age=63, height=40, weight=40):
    def __init__(self):
        self.racial_ability.add(constitution=1)
        self.traits.update({TRAIT.ARTIFICERS_LORE, TRAIT.TOOL_TINKER_PROFICIENCY})


class HalfElf(Race):  # Inneo Breeks, 77,66,146
    name = 'Half-Elf'
    racial_ability = Ability(charisma=2)
    traits = {TRAIT.DARKVISION, TRAIT.FEY_ANCESTRY, TRAIT.SKILL_VERSATILITY, TRAIT.ABILITY_VERSATILITY}
    speed = 30
    size = SIZE.MEDIUM
    age = (20, 200)
    height = (4*12+6, 7*12)
    weight = (int(140*5/6+0.5), int(180*4/3+0.5))  #book doesn't say, taking 5/6 of 140, and 4/3 of 180


#    def __init__(self, name='Inneo Breeks', age=77, height=66, weight=146):


class HalfOrc(Race):  # onraquo, 27,66,147
    name = 'Half-Orc'
    racial_ability = Ability(strength=2, constitution=1)
    traits = {TRAIT.DARKVISION, TRAIT.MENACING, TRAIT.RELENTLESS_ENDURANCE, TRAIT.SAVAGE_ATTACKS}
    speed = 30
    size = SIZE.MEDIUM
    age = (11, 75)
    height = (5*12, 7*12)
    weight = (int(180*5/6+0.5), int(220*4/3+0.5))  #book doesn't say, taking 5/6 of 140, and 4/3 of 180

#   def __init__(self, name='Onraquo', age=27, height=66, weight=147):


class Tiefling(Race):  # Jiollyn, 33,68,143
    name = 'Tiefling'
    racial_ability = Ability(strength=2, constitution=1)
    traits = {TRAIT.DARKVISION, TRAIT.HELLISH_RESISTANCE, TRAIT.INFERNAL_LEGACY}
    size = SIZE.MEDIUM
    speed = 30
    age = (20, 120)
    height = (4*12+6, 7*12)
    weight = (int(140*5/6+0.5), int(180*4/3+0.5))  #book doesn't say, taking 5/6 of 140, and 4/3 of 180

#    def __init__(self, name='Jiollyn', age=33, height=68, weight=143):
