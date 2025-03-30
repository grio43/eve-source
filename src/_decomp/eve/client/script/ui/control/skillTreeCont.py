#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\skillTreeCont.py
import localization
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.common.lib import appConst as const
from skills.client.skillController import SkillController
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
COLOR_GRAY = (1.0, 1.0, 1.0, 0.5)

class SkillTreeCont(Container):
    default_name = 'SkillTreeCont'
    isDragObject = True
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 18
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_SkillsRemovedFromQueue']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        typeID = attributes.typeID
        self.requiredLevel = attributes.requiredLevel
        indent = attributes.get('indent', 0)
        self.tooltipPointerDirection = attributes.get('tooltipPointerDirection', None)
        self.ConstructLayout(indent=indent)
        self.skillController = SkillController(typeID)
        self.UpdateTextAndIcon()

    def ConstructLayout(self, indent):
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=16, left=indent)
        self.icon = Sprite(parent=iconCont, align=uiconst.CENTER, width=16, height=16)
        skillBarCont = Container(name='SkillBarCont', parent=self, align=uiconst.TORIGHT, width=70)
        self.timeToTrainLabel = Label(name='Time to train label', parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=8), align=uiconst.CENTERRIGHT, opacity=0.5)
        self.skillAndLevelLabelParent = Container(name='labelContainer', parent=self, align=uiconst.TOALL, left=5)
        self.skillAndLevelLabel = Label(name='SkillNameAndLevelLabel', parent=self.skillAndLevelLabelParent, align=uiconst.CENTERLEFT)
        self.skillBar = SkillBar(name='SkillBar', parent=skillBarCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED)
        self.backgroundFill = None

    def UpdateTextAndIcon(self):
        self.UpdateIcon()
        self.UpdateTimeToTrainLabel()
        self.UpdateSkillAndLevelLabel()
        self.skillBar.SetSkillID(self.skillController.GetTypeID())
        self.skillBar.SetRequiredLevel(self.requiredLevel)
        self.UpdateBackground()

    def UpdateSkillAndLevelLabel(self):
        if self.requiredLevel is not None:
            if self.skillController.GetMyLevel() >= self.requiredLevel:
                self.skillAndLevelLabel.opacity = 0.5
            text = self.skillController.GetRequiredSkillNameAndLevelComparedToTrainedLevel(self.requiredLevel)
        else:
            text = self.skillController.GetName()
        self.skillAndLevelLabel.SetText(text)

    def UpdateTimeToTrainLabel(self):
        if self.requiredLevel is not None:
            text = self.skillController.GetTimeToTrainToLevelText(self.requiredLevel)
        else:
            text = ''
        self.timeToTrainLabel.SetText(text)

    def SetIcon(self, texturePath, color, hint):
        self.icon.SetTexturePath(texturePath)
        self.icon.SetRGBA(*color)
        self.icon.hint = hint

    def UpdateIcon(self):
        if self.requiredLevel is None:
            self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png', color=COLOR_GRAY, hint=None)
        elif not self.skillController.IsInjected():
            if self.skillController.IsSkillAvailableForPurchase():
                self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillBookNotInjected.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/SkillQueue/SkillBookMissing'))
            else:
                self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/RareSkillBookNotInjected.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/SkillQueue/RareSkillBookMissing'))
        elif self.skillController.GetMyLevel() >= self.requiredLevel:
            self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillRequirementMet.png', color=COLOR_GRAY, hint=localization.GetByLabel('UI/InfoWindow/SkillTrainedToRequiredLevel'))
        else:
            self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/InfoWindow/SkillNotTrainedToRequiredLevel'))

    def UpdateBackground(self):
        if self.requiredLevel is None or self.skillController.GetMyLevel() >= self.requiredLevel:
            self.HideBackground()
        else:
            self.ShowBackground()

    def ShowBackground(self):
        if self.backgroundFill is None:
            self.backgroundFill = Fill(bgParent=self, color=COLOR_SKILL_1, opacity=0.05, padding=(0, 1, 0, 1))

    def HideBackground(self):
        if self.backgroundFill is not None:
            self.backgroundFill.Close()
            self.backgroundFill = None

    def UpdateAlignment(self, *args, **kwargs):
        alignment = super(SkillTreeCont, self).UpdateAlignment(*args, **kwargs)
        self.UpdateLabelFade()
        return alignment

    def UpdateLabelFade(self):
        availableWidth = self.skillAndLevelLabelParent.displayWidth - const.defaultPadding
        self.skillAndLevelLabel.SetRightAlphaFade(fadeEnd=availableWidth, maxFadeWidth=20)

    def OnDblClick(self, *args):
        sm.GetService('info').ShowInfo(self.skillController.GetTypeID())

    def GetMenu(self):
        return self.skillController.GetMenu()

    def GetDragData(self, *args):
        return self.skillController.GetDragData()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.tooltipHandler.IsUnderTooltip(self):
            return
        from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
        LoadSkillEntryTooltip(tooltipPanel, self.skillController.GetTypeID())

    def GetTooltipPointer(self):
        return self.tooltipPointerDirection

    def OnSkillsChanged(self, *args):
        self._Update()

    def OnSkillQueueChanged(self):
        self._Update()

    def OnClientEvent_SkillAddedToQueue(self, typeID, level):
        if typeID == self.skillController.GetTypeID():
            self._Update()

    def OnClientEvent_SkillsRemovedFromQueue(self, skillRequirements):
        for typeID, level in skillRequirements:
            if typeID == self.skillController.GetTypeID():
                self._Update()
                return

    def _Update(self):
        self.UpdateTextAndIcon()
        self.skillBar.Update()
