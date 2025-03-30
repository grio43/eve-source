#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageResourceHarvesting.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.resourceHarvestingInfoCont import ResourceHarvestingInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eveservices.xmppchat import GetChatService
from localization import GetByLabel

class ContentPageResourceHarvesting(SingleColumnContentPage):

    def ConstructInfoContainer(self):
        self.infoContainer = ResourceHarvestingInfoContainer(parent=self)

    def ConstructJoinChatButton(self):
        Button(parent=Container(parent=self.informationContainer, align=uiconst.TOTOP, height=27), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/chatchannel.png', func=lambda x: GetChatService().JoinChannel(self.chatChannelID), label=GetByLabel('UI/Agency/JoinChat'), hint=GetByLabel('UI/Agency/JoinChatChannel', contentTypeName=self.contentGroup.GetName()))
