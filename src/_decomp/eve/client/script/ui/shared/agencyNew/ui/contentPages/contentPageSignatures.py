#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageSignatures.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.signatureInfoContainer import SignatureInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.scanningTooltip import ScanningTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.signatureTypesTooltip import SignatureTypesTooltip
from eveservices.xmppchat import GetChatService
from localization import GetByLabel

class ContentPageSignatures(SingleColumnContentPage):
    default_name = 'ContentPageSignatures'

    def ConstructInfoContainer(self):
        self.infoContainer = SignatureInfoContainer(parent=self)

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/ProbeScanning'), tooltipPanelClassInfo=ScanningTooltip(), top=5)
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/SignatureTypes'), tooltipPanelClassInfo=SignatureTypesTooltip(), top=5)

    def ConstructJoinChatButton(self):
        Button(parent=Container(parent=self.informationContainer, align=uiconst.TOTOP, height=27), align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/WindowIcons/chatchannel.png', func=lambda x: GetChatService().JoinChannel(self.chatChannelID), label=GetByLabel('UI/Agency/JoinChat'), hint=GetByLabel('UI/Agency/JoinChatChannel', contentTypeName=self.contentGroup.GetName()))
