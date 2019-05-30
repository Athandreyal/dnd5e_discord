# intended for battle specific code
import dnd5e_character_sheet as character
import dnd5e_creatures as creatures
import random
import dnd5e_misc as misc
debug = False


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
    def __init__(self, encounter_map=None, player_party=None, hostile_party=None, difficulty='Normal', reward=None,
                 verbose=False, silent=False, auto_run=False, debug_rewards=False):
        self.map = encounter_map
        self.player_party = Party(*player_party.members.copy())
        self.difficulty = difficulty
        self.hostile_party = hostile_party
        self.reward = reward  # todo: implement gem/item/coin rewards
        self.debug_rewards = debug_rewards
        if hostile_party is None:  # generate one
            self.generate_hostile(self.difficulty)
        self.verbose = verbose
        self.silent = silent
        self.auto_run = auto_run

    def do_battle(self):
        #from dnd5e_enums import EVENT
        if not self.silent:
            print('\n\n******************************************************')
            print(self.difficulty + ' Difficulty Encounter start!\n')
            print('player_party: ')
            print(str(self.player_party))
            print('enemy_party: ')
            print(str(self.hostile_party))
        # rank by initiative
        initiative_list = sorted(self.player_party.members+self.hostile_party.members,
                                 key=lambda x: x.initiative, reverse=True)

        for entity in initiative_list:  # take turns in order of initiative
            entity.effects.before_battle()
        while self.hostile_party.is_able() and self.player_party.is_able():
            for entity in initiative_list:  # take turns in order of initiative
                player = isinstance(entity, character.CharacterSheet)
                event = entity.effects
                if debug:
                    print('beginning %s\'s turn' % entity.name)
                if entity.hp < 0:  # test for incapacitated and roll for recovery
                    event.incapacitated()  # might recover
                    # todo: do 3 step death recovery here.
                if entity.hp > 0:
                    attack = entity.melee_attack()
                    event.before_turn(attack=attack)
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
                    #  dict with keys num, weapons, calculation
                    #      num is number of attacks to be made in this attack
                    #      calculation is a list of lists, containing a damage function, and weapon function
                    #      weapons is a list of the weapons themselves, with their related criteria.
                    calculation = attack.calculation
                    while attack.num:
                        event.before_action()
                        # todo: move ^this^ when a choice is possible - its for all potential actions, not just attacks
                        event.attack(attack=attack)
                        for weapon in attack.weapons:
                            if weapon is not None and self.hostile_party.is_able() and self.player_party.is_able():

                                if player:
                                    target = random.choice(self.hostile_party.able_bodied())
                                else:
                                    target = random.choice(self.player_party.able_bodied())
                                # status effects that require a hit should be applied to target's list, with a state var
                                # to indicate awaiting a hit, and prep to clear on turn end if not triggered.
                                attack.advantage, attack.disadvantage = misc.getAdvantage(entity, target)
                                attack_roll, critical = attack.result()  # todo: have lucky check the rolls here.
                                event.roll_attack(attack=attack)
                                attack_roll += weapon.hit_bonus + attack.bonus_attack  # todo: get and include any
                                # status/trait bonuses
                                if player:
                                    attack_roll += entity.abilities.STR_MOD

                                # pass entity for return effects.  pass
                                multi = 1
                                if critical:
                                    event.critical(attacker=entity, attack=attack)
                                    multi = attack.critical_multi
                                damage = calculation(weapon).__next__()[0]
                                for d in damage:
                                    d += attack.bonus_damage
                                    d *= multi

                                attack.damage = damage
                                defence = misc.Defend()  # passes defence object to catch trait/skill AC calculations.
                                target.effects.defend(attacker=entity, attack=attack, defender=target, defence=defence)
                                defence.armor_classes.append(target.get_armor_class())
                                target_ac = defence.get_armor_class()

                                if target_ac > attack_roll:  # miss
                                    if not self.silent and self.verbose:
                                        print(entity.name + ' attacks ' + target.name + ' with ' + str(weapon) +
                                              ' and misses')
                                else:
                                    # todo: currently assuming all attacks are melee attacks
                                    #  - allow selection and grabbing the appropriate functions.
                                    damage_done, counter_effects = target.receive_damage(attack.damage)
                                    if not self.silent and self.verbose:
                                        print(entity.name + ' attacks ' + target.name + ' with ' + str(weapon) +
                                              ' and does ' + str(damage_done) + (' critical' if critical else '') +
                                              ' damage')
                                    if target.hp < 1:
                                        target.effects.incapacitated()  # todo: use incapacitated instead
                                        if not self.silent and self.verbose:
                                            print(target.name + ' has been incapacitated')
                                        if player:
                                            self.hostile_party.members.remove(target)
                                        else:
                                            self.player_party.members.remove(target)
