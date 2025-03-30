#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\trinity\_singletons.py
import blue
from . import _trinity
platform = _trinity._ImportDll()
adapters = _trinity._blue.classes.CreateInstance('trinity.Tr2VideoAdapters')
device = _trinity._blue.classes.CreateInstance('trinity.TriDevice')
mainWindow = _trinity._blue.classes.CreateInstance('trinity.Tr2MainWindow')
app = mainWindow
platformInfo = _trinity._blue.classes.CreateInstance('trinity.Tr2PlatformInfo')
from . import renderjobs
renderJobs = renderjobs.RenderJobs()
from . import GraphManager
graphs = GraphManager.GraphManager()

def _ReportRemovedDevice(hr, message, count, marker, pageFaultResource, offendingShader):
    import monolithsentry
    if len(offendingShader) > 200:
        offendingShader = '...' + offendingShader[len(offendingShader) - 197:]
    monolithsentry.capture_error('GPU device removed', extra={'count': count,
     'error_message': message,
     'pageFaultResource': pageFaultResource}, new_tags={'reason': '0x%x' % hr,
     'marker': marker,
     'offendingShader': offendingShader})


device.onDeviceRemoved = _ReportRemovedDevice
