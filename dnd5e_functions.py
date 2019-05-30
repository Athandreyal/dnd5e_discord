# all the functions referenced by abilities, traits, effects, statuses, etc, they go here, as callable classes
# prepended with owner of function, such as Giant_Spider being owner of a bite called GiantSpiderBite
#import dnd5e_misc as misc
import dnd5e_enums as enums
#from dnd5e_entity import Entity
from trace import print

debug = False
# todo: assign traits which are actions, to entity actions list for choice as an action when interactive
# todo: use status effects type class to pass/apply damage?

# because the events are sets, you can abruptly terminate a function's existence via raise StopIteration


# class GenericAttack:
#     # noinspection SpellCheckingInspection
#     # todo: remove this parent class if I end up not using it - it had a purpose, lost it
#     pass
#
#
# class GenericMelee(GenericAttack):
#     atype = enums.ATTACK.MELEE  # todo: make sure atype is passed around on attacks
#
#     def __init__(self, name, to_hit, reach, targets, damage):
#         self.name = name
#         self.to_hit = to_hit
#         self.reach = reach
#         self.targets = targets
#         self.die = misc.Die(damage['die_qty'], damage['die_sides'])
#         self.dtype = damage['dtype']
#
#     def __repr__(self):
#         return self.name + ' ' + str(self.die)
#
#     def __call__(self, owner, target):
#         if None in [owner, target]:
#             raise ValueError
#         advantage, disadvantage = misc.getAdvantage(owner, target)
#         attack_roll, critical = misc.attack_roll(advantage, disadvantage, owner.is_lucky())
#         attack_roll += self.to_hit
#         armor_class = target.get_ac(self.atype)
#         damage = self.die.roll()
#         for d in self.dtype:
#             d(damage)
#         return self.dtype

#
# class TraitsBase:
#     def __init__(self, parent: Entity):
#         # put self's functions into respective parent event sets.
#         parent.effects.init.update(self.init)
#         parent.effects.before_battle.update(self.before_battle)
#         parent.effects.after_turn.update(self.after_turn)
#         parent.effects.action.update(self.action)
#         parent.effects.defend.update(self.defend)
#         parent.effects.after_battle.update(self.after_battle)
#         parent.effects.level_up.update(self.level_up)
#         parent.effects.equip.update(self.equip)
#         parent.effects.unequip.update(self.unequip)


