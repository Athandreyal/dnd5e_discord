from inspect import getframeinfo, stack
import os, sys

__LINE__ = lambda offset=0: os.path.basename(getframeinfo(stack()[1+offset][0]).filename) \
                   + '_' + str(getframeinfo(stack()[1+offset][0]).lineno) + ': '


# noinspection PyShadowingBuiltins
def print(*args, **kwargs):
    __builtins__['print'](__LINE__(1), *args, **kwargs)
    sys.stdout.flush()
