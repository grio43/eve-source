#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\util.py
import utillib
from carbonui.control.scrollentries import ScrollEntryNode

def GetFromClass(entryType, data = None):
    if data is None:
        data = {}
    if isinstance(data, utillib.KeyVal):
        data = data.__dict__
    entry_data = {'__guid__': getattr(entryType, '__guid__', None),
     'decoClass': entryType}
    entry_data.update(data)
    return ScrollEntryNode(**entry_data)
