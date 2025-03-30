#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillsCatalogue\skillGroupEntry.py
import evetypes
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from carbonui.util.color import Color
from clonegrade import COLOR_OMEGA_ORANGE
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.skillPlan.scrollContEntry import ScrollContEntry
from eve.client.script.ui.skillPlan.skillsCatalogue.skillsPanelUtil import LoadSkillGroupTooltipPanel
from eveui import Sprite
from skills.client.skillGroupController import SkillGroupController

class SkillGroupEntryUnderlay(ListEntryUnderlay):
    default_texturePath = 'res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png'
    default_color = eveColor.WHITE
    default_cornerSize = 12
    default_opacity = 0.1
    OPACITY_SELECTED = 1.0


class SkillGroupEntry(ScrollContEntry):

    def ApplyAttributes(self, attributes):
        super(SkillGroupEntry, self).ApplyAttributes(attributes)
        self.groupID = attributes.groupID
        self.controller = SkillGroupController(self.groupID)
        self.numSkills = 0
        self.iconCont = Container(parent=self, align=uiconst.TOLEFT, width=36, padding=(2, 0, 2, 0))
        self.iconBg = Frame(bgParent=self.iconCont, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_SolidMirrored.png', cornerSize=12, color=eveThemeColor.THEME_FOCUS, opacity=0.2)
        Sprite(parent=self.iconCont, align=uiconst.CENTER, texturePath=self.controller.GetIcon(), pos=(0, 0, 32, 32))
        mainCont = Container(name='mainCont', parent=self)
        numFiltercont = ContainerAutoSize(parent=mainCont, align=uiconst.TORIGHT, padding=(6, 0, 8, 0))
        self.label = EveLabelLarge(parent=Container(name='labelCont', parent=mainCont), align=uiconst.CENTERLEFT, text=evetypes.GetGroupNameByGroup(self.groupID), left=8, autoFadeSides=True)
        self.numFilteredLabel = EveLabelLarge(parent=numFiltercont, align=uiconst.CENTER)
        self.progressBar = Fill(name='progressBar', parent=mainCont, align=uiconst.TOLEFT_PROP, color=eveThemeColor.THEME_ACCENT, opacity=0.2)
        self.omegaProgressBar = Fill(name='omegaProgressBar', parent=mainCont, align=uiconst.TOLEFT_PROP, color=COLOR_OMEGA_ORANGE, opacity=0.6)
        self.UpdateProgress()

    def UpdateProgress(self):
        disabledRatio = self.controller.GetAccumulatedLevelsTrainedAndDisabledRatio()
        self.omegaProgressBar.width = disabledRatio
        self.progressBar.width = self.controller.GetAccumulatedLevelsTrainedRatio() - disabledRatio

    def ConstructUnderlay(self):
        self.underlay = ListEntryUnderlay(bgParent=self, padding=(40, 0, 0, 0))

    def GetHint(self):
        return self.controller.GetHint()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        LoadSkillGroupTooltipPanel(self.controller, tooltipPanel)

    def SetNumSkills(self, numSkills, i):
        self.numSkills = numSkills
        animate = numSkills != self.numSkills
        if self.numSkills:
            self.numFilteredLabel.text = '%s' % self.numSkills
        else:
            self.numFilteredLabel.text = ''
        if animate:
            animations.FadeTo(self.numFilteredLabel, 0, 1.0, duration=0.3, timeOffset=i * 0.02)
        opacity = 1.0 if numSkills else 0.4
        animations.FadeTo(self, self.opacity, opacity, duration=0.3)

    def SetSelected(self):
        super(SkillGroupEntry, self).SetSelected()
        color = Color(*eveThemeColor.THEME_FOCUSDARK).SetOpacity(ListEntryUnderlay.OPACITY_SELECTED).GetRGBA()
        animations.SpColorMorphTo(self.iconBg, self.iconBg.GetRGBA(), color, duration=uiconst.TIME_SELECT)

    def SetDeselected(self):
        super(SkillGroupEntry, self).SetDeselected()
        color = Color(*eveThemeColor.THEME_FOCUSDARK).SetOpacity(ListEntryUnderlay.OPACITY_HOVER).GetRGBA()
        animations.SpColorMorphTo(self.iconBg, self.iconBg.GetRGBA(), color, duration=uiconst.TIME_DESELECT)

    def OnClick(self):
        super(SkillGroupEntry, self).OnClick()
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
