#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\skillPlanDropIndicatorCont.py
import uthread2
from carbonui.control.dragdrop import dragdata
from carbonui.primitives.container import Container
from carbonui import const as uiconst
from carbonui.uicore import uicore
from eve.client.script.ui.shared.neocom.skillConst import COLOR_MOVE_INDICATOR
from eve.client.script.ui.skillPlan import skillPlanUtil
from eve.client.script.ui.skillPlan.skillPlanEditor.dragIndicatorLine import DragIndicatorLine
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanEditorSkillEntry import VALID_LINE_COLOR, INVALID_LINE_COLOR

class BaseDropIndicatorCont(Container):
    default_height = 20
    default_state = uiconst.UI_NORMAL
    default_name = 'baseDropIndicatorCont'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.indicatorLine = DragIndicatorLine(parent=self, align=uiconst.TOTOP_NOPUSH, idx=0, padRight=11)
        self.HideIndicator()

    def OnDragEnterFromParent(self, *args, **kwargs):
        raise NotImplementedError

    def ShowIndicator(self, isValid = True):
        self.indicatorLine.Show()
        self.indicatorLine.color = VALID_LINE_COLOR if isValid else INVALID_LINE_COLOR

    def HideIndicator(self):
        self.indicatorLine.Hide()


class SkillPlanDropIndicatorCont(BaseDropIndicatorCont):
    default_name = 'skillPlanDropIndicatorCont'

    def OnDragEnterFromParent(self, draggedEntries, skillPlan, scroll):
        dragData = draggedEntries[0]
        while uicore.uilib.mouseOver.IsUnder(self) or uicore.uilib.mouseOver is self:
            if self.destroyed or not skillPlan or not uicore.IsDragging():
                self.HideIndicator()
                return
            if scroll.IsVerticalScrollBarVisible():
                if scroll.GetPositionVertical() >= 1.0:
                    if isinstance(dragData, dragdata.SkillLevelDragData):
                        originalIndex = skillPlan.GetSkillRequirementIndex(dragData.typeID, dragData.level)
                        dropIndex = len(skillPlan.GetSkillRequirements())
                        isValidMove = skillPlan.IsSkillRequirementMoveValid(originalIndex, dropIndex)
                        self.ShowIndicator(isValidMove)
                    elif skillPlanUtil.IsValidContentsDragData(dragData):
                        self.ShowIndicator()
                else:
                    scroll.ScrollMoveVertical(0.1)
            uthread2.Sleep(0.1)

        self.HideIndicator()


class SkillQueueDropIndicatorCont(BaseDropIndicatorCont):
    default_name = 'SkillQueueDropIndicatorCont'

    def OnDragEnterFromParent(self, draggedEntries, scroll):
        dragData = draggedEntries[0]
        skillQueueSvc = sm.GetService('skillqueue')
        while uicore.uilib.mouseOver.IsUnder(self) or uicore.uilib.mouseOver is self:
            if self.destroyed or not uicore.IsDragging():
                self.HideIndicator()
                return
            if scroll.IsScrollbarVisible():
                if scroll.GetScrollProportion() >= 1.0:
                    if IsMultiSkillEntryMove(draggedEntries):
                        self.ShowNeutralMoveIndicator()
                    else:
                        isValidMove = skillQueueSvc.IsMoveAllowed(dragData, None)
                        self.ShowIndicator(isValidMove)
                else:
                    scroll.Scroll(-0.2)
            uthread2.Sleep(0.1)

        self.HideIndicator()

    def ShowNeutralMoveIndicator(self):
        self.indicatorLine.Show()
        self.indicatorLine.color = COLOR_MOVE_INDICATOR


def IsMultiSkillEntryMove(draggedEntries):
    if len(draggedEntries) < 2:
        return False
    for data in draggedEntries:
        if getattr(data, '__guid__', None) != 'listentry.SkillQueueSkillEntry':
            return False

    return True
