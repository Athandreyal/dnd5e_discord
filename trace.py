from inspect import getframeinfo, stack
import os

__LINE__ = lambda: os.path.basename(getframeinfo(stack()[1][0]).filename) \
                   + '_' + str(getframeinfo(stack()[1][0]).lineno) + ': '
