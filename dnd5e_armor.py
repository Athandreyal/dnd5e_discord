import dnd5e_items as items
import dnd5e_enums as enums


class Armor(items.Item):
    def __init__(self, name, cost, armor_class, dex_limit, str_req, enum_type, weight, can_stealth, flags, don_doff_t,
                 equip_function, defend_function):
        # TODO: embed static armor criteria in the armor type enum?
        qty = 1
        super().__init__(name=name, cost=cost, weight=weight, qty=qty, enum_type=enum_type,
                         equip_to=enums.EQUIP_SLOT.ARMOR, function=equip_function)

        self.armor_class = armor_class
        self.dex_limit = dex_limit
        self.str_req = str_req  # todo: implement str_req for armors.
        self.enum_type = enum_type
        self.can_stealth = can_stealth
        self.flags = flags
        self.equipFunction = equip_function  # used to put this item's effect into the event system
        self.defend_function = defend_function  # used to put this items effect into the event system
        self.don = don_doff_t[0]
        self.doff = don_doff_t[1]


class Shield(items.Item):
    def __init__(self):
        qty = 1
        name = None
        cost = None
        weight = None
        enum_type = None
        equip_function = None
        super().__init__(name=name, cost=cost, weight=weight, qty=qty, enum_type=enum_type,
                         equip_to=enums.EQUIP_SLOT.SHIELD, function=equip_function)
        pass  # todo: implement shields


# example definitions
plate_Armor = Armor(
                    name='Plate Armor',
                    cost=150000,
                    armor_class=18,
                    dex_limit=0,
                    str_req=15,
                    enum_type={enums.ARMOR.HEAVY.PLATE},
                    weight=7,
                    can_stealth=False,
                    flags={enums.PROFICIENCY.ARMOR.METAL, enums.PROFICIENCY.ARMOR.PLATE},
                    don_doff_t=(10, 6),  # time to put on, take off, in minutes.
                    equip_function=None,  # the name of a function which executes a special effect on the target
                    defend_function=None,  # the name of a function which executes a special effect on the target
                    )