class TraitsBase:
    def __init__(self, *args, **kwargs):
        host = kwargs.get('host', None)
        # todo: when done testing, re-introduce the if host is none test
        if host is None:
            raise ValueError
        self.host = host  # reference to who owns this particular trait.
        self._install()

    def _install(self, *args, **kwargs):
        method_list = [func for func in dir(self.host.effects)
                       if callable(getattr(self.host.effects, func)) and not func.startswith("_") and func != 'Effect'
                       and hasattr(self, func)]
        for method in method_list:
            set = getattr(self.host.effects, method)
            m = getattr(self, method)
            set.add(m)
        try:
            self.install()  # silenced the not found warning.
        except AttributeError:
            pass

    def _uninstall(self, *args, **kwargs):
        method_list = (func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("_"))
        for method in method_list:
            set = getattr(self.host.effects, method)
            m = getattr(self, method)
            set.remove(m)
        try:
            self.uninstall()  # silenced the not found warning.
        except AttributeError:
            pass

    def add_affector(self, what, where):
        if debug:
            printout = {}
            print('attempting to add', what, 'in ', 'self.host.' + where)
        where_set = getattr(self.host, where)
        for effect in what:
            where_set = getattr(self.host, where)
            if effect in where_set:
                if debug:
                    print('found', effect, ', with affectors:', effect.affectors)
                affected = where_set.get(effect)
                affected.affectors.append(self)
            else:
                if debug:
                    print('didn\'t find', effect, ', instantiating it with affector', self)
                affected = effect()
                affected.affectors.append(self)
                where_set.add(affected)
            if debug:
                print(affected, 'affectors is now', affected.affectors)
        if debug:
            print('final self.host.' + where, 'is', where_set)

    def remove_affector(self, what, where):
        remove = []
        if debug:
            printout = {}
            print('attempting to remove', what, 'in ', 'self.host.' + where)
        where_set = getattr(self.host, where)
        for w in what:
            effect = where_set.get(w)
            if debug:
                print('found', what, ', with affectors:', effect.affectors)
                printout[effect] = effect.affectors.copy()
            effect.affectors.remove(self)
            if not effect.affectors:
                if debug:
                    print('removing', self, 'from', effect.affectors)
                remove.append(effect)
        for r in remove:
            if debug:
                print('trying to remove', r, ', from', where, 'due to no affectors')
            where_set.remove(r)
            if debug:
                print(where_set)

     # def install(self):
     #     self.host.effects.init.add(self)
     #     self.host.effects.equip.add(self)
     #     self.host.effects.unequip.add(self)
     #     self.host.effects.before_battle.add(self)
     #     self.host.effects.after_battle.add(self)
     #     self.host.effects.before_turn.add(self)
     #     self.host.effects.after_turn.add(self)
     #     self.host.effects.before_action.add(self)
     #     self.host.effects.after_action.add(self)
     #     self.host.effects.attack.add(self)
     #     self.host.effects.defend.add(self)
     #     self.host.effects.critical.add(self)
     #     self.host.effects.level_up.add(self)
     #     self.host.effects.rest_long.add(self)
     #     self.host.effects.rest_short.add(self)
     #     self.host.effects.roll_attack.add(self)
     #     self.host.effects.roll_damage.add(self)
     #     self.host.effects.roll_dc.add(self)
     #     self.host.effects.roll_hp.add(self)
     #     self.host.effects.death.add(self)
     #
     # def uninstall(self):
     #     self.host.effects.init.remove(self)
     #     self.host.effects.equip.remove(self)
     #     self.host.effects.unequip.remove(self)
     #     self.host.effects.before_battle.remove(self)
     #     self.host.effects.after_battle.remove(self)
     #     self.host.effects.before_turn.remove(self)
     #     self.host.effects.after_turn.remove(self)
     #     self.host.effects.before_action.remove(self)
     #     self.host.effects.after_action.remove(self)
     #     self.host.effects.attack.remove(self)
     #     self.host.effects.defend.remove(self)
     #     self.host.effects.critical.remove(self)
     #     self.host.effects.level_up.remove(self)
     #     self.host.effects.rest_long.remove(self)
     #     self.host.effects.rest_short.remove(self)
     #     self.host.effects.roll_attack.remove(self)
     #     self.host.effects.roll_damage.remove(self)
     #     self.host.effects.roll_dc.remove(self)
     #     self.host.effects.roll_hp.remove(self)
     #     self.host.effects.death.remove(self)

# keep trait objects in a big event pool, and throw the event name?
# write each as a big block, and query to see what event we've been given?
# if none of the events that matter to us, return
# if an event we care about, execute that code only

# host kwarg for parent/host object of trait
# target kwarg for applying to someone not yourself.

# if the object has state, be sure to have an init function, for re-initialising it on character level up.