#                                        initiative_list.remove(target)  # save this for death, not incapacitation
                        attack.num -= 1
                        event.after_action()
                event.after_turn()
            if debug:
                print('ending %s\'s turn' % entity.name)
        for entity in self.player_party.members:
            entity.effects.after_battle()  # todo properly trigger the before battle

        if not self.silent:
            print('\n\n' + str(self.player_party), end='')
            print('You have ' + ('won!' if self.player_party.is_able() else 'lost!'))
        if not self.silent and not self.auto_run:
            input('press enter to continue')
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
        if not self.debug_rewards:
            reward_xp = int(hostile_xp ** 0.66)
        else:
            reward_xp = int(hostile_xp)
        reward_gold = 0
        # todo, restore sqrt exp reward once done testing faster growth rates
        self.hostile_party = Party(*hostiles)
        self.reward = {'xp': reward_xp, 'gold': reward_gold}


# todo: write a proper encounter generator which can poll the list of available creates, pick from there, and maintain
#  a theme if relevant

#     1:  {'Easy':   25, 'Normal':   50, 'Hard':   75, 'Deadly':   100},
#     2:  {'Easy':   50, 'Normal':  100, 'Hard':  150, 'Deadly':   200},
#     3:  {'Easy':   75, 'Normal':  150, 'Hard':  225, 'Deadly':   400},
#     4:  {'Easy':  125, 'Normal':  250, 'Hard':  375, 'Deadly':   500},
#      5:  {'Easy':  250, 'Normal':  500, 'Hard':  750, 'Deadly':  1100},
#      6:  {'Easy':  300, 'Normal':  600, 'Hard':  900, 'Deadly':  1400},
#      7:  {'Easy':  350, 'Normal':  750, 'Hard': 1100, 'Deadly':  1700},
#      8:  {'Easy':  450, 'Normal':  900, 'Hard': 1400, 'Deadly':  2100},
#      9:  {'Easy':  550, 'Normal': 1100, 'Hard': 1600, 'Deadly':  2400},
#      10: {'Easy':  600, 'Normal': 1200, 'Hard': 1900, 'Deadly':  2800},
#      11: {'Easy':  800, 'Normal': 1600, 'Hard': 2400, 'Deadly':  3600},
#      12: {'Easy': 1000, 'Normal': 2000, 'Hard': 3000, 'Deadly':  4500},
#      13: {'Easy': 1100, 'Normal': 2200, 'Hard': 3400, 'Deadly':  5100},
#      14: {'Easy': 1250, 'Normal': 2500, 'Hard': 3800, 'Deadly':  5700},
#      15: {'Easy': 1400, 'Normal': 2800, 'Hard': 4300, 'Deadly':  6400},
#      16: {'Easy': 1600, 'Normal': 3200, 'Hard': 4800, 'Deadly':  7200},
#      17: {'Easy': 2000, 'Normal': 3900, 'Hard': 5900, 'Deadly':  8800},
#      18: {'Easy': 2100, 'Normal': 4200, 'Hard': 6300, 'Deadly':  9500},
#      19: {'Easy': 2400, 'Normal': 4900, 'Hard': 7300, 'Deadly': 10900},
#      20: {'Easy': 2800, 'Normal': 5700, 'Hard': 8500, 'Deadly': 12700},
#     }
XP_thresholds = {
    1:  {'Why':   15, 'CakeWalk':   25, 'Easy':   35, 'Normal':   50, 'Hard':   75, 'Deadly':   115, 'WTF':   175},
    2:  {'Why':   30, 'CakeWalk':   45, 'Easy':   65, 'Normal':  100, 'Hard':  150, 'Deadly':   225, 'WTF':   340},
    3:  {'Why':   45, 'CakeWalk':   65, 'Easy':  100, 'Normal':  150, 'Hard':  225, 'Deadly':   340, 'WTF':   510},
    4:  {'Why':   75, 'CakeWalk':  110, 'Easy':  165, 'Normal':  250, 'Hard':  375, 'Deadly':   565, 'WTF':   850},
    5:  {'Why':  150, 'CakeWalk':  225, 'Easy':  335, 'Normal':  500, 'Hard':  750, 'Deadly':  1125, 'WTF':  1690},
    6:  {'Why':  175, 'CakeWalk':  265, 'Easy':  400, 'Normal':  600, 'Hard':  900, 'Deadly':  1350, 'WTF':  2025},
    7:  {'Why':  225, 'CakeWalk':  335, 'Easy':  500, 'Normal':  750, 'Hard': 1125, 'Deadly':  1690, 'WTF':  2535},
    8:  {'Why':  265, 'CakeWalk':  400, 'Easy':  600, 'Normal':  900, 'Hard': 1350, 'Deadly':  2025, 'WTF':  3040},
    9:  {'Why':  325, 'CakeWalk':  490, 'Easy':  735, 'Normal': 1100, 'Hard': 1650, 'Deadly':  2475, 'WTF':  3715},
    10: {'Why':  355, 'CakeWalk':  535, 'Easy':  800, 'Normal': 1200, 'Hard': 1800, 'Deadly':  2700, 'WTF':  4050},
    11: {'Why':  475, 'CakeWalk':  710, 'Easy': 1065, 'Normal': 1600, 'Hard': 2400, 'Deadly':  3600, 'WTF':  5400},
    12: {'Why':  595, 'CakeWalk':  890, 'Easy': 1335, 'Normal': 2000, 'Hard': 3000, 'Deadly':  4500, 'WTF':  6750},
    13: {'Why':  650, 'CakeWalk':  975, 'Easy': 1465, 'Normal': 2200, 'Hard': 3300, 'Deadly':  4950, 'WTF':  7425},
    14: {'Why':  740, 'CakeWalk': 1110, 'Easy': 1665, 'Normal': 2500, 'Hard': 3750, 'Deadly':  5625, 'WTF':  8440},
    15: {'Why':  830, 'CakeWalk': 1245, 'Easy': 1865, 'Normal': 2800, 'Hard': 4200, 'Deadly':  6300, 'WTF':  9450},
    16: {'Why':  950, 'CakeWalk': 1425, 'Easy': 2135, 'Normal': 3200, 'Hard': 4800, 'Deadly':  7200, 'WTF': 10800},
    17: {'Why': 1155, 'CakeWalk': 1735, 'Easy': 2600, 'Normal': 3900, 'Hard': 5850, 'Deadly':  8775, 'WTF': 13165},
    18: {'Why': 1245, 'CakeWalk': 1865, 'Easy': 2800, 'Normal': 4200, 'Hard': 6300, 'Deadly':  9450, 'WTF': 14175},
    19: {'Why': 1450, 'CakeWalk': 2175, 'Easy': 3265, 'Normal': 4900, 'Hard': 7350, 'Deadly': 11025, 'WTF': 16540},
    20: {'Why': 1690, 'CakeWalk': 2535, 'Easy': 3800, 'Normal': 5700, 'Hard': 8550, 'Deadly': 12825, 'WTF': 19240}
    }

