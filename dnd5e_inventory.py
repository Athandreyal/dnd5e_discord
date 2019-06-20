import dnd5e_weaponry as weaponry
import dnd5e_armor as armor
import dnd5e_enums as enums
import dnd5e_misc as misc
import json

class Equipped:
    # todo: equip events - curses, attunement bonuses, etc
    # todo: unequip and unequip events
    def __init__(self):
        self.left_hand = None
        self.right_hand = None
        self.armor = None
        self.shield = None
        self.back = None
        self.jaw = None
        self.collar = None
        self.neck = None
        self.gloves = None
        self.fingers = None
        self.belt = None
        self.shoulders = None
        self.inventory = None

    def equip(self, equipment):
        if not isinstance(equipment, list):
            equipment = [equipment]
        # todo rings, amulets, etc.
        for e in equipment:
            if isinstance(e, weaponry.Weapon):
                #could go to hands, jaw(bite), or fingers(claws, talons, etc)
                self.equip_weapon(e)
            elif isinstance(e, armor.Armor):
                self.equip_armor(e)
            elif isinstance(e, armor.Shield):
                self.equip_shield(e)

    def equip_weapon(self, weapon: weaponry.Weapon):
        # todo: support dual wielding
        if weapon.equip_to is enums.EQUIP_SLOT.JAW:
            self.jaw = weapon
            self.jaw.attack_die = self.jaw.die1
        elif weapon.equip_to is enums.EQUIP_SLOT.FINGERS:
            self.fingers = weapon
            self.fingers.attack_die = self.fingers.die1
        elif weapon.equip_to is enums.EQUIP_SLOT.HAND:
            self.right_hand = weapon
            # un-equip shield if equipping a two-hander
            if weapon.flags is not None:
                if enums.WEAPONFLAGS.TWO_HANDED in weapon.flags:
                    self.left_hand = None
                if enums.WEAPONFLAGS.VERSATILE in weapon.flags and self.shield is None:
                    self.right_hand.attack_die = self.right_hand.die2
                else:
                    self.right_hand.attack_die = self.right_hand.die1
            else:
                if self.right_hand.die1 is not None:
                    self.right_hand.attack_die = self.right_hand.die1
                elif self.right_hand.die2 is not None:
                    self.right_hand.attack_die = self.right_hand.die2

            if self.right_hand.attack_die is None:
                from trace import __LINE__
                print(__LINE__(), weapon.name, weapon.damage, weapon.flags)

    def equip_armor(self, _armor: armor.Armor):
        self.armor = _armor

    def equip_shield(self, shield: armor.Shield):
        self.shield = shield
        # un-equip two-hander if equipping a shield
        if self.right_hand is not None and enums.WEAPONFLAGS.TWO_HANDED in self.right_hand.flags:
            self.right_hand = None

        if enums.WEAPONFLAGS.VERSATILE in self.right_hand.flags:
            self.right_hand.attackDie = self.right_hand.die1
        else:
            self.right_hand.attackDie = self.right_hand.die2

    def get_equipped(self):
        return [x for x in [self.left_hand, self.right_hand, self.armor, self.shield, self.back, self.jaw, self.neck,
                            self.collar, self.gloves, self.fingers, self.belt, self.shoulders]
                if x is not None]

    def unequip(self, slot=None, gear=None):
        # if both slot and equip are lists
        if isinstance(slot, list):
            for s in slot:
                self.unequip(slot=s)
        if isinstance(gear, list):
            for g in gear:
                self.unequip(gear=g)
        if slot:
            self.unequip_slot(slot)
        if gear:
            self.unequip_slot(gear.equip_to)

    def unequip_slot(self, slot: enums.EQUIP_SLOT, item=None):
        def check_if_one_hand_weapon_now_two_handed():
            if self.left_hand is None and self.right_hand is None \
               or self.left_hand is not None and self.right_hand is not None:
                return  # must have a weapon in only one hand, if both are empty, or both have weapons, leave
            if self.right_hand is None:
                self.right_hand = self.left_hand
                self.left_hand = None

            if enums.WEAPONFLAGS.VERSATILE in self.right_hand.flags and self.shield is None:
                self.right_hand.attack_die = self.right_hand.die2

        # todo rings, amulets, etc.
        if isinstance(slot, enums.EQUIP_SLOT.JAW):
            self.jaw = None
        elif isinstance(slot, enums.EQUIP_SLOT.COLLAR):
            self.collar = None
        elif isinstance(slot, enums.EQUIP_SLOT.NECK):
            # multiple
            if item is None: return
            self.neck.remove(item)
        elif isinstance(slot, enums.EQUIP_SLOT.GLOVES):
            self.gloves = None
        elif isinstance(slot, enums.EQUIP_SLOT.FINGERS):
            if item is None: return
            self.fingers = None
        elif isinstance(slot, enums.EQUIP_SLOT.BELT):
            self.belt = None
        elif isinstance(slot, enums.EQUIP_SLOT.BACK):
            self.back = None
        elif isinstance(slot, enums.EQUIP_SLOT.SHOULDER):
            if item is None: return
            self.shoulders = None
        elif isinstance(slot, enums.EQUIP_SLOT.SHIELD):
            self.shield = None
            check_if_one_hand_weapon_now_two_handed()
        elif isinstance(slot, enums.EQUIP_SLOT.ARMOR):
            self.armor = None
        elif isinstance(slot, enums.EQUIP_SLOT.HAND):
            if self.left_hand is item:
                self.left_hand = None
            elif self.right_hand is item:
                self.right_hand = None
            check_if_one_hand_weapon_now_two_handed()

    def to_dict(self):
        return json.dumps({
                'left_hand': self.left_hand.to_dict() if self.left_hand else None,
                'right_hand': self.right_hand.to_dict() if self.right_hand else None,
                'armor': self.armor.to_dict() if self.armor else None,
                'shield': self.shield.to_dict() if self.shield else None,
                'back': self.back.to_dict() if self.back else None,
                'jaw': self.jaw.to_dict() if self.jaw else None,
                'collar': self.collar.to_dict() if self.collar else None,
                'neck': self.neck.to_dict() if self.neck else None,
                'gloves': self.gloves.to_dict() if self.gloves else None,
                'fingers': self.fingers.to_dict() if self.fingers else None,
                'belt': self.belt.to_dict() if self.belt else None,
                'shoulders': self.shoulders.to_dict() if self.shoulders else None,
                'inventory': self.inventory.to_dict() if self.inventory else None
                })

    @staticmethod
    def from_dict(d):
        if not type(d) == type(dict()):
            d = json.loads(d)
        e = Equipped()
        slots = ['left_hand', 'right_hand', 'armor', 'shield', 'back', 'jaw', 'collar', 'neck', 'gloves', 'fingers',
                 'belt', 'shoulders', 'inventory']
        for slot in slots:
            if slot in d and d[slot]:
                klass = misc.get_attrib_from_qualname(__import__(d[slot]['constructor'].split('.', 1)[0]),
                                                          d[slot]['constructor'])
                setattr(e, slot, klass.from_dict(d[slot]))
        return e


if __name__ == '__main__':
    e = Equipped()
    e.equip(weaponry.greataxe)
    e.equip(armor.breastplate_Armor)
    ed = e.to_dict()
    print(ed)
    e2 = Equipped.from_dict(ed)
    ed2 = e2.to_dict()
    print(ed2)
