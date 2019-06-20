import dnd5e_items as items
import dnd5e_enums as enums


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
        d['armor_class'] = self.armor_class
        d['dex_limit'] = self.dex_limit
        d['str_req'] = self.str_req
        d['stealth'] = self.can_stealth
        d['defend_function'] = self.defend_function
        d['don'] = self.don
        d['doff'] = self.doff
        return d


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
        d['armor_class'] = self.armor_class
        d['str_req'] = self.str_req
        d['don'] = self.don
        d['doff'] = self.doff
        d['defend_function'] = self.defend_function
        return d


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
