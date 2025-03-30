#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageFleetUpRegister.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.ui.agencyUIConst import CONTENT_PAGE_HEIGHT
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.fleetupUI.fleetRegister import FleetRegister

class ContentPageFleetUpRegister(Container):
    default_name = 'ContentPageFleetUpRegister'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.contentGroup = attributes.contentGroup
        self.contentGroupID = self.contentGroup.contentGroupID
        self.ConstructLayout()

    def ConstructLayout(self):
        FleetRegister(name='FleetRegister', parent=self, align=uiconst.TOTOP, height=CONTENT_PAGE_HEIGHT, padding=(0, 22, 0, 0))
