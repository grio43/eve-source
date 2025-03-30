#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\sovereignty\workforce\workforceConst.py
from collections import OrderedDict
MODE_IDLE = 'inactive'
MODE_IMPORT = 'import_settings'
MODE_EXPORT = 'export_settings'
MODE_TRANSIT = 'transit'
MODE_UNKNOWN = -1
LABELPATH_BY_MODE = OrderedDict({MODE_IDLE: 'UI/Sovereignty/SovHub/HubWnd/WorkforceIdle',
 MODE_IMPORT: 'UI/Sovereignty/SovHub/HubWnd/WorkforceImport',
 MODE_EXPORT: 'UI/Sovereignty/SovHub/HubWnd/WorkforceExport',
 MODE_TRANSIT: 'UI/Sovereignty/SovHub/HubWnd/WorkforceTransit'})
