import dnd5e_items as items
import dnd5e_enums as enums
import json
import dnd5e_misc as misc
import dnd5e_functions as functions


class Armor(items.Item):
    def __init__(self, name, cost, armor_class, dex_limit, str_req, enum_type, weight, can_stealth, don_doff_t,
                 equip_function, defend_function):
        # TODO: embed static armor criteria in the armor type enum?
        qty = 1
        super().__init__(name=name, cost=cost, weight=weight, qty=qty, enum_type=enum_type,
                         equip_to=enums.EQUIP_SLOT.ARMOR, function=equip_function)

        self.armor_class = armor_class
        self.dex_limit = dex_limit
        self.str_req = str_req  # todo: implement str_req for armors.
        self.can_stealth = can_stealth
        self.defend_function = defend_function  # used to put this items effect into the event system
        self.don = don_doff_t[0]
        self.doff = don_doff_t[1]

    def to_dict(self):
        d = super().to_dict()

        def wrap(obj):
            if type(obj) != type(""):
                return json.dumps(obj)
            return obj

        d['armor_class'] = self.armor_class
        d['dex_limit'] = self.dex_limit
        d['str_req'] = self.str_req
        d['stealth'] = self.can_stealth
        d['defend_function'] = wrap(misc.get_full_qualname(self.defend_function)) if self.defend_function else None
        d['dondoff'] = wrap([self.don, self.doff])
        return d

    @staticmethod
    def from_dict(d):
        return Armor(name=d['name'],
                     cost=d['cost'],
                     armor_class=d['armor_class'],
                     dex_limit=d['dex_limit'],
                     str_req=d['str_req'],
                     enum_type=misc.get_sets_of_attribs_from_sets_of_qualnames(enums, json.loads(d['type'])),
                     weight=d['weight'],
                     can_stealth=d['stealth'],
                     don_doff_t=json.loads(d['dondoff']),
                     equip_function=getattr(functions, d['function']) if d['function'] else None,
                     defend_function=getattr(functions, d['defend_function']) if d['defend_function'] else None
                     )


class Shield(items.Item):
    def __init__(self, name, cost, armor_class, str_req, enum_type, weight, don_doff_t, equip_function, defend_function):
        qty = 1
        super().__init__(name=name, cost=cost, weight=weight, qty=qty, enum_type=enum_type,
                         equip_to=enums.EQUIP_SLOT.SHIELD, function=equip_function)
        self.armor_class = armor_class
        self.str_req = str_req
        self.don = don_doff_t[0]
        self.doff = don_doff_t[1]
        self.defend_function = defend_function

    def to_dict(self):
        d = super().to_dict()

        def wrap(obj):
            if type(obj) != type(""):
                return json.dumps(obj)
            return obj

        d['armor_class'] = self.armor_class
        d['str_req'] = self.str_req
        d['defend_function'] = wrap(misc.get_full_qualname(self.defend_function)) if self.defend_function else None
        d['dondoff'] = wrap([self.don, self.doff])
        return d

    @staticmethod
    def from_dict(d):
        return Shield(name=d['name'],
                      cost=int(d['cost']),
                      armor_class=int(d['armor_class']),
                      str_req=int(d['str_req']),
                      enum_type=misc.get_sets_of_attribs_from_sets_of_qualnames(enums, json.loads(d['type'])),
                      weight=int(d['weight']),
                      don_doff_t=json.loads(d['dondoff']),
                      equip_function=getattr(functions, d['function']) if d['function'] else None,
                      defend_function=getattr(functions, d['defend_function']) if d['defend_function'] else None
                      )

# example definitions
plate_Armor = Armor(
                    name='Plate Armor',
                    cost=150000,
                    armor_class=18,
                    dex_limit=0,
                    str_req=15,
                    enum_type={enums.ARMOR.HEAVY.PLATE},
                    weight=65,
                    can_stealth=False,
                    don_doff_t=(10, 6),  # time to put on, take off, in minutes.
                    equip_function=None,  # the name of a function which executes a special effect on the target
                    defend_function=None,  # the name of a function which executes a special effect on the target
                    )

breastplate_Armor = Armor(
                    name='Breastplate Armor',
                    cost=40000,
                    armor_class=15,
                    dex_limit=2,
                    str_req=0,
                    enum_type={enums.ARMOR.MEDIUM.BREASTPLATE},
                    weight=20,
                    can_stealth=False,
                    don_doff_t=(5, 3),  # time to put on, take off, in minutes.
                    equip_function=None,  # the name of a function which executes a special effect on the target
                    defend_function=None,  # the name of a function which executes a special effect on the target
                    )

kite_shield = Shield(
                    name='Kite Shield',
                    cost=8000,
                    armor_class=3,
                    str_req=15,
                    enum_type={enums.SHIELDS.KITE},
                    weight=14,
                    don_doff_t=(1, 1),
                    equip_function=None,
                    defend_function=None
                    )


if __name__ == '__main__':
    print(plate_Armor)
    p = plate_Armor.to_dict()
    print(p)
    p2 = Armor.from_dict(p)
    print(p2)
    p2 = p2.to_dict()
    print(p2)

    print(kite_shield)
    k = kite_shield.to_dict()
    print(k)
    k2 = Shield.from_dict(k)
    print(k2)
    k2 = k2.to_dict()
    print(k2)
