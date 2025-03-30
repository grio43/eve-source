#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageESS.py
from carbonui import uiconst
from carbonui.primitives.gridcontainer import GridContainer
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPageInfoConts.essSystemInfoContainer import ESSSystemInfoContainer
from eve.client.script.ui.shared.agencyNew.ui.contentPages.singleColumnContentPage import SingleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.ess.essGameplayTooltip import EssGameplayTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.ess.essMainBankTooltip import EssMainBankTooltip
from eve.client.script.ui.shared.agencyNew.ui.tooltips.ess.essReserveBankTooltip import EssReserveBankTooltip
from eve.client.script.ui.control.simpleTextTooltip import SimpleTextTooltip
from localization import GetByLabel
LABEL_MAX_WIDTH = 128

class ContentPageESS(SingleColumnContentPage):
    default_name = 'ContentPageESS'

    def ConstructInfoContainer(self):
        self.infoContainer = ESSSystemInfoContainer(parent=self)

    def ConstructTooltips(self):
        infoContainer = GridContainer(name='infoGridContainer', parent=self.informationContainer, align=uiconst.TOTOP, lines=2, columns=2, height=70)
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/ESS/ESSGameplay'), tooltipPanelClassInfo=EssGameplayTooltip(), height=10, maxWidth=LABEL_MAX_WIDTH)
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/ESS/ESSMainBank'), tooltipPanelClassInfo=EssMainBankTooltip(), height=10, maxWidth=LABEL_MAX_WIDTH)
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/ESS/ESSReserveBank'), tooltipPanelClassInfo=EssReserveBankTooltip(), height=10, maxWidth=LABEL_MAX_WIDTH)
        DescriptionIconLabel(parent=infoContainer, align=uiconst.TOALL, text=GetByLabel('UI/Agency/ESS/DynamicBounties'), tooltipPanelClassInfo=SimpleTextTooltip(text=GetByLabel('UI/Agency/Tooltips/Exploration/ESS/DynamicBounties')), height=10, maxWidth=LABEL_MAX_WIDTH)
