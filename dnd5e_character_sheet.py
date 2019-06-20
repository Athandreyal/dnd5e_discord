import dnd5e_enums as enums
import dnd5e_misc as misc
import dnd5e_races as RACE
import dnd5e_classes as CLASS
import dnd5e_weaponry as weaponry
import dnd5e_armor as armor
import json
from dnd5e_entity import Entity

debug = lambda *args, **kwargs: False  #dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


class CharacterSheet(Entity):
    # todo: embed senses relevant to hostile detection for when it comes time to do battles  darkness is irrelevant
    #  if no one can see anyway and everyone knows where everyone is by default as a consequence.

    def __init__(self, name, age, height, weight, uid, experience, level, unspent, player_race, player_class, skills,
                 background, abilities, hp_dice, hp_current, equipment):
        if level == 0:  # fresh character init
            self.level = 1
            hp_max = abilities.CON_MOD + player_class.hitDie
            self.hp_dice = hp_max
        else:
            self.level = level
            hp_max = hp_dice + (level - 1) * abilities.CON_MOD
            self.hp_dice = hp_dice
        player_race = player_race.__class__()
        player_class = player_class.__class__(self.level)
        proficiency_bonus = player_class.get_proficiency_bonus(self.level)
        traits = player_race.traits.union(player_class.traits)
        traits.add(enums.TRAIT.NATURAL_DEFENCE)
        super().__init__(name=name, traits=traits, abilities=abilities, hp=hp_current, hp_max=hp_max, skills=skills,
                         saving_throws=player_class.saving_throws, equipment=equipment, speed=player_race.speed,
                         proficiency_bonus=proficiency_bonus, unspent_ability=unspent)
        self.age = age
        self.height = height
        self.weight = weight
        self.uid = uid

