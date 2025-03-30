#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\sequence\tooltipInfoIcons.py
import carbonui
from carbonui import uiconst, TextColor
from cosmetics.common.ships.skins.static_data import sequencing_const
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.tooltips import TooltipPanel
from eve.client.script.ui.shared.shipTree.infoBubble import SkillEntry
from localization import GetByLabel
from skills.client.util import get_skill_service

class NumRunsInfoIcon(InfoIcon):

    def ConstructTooltipPanel(self):
        return NumRunsTooltipPanel()


class NumRunsTooltipPanel(TooltipPanel):
    default_columns = 2
    default_state = uiconst.UI_NORMAL

    def __init__(self, **kw):
        super(NumRunsTooltipPanel, self).__init__(**kw)
        self.LoadStandardSpacing()
        self.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/NumRunsTooltipText'), width=300, color=TextColor.SECONDARY), colSpan=2)
        for type_id in sequencing_const.max_runs_skills:
            level = get_skill_service().GetMyLevel(type_id)
            self.AddRow(rowClass=SkillEntry, typeID=type_id, level=level, showLevel=False)


class SequencingTimeSkillsInfoIcon(InfoIcon):

    def ConstructTooltipPanel(self):
        return SequencingTimeSkillsTooltipPanel()


class SequencingTimeSkillsTooltipPanel(TooltipPanel):
    default_columns = 2
    default_state = uiconst.UI_NORMAL

    def __init__(self, **kw):
        super(SequencingTimeSkillsTooltipPanel, self).__init__(**kw)
        self.LoadStandardSpacing()
        self.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/JobDurationTooltipText'), width=300, color=TextColor.SECONDARY), colSpan=2)
        for type_id in sequencing_const.sequencing_time_bonus_skills:
            level = get_skill_service().GetMyLevel(type_id)
            self.AddRow(rowClass=SkillEntry, typeID=type_id, level=level, showLevel=False)


class MaxConcurrentJobsSkillsInfoIcon(InfoIcon):

    def ConstructTooltipPanel(self):
        return MaxConcurrentJobsSkillsTooltipPanel()


class MaxConcurrentJobsSkillsTooltipPanel(TooltipPanel):
    default_columns = 2
    default_state = uiconst.UI_NORMAL

    def __init__(self, **kw):
        super(MaxConcurrentJobsSkillsTooltipPanel, self).__init__(**kw)
        self.LoadStandardSpacing()
        self.AddCell(carbonui.TextBody(text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Studio/MaxConcurrentSequencingJobsTooltipText'), width=300, color=TextColor.SECONDARY), colSpan=2)
        for type_id in sequencing_const.max_concurrent_jobs_skills:
            level = get_skill_service().GetMyLevel(type_id)
            self.AddRow(rowClass=SkillEntry, typeID=type_id, level=level, showLevel=False)
