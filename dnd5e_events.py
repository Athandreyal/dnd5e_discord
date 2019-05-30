import re
import json
from trace import print, called_with

debug = False


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
            # import inspect
            # stack = inspect.stack()
            # for i in [0,1,2]:
            #     print('stack'+str(i), end='')
            #     for j in range(6):
            #         __builtins__['print']('\n\t', stack[i][j], end='')
            #     __builtins__['print']('')
            # print(stack[1][4])
            if debug:
                caller = called_with()
                print(caller)
            for f in self:
                try:
                    # for key in dir(f):
                    #     print(key)
                    #     print('\t', dir(getattr(f, key)))
                    if debug:
                        print(f.__name__, 'event function triggered for', f.__self__.host.name, 'from',
                              f.__self__.__class__.__name__)
                    f(*args, **kwargs)
                except Exception as e:
                    print(e)
                    print(f.__name__)
                    raise e

        def __repr__(self):
            return '{%s}' % re.sub('["[\]]', '', json.dumps([x.__class__.__name__ for x in self]))
#            return 'Event(%s)' % re.sub('["[\]]', '', json.dumps([(x, dir(x)) for x in self]))

        def get(self, item):
            __name__ = item.__name__ if hasattr(item, '__name__') else item.__class__.__name__
            for obj in self:
                if isinstance(obj, item) and obj.__class__.__name__ == __name__:
                    return obj

    def none(self):
        return self._none

#    all = Effect(set())  # one big list - use temporarily while testing, migrate to separate lists for performance
    def __init__(self):
        self.init = self.Effect(set())  # applies on character creation - including loading
        self.equip = self.Effect(set())
        self.unequip = self.Effect(set())
        self.before_battle = self.Effect(set())  # applies on battle start
        self.after_battle = self.Effect(set())  # applies whenever a battle ends
        self.before_turn = self.Effect(set())  # applies on start of each turn
        self.after_turn = self.Effect(set())  # applies after each turn
        self.before_action = self.Effect(set())  # applies whenever a character acts
        self.after_action = self.Effect(set())  # applies whenever a character acts
        self.attack = self.Effect(set())  # applies whenever a character attacks
        self.defend = self.Effect(set())  # applies whenever a character defends
        self.critical = self.Effect(set())
        self.level_up = self.Effect(set())  # applies on levelup
        self.rest_long = self.Effect(set())
        self.rest_short = self.Effect(set())
        self.roll_attack = self.Effect(set())
        self.roll_damage = self.Effect(set())
        self.roll_dc = self.Effect(set())
        self.roll_hp = self.Effect(set())
        self.incapacitated = self.Effect(set())
        self.death = self.Effect(set())
        self.heal = self.Effect(set())
        self.move = self.Effect(set())
        self.proficiency_check = self.Effect(set())
        self._none = self.Effect(set())  # use this for related but non event locations

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


if __name__ == '__main__':
#    from trace import print

    def foo(*args, **kwargs):
        print('foo(', *args, ')')

    def bar(*args, **kwargs):
        print('bar(', *args, ')')

    def baz(*args, **kwargs):
        print('baz(', *args, ')')

    print("\n>>> def foo(*args, **kwargs):\n\tprint('foo(', *args, ')')")
    print("\n>>> def bar(*args, **kwargs):\n\tprint('bar(', *args, ')')")
    print("\n>>> def baz(*args, **kwargs):\n\tprint('baz(', *args, ')')")

    print('>>> e = Event.init')
    e = Event().init
    print('>>> e()')
    e()
    print('>>> e.update({foo, bar})')
    e.update({foo, bar})
    e()
    print(">>> print(e('a', 'b'))")
    e('a', 'b')
    print('>>> e()')
    e()
    print('>>> e.add(baz)')
    e.add(baz)
    print(">>> e('a', 'b')")
    e('a', 'b')
    print('>>> e.remove(baz)')
    e.remove(baz)
    print(">>> e('a', 'b')")
    e('a', 'b')

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
