# all the functions referenced by abilities, traits, effects, statuses, etc, they go here, as callable classes
# prepended with owner of function, such as Giant_Spider being owner of a bite called GiantSpiderBite
#import dnd5e_misc as misc
import dnd5e_enums as enums
#from dnd5e_entity import Entity
from trace import print


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
            return
#            print(dir(self.__class__))
#            print(self.__class__.__name__)
#            raise ValueError('A host is required for %s' % self.__class__.__name__)
        self.host = host  # reference to who owns this particular trait.
#        host.effects.all.add(self)
        self.install()

#     def __call__(self, *args, **kwargs):
#         try:
#             self.onEvent(*args, **kwargs)
#         except TypeError as e:
#             pass  # todo: un-pass this, and let the errors flow forth - find and kill.

    def install(self): pass
    def uninstall(self): pass

    def add_affector(self, what, where):
        for effect in what:
            if effect in where:
                affected = where.get(effect)
                affected.affectors.append(self)
            else:
                affected = effect()
                affected.affectors.append(self)
                where.add(affected)

    def remove_affector(self, what, where):
        remove = []
        for w in what:
            effect = where.get(w)
            effect.affectors.remove(self)
            if not effect.affectors:
                remove.append(effect)
        for r in remove:
            where.remove(r)

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


