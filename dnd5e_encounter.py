# intended for battle specific code
import dnd5e_character_sheet as character
import dnd5e_creatures as creatures
import random
import dnd5e_misc as misc
import dnd5e_interactions as interactions
import asyncio


debug = lambda *args, **kwargs: False  # dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


class Party:
    def __init__(self, *args):
        self.members = list(args)
        for member in self.members:
            member.Party = self

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
    # choices = {'Search': Action.CombatSearch, 'Ready': Action.CombatReady, 'Use': Action.CombatUse,
    #            'Assist': Action.CombatAssist, 'Dodge': Action.CombatDodge, 'Dash': Action.CombatDash,
    #            'Disengage': Action.CombatDisengage, 'Hide': Action.CombatHide, 'Attack': Action.CombatAttack}

    def __init__(self, encounter_map=None, party1=None, party2=None, difficulty='Normal', reward=None,
                 verbose=False, silent=False, auto_run=False, debug_rewards=False):
        self.map = encounter_map
        self.party1 = Party(*party1.members.copy())
        self.difficulty = difficulty
        self.reward = reward  # todo: implement gem/item/coin rewards
        self.debug_rewards = debug_rewards
        if party2 is None:  # generate one
            self.party2, self.reward = self.generate_party2(self.party1, debug_rewards, reward, difficulty)
        else:
            self.party2 = party2

        self.verbose = verbose
        self.silent = silent
        self.auto_run = auto_run

    async def do_battle(self, **kwargs):
        # score the choices, and use the penalty/bonus ratio to determine if the automation should spend actions on it?
        channel = None
        author = None
        ctx = kwargs.get('ctx', None)
        self.m1 = None
        self.m2 = None
        self.m3 = None
        self.m4 = None
        self.init_print = True
        bot = None
        if ctx:
            # create the party message windows
            await ctx.send('discord encounter battle initiated')
            channel = ctx.channel
            bot = kwargs['bot']

        def pred(m):
            debug(m, m.author.id, author, m.channel, channel, m.author.id == author and m.channel == channel)
            return m.author.id == author and m.channel == channel

        async def print_parties():
            debug('print parties', self.party1, self.party2)
            if not self.silent:
                p1 = f'party1: \n{str(self.party1)}\n'
                p2 = f'party2: \n{str(self.party2)}\n'
                debug(p1, p2)
                if ctx:
                    debug('if ctx=True')
                    # if anyone is not auto
                    if any(not c.auto for c in self.party1.members+self.party2.members):
                        debug('if any not auto = True')
                        if self.init_print:
                            debug('init_print')
                            self.m1 = await ctx.send(p1)
                            # last action message
                            self.m2 = await ctx.send('Last Action:')
                            # party1 party message
                            self.m3 = await ctx.send(p2)
                            # bot response/options message
                            self.m4 = await ctx.send('Choices')
                            self.init_print = False
                        else:
                            debug('not init_print,', self.m1, self.m3)
                            await self.m1.edit(content=p1)
                            # party1 party message
                            await self.m3.edit(content=p2)
                            debug('not init_print end,', self.m1, self.m3)
                else:
                    print(p1+p2)

        if not self.silent:
            s = '\n\n******************************************************\n'
            s += self.difficulty + ' Difficulty Encounter start!'
            if ctx:
                await ctx.send(s)
            else:
                print(s)
        await print_parties()
        # rank by initiative
        initiative_list = self.before_battle()
        while self.party1.is_able() and self.party2.is_able():
            if ctx:
                await self.m2.edit(content='Last Action:')
            for entity in initiative_list:  # take turns in order of initiative
                event = entity.effects
                debug(entity.name, 'has', entity.hp, 'hp')
                if debug:
                    debug('beginning %s\'s turn' % entity.name)
                if entity.hp <= 0:  # test for incapacitated and roll for recovery
                    event.incapacitated()  # might recover
                    # todo: do 3 step death recovery here.
                    if entity.hp > 0:
                        if entity.party is 1:
                            self.party1.members.append(entity)
                        else:
                            self.party2.members.append(entity)
                if entity.hp > 0:
                    try:
                        author = int(entity.uid[2:-1])
                    except TypeError:
                        pass
                    except AttributeError:
                        author = -1
                    actions = {}
                    event.is_action(actions=actions)   # get the trait/spell/item enabled actions
                    # strip any unavailable or not implemented actions
                    for action in actions:
                        debug(action, actions[action][1] is not None)
                    remove = [action for action in actions if actions[action][1] is None]
                    for action in remove:
                        del actions[action]
                    debug(actions)
                    #get attack data and throw the before_turn event
                    attack = entity.melee_attack()
                    # ====================================
                    # turn begins here
                    event.before_turn(attack=attack)
                    debug('attack num:', attack.num)
                    while actions and any(x[0] for x in actions):
                        # ------------------------------------
                        # action begins here
                        event.before_action()
                        mn = self.m1 if entity.party == 1 else self.m3
                        CombatAction = interactions.ChooseCombatAction
                        action = await CombatAction(choices=actions, entity=entity, attack=attack,
                                                    party1=self.party1, party2=self.party2,
                                                    encounter=self, ctx=ctx, party_message=mn,
                                                    action_message=self.m2, dialogue_message=self.m4,
                                                    pred=pred, bot=bot)
                        if action == interactions.ActionEndTurn:
                            actions = dict()
                        debug(action)
                        event.after_action()
                        # action ends here
                        # ------------------------------------
                        if not (self.party1.is_able() and self.party2.is_able()):
                            break
                    # turn ends here
                    # ====================================
                # todo: present choice of action to script/both parties players
                # todo: a more intelligent target selection process than random choice
                event.after_turn()
                if debug():
                    debug('ending %s\'s turn' % entity.name)
                    debug('\n\n')
                    await print_parties()
