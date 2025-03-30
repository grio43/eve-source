#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\skillPlanEditorSkillEntry.py
from carbonui import uiconst
from carbonui.control.button import Button
from carbonui.control.dragdrop import dragdata
from eve.client.script.ui import eveColor
from eve.client.script.ui.skillPlan import skillPlanUtil
from eve.client.script.ui.skillPlan.contents.skillPlanSkillEntry import SkillPlanSkillEntry
from eve.client.script.ui.skillPlan.skillPlanEditor.dragIndicatorLine import DragIndicatorLine
from localization import GetByLabel
from signals import Signal
VALID_LINE_COLOR = (0.8, 0.8, 0.8)
INVALID_LINE_COLOR = (0.7, 0.0, 0.0)

class EditorSkillLevelEntryPrimaryButton(Button):
    default_texturePath = 'res:/UI/Texture/classes/SkillPlan/buttonIcons/removeIcon.png'
    default_disabled_color = eveColor.BLACK
    default_soundClick = uiconst.SOUND_REMOVE

    def ApplyAttributes(self, attributes):
        super(EditorSkillLevelEntryPrimaryButton, self).ApplyAttributes(attributes)
        self.skillPlan = attributes.skillPlan
        self.level = attributes.skillLevel
        self.controller = attributes.skillController
        self.func = self._Remove

    def _Remove(self, *args):
        if self.skillPlan:
            self.skillPlan.RemoveSkillRequirement(self.controller.GetTypeID(), self.level)

    def UpdateState(self):
        if not self.controller:
            return
        if self.skillPlan.CanRemoveSkillRequirement(self.controller.GetTypeID(), self.level):
            self.Enable()
            self.SetHint(GetByLabel('UI/SkillPlan/RemoveFromPlan'))
        else:
            self.Disable()
            self.SetHint(GetByLabel('UI/SkillPlan/RemoveFromPlanLocked'))


class SkillPlanEditorSkillEntry(SkillPlanSkillEntry):

    def ApplyAttributes(self, attributes):
        super(SkillPlanEditorSkillEntry, self).ApplyAttributes(attributes)
        self.skillPlan = attributes.skillPlan
        self.onDropDataSignal = Signal(__name__ + '_onDropDataSignal')
        self.onDragEnterSignal = Signal(__name__ + '_onDragEnterSignal')
        self.primaryButton = EditorSkillLevelEntryPrimaryButton(parent=self, align=uiconst.TORIGHT, skillController=self.controller, skillLevel=self.level, skillPlan=self.skillPlan, idx=0)
        self.dragIndicatorLine = DragIndicatorLine(parent=self, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_HIDDEN, idx=0)
        self.UpdatePrimaryButton()

    def ShowIndicatorLine(self, valid = True):
        self.dragIndicatorLine.color = VALID_LINE_COLOR if valid else INVALID_LINE_COLOR
        self.dragIndicatorLine.Show()

    def OnDropData(self, dragSource, dragData):
        self.onDropDataSignal(self, dragData)
        self.dragIndicatorLine.Hide()

    def GetDragData(self):
        return (dragdata.SkillLevelDragData(self.typeID, self.level),)

    def OnDragEnter(self, dragSource, dragDataList):
        dragData = dragDataList[0]
        if skillPlanUtil.IsValidContentsDragData(dragData):
            self.onDragEnterSignal(self, dragData)

    def OnDragExit(self, dragSource, dragData):
        self.dragIndicatorLine.Hide()

    def Refresh(self):
        super(SkillPlanEditorSkillEntry, self).Refresh()
        self.UpdatePrimaryButton()

    def UpdatePrimaryButton(self):
        self.primaryButton.UpdateState()
