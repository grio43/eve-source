#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPages\contentPageAgents.py
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.ui.common.descriptionIcon import DescriptionIconLabel
from eve.client.script.ui.shared.agencyNew.ui.contentPages.doubleColumnContentPage import DoubleColumnContentPage
from eve.client.script.ui.shared.agencyNew.ui.tooltips.standingsTooltip import StandingsTooltip
from localization import GetByLabel

class ContentPageAgents(DoubleColumnContentPage):
    default_name = 'ContentPageAgents'
    default_height = 490

    def ConstructTooltips(self):
        DescriptionIconLabel(parent=self.informationContainer, align=uiconst.TOTOP, text=GetByLabel('UI/Agency/StandingsSystem'), tooltipPanelClassInfo=StandingsTooltip())