#                    input()
                elif ctx:
                    await print_parties()
        self.after_battle()

        if not self.silent:
            if self.party1.is_able():
                for char in self.party1.members:
                    char.experience += self.reward['xp']
                    # todo: add gold from kills
            s = '\n\n' + str(self.party1) + 'You have ' + ('won!' if self.party1.is_able() else 'lost!')
            if ctx:
                await ctx.send(s)
            else:
                print(s)
        if not self.silent and not self.auto_run:
            input('press enter to continue')
        return self.reward if self.party1.is_able() else {'xp': 0, 'gold': 0}

    def before_battle(self):
        for entity in self.party1.members:
            entity.party = 1
            entity.effects.before_battle()
            entity.target = None  # give them a target attribute, so they can remember who they are attacking.
        for entity in self.party2.members:
            entity.party = 2
            entity.effects.before_battle()
            entity.target = None  # give them a target attribute, so they can remember who they are attacking.
        return sorted(self.party1.members+self.party2.members, key=lambda x: x.initiative, reverse=True)

    def after_battle(self):
        for entity in self.party1.members:
            del entity.party
            del entity.target
            entity.effects.after_battle()
        for entity in self.party2.members:
            del entity.party
            del entity.target
            entity.effects.after_battle()

    @staticmethod
    def target_defence(entity, attack):
        defence = misc.Defend()  # creates defence object to get trait/skill AC calculations
        entity.target.effects.defend(attacker=entity, attack=attack,
                                     defender=entity.target, defence=defence)
        defence.armor_classes.append(entity.target.get_armor_class())
        return defence

    @classmethod
    def attack_roll(cls, event, attack, entity, weapon):
        attack.advantage, attack.disadvantage = misc.getAdvantage(entity, entity.target)
        debug('attacker has disadvantage?', attack.disadvantage)
        entity.roll_attack(attack)
        event.roll_attack(attack=attack)
        attack_roll_bonus = weapon.hit_bonus + attack.bonus_attack  # todo: get and include any
        # status/trait bonuses
        if isinstance(entity, character.CharacterSheet):
            attack_roll_bonus += entity.abilities.STR_MOD
        attack.attack_roll_bonus = attack_roll_bonus
        damage = attack.calculation(weapon).__next__()[0]
        for d in damage:
            d += attack.bonus_damage
        attack.damage = damage

        defence = cls.target_defence(entity, attack)
        target_ac = defence.get_armor_class()
        attack_roll, critical = attack.result()  # todo: have lucky check the rolls here.

        # pass entity for return effects.  pass
        if critical:
            event.critical(attacker=entity, attack=attack)
            multi = attack.critical_multi
            for d in attack.damage:
                d *= multi
        attack.num -= 1  # decrement the attack counter
        return attack_roll, critical, target_ac

    @staticmethod
    async def get_target(**kwargs):
        entity = kwargs['entity']
        party1 = kwargs['party1']
        party2 = kwargs['party2']
        # permit players to choose their target
        from dnd5e_interactions import get_target
        if entity.party is 1:
            if entity.auto:
                entity.target = random.choice(party2.able_bodied())
            else:
                entity.target = await get_target(party2.able_bodied(), **kwargs)
        else:
            if entity.auto:
                entity.target = random.choice(party1.able_bodied())
            else:
                entity.target = await get_target(party1.able_bodied(), **kwargs)

    def target_hit(self, entity, weapon, attack, critical):
        damage_done, counter_effects = entity.target.receive_damage(attack.damage)
        s = ''
        if not self.silent and self.verbose:
            s = entity.name + ' attacks ' + entity.target.name + ' with ' + str(weapon) + \
               ' and does ' + str(damage_done) + (' critical' if critical else '') + \
               ' damage'
        if entity.target.hp < 1:
            s2 = self.incapacitate_target(entity.target)
            if s2:
                s += '\n' + s2
            entity.target = None
        return s

    def miss(self, entity, weapon, attack_roll, target_ac):
        if not self.silent and self.verbose:
            if debug():
                return entity.name + ' attacks ' + entity.target.name + ' with ' + \
                       str(weapon) + ' and misses because', target_ac, '>', attack_roll
            else:
                return entity.name + ' attacks ' + entity.target.name + ' with ' + \
                       str(weapon) + ' and misses'
        return ''

    def incapacitate_target(self, target, **kwargs):
        s = None
        if not self.silent and self.verbose:
            s = target.name + ' has been incapacitated'
        if target.party is 1:
            self.party1.members.remove(target)
        else:
            self.party2.members.remove(target)
        return s

    @staticmethod
    def generate_party2(party1, debug_rewards=False, reward=None, difficulty='Normal'):
        # todo: make this obey region themes - no dryads among the undead....
        # get party  thresholds
        threshold = {}
        for m in party1.members:
            member_threshold = XP_thresholds[m.level]
            for k in member_threshold:
                try:
                    threshold[k] += member_threshold[k]
                except KeyError:
                    threshold[k] = member_threshold[k]
        XP = threshold[difficulty]

        creature_list = sorted(creatures.creatures, key=lambda x: x.challenge[1], reverse=True)
        hostile_xp = 0  # need this for calculating resultant xp?
        player_average_level = sum((x.level for x in party1.members)) // len(party1.members)

        hostiles = []

        party_mod = {1: 2,  2: 1,   3: 0,   4: -1, 5: -1,  6: -2}.get(party1.size(), -2) + 2
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
            elif difficulty not in ['Deadly', 'Hard', 'Normal'] and \
                    creature_list[0].challenge[0] >= int(player_average_level*.9):
                creature_list.pop(0)
            else:
                if XP >= creature_list[0].challenge[1] * modifier:
                    XP -= creature_list[0].challenge[1] * modifier
                    hostile_xp += creature_list[0].challenge[1] * modifier
                    hostiles.append(creature_list[0]())
                else:
                    creature_list.pop(0)
        if not debug_rewards:
            reward_xp = int(hostile_xp ** 0.66)
        else:
            reward_xp = int(hostile_xp)
        reward_gold = 0
        # todo, restore sqrt exp reward once done testing faster growth rates
        party2 = Party(*hostiles)
        if not reward:
            reward = {'xp': reward_xp, 'gold': reward_gold}
        return party2, reward


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
    from trace import line

    player = character.init_wulfgar()
    player.name = 'Wulfgar 1'
    player.auto = False

    player2 = character.init_wulfgar()
    player2.name = 'Wulfgar 2'
    player2.auto = True

    players = player, player2

    while player.level < 1:
        player.experience += 100
        player2.experience += 100
    ttl_wins = 0
    ttl_losses = 0
    win_rate = []
    difficulty = 'Normal'
    print('Note: battle output currently silenced for testing purposes - accelerates the climb though lvl 20 when '
          'I/O is not involved.  To see what is occurring, edit the Encounter call on line', str(line()+2))
    while sum(p.hp for p in players) > 0 and player.level < 20:
        encounter = Encounter(party1=Party(player, player2), difficulty=difficulty, verbose=True, silent=False,
                              auto_run=True, debug_rewards=True)

        rewards = asyncio.run(encounter.do_battle())
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

#    from dnd5e_enums import ABILITY
#
#    while debug() is not False:
#        player.roll_dc(ABILITY.STR, player.abilities.STR)
#        input('this is an infinitely looped test case, press enter to continue, or terminate the program yourself')