class TraitAbilityScoreImprovement(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def level_up(self, *args, **kwargs):
        if self.host.level in [4, 8, 12, 16, 19]:
            self.host.unspent_ability += 2

#    def install(self, *args, **kwargs):
#        self.host.effects.level_up.add(self.level_up)


class DCThrow(TraitsBase):
    def __init__(self, *args, **kwargs):
        import dnd5e_misc as misc
        super().__init__(*args, **kwargs)
        self.die = misc.Die(1, 20)

    def roll_dc(self, *args, **kwargs):
        roll_for = kwargs.get('roll_for', None)
        difficulty = kwargs.get('difficulty', None)
        proficiency = 0
        for throw in self.host.saving_throws:
            if isinstance(roll_for, throw):
                proficiency = max(self.host.proficiency, proficiency)


class TraitNaturalDefence(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.armor_class = self.host.abilities.DEX_MOD + 10

    def init(self, *args, **kwargs):
        self.armor_class = self.host.abilities.DEX_MOD + 10

#    def install(self, *args, **kwargs):
#        self.host.effects.init.add(self.init)
#        self.host.effects.defend.add(self.defend)

    def defend(self, *args, **kwargs):
        defence = kwargs['defence']
        defence.armor_classes.append(self.armor_class)


class ClassTraitRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rages = self.get_rage_count()  # number of times one can rage
        self.bonus = self.get_rage_bonus()  # damage bonus for being enraged
        self.raging = False  # current state, are we raging now?
        self.duration = 0  # how long have we been raging
        self.last_attack = 0  # how many increments ago did we last attack something?
        self.hvy_armor = False
        self.added_effects = False
        self.added_rage_effects = False
        self.hvy_armor_types = enums.ARMOR.HEAVY.Set()

    def get_rage_count(self):
        level = self.host.level
        return 2 + (1 if level >= 3 else 0) + (1 if level >= 6 else 0) + (1 if level >= 12 else 0)  \
                 + (1 if level >= 17 else 0) + (1000000 if level >= 20 else 0)

    def get_rage_bonus(self):
        level = self.host.level
        return 2 + (1 if level >= 9 else 0) + (1 if level >= 16 else 0)

    def prevent_casting(self, prevent=True):
        if self.hvy_armor: return
        # todo, apply a 'silence' or sorts to self - disable spell casting for duration of a rage.
        pass

    def init(self, *args, **kwargs):
        if debug:
            print('rage init')
        self.rages = self.get_rage_count()
        self.bonus = self.get_rage_bonus()
        self.raging = False
        self.duration = 0
        self.last_attack = 0
        self.added_effects = False
        self.hvy_armor = any(a in self.hvy_armor_types for a in self.host.equipment.armor.enum_type)
        if self.hvy_armor:
            if debug:
                print('hvy armor, rage cancelling init')
            return
        elif not self.added_effects:
            self.added_effects = True
            if debug:
                print('rage init, no hvy armor, adding STR and CON advantages')
            self.add_affector({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON}, 'advantage')

    rest_long = init

    def death(self, *args, **kwargs):
        if self.hvy_armor: return
        self.raging = False
        self.duration = 0
        self.last_attack = 0

    def attack(self, *args, **kwargs):
        if self.hvy_armor: return
        attack = kwargs.get('attack', None)
        if attack is None:
            raise ValueError
        if self not in attack.effects:
            attack.bonus_damage += self.bonus
        self.last_attack = -1  # use end_turn to increment to zero

    def equip_change(self, *args, **kwargs):
        self.hvy_armor = any(a in self.hvy_armor_types for a in self.host.equipment.armor.enum_type)

        if not self.hvy_armor:
            self.rages = self.get_rage_count()
            self.bonus = self.get_rage_bonus()
            if not self.added_effects:
                print('rage equip_change init, no hvy armor, adding STR and CON advantages')
                self.add_affector({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON}, 'advantage')
                self.added_effects = True
        else:
            if self.added_effects:
                print('rage equip_change init, hvy armor, removing STR and CON advantages')
                self.remove_affector({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON}, 'advantage')
                self.added_effects = False

    equip = equip_change
    unequip = equip_change

    def before_turn(self, *args, **kwargs):
        if self.hvy_armor: return
        if debug:
            print('rage before_turn, no hvy armor')
        if self.raging:
            if self.last_attack == 1 or self.duration > 10:
                self.raging = False
                self.rages -= 1
                self.duration = 0
                self.last_attack = 0
                self.prevent_casting(False)
                if self.added_rage_effects:
                    self.added_rage_effects = False
                    self.remove_affector({enums.DAMAGETYPE.BLUNT, enums.DAMAGETYPE.PIERCING, enums.DAMAGETYPE.SLASHING},
                                         'damage_resist')
        elif self.rages > 0:
            # todo: enable choosing to rage as an action, rather than automatically defaulting to yes.
            #  automatic
            self.raging = True
            self.last_attack = -1  # use end_turn to increment to zero
            self.prevent_casting()
            if not self.added_rage_effects:
                self.added_rage_effects = True
                self.add_affector({enums.DAMAGETYPE.BLUNT, enums.DAMAGETYPE.PIERCING, enums.DAMAGETYPE.SLASHING},
                                  'damage_resist')

    def after_battle(self, *args, **kwargs):
        if self.hvy_armor: return
        if debug:
            print('rage after_battle, no hvy armor')
        self.raging = False

    def after_turn(self, *args, **kwargs):
        if self.hvy_armor: return
        if debug:
            print('rage after_turn, no hvy armor')
        if self.raging:
            self.duration += 1
            self.last_attack += 1


class ClassTraitUnarmoredDefence(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.armor_class = 10 + self.host.abilities.DEX_MOD + self.host.abilities.CON_MOD

    # def install(self, *args, **kwargs):
    #     self.host.effects.equip.add(self.equip_change)
    #     self.host.effects.unequip.add(self.equip_change)
    #     self.host.effects.defend.add(self.defend)
    #     self.host.effects.level_up.add(self.level_up)
    #
    # def uninstall(self, *args, **kwargs):
    #     self.host.effects.equip.remove(self.equip_change)
    #     self.host.effects.unequip.remove(self.equip_change)
    #     self.host.effects.defend.remove(self.defend)
    #     self.host.effects.level_up.remove(self.level_up)

    def equip_change(self, *args, **kwargs):
        if self.host.equipment.armor is None:
            self.install()
        else:
            self.uninstall()

    equip = equip_change
    unequip = equip_change

    def init(self, *args, **kwargs):
        self.armor_class = 10 + self.host.abilities.DEX_MOD + self.host.abilities.CON_MOD

    def level_up(self, *args, **kwargs):
        self.init()

    def defend(self, *args, **kwargs):
        defence = kwargs['defence']
        attack = kwargs['attack']
        defence.armor_classes.append(self.armor_class)
        for damage in attack.damage:
            if damage in self.host.damage_resist:
                damage //= 2
            elif damage in self.host.damage_vulnerable:
                damage *= 2


class ClassTraitRecklessAttack(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.activated = False

    def before_turn(self, *args, **kwargs):
        if debug:
            print(self.host.name, 'reckless before_turn, activated =', self.activated, end=', ')
        if self.activated: return
        if debug:
            __builtins__['print']('proceeding...')
        self.add_affector({enums.ATTACK.MELEE}, 'advantage')

    def attack(self, *args, **kwargs):
        if debug:
            print(self.host.name, 'reckless attack, activated =', self.activated, end=', ')
        if self.activated: return
        if debug:
            __builtins__['print']('proceeding...')
        self.remove_affector({enums.ATTACK.MELEE}, 'advantage')
        self.add_affector({enums.DEFENCE.MELEE}, 'disadvantage')
        self.activated = True

    def after_turn(self, *args, **kwargs):
        if debug:
            print(self.host.name, 'reckless after_turn, activated =', self.activated, end=', ')
        if not self.activated: return
        if debug:
            __builtins__['print']('proceeding...')
        self.activated = False
        if debug:
            print(self.host.name, self.host.advantage, 'disadvantage')
            for adv in self.host.advantage:
                print(adv,  end='')
                if hasattr(adv, 'affectors'):
                    __builtins__['print'](adv.affectors)
                else:
                    __builtins__['print']('')
        self.remove_affector({enums.DEFENCE.MELEE}, 'disadvantage')


class ClassTraitDangerSense(TraitsBase):
    # todo: ensure that blinded, deafened, and incapacitated are not in self.host.status
    # todo test this
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)
        self.advantage = False

#    def init(self, *args, **kwargs):
#        self.add_affector({enums.SKILL.PERCEPTION}, self.host.advantage)

    # def install(self, *args, **kwargs):
    #     self.host.effects.init.add(self.init)
    #     self.host.effects.before_turn.add(self.before_turn)
    #     # self.host.effects.roll_dc.add(self)  # todo: implement roll_dc event
    #
    # def uninstall(self, *args, **kwargs):
    #     self.host.effects.init.remove(self.init)
    #     self.host.effects.before_turn.remove(self.before_turn)
    # #     self.host.effects.roll_dc.remove(self)

    def before_turn(self, *args, **kwargs):
        # todo: implement getter for status list
        # todo: implement test if status in self.host.status
        if not self.advantage and (self.host.status.get(enums.STATUS.BLINDED) is None
                                   and self.host.status.get(enums.STATUS.DEAFENED) is None
                                   and self.host.status.get(enums.STATUS.INCAPACITATED) is None):
            self.add_affector({enums.SKILL.PERCEPTION}, 'advantage')
            self.advantage = True
        if self.advantage and (self.host.status.get(enums.STATUS.BLINDED) is not None
                               or self.host.status.get(enums.STATUS.DEAFENED) is not None
                               or self.host.status.get(enums.STATUS.INCAPACITATED) is not None):
            self.remove_affector({enums.SKILL.PERCEPTION}, 'advantage')
            self.advantage = False


class ClassTraitExtraAttack(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before_turn(self, *args, **kwargs):
        attack = kwargs.get('attack', None)
        if attack.num < 2:
            attack.num += 1


class ClassTraitFastMovement(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_speed = self.host.speed
        self.hvy_armor = False

    def equip_change(self, *args, **kwargs):
        if self.host.equipment.armor.type not in enums.ARMOR.HEAVY.Set():
            self.add_affector({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON}, 'advantage')
#            self.host.advantage.update({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON})
            # todo: embed a list of everyone who confers a trait/advantage within said trait/advantage, so that
            #  removal of one supplier does not also remove the trait/advantage until all are moved.
            self.hvy_armor = False
            self.host.speed = self.host_speed + 10
        else:
            self.hvy_armor = True
            self.host.speed = self.host_speed
            self.remove_affector({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON}, 'advantage')

    equip = equip_change
    unequip = equip_change
    init = equip_change


class ClassTraitFeralInstinct(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # todo: implement me.  This trait is kinda weird for how things are.
        #    We aren't rolling initiative currently, and surprise is not a thing....yet


class ClassTraitBrutalCritical(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def critical(self, *args, **kwargs):
        attack = kwargs.get('attack', None)
        if attack.critical_multi <= 2:
            attack.critical_multi += 1


class ClassTraitRelentlessRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dc = 5

    def incapacitated(self, *args, **kwargs):
        # todo: create an incapacitated event
        # todo: change do_battle to use the incapacitated event, and trigger revive / death checks
        self.host.hp = 1


class ClassTraitPersistentRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitIndomitableMight(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitPrimalChampion(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitFrenzy(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitMindlessRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitIntimidatingPresence(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitRetaliation(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitSpiritSeeker(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitSpiritWalker(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitTotemBear(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitAspectBear(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitAttuneBear(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitTotemEagle(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitAspectEagle(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitAttuneEagle(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitTotemWolf(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitAspectWolf(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ClassTraitAttuneWolf(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class RaceTraitLucky(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def roll_dc(self, *args, **kwargs):
        pass  # todo: implement lucky's roll_dc

    def roll_hp(self, *args, **kwargs):
        pass  # todo: implement lucky's roll_hp

    def roll_attack(self, *args, **kwargs):
        attack = kwargs.get('attack', None)
        if attack.roll1 == 1:
            attack.roll1 = attack.attack_die.roll()
        elif attack.roll2 == 1:
            attack.roll2 = attack.attack_die.roll()

    def roll_damage(self, *args, **kwargs):
        attack = kwargs.get('attack', None)


if __name__ == '__main__':
    from trace import print
    import dnd5e_character_sheet as character
    wulfgar = character.init_wulfgar()
    try:
        rage = ClassTraitRage()
    except ValueError as e:
        print('caught the intended value error in ClassTraitRage: ', e)
    print(wulfgar.effects.init)
    for f in wulfgar.effects.init:
        print(f)
