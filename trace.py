from inspect import getframeinfo, stack
import os, sys

__LINE__ = lambda offset=0: os.path.basename(getframeinfo(stack()[1+offset][0]).filename) \
                   + '_' + str(getframeinfo(stack()[1+offset][0]).lineno) + ': '


# noinspection PyShadowingBuiltins
def print(*args, offset=None, **kwargs):
    if offset is None:
        offset = 1
    __builtins__['print'](__LINE__(offset=offset), *args, **kwargs)
    sys.stdout.flush()
