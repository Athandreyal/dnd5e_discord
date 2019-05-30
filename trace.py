from inspect import getframeinfo, stack
import os, sys

__LINE__ = lambda offset=0: os.path.basename(getframeinfo(stack()[1+offset][0]).filename) \
                   + '_' + str(getframeinfo(stack()[1+offset][0]).lineno) + ': '


def line(offset=None):
    if offset is None:
        offset = 0
    return getframeinfo(stack()[1 + offset][0]).lineno


def called_with():
    text = stack()[2][4][0]  # stack()[1] is the caller, but as this is called to get a previous caller, use ()[2]
    if '#' in text:  #strip off the comment
        index = text.find('#')
        text = text[:index]
    return text.strip()  # toss leading/trailing spaces


# noinspection PyShadowingBuiltins
def print(*args, offset=None, **kwargs):
    if offset is None:
        offset = 1
    __builtins__['print'](__LINE__(offset=offset), *args, **kwargs)
    sys.stdout.flush()
