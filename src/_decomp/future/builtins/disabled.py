#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\future\builtins\disabled.py
from __future__ import division, absolute_import, print_function
from future import utils
OBSOLETE_BUILTINS = ['apply',
 'chr',
 'cmp',
 'coerce',
 'execfile',
 'file',
 'input',
 'long',
 'raw_input',
 'reduce',
 'reload',
 'unicode',
 'xrange',
 'StandardError']

def disabled_function(name):

    def disabled(*args, **kwargs):
        raise NameError('obsolete Python 2 builtin {0} is disabled'.format(name))

    return disabled


if not utils.PY3:
    for fname in OBSOLETE_BUILTINS:
        locals()[fname] = disabled_function(fname)

    __all__ = OBSOLETE_BUILTINS
else:
    __all__ = []