#        player_race = RACE.Human()
#        player_class = CLASS.Barbarian(level)
#        class_skills = {enums.SKILL.ATHLETICS, enums.SKILL.PERCEPTION}
#        background = enums.BACKGROUNDS.OUTLANDER

        self._experience = experience
        self.player_race = player_race
        self.player_class = player_class

        self.nextLevel = self.get_next_level_xp()
        self.proficiency_weapons = self.player_class.proficiencies.intersection(enums.WEAPONS.Set())
        self.proficiency_armor = self.player_class.proficiencies.intersection(enums.ARMOR.Set())
        #                    todo: apply proficiencies from class/race to character
        self.proficiency_tools = set()  # todo: apply proficiencies from class/race to character
        self.initiative = self.abilities.DEX_MOD  # todo: proper initiative
        self.background = background  # todo: complete the init of backgrounds
        self.traits.update(self.traits.union(traits))

        # register all the traits
        for trait in self.traits:
            debug('installing trait', trait)
            trait(host=self)

        # todo: execute init event - the always event
        self.effects.init()
        if self.experience > self.get_next_level_xp():
            self.level_up()


    @property
    def experience(self):
        return self._experience

    @experience.setter
    def experience(self, xp):
        self._experience = xp
        if self.experience > self.get_next_level_xp():
            self.level_up()

    def level_up(self):
        # todo: run all statuses/traits to get their combined additional effects
        #  subtract those effects from the character, re-init() the character, re-apply all the statuses/traits
        while self.get_next_level_xp() < self.experience:
            self.level += 1
            self.hp_dice += misc.Die(1, self.player_class.hitDie).roll()
            self.__init__(name=self.name, age=self.age, height=self.height, weight=self.weight, uid=self.uid,
                          experience=self.experience, level=self.level, player_race=self.player_race,
                          player_class=self.player_class, skills=self.proficiency_skills, background=self.background,
                          abilities=self.abilities, hp_dice=self.hp_dice, hp_current=None, equipment=self.equipment,
                          unspent=self.unspent_ability)
            self.effects.level_up()

    def get_next_level_xp(self):
        xp = {2:     300,
              3:     900,
              4:    2700,
              5:    6500,
              6:   14000,
              7:   23000,
              8:   34000,
              9:   48000,
              10:  64000,
              11:  85000,
              12: 100000,
              13: 120000,
              14: 140000,
              15: 165000,
              16: 195000,
              17: 225000,
              18: 265000,
              19: 305000,
              20: 355000,
              21: 999999999999999999999999}
        return xp.get(self.level+1, -1)

    def full_str(self):
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
        s += 'Hitpoints: \t\t\t\t' + '{:,}'.format(self.hp) + '/' + '{:,}'.format(self.hp_max)+'\n'
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
                'level': self.level,
                'hp': '{:,}'.format(self.hp) + '/' + '{:,}'.format(self.hp_max),
                }

    def get_armor_class(self):  # todo: apply modifiers from various traits, statuses, and spell effects
        # DETERMINE WHAT AC FORMULAS CAN BE USED FOR CHARACTER
        #   CLASSES CAN HAVE DEFENSIVE ARMOR CALCULATIONS(BARBARIAN UNARMORED DEFENCE FOR EXAMPLE)
        # DETERMINE WHICH YIELDS HIGHEST RESULT
        #   THEY DO NOT STACK, SO USE THE BEST ONE
        # TACK ON ANY BONUSES TO AC
        #   SHIELDS TO NOT HAVE A CALCULATION, THEY SIMPLY ADD 2 TO AC, AS AN EXAMPLE
        # RETURN RESULT

        # todo: throw defence event related to specific attack type, modify ac if necessary - may need to return
        #  statuses from here for thorns like effects

        # todo: poll all gear(not just armor), and sum the AC values.
        # todo: run racial/class defence functions, keep best AC value.
        # CURRENTLY NO EQUIPMENT IN USE, SO ALWAYS RETURNS BASIC ARMOR FOR NOW.
        if self.equipment.armor is None:
            return 10 + self.abilities.DEX_MOD
        else:  # have armor, calculate it.
            base_armor_class = self.equipment.armor.armor_class
            dex_bonus = min(self.abilities.DEX_MOD, self.equipment.armor.dex_limit)
            proficiency = self.equipment.armor.type.intersection(self.proficiency_armor)
            if proficiency:
                proficiency_bonus = self.proficiency_bonus
            else:
                proficiency_bonus = 0

            armor_class = base_armor_class + dex_bonus + proficiency_bonus

            return armor_class

    def to_dict(self):
        d = super().to_dict()
        skills = self.player_class.skills.difference(self.background.SKILLS)

        def pop(x):
            try:
                return x.pop().__name__
            except KeyError:
                return None

        s = []
        for n in range(4):
            s.append(pop(skills))
        d['unspent_pts'] = self.unspent_ability
        d['race'] = self.player_race.name
        d['class'] = self.player_class.name
        d['background'] = self.background.__name__
        d['path'] = None
        d['skill1'] = s[0]
        d['skill2'] = s[1]
        d['skill3'] = s[2]
        d['skill4'] = s[3]
        d['str'] = self.abilities.STR
        d['con'] = self.abilities.CON
        d['dex'] = self.abilities.DEX
        d['int'] = self.abilities.INT
        d['wis'] = self.abilities.WIS
        d['cha'] = self.abilities.CHA
        d['hp_dice'] = self.hp_dice
        d['hp_current'] = self.hp
        d['uid'] = self.uid
        # todo: when having a  path becomes a thing, save the path here
        return d


def init_wulfgar():
    # THESE ARE WHAT WE NEED TO KNOW IN ORDER TO LOAD A CHARACTER
    # INVENTORY IS GONNA BE AN EXPANSIVE MESS...PERHAPS JUST A DATABASE TABLE ID - LOAD EVERYTHING WE FIND THERE?
    #
    name = 'Wulfgar, son of Beornegar'
    age = 21
    height = 7 * 12 + 1  # 7` 1"
    weight = 223
    uid = 1
