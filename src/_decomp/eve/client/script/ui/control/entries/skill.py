#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\skill.py
import evetypes
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from eve.common.lib import appConst as const
from skills.client.skillController import SkillController

class SkillTreeEntry(Generic):
    __guid__ = 'listentry.SkillTreeEntry'
    isDragObject = True
    default_showHilite = True

    def ApplyAttributes(self, attributes):
        super(SkillTreeEntry, self).ApplyAttributes(attributes)
        self.initialized = False

    def Startup(self, *args):
        super(SkillTreeEntry, self).Startup(*args)
        self.skillService = sm.GetService('skills')
        self.infoService = sm.GetService('info')

    def Load(self, data):
        super(SkillTreeEntry, self).Load(data)
        self.indent = 15 * data.indent - 11
        self.skillID = data.typeID
        self.skillController = SkillController(self.skillID)
        data.text = evetypes.GetName(self.skillID)
        if not self.initialized:
            self.Layout()
            self.initialized = True
        self.Refresh(data)

    def Refresh(self, data):
        requiredLevel = data.lvl
        self.node = data
        text = self.skillController.GetTimeToTrainToLevelText(requiredLevel)
        self.timeToTrainLabel.SetText(text)
        text = self.skillController.GetRequiredSkillNameAndLevelComparedToTrainedLevel(data.lvl)
        self.skillAndLevelLabel.SetText(text)
        self.skillBar.SetRequiredLevel(requiredLevel)
        if not self.skillController.IsInjected():
            if self.skillController.IsSkillAvailableForPurchase():
                self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillBookNotInjected.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/SkillQueue/SkillBookMissing'))
            else:
                self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/RareSkillBookNotInjected.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/SkillQueue/RareSkillBookMissing'))
            self.ShowBackground()
        elif self.skillController.GetMyLevel() >= requiredLevel:
            self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillRequirementMet.png', color=(1.0, 1.0, 1.0, 0.5), hint=localization.GetByLabel('UI/InfoWindow/SkillTrainedToRequiredLevel'))
            self.skillAndLevelLabel.SetRGBA(1.0, 1.0, 1.0, 0.5)
            self.HideBackground()
        else:
            self.SetIcon(texturePath='res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/InfoWindow/SkillNotTrainedToRequiredLevel'))
            self.ShowBackground()

    def SetIcon(self, texturePath, color, hint):
        if self.icon is None:
            self.icon = Sprite(parent=self.iconCont, align=uiconst.CENTER, texturePath=texturePath, width=16, height=16, color=color, hint=hint)
        else:
            self.icon.SetTexturePath(texturePath)
            self.icon.SetRGBA(*color)
            self.icon.hint = hint

    def ShowBackground(self):
        if self.backgroundFill is None:
            self.backgroundFill = Fill(bgParent=self, color=COLOR_SKILL_1, opacity=0.05, padding=(0, 1, 0, 1))

    def HideBackground(self):
        if self.backgroundFill is not None:
            self.backgroundFill.Close()
            self.backgroundFill = None

    def Layout(self):
        self.iconCont = Container(parent=self, align=uiconst.TOLEFT, width=16, left=self.indent)
        self.icon = None
        self.skillBar = SkillBar(name='Skill Bar', parent=Container(name='Skill Bar Container', parent=self, align=uiconst.TORIGHT, width=70), align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, skillID=self.skillID)
        self.timeToTrainLabel = Label(name='Time to train label', parent=ContainerAutoSize(parent=self, align=uiconst.TORIGHT, left=8), align=uiconst.CENTERRIGHT, opacity=0.5)
        self.skillAndLevelLabelParent = Container(name='label container', parent=self, align=uiconst.TOALL, left=5)
        self.skillAndLevelLabel = Label(name='Skill Name And Level Label', parent=self.skillAndLevelLabelParent, align=uiconst.CENTERLEFT)
        self.backgroundFill = None

    def UpdateAlignment(self, *args, **kwargs):
        alignment = super(SkillTreeEntry, self).UpdateAlignment(*args, **kwargs)
        if self.initialized:
            self.UpdateLabelFade()
        return alignment

    def UpdateLabelFade(self):
        availableWidth = self.skillAndLevelLabelParent.displayWidth - const.defaultPadding
        self.skillAndLevelLabel.SetRightAlphaFade(fadeEnd=availableWidth, maxFadeWidth=20)

    def GetHeight(self, *args):
        return 28

    def OnDblClick(self, *args):
        self.infoService.ShowInfo(self.skillID)

    def GetMenu(self):
        return self.skillController.GetMenu()

    def GetDragData(self, *args):
        return [self.node]

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.tooltipHandler.IsUnderTooltip(self):
            return
        from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
        LoadSkillEntryTooltip(tooltipPanel, self.skillID)
