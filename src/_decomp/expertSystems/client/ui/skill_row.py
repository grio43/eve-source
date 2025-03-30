#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\expertSystems\client\ui\skill_row.py
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceManager import ServiceManager
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control import themeColored
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.skillBar.skillBar import SkillBar

class SkillRow(Container):
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_SkillsRemovedFromQueue']
    default_state = uiconst.UI_NORMAL
    default_height = 32
    isDragObject = True

    def __init__(self, skill_type_id, rowSelectFunc = None, required_level = None, **kwargs):
        self.skill_type_id = skill_type_id
        self.required_level = required_level
        self.skill_bar = None
        self.name_label = None
        self.hover_indicator = None
        self.rowSelectFunc = rowSelectFunc
        self.selected = False
        super(SkillRow, self).__init__(**kwargs)
        self.layout()
        ServiceManager.Instance().RegisterNotify(self)

    def layout(self):
        self.skill_bar = SkillBar(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, padLeft=10, skillID=self.skill_type_id, requiredLevel=self.required_level)
        self.name_label = EveLabelMedium(align=uiconst.CENTERLEFT, parent=self, left=80, autoFadeSides=25, text=evetypes.GetName(self.skill_type_id))

    def get_copy_data(self):
        name = evetypes.GetName(self.skill_type_id)
        return u'{} {}'.format(name, self.required_level)

    def update(self):
        self.skill_bar.Update()

    def select(self):
        if not self.selected:
            self.selected = True
            self.hilight()

    def deselect(self):
        if self.selected:
            self.selected = False
            self.unhilight()

    def hilight(self):
        if self.hover_indicator is None:
            self.hover_indicator = themeColored.FillThemeColored(bgParent=self, cornerSize=10, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        animations.FadeIn(self.hover_indicator, duration=0.25, endVal=uiconst.DEFAULT_MODAL_OPACITY)

    def unhilight(self):
        if self.hover_indicator:
            animations.FadeOut(self.hover_indicator, duration=0.25)

    def OnClick(self, *args):
        deselect_others = True
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            deselect_others = False
        if self.rowSelectFunc:
            self.rowSelectFunc(self, deselect_others=deselect_others)

    def OnMouseEnter(self, *args):
        if not self.selected:
            self.hilight()

    def OnMouseExit(self, *args):
        if not self.selected:
            self.unhilight()

    def GetMenu(self):
        return self.skill_bar.GetMenu()

    def GetDragData(self):
        return self.skill_bar.GetDragData()

    def GetTooltipPointer(self):
        return uiconst.POINT_LEFT_2

    def LoadTooltipPanel(self, tooltip_panel, owner):
        from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
        LoadSkillEntryTooltip(tooltip_panel, self.skill_type_id)

    def OnSkillsChanged(self, skill_info):
        self.update()

    def OnSkillQueueChanged(self):
        self.update()

    def OnClientEvent_SkillAddedToQueue(self, type_id, level):
        if type_id == self.skill_type_id:
            self.update()

    def OnClientEvent_SkillsRemovedFromQueue(self, skillRequirements):
        for type_id, level in skillRequirements:
            if type_id == self.skill_type_id:
                self.update()
                return
