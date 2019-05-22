# intended for battle specific code
import dnd5e_character_sheet as character
import dnd5e_creatures as creatures
import random
import dnd5e_misc as misc


class Party:
    def __init__(self, *args):
        self.members = list(args)

    def dict(self):
        return [m.dict_short() for m in self.members]

    def heal(self):  # todo remove this, its here while testing only
        for m in self.members:
            m.hp = m.hp_max

    def size(self):
        return len(self.members)

    def is_able(self):  # todo: consider status effects like incapacitated, petrified, etc.
        return sum((x.hp for x in self.members)) > 0

    def able_bodied(self):
        return [x for x in self.members if x.hp > 0]

    def __str__(self):
        s = ''
        for m in self.members:
            d = m.dict_short()
            s += d['name'] + ': '
            if isinstance(m, character.CharacterSheet):
                s += 'LVL: ' + str(m.level) + ',  '
                s += 'EXP: ' + str(m.experience) + ',  '
            s += 'HP: ' + d['hp']
            s += '\n'
        return s


class Encounter:
    def __init__(self, encounter_map=None, player_party=None, hostile_party=None, difficulty='Normal', reward=None):
        self.map = encounter_map
        self.player_party = Party(*player_party.members.copy())
        self.difficulty = difficulty
        self.hostile_party = hostile_party
        self.reward = reward  # todo: implement gem/item/coin rewards
        if hostile_party is None:  # generate one
            self.generate_hostile(self.difficulty)

    def do_battle(self):
        print('Encounter start!\n')
        print('player_party: ')
        print(str(self.player_party))
        print('enemy_party: ')
        print(str(self.hostile_party))
        # rank by initiative
        initiative_list = sorted(self.player_party.members+self.hostile_party.members,
                                 key=lambda x: x.initiative, reverse=True)
        attack_die = misc.Die(1,20)
        while self.hostile_party.is_able() and self.player_party.is_able():
 #           terminate = False
            for entity in initiative_list:  # take turns in order of initiative
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
                #  dict with keys num, weapons, calculation
                #      num is number of attacks to be made in this attack
                #      calculation is a list of lists, containing a damage function, and weapon function
                #      weapons is a list of the weapons themselves, with their related criteria.
                calculation = attacks['calculation']
                damages = []
                for atk in range(attacks['num']):
                    for weapon in attacks['weapons']:
                        if weapon is not None and self.hostile_party.is_able() and self.player_party.is_able():
                            player = isinstance(entity, character.CharacterSheet)

                            if player:
                                target = random.choice(self.hostile_party.able_bodied())
                            else:
                                target = random.choice(self.player_party.able_bodied())
                            advantage, disadvantage = misc.getAdvantage(entity, target)
                            attack_roll, critical = misc.attack_roll(advantage, disadvantage, entity.is_lucky())
                            attack_roll += weapon.hit_bonus  # todo: get and include any status/trait bonuses
                            if player:
                                attack_roll += entity.abilities.STR_MOD

                            if critical:
                                damage = calculation(weapon).__next__()[0] * 2
                            else:
                                damage = calculation(weapon).__next__()[0]
#                            damages.append([attack_roll, critical, damage])
#                            print(__LINE__(), attack_roll, critical, damages)

                            # todo: currently assuming all attacks are melee attacks - allow selection and grabbing the
                            #  appropriate functions.
#                            damage_die, dtypes, effects = entity.melee_attack(target)
                            damage_done, counter_effects = target.receive_damage(damage)
                            print(entity.name + ' attacks ' + target.name + ' with ' + str(weapon) +
                                  ' and does ' + str(damage_done) + ' damage')
                            if target.hp < 1:
                                print(target.name + ' has been incapacitated')
                                if player:
                                    self.hostile_party.members.remove(target)
                                else:
                                    self.player_party.members.remove(target)
                                initiative_list.remove(target)

        print('\n\n' + str(self.player_party), end='')
        print('You have ' + ('won!' if self.player_party.is_able() else 'lost!'))
        input()
        return self.reward if self.player_party.is_able() else {'xp': 0, 'gold': 0}

    def generate_hostile(self, difficulty):
        # todo: make this obey region themes - no dryads among the undead....
        # get party  thresholds
        threshold = {}
        for m in self.player_party.members:
            member_threshold = XP_thresholds[m.level]
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

        party_mod = {1: 2,  2: 1,   3: 0,   4: -1, 5: -1,  6: -2}.get(self.player_party.size(), -2) + 2
        # the +2 offset is so that when combined with mobs_mod, we consider 0 as pos2, which allows the -2 to have value
        #  in the array as well

        nmobs_mod = [1, 2, 3, 5, 8, 11, 15, 20, 30]
        multi = [0.25, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9]

        # we are adding a creature, so add one now to always use the next value.

        while creature_list and XP:
            mobs_mod = sum([1 for x in nmobs_mod if x <= len(hostiles)]) + 1
            modifier = multi[mobs_mod + party_mod]
            if difficulty != 'Deadly' and creature_list[0].challenge[0] > player_average_level:
                creature_list.pop(0)
            elif difficulty not in ['Deadly', 'Hard'] and creature_list[0].challenge[0] >= player_average_level:
                creature_list.pop(0)
            elif difficulty not in ['Deadly', 'Hard', 'Normal'] and creature_list[0].challenge[0] >= int(player_average_level*.9):
                creature_list.pop(0)
            else:
                if XP >= creature_list[0].challenge[1] * modifier:
                    XP -= creature_list[0].challenge[1] * modifier
                    hostile_xp += creature_list[0].challenge[1] * modifier
                    hostiles.append(creature_list[0]())
                else:
                    creature_list.pop(0)
#        reward_xp = int(hostile_xp ** 0.5)
        reward_xp = int(hostile_xp)
        # todo, restore sqrt exp reward once done testing faster growth rates
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

if __name__ == '__main__':
    from trace import print
    player = character.init_wulfgar()
    player.name = 'Wulfgar 1'
    player2 = character.init_wulfgar()
    player2.name = 'Wulfgar 2'
    print(player.dict_short())
    print(player2.dict_short())
    print(player.hp, player2.hp)
    while player.hp + player2.hp > 0:
        encounter = Encounter(player_party=Party(player, player2))
        rewards = encounter.do_battle()
        player.experience += rewards['xp']//2
        player2.experience += rewards['xp']//2
        player.hp = player.hp_max
        player2.hp = player2.hp_max

