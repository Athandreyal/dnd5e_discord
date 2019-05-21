# intended for battle specific code
import dnd5e_character_classes as character
import dnd5e_creatures as creatures
import random
import dnd5e_misc as misc

class Party:
    def __init__(self, *args):
        self.members = args

    def dict(self):
        return [m.dict_short() for m in self.members]

    def heal(self):  # todo remove this, its here while testing only
        for m in self.members:
            m.hp = m.hp_max

    def is_able(self):  # todo: consider status effects like incapacitated, petrified, etc.
        return sum((x.hp for x in self.members)) > 0

    def able_bodied(self):
        return [x for x in self.members if x.hp > 0]


class Encounter:
    def __init__(self, encounter_map=None, player_party=None, hostile_party=None, difficulty='Normal', reward=None):
        self.map = encounter_map
        self.player_party = player_party
        self.difficulty = difficulty
        self.hostile_party = hostile_party
        if hostile_party is None:  # generate one
            self.generate_hostile(self.difficulty)
        self.reward = reward  # todo: implement gem/item/coin rewards

    def do_battle(self):
        # rank by initiative
        initiative_list = sorted(self.player_party+self.hostile_party, key=lambda x: x.initiative, reverse=True)
        while self.hostile_party.is_able() and self.player_party.is_able():
            for entity in initiative_list:  # take turns in order of initiative
                if entity in self.player_party:
                    # todo: present choice of action to script/both parties players
                    # todo: a more intelligent target selection process than random choice
                    # todo: complete this attack process from outside both CharacterSheet and Creature
                    # when entity attacks a target:
                    #     get entity attack criteria
                    #         throw entity attack event(s)
                    #         respond with damage, dtypes, effects function(s) for application to target on success
                    #             target executes on self if success
                    #     get target defence criteria
                    #         throw target defence events(s)
                    #         respond with armor_class, effects function(s) for application to entity
                    #             entity executes on self on attack success/fail
                    #     if attack succeeds
                    #         call target.receive_damage to give damage to target
                    #         call target.receive_effects give effects to the target
                    attacks = entity.melee_attack()

                    for attack in attacks:

                        target = random.choice(self.hostile_party.able_bodied())
                        advantage, disadvantage = misc.getAdvantage(entity, target)
                        attack_roll, critical = misc.attack_roll(advantage, disadvantage, entity.is_lucky())
                        misc.Roll(1, 20) + attack_roll + atk_bonus

                        # todo: currently assuming all attacks are melee attacks - allow selection and grabbing the
                        #  appropriate functions.
                        damage_die, dtypes, effects = entity.melee_attack(target)
                        target.receive_damage(damage, dtype)

    def generate_hostile(self, difficulty):
        # todo: make this obey region themes - no dryads among the undead....
        # get party  thresholds
        threshold = {}
        for m in self.player_party.members:
            member_threshold = XP_thresholds[m.level]
            print(member_threshold)
            for k in member_threshold:
                try:
                    threshold[k] += member_threshold[k]
                except KeyError:
                    threshold[k] = member_threshold[k]
        XP = threshold[difficulty]

        creature_list = sorted(creatures.creatures,key=lambda x: x.challenge[1], reverse=True)
        hostile_xp = 0  # need this for calculating resultant xp?
        player_average_level = sum((x.level for x in self.player_party.members)) // len(self.player_party.members)

        hostiles = []
        reward_xp = 0
        reward_gold = 0
        while creature_list and XP:
            if difficulty != 'Deadly' and creature_list[0].challenge[0] > player_average_level:
                creature_list.pop(0)
            elif difficulty not in ['Deadly', 'Hard'] and creature_list[0].challenge[0] >= player_average_level:
                creature_list.pop(0)
            elif difficulty not in ['Deadly', 'Hard', 'Normal'] and creature_list[0].challenge[0] >= int(player_average_level*.9):
                creature_list.pop(0)
            else:
                if XP >= creature_list[0].challenge[1]:
                    XP -= creature_list[0].challenge[1]
                    hostile_xp += creature_list[0].challenge[1]
                    hostiles.append(creature_list[0]())
                else:
                    creature_list.pop(0)

        self.hostile_party = Party(*hostiles)
        self.reward = {'xp': reward_xp, 'gold': reward_gold}


# todo: write a proper encounter generator which can poll the list of available creates, pick from there, and maintain
#  a theme if relevant

XP_thresholds = {
     1:  {'Easy':   25, 'Normal':   50, 'Hard':   75, 'Deadly':   100},
     2:  {'Easy':   50, 'Normal':  100, 'Hard':  150, 'Deadly':   200},
     3:  {'Easy':   75, 'Normal':  150, 'Hard':  225, 'Deadly':   400},
     4:  {'Easy':  125, 'Normal':  250, 'Hard':  375, 'Deadly':   500},
     5:  {'Easy':  250, 'Normal':  500, 'Hard':  750, 'Deadly':  1100},
     6:  {'Easy':  300, 'Normal':  600, 'Hard':  900, 'Deadly':  1400},
     7:  {'Easy':  350, 'Normal':  750, 'Hard': 1100, 'Deadly':  1700},
     8:  {'Easy':  450, 'Normal':  900, 'Hard': 1400, 'Deadly':  2100},
     9:  {'Easy':  550, 'Normal': 1100, 'Hard': 1600, 'Deadly':  2400},
     10: {'Easy':  600, 'Normal': 1200, 'Hard': 1900, 'Deadly':  2800},
     11: {'Easy':  800, 'Normal': 1600, 'Hard': 2400, 'Deadly':  3600},
     12: {'Easy': 1000, 'Normal': 2000, 'Hard': 3000, 'Deadly':  4500},
     13: {'Easy': 1100, 'Normal': 2200, 'Hard': 3400, 'Deadly':  5100},
     14: {'Easy': 1250, 'Normal': 2500, 'Hard': 3800, 'Deadly':  5700},
     15: {'Easy': 1400, 'Normal': 2800, 'Hard': 4300, 'Deadly':  6400},
     16: {'Easy': 1600, 'Normal': 3200, 'Hard': 4800, 'Deadly':  7200},
     17: {'Easy': 2000, 'Normal': 3900, 'Hard': 5900, 'Deadly':  8800},
     18: {'Easy': 2100, 'Normal': 4200, 'Hard': 6300, 'Deadly':  9500},
     19: {'Easy': 2400, 'Normal': 4900, 'Hard': 7300, 'Deadly': 10900},
     20: {'Easy': 2800, 'Normal': 5700, 'Hard': 8500, 'Deadly': 12700},
    }
# Easy
# Normal
# Hard
# Deadly


player = character.init_wulfgar()
player = Party(player)
encounter = Encounter(player_party=player)
print(encounter.player_party.is_able(), encounter.hostile_party.is_able())
