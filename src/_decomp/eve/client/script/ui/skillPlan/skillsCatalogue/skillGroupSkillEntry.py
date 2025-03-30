#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillGroupSkillEntry.py
import evetypes
from carbonui import uiconst
from carbonui.control.dragdrop import dragdata
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltipInfoOnly
from eve.client.script.ui.skillPlan.contents.skillEntryPrimaryButton import SkillEntryPrimaryButton
from eve.client.script.ui.skillPlan.scrollContEntry import ScrollContEntry
ENTRY_HEIGHT = 32

class SkillGroupSkillEntry(ScrollContEntry):
    default_height = ENTRY_HEIGHT
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(SkillGroupSkillEntry, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.showPrimaryButton = attributes.get('showPrimaryButton', False)
        self.primaryButton = None
        self.skillBar = SkillBar(parent=self, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=8, skillID=self.controller.GetTypeID())
        self._CreatePrimaryButton()
        self._ConstructLabel()
        self.UpdatePrimaryButton()

    def ConstructUnderlay(self):
        self.underlay = ListEntryUnderlay(bgParent=self, padRight=40, padBottom=0)

    def _ConstructLabel(self):
        self.trainingTimeLabelCont = ContainerAutoSize(name='timeRemainingCont', parent=self, align=uiconst.TORIGHT, padLeft=8)
        self.trainingTimeLabel = EveLabelLarge(name='timeRemainingLabel', parent=self.trainingTimeLabelCont, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, opacity=0.35)
        self.UpdateTrainingTimeLabel()
        textCont = Container(name='textCont', parent=self)
        EveLabelLarge(parent=textCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, left=75, text=evetypes.GetName(self.controller.GetTypeID()), autoFadeSides=16)

    def UpdateTrainingTimeLabel(self):
        level = self.controller.GetNextLevelToAddToQueue()
        if level:
            text = self.controller.GetTrainingTimeForLevelText(level)
        else:
            text = ''
        self.trainingTimeLabel.SetText(text)
        if not text:
            self.trainingTimeLabelCont.Hide()
        else:
            self.trainingTimeLabelCont.Show()

    def GetDragData(self):
        return dragdata.TypeDragData(self.controller.GetTypeID())

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.IsDragging():
            return
        LoadSkillEntryTooltipInfoOnly(tooltipPanel, self.controller.typeID)

    def GetTooltipPointer(self):
        return uiconst.POINT_BOTTOM_2

    def GetMenu(self):
        return self.controller.GetMenu()

    def Refresh(self):
        self.skillBar.Refresh()
        self.UpdatePrimaryButton()

    def _CreatePrimaryButton(self):
        if not self.showPrimaryButton or self.primaryButton is not None:
            return
        self.primaryButton = SkillEntryPrimaryButton(parent=self, align=uiconst.TORIGHT, iconAlign=uiconst.CENTER, iconLeft=0, fixedwidth=36, padLeft=8, skillController=self.controller)

    def UpdatePrimaryButton(self):
        if not self.showPrimaryButton:
            return
        if not self.primaryButton:
            self._CreatePrimaryButton()
        self.primaryButton.UpdateState()
        self.UpdateTrainingTimeLabel()

    def OnDblClick(self):
        sm.GetService('info').ShowInfo(self.controller.GetTypeID())
