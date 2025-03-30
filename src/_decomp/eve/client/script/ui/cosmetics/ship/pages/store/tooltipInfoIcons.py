#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\tooltipInfoIcons.py
import carbonui
from carbonui import uiconst, TextColor
from cosmetics.common.ships.skins.static_data import trading_const
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from localization import GetByLabel
from skills.client.util import get_skill_service

class HubTaxRateSkillsInfoIcon(InfoIcon):

    def ConstructTooltipPanel(self):
        return HubTaxRateSkillsTooltipPanel()


class HubTaxRateSkillsTooltipPanel(TooltipPanel):
    default_columns = 2
    default_state = uiconst.UI_NORMAL

    def __init__(self, **kw):
        super(HubTaxRateSkillsTooltipPanel, self).__init__(**kw)
        self.LoadStandardSpacing()
        self.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/HubTaxRateSkillsTooltipText'), width=300, color=TextColor.SECONDARY), colSpan=2)
        for type_id in trading_const.tax_rate_reduction_skills:
            level = get_skill_service().GetMyLevel(type_id)
            self.AddRow(rowClass=SkillEntry, typeID=type_id, level=level, showLevel=False)