class TraitNaturalDefence(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return
        self.armor_class = self.host.abilities.DEX_MOD + 10

    def init(self, *args, **kwargs):
        self.armor_class = self.host.abilities.DEX_MOD + 10

    def install(self):
        self.host.effects.init.add(self.init)
        self.host.effects.defend.add(self.defend)

    def defend(self, *args, **kwargs):
        try:
            defence = kwargs['defence']
            defence.armor_classes.append(self.armor_class)
        except ValueError as e:
            print(e)


class ClassTraitRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return
        self.rages = self.get_rage_count()  # number of times one can rage
        self.bonus = self.get_rage_bonus()  # damage bonus for being enraged
        self.raging = False  # current state, are we raging now?
        self.duration = 0  # how long have we been raging
        self.last_attack = 0  # how many increments ago did we last attack something?

    def get_rage_count(self):
        level = self.host.level
        return 2 + (1 if level >= 3 else 0) + (1 if level >= 6 else 0) + (1 if level >= 12 else 0)  \
                 + (1 if level >= 17 else 0) + (1000000 if level >= 20 else 0)

    def get_rage_bonus(self):
        level = self.host.level
        return 2 + (1 if level >= 9 else 0) + (1 if level >= 16 else 0)

    def prevent_casting(self, prevent=True):
        # todo, apply a 'silence' or sorts to self - disable spell casting for duration of a rage.
        pass

    def install(self):
        self.host.effects.init.add(self.reset)
        self.host.effects.equip.add(self.equip_change)
        self.host.effects.unequip.add(self.equip_change)
        self.host.effects.after_battle.add(self.after_battle)
        self.host.effects.before_turn.add(self.before_turn)
        self.host.effects.after_turn.add(self.after_turn)
        self.host.effects.attack.add(self.attack)
        self.host.effects.rest_long.add(self.reset)
        self.host.effects.death.add(self.death)
        self.add_affector({enums.DAMAGETYPE.BLUNT, enums.DAMAGETYPE.PIERCING, enums.DAMAGETYPE.SLASHING},
                          self.host.damage_resist)

    def uninstall(self):
        self.host.effects.init.remove(self.reset)
        self.host.effects.after_battle.remove(self.after_battle)
        self.host.effects.after_turn.remove(self.after_turn)
        self.host.effects.before_turn.remove(self.before_turn)
        self.host.effects.attack.remove(self.attack)
        self.host.effects.rest_long.remove(self.reset)
        self.host.effects.death.remove(self.death)
        # todo: make these instances, or carry an int for number of times applied so as to know when to remove or not.
#        self.host.damage_resist.remove({enums.DAMAGETYPE.BLUNT, enums.DAMAGETYPE.PIERCING, enums.DAMAGETYPE.SLASHING})
        self.remove_affector({enums.DAMAGETYPE.BLUNT, enums.DAMAGETYPE.PIERCING, enums.DAMAGETYPE.SLASHING},
                             self.host.damage_resist)
        # remove = []  # todo: test that this does what it says on the tin
        # for damage in {enums.DAMAGETYPE.BLUNT, enums.DAMAGETYPE.PIERCING, enums.DAMAGETYPE.SLASHING}:
        #     resist = self.host.damage_resist.get(damage)
        #     resist.affectors.remove(self)
        #     if not resist.affectors:
        #         remove.append(resist)
        # for r in remove:
        #     self.host.damage_resist.remove(r)

    def reset(self, *args, **kwargs):
        self.rages = self.get_rage_count()
        self.bonus = self.get_rage_bonus()
        self.raging = False
        self.duration = 0
        self.last_attack = 0

    def death(self, *args, **kwargs):
        self.raging = False
        self.duration = 0
        self.last_attack = 0

    def attack(self, *args, **kwargs):
        attack = kwargs.get('attack', None)
        if attack is None:
            raise ValueError
        if self not in attack.effects:
            attack.bonus_damage += self.bonus
        self.last_attack = -1  # use end_turn to increment to zero

    def equip_change(self, *args, **kwargs):
        if self.host.equipment.armor.type not in enums.ARMOR.HEAVY.Set():
            self.host.advantage.update({enums.ADVANTAGE.STR, enums.ADVANTAGE.CON})
            # todo: embed a list of everyone who confers a trait/advantage within said trait/advantage, so that
            #  removal of one supplier does not also remove the trait/advantage until all are moved.
            self.rages = self.get_rage_count()
            self.bonus = self.get_rage_bonus()
            self.install()
        else:
            self.uninstall()

    def before_turn(self, *args, **kwargs):
        if self.raging:
            if self.last_attack == 1 or self.duration > 10:
                self.raging = False
                self.rages -= 1
                self.duration = 0
                self.last_attack = 0
                self.prevent_casting(False)
        elif self.rages > 0:
            # todo: enable choosing to rage as an action, rather than automatically defaulting to yes.
            #  automatic
            self.raging = True
            self.last_attack = -1  # use end_turn to increment to zero
            self.prevent_casting()

    def after_battle(self, *args, **kwargs):
        self.raging = False

    def after_turn(self, *args, **kwargs):
        if self.raging:
            self.duration += 1
            self.last_attack += 1


class ClassTraitUnarmoredDefence(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return
        self.armor_class = 10 + self.host.abilities.DEX_MOD + self.host.abilities.CON_MOD

    def install(self):
        self.host.effects.equip.add(self.equip_change)
        self.host.effects.unequip.add(self.equip_change)
        self.host.effects.defend.add(self.defend)
        self.host.effects.level_up.add(self.level_up)

    def uninstall(self):
        self.host.effects.equip.remove(self.equip_change)
        self.host.effects.unequip.remove(self.equip_change)
        self.host.effects.defend.remove(self.defend)
        self.host.effects.level_up.remove(self.level_up)

    def equip_change(self, *args, **kwargs):
        if self.host.equipment.armor is None:
            self.install()
        else:
            self.uninstall()

    def init(self):
        self.armor_class = 10 + self.host.abilities.DEX_MOD + self.host.abilities.CON_MOD

    def level_up(self):
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
        if kwargs.get('host', None) is None:
            return
        self.activated = False

    def before_turn(self, *args, **kwargs):
        if self.activated: return
        self.add_affector({enums.ATTACK.MELEE}, self.host.advantage)
        self.add_affector({enums.DEFENCE.MELEE}, self.host.disadvantage)
        self.activated = True

    def init(self, *args, **kwargs):
        self.activated = False

    def after_turn(self, *args, **kwargs):
        self.activated = False
        self.remove_affector({enums.ATTACK.MELEE}, self.host.advantage)
        self.remove_affector({enums.DEFENCE.MELEE}, self.host.disadvantage)

    def install(self):
        # todo: leave this disabled until player choice is a thing - may need before/after attack events to [dis/en]able
        pass
        # self.host.effects.init.add(self.init)
        # self.host.effects.before_turn.add(self.before_turn)
        # self.host.effects.after_turn.add(self.after_turn)

    def uninstall(self):
        # todo: leave this disabled until player choice is a thing - may need before/after attack events to [dis/en]able
        pass
        # self.host.effects.init.remove(self)
        # self.host.effects.before_turn.remove(self)
        # self.host.effects.after_turn.remove(self)


class ClassTraitDangerSense(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitExtraAttack(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitFastMovement(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitFeralInstinct(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitBrutalCritical(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitRelentlessRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitPersistentRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitIndomitableMight(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitPrimalChampion(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitFrenzy(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitMindlessRage(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitIntimidatingPresence(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitRetaliation(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitSpiritSeeker(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitSpiritWalker(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitTotemBear(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitAspectBear(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitAttuneBear(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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



class ClassTraitTotemEagle(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitAspectEagle(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitAttuneEagle(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitTotemWolf(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitAspectWolf(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


class ClassTraitAttuneWolf(TraitsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('host', None) is None:
            return

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


if __name__ == '__main__':
    from trace import print
    import dnd5e_character_sheet as character
    wulfgar = character.init_wulfgar()
    try:
        rage = ClassTraitRage()
    except ValueError as e:
        print('caught the intended value error in ClassTraitRage: ', e)
