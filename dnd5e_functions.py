# all the functions referenced by abilities, traits, effects, statuses, etc, they go here, as callable classes
# prepended with owner of function, such as Giant_Spider being owner of a bite called GiantSpiderBite
import dnd5e_misc as misc
import dnd5e_enums as enums
from dnd5e_enums import DAMAGETYPE

# todo: use status effects type class to pass/apply damage?


class GenericAttack:
    # noinspection SpellCheckingInspection
    # todo: remove this parent class if I end up not using it - it had a purpose, lost it
    pass


class GenericMelee(GenericAttack):
    atype = enums.ATTACK.MELEE  # todo: make sure atype is passed around on attacks

    def __init__(self, name, to_hit, reach, targets, damage, dtypes):
        self.name = name
        self.to_hit = to_hit
        self.reach = reach
        self.targets = targets
        self.dtypes = dtypes
        self.die = misc.Die(damage['die_qty'], damage['die_sides'])
        self.dtype = damage['dtype']

    def __repr__(self):
        return self.name + ' ' + str(self.die)

    def __call__(self, owner, target):
        if None in [owner, target]:
            raise ValueError
        advantage, disadvantage = misc.getAdvantage(owner, target)
        attack_roll, critical = misc.attack_roll(advantage, disadvantage, owner.is_lucky())
        attack_roll += self.to_hit
        armor_class = target.get_ac(self.atype)
        damage = self.die.roll()
        for d in self.dtype:
            d(damage)

        return





