#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageIncursions.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.agencyNew import agencySignals
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.doubleColumnContentPage import DoubleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.incursions.incursionMechanicsTooltip import IncursionMechanicsTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.incursions.incursionRewardsTooltip import IncursionRewardsTooltip
from eveservices.xmppchat import GetChatService
from localization import GetByLabel

class ContentPageIncursions(DoubleColumnContentPage):
    default_name = 'ContentPageIncursions'

    def OnCardSelected(self, selectedCard):
        agencySignals.on_content_group_selected(contentGroupConst.contentGroupIncursion, itemID=selectedCard.contentPiece.GetConstellationID())

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/IncursionMechanics'), tooltipPanelClassInfo=IncursionMechanicsTooltip(), top=5)
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/Tooltips/Encounters/Incursions/IncursionRewards'), tooltipPanelClassInfo=IncursionRewardsTooltip(), top=5)

    def ConstructLayout(self):
        super(ContentPageIncursions, self).ConstructLayout()
        self.buttonRowCont.Hide()

    def ConstructJoinChatButton(self):
        buttonIconContainer = Container(parent=self.informationContainer, align=uiconst.TOTOP, height=26)
        Sprite(name='groupContentSprite', parent=buttonIconContainer, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/classes/agency/iconGroupActivity.png', width=32, height=32, hint=GetByLabel('UI/Agency/Tooltips/NavigationCards/GroupContentHint'))
        Button(parent=buttonIconContainer, align=uiconst.CENTERLEFT, fixedheight=26, left=40, texturePath='res:/UI/Texture/WindowIcons/chatchannel.png', func=lambda x: GetChatService().JoinChannel(self.chatChannelID), label=GetByLabel('UI/Agency/JoinChat'), hint=GetByLabel('UI/Agency/JoinChatChannel', contentTypeName=self.contentGroup.GetName()))

    def SelectFirstCard(self):
        pass