#    experience = 85001  # lvl 11
    experience = 1  # lvl 11
    level = 0
    unspent_pts = 0
    player_race = RACE.Human()
    player_class = CLASS.Barbarian(level)
    class_skills = {enums.SKILL.ATHLETICS, enums.SKILL.PERCEPTION}
    background = enums.BACKGROUNDS.OUTLANDER
    # abilities = enums.Ability(24, 16, 22, 9, 14, 11)
    abilities = enums.Ability(15, 13, 14, 8, 12, 10)
    # hp_dice = 179  # sum total of all hp rolls to date - needs to be kept for recalculating hp on con_mod change
    hp_dice = 0
    # hp_current = 236
    hp_current = None
    weapon = weaponry.greataxe  # todo: implement weapons/shields/armor
    _armor = armor.breastplate_Armor  # todo: implement weapons/shields/armor
    shield = None  # todo: implement weapons/shields/armor
    return CharacterSheet(name, age, height, weight, uid, experience, level, unspent_pts, player_race, player_class,
                          class_skills, background, abilities, hp_dice, hp_current, [weapon, _armor, shield])


if __name__ == '__main__':
    from trace import print

    wulfgar = init_wulfgar()
    print(wulfgar, '\n\n', wulfgar.dict_short(), '\n', wulfgar.full_str())

    block = '''\n\n
    \t\t****************************
    \t\t***   get attack debug   ***
    \t\t****************************\n\n'''
    print(block)
    print(wulfgar.melee_attack())

    attack = wulfgar.melee_attack()
    print(attack)

    results = [None, None]
    calculation = attack.calculation
    for n in range(attack.num):
        results[n] = calculation(attack.weapons[n])
    print(results)
    results2 = []
    for d in attack.weapons[0].damage_type:
        print(d)
    for n in range(len(results)):
        for a in range(attack.num):
            print(str(n)+'_'+str(a), attack.weapons[n], attack.weapons[n] is not None)
            if attack.weapons[n] is not None:
                print(attack.weapons[n].damage_type)
                damage = results[n].__next__()[0]
                print(damage)
                [results2.append(damage) for x in attack.weapons[n].damage_type]
                print(results2)
    print('attacks and damage types:', results2)

    import dnd5e_enums as enums

    if wulfgar.roll_dc(enums.ABILITY.CON, 10):
        print('success')
    else:
        print('fail')
    if wulfgar.roll_dc(enums.SKILL.ATHLETICS, 10):
        print('success')
    else:
        print('fail')

    print('ability limit test')
    print(wulfgar.abilities)
    for n in range(20):
        wulfgar.abilities.add(strength=1, constitution=1, dexterity=1, intelligence=1, wisdom=1, charisma=1)
        print(wulfgar.abilities)
    # should be all 20 now
    wulfgar.abilities.set_max(STR=24, CON=24)
    for n in range(4):
        wulfgar.abilities.add(strength=1, constitution=1, dexterity=1, intelligence=1, wisdom=1, charisma=1)
        print(wulfgar.abilities)
    print('calling to_dict()')
    while wulfgar.level < 17:
        wulfgar.experience += 200
    w = wulfgar.to_dict()
    print(w)
    ability = enums.Ability(strength=w['str'], constitution=w['con'], dexterity=w['dex'], intelligence=w['int'],
                            wisdom=w['wis'], charisma=w['cha'])
    wulfgar2 = CharacterSheet(w['name'], w['age'], w['height'], w['weight'], w['uid'], w['experience'], w['level'],
                              w['unspent_pts'], w['race'], w['class'],
                              [x for x in [w['skill1'], w['skill2'],w['skill3'], w['skill4']]if x is not None],
                              w['background'], ability, w['hp_dice'], w['hp_current'], [weapon, _armor, shield])
