#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\projectdiscovery\client\ui\projectcontainer.py
from carbonui.primitives.container import Container

class BaseProjectContainer(Container):
    __notifyevents__ = ['OnProjectDiscoveryRescaled']

    def ApplyAttributes(self, attributes):
        super(BaseProjectContainer, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.window = attributes.get('window')
        self.scale = attributes.get('scale', 1.0)

    def OnProjectDiscoveryRescaled(self, scale):
        self.scale = scale

    def _get_service(self):
        return sm.RemoteSvc('ProjectDiscovery')
