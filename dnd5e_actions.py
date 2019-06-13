# using this file to hold code related to taking some action, such as attacking, searching, moving, etc.
import dnd5e_enums as enums
import dnd5e_misc as misc

add_affector = misc.add_affector
remove_affector = misc.remove_affector

debug = lambda *args, **kwargs: False  #dummy out the debug prints when disabled
if debug():
    from trace import print as debug
    debug = debug


# planning to implement a means to utilise the add/remove affectors functions from here, token will be the assigned
# object used to indicate active effects.


def CombatSearch():
    pass
    # todo: implement a reason to want to search during encounters.


def CombatReady():
    pass
    # todo: a reason to want to ready something - this does not apply to spells.


def CombatUse():
    pass
    # todo: a means to use and enjoy the effects of items


# receives both the recipient of the assist command as target, and the assiting entity
def CombatAssist(entity, assisted):
    debug('combat assist action triggered - entry')
    # todo, verify they are only 5ft away for combat advantages
    # put bonus to attack for assisted entity, ends after their next action
    # put bonus to saving throws for assisted entity, ends after next action
    debug(entity, assisted)

    def CombatAssistEnded(*args, **kwargs):
        if token.assist:  # only strip the affector if we've added it previously
            debug('combatAssist executing')
            token.assist = False
            remove_affector(token, assisted, bonus, 'advantage')

    def RemoveCombatAssist(*args, **kwargs):
        debug('removing combatAssist')
        assisted.effects.after_action.discard(CombatAssistEnded)

    bonus = enums.ADVANTAGE.ATTACK.Set().union(enums.SKILL.Set())
    bonus.discard(enums.SKILL)
    bonus.discard(enums.ATTACK)
    token = type('Action', (), {'host': entity, 'assist': True})
    add_affector(token, assisted, bonus, 'advantage')
    assisted.effects.after_action.add(CombatAssistEnded)
    assisted.effects.battle_cleanup.add(RemoveCombatAssist)
    debug('combat assist action triggered - exit')


# receives entity which is defending.
def CombatDodge(entity):
    debug('combat dodge action triggered - entry')
    # put a bonus on defender until before_turn event.
    #   put a malus on any attacker via defend event
    #       strip malus from attacker via after_action event

    def CombatDodgeDefend(*args, **kwargs):
        attack = kwargs['attack']
        attack.advantage = False
        attack.disadvantage = True
        debug('forcing attack.disadvantage')

    def CombatDodgeEnded(*args, **kwargs):
        if token.dodge:
            token.dodge = False
            remove_affector(token, entity, bonus, 'advantage')
            entity.effects.defend.discard(CombatDodgeDefend)

    def RemoveCombatDodge(*args, **kwargs):
        debug('removing combatAssist')
        entity.effects.before_turn.discard(CombatDodgeEnded)

    bonus = {enums.ABILITY.DEX}
    token = type('Action', (), {'host': entity, 'dodge': True})
    add_affector(token, entity, bonus, 'advantage')
    entity.effects.defend.add(CombatDodgeDefend)
    entity.effects.before_turn.add(CombatDodgeEnded)
    entity.effects.battle_cleanup.add(RemoveCombatDodge)
    debug('combat dodge action triggered - exit')


def CombatDash():
    # allows you to move up to your rated movement, spent over whatever difficulty or movement type you've used
    # does not need to be spent all at once, can move, attack, move attack, etc, until moves and attacks run out
    pass


def CombatDisengage():
    # prevents suffering reactionary attacks when attempting to move away from a hostile within 5ft of you
    pass


def CombatHide():
    # is roll_dc succeeds on a roll for stealth,
    pass


def CombatAttack():
    pass
    # bring almost the entire dnd5e_encounters.Encounter.do_battle main loop here
    # check if automated, or interactive.
    #   if interactive, interact with user for:
    #       target selection, melee or ranged attack, weapon for the attack.


if __name__ == '__main__':
    import dnd5e_character_sheet as CS
    import dnd5e_encounter as ENC
    import sys
    char = CS.init_wulfgar()
    char2 = CS.init_wulfgar()

    # combat assist test 1
    debug(char2.advantage)
    debug(char, char2)
    CombatAssist(char, char2)
    debug(char2.advantage)
    char2.effects.after_action()
    debug(char2.advantage)
    debug(char2.effects.after_action)
    char2.effects.battle_cleanup()
    debug(char2.effects.after_action)

    char = CS.init_wulfgar()
    char2 = CS.init_wulfgar()

    # dodge test 1
    debug(char.advantage)
    CombatDodge(char)
    debug(char.advantage)
    debug(char2.disadvantage)
    attack = char2.melee_attack()
    weapon = attack.weapons[0]
    char2.target = char
    ENC.Encounter.attack_roll(char2.effects, attack, char2, weapon)
    debug(char2.disadvantage)
    sys.stdout.flush()
    char.effects.before_turn()
    char2.effects.after_action()
    debug(char.advantage)
    debug(char2.disadvantage)
