import dnd5e_weaponry as weaponry
import dnd5e_armor as armor
import dnd5e_enums as enums


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
        for e in equipment:
            if isinstance(e, weaponry.Weapon):
                #could go to hands, jaw(bite), or fingers(claws, talons, etc)
                self.equip_weapon(e)
            elif isinstance(e, armor.Armor):
                self.equip_armor(e)
            elif isinstance(e, armor.Shield):
                self.equip_shield(e)

    def equip_weapon(self, weapon: weaponry.Weapon):
        if weapon.wield_from is enums.EQUIP_SLOT.JAW:
            self.jaw = weapon
            self.jaw.attack_die = self.jaw.die1
        elif weapon.wield_from is enums.EQUIP_SLOT.FINGERS:
            self.fingers = weapon
            self.fingers.attack_die = self.fingers.die1
        elif weapon.wield_from is enums.EQUIP_SLOT.HAND:
            self.right_hand = weapon
            # un-equip shield if equipping a two-hander
            if weapon.flags is not None:
                if enums.WEAPONFLAGS.TWO_HANDED in weapon.flags:
                    self.left_hand = None
                if enums.WEAPONFLAGS.VERSATILE in weapon.flags and self.shield is None:
                    self.right_hand.attack_die = self.right_hand.die2
                else:
                    self.right_hand.attack_die = self.right_hand.die1

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
