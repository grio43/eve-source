#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\scrollContEntry.py
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from signals import Signal

class ScrollContEntry(Container):
    isDragObject = True
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ScrollContEntry, self).ApplyAttributes(attributes)
        self.onClickSignal = Signal('SkillPlanEntry_onClickSignal')
        self.onDblClickSignal = Signal('SkillPlanEntry_onDblClickSignal')
        self.isSelected = False
        self.ConstructUnderlay()

    def ConstructUnderlay(self):
        self.underlay = ListEntryUnderlay(bgParent=self)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        self.underlay.hovered = True

    def OnMouseExit(self, *args):
        self.underlay.hovered = False

    def SetSelected(self):
        self.underlay.Select()
        self.isSelected = True

    def SetDeselected(self):
        if self.isSelected:
            self.underlay.Deselect()
            self.isSelected = False

    def OnClick(self):
        self.onClickSignal(self)

    def OnDblClick(self):
        self.onDblClickSignal(self)
