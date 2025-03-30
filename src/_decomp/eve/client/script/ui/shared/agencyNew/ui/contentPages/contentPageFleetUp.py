#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageFleetUp.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.fleetupUI.fleetupSearchCont import FleetupSearchCont
CONTENT_HEIGHT = 520

class ContentPageFleetUp(Container):
    default_name = 'ContentPageFleetUp'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.contentGroup = attributes.contentGroup
        self.contentGroupID = self.contentGroup.contentGroupID
        self.ConstructLayout()

    def ConstructLayout(self):
        FleetupSearchCont(name='FleetUpCont', parent=self, align=uiconst.TOTOP, height=CONTENT_HEIGHT, padding=(0, 0, 0, 0))