# Easy
# Normal
# Hard
# Deadly


def difficulty_change(diff, offset):
    diffs = ['Why', 'CakeWalk', 'Easy', 'Normal', 'Hard', 'Deadly', 'WTF']
    return diffs[max(0, min(len(diffs)-1, diffs.index(diff)+offset))]


if __name__ == '__main__':
    from trace import print, line


    player = character.init_wulfgar()
    player.name = 'Wulfgar 1'

    player2 = character.init_wulfgar()
    player2.name = 'Wulfgar 2'
    players = player, player2
    ttl_wins = 0
    ttl_losses = 0
    win_rate = []
    difficulty = 'Normal'
    print('Note: battle output currently silenced for testing purposes - accelerates the climb though lvl 20 when '
          'I/O is not involved.  To see what is occurring, edit the Encounter call on line', str(line()+2))
    while sum(p.hp for p in players) > 0 and player.level < 20:
        encounter = Encounter(player_party=Party(player, player2), difficulty=difficulty, verbose=True, silent=False,
                              auto_run=True, debug_rewards=True)
        rewards = encounter.do_battle()
        result = 1 if rewards['xp'] > 0 else -1
        if result > 0:
            ttl_wins += 1
        else:
            ttl_losses += 1
        win_rate.append(result)
        if len(win_rate) > 5:
            win_rate.pop(0)
        wins = sum(1 for x in win_rate if x is 1)
        losses = sum(-1 for x in win_rate if x is -1)
        if wins > 3:
            win_rate = []
            difficulty = difficulty_change(difficulty, 1)
        if losses < -3:
            win_rate = []
            difficulty = difficulty_change(difficulty, -1)
        reward = rewards['xp']//len(players)
        for p in players:
            p.experience += reward
            p.hp = p.hp_max

    for p in players:
        print(p.dict_short())
    print('level 20 achieved in', ttl_losses + ttl_wins, 'encounters')
