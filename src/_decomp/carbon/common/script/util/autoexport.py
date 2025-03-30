#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\autoexport.py
import types

def AutoExports(namespace, globals_):
    return dict([ ('%s.%s' % (namespace, name), val) for name, val in globals_.iteritems() if not name.startswith('_') and not isinstance(val, types.ModuleType) and not hasattr(val, '__guid__') ])
