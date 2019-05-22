import re
import json


class Event:
    # todo: complete the event system for player characters
    # re-organise?
    #   register within appropriate event window for when to apply effect
    #      event windows are:
    #        combat events: before_battle, before_turn, after_turn, action, attack, defend, after_battle
    #        standard events: before_battle, before_turn, after_turn, action, after_battle, init, levelup
    #   before/after battle: init/end triggers for combat,
    #                        used to convert ongoing timed events to iterative battle triggers, or battle to timed
    #   before/after turn: in battle, these occur every 6 seconds.  Out of battle, these occur every time the bot
    #                      decides you need to be contacted for clarification of an important decision.  If
    #                      someone dies, the bot will contact you about retreating, or pressing on, for example.
    #   action: events which trigger when you do things.  Flight for example - if an item grants you the power
    #           to fly, then the flight effect would exist in the action trigger - you have to try to fly for it
    #           to do anything
    #   attack/defend:  these occur as part of battle.  attack events occur when you launch an attack,
    #                   defend triggers when you are attacked

    class Effect(set):  # minimalist event handler abusing the set class
        #     >>> e = Event({foo, bar})
        #     >>> e('a', 'b')
        #     foo(a b)
        #     bar(a b)
        #     >>> e
        #     Event(foo, bar)
        #     >>> e.add(baz)
        #     >>> e
        #     Event(foo, baz, bar)
        #     >>> e('a', 'b')
        #     foo(a b)
        #     baz(a b)
        #     bar(a b)
        #     >>> e.remove(foo)
        #     >>> e('a', 'b')
        #     baz(a b)
        #     bar(a b)

        def __call__(self, *args, **kwargs):
            respond = None
            for f in self:
                respond = f(*args, **kwargs)
            if 'target' in kwargs:
                return respond  # todo catch and return the results of each event for return to caller

        def __repr__(self):
            return 'Event(%s)' % re.sub('["[\]]', '', json.dumps([x.__name__ for x in self]))

    before_battle = Effect(set())  # applies on battle start
    before_turn = Effect(set())  # applies on start of each turn
    after_turn = Effect(set())  # applies after each turn
    action = Effect(set())  # applies whenever a character acts
    attack = Effect(set())  # applies whenever a character attacks
    defend = Effect(set())  # applies whenever a character defends
    after_battle = Effect(set())  # applies whenever a battle ends
    init = Effect(set())  # applies on character creation - including loading
    level_up = Effect(set())  # applies on levelup
    # class When:
    #     def __init__(self):
    #         self.status = []
    #         self.temporary = []
    #         self.permanent = []
    #
    # def __init__(self):
    #     self.always = self.When()
    #     self.before_turn = self.When()
    #     self.on_action = self.When()
    #     self.after_turn = self.When()
