#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\steps\empireSelection\sidePanelFactionAndSchool.py
import uthread
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.uianimations import animations
from characterdata import factions, schools
from eve.client.script.ui.const.eveIconConst import RACE_ICONS
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelLarge, EveCaptionSmall
from eve.client.script.ui.login.charcreation_new import charCreationSignals
from eve.client.script.ui.login.charcreation_new.baseSidePanel import BaseSidePanel
from eve.client.script.ui.login.charcreation_new.steps.empireSelection import empireSelectionConst
from eve.client.script.ui.login.charcreation_new.steps.empireSelection.empireSelectionConst import FACTIONSELECT_ANIMATION_DURATION
from eve.common.lib import appConst
from eveui import Sprite
LEFT = 30

class SidePanelFactionAndSchool(ContainerAutoSize):
    default_name = 'SidePanelFactionAndSchool'

    def ApplyAttributes(self, attributes):
        super(SidePanelFactionAndSchool, self).ApplyAttributes(attributes)
        factionID = attributes.factionID
        schoolID = attributes.schoolID
        self.factionPanel = SidePanelFaction(parent=self, align=uiconst.TOTOP, factionID=factionID)
        self.schoolPanel = SidePanelSchool(parent=self, align=uiconst.TOTOP, padTop=10, schoolID=schoolID, factionID=factionID)

    def HideSchoolPanel(self):
        self.schoolPanel.Hide()

    def ShowSchoolPanel(self):
        self.schoolPanel.Show()


class SidePanelFaction(BaseSidePanel):
    default_height = 270
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        super(SidePanelFaction, self).ApplyAttributes(attributes)
        factionID = attributes.factionID
        charCreationSignals.onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        self.factionIcon = Sprite(name='factionIcon', parent=self.mainCont, align=uiconst.CENTERTOP, pos=(0, 25, 100, 100))
        self.factionNameLabel = EveCaptionLarge(name='factionNameLabel', parent=self.mainCont, align=uiconst.TOPLEFT, pos=(LEFT,
         115,
         0,
         0))
        self.descriptionLabel = EveLabelLarge(name='descriptionLabel', parent=self.mainCont, align=uiconst.TOPLEFT, pos=(LEFT,
         170,
         375,
         0))
        if factionID:
            self._UpdateFaction(factionID)
            self.opacity = 1.0

    def OnEmpireFactionSelected(self, factionID):
        uthread.new(self._OnEmpireFactionSelected, factionID)

    def _OnEmpireFactionSelected(self, factionID):
        duration = FACTIONSELECT_ANIMATION_DURATION / 2
        animations.FadeTo(self, self.opacity, 0.0, duration=duration, sleep=True)
        self._UpdateFaction(factionID)
        animations.FadeIn(self, duration=duration, timeOffset=duration * 1.5)

    def _UpdateFaction(self, factionID):
        self.factionIcon.texturePath = RACE_ICONS[appConst.raceByFaction[factionID]]
        color = empireSelectionConst.COLOR_BY_FACTIONID[factionID]
        self.factionNameLabel.text = factions.get_faction_name(factionID)
        self.factionNameLabel.SetRGBA(*color)
        self.descriptionLabel.text = factions.get_faction_short_description(factionID)


class SidePanelSchool(BaseSidePanel):
    default_height = 210
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        super(SidePanelSchool, self).ApplyAttributes(attributes)
        schoolID = attributes.schoolID
        self.factionID = attributes.factionID
        self.schoolID = None
        charCreationSignals.onEmpireSchoolSelected.connect(self.OnSchoolSelected)
        charCreationSignals.onEmpireFactionSelected.connect(self.OnEmpireFactionSelected)
        self.icon = Sprite(name='icon', parent=self.mainCont, align=uiconst.CENTERLEFT, pos=(LEFT,
         0,
         64,
         64))
        Sprite(name='iconBG', parent=self.mainCont, align=uiconst.CENTERLEFT, pos=(LEFT - 4,
         0,
         72,
         64), texturePath='res:/UI/Texture/Classes/CharacterSelection/EmpireSelection/iconBG.png')
        textCont = ContainerAutoSize(name='textCont', parent=self.mainCont, align=uiconst.CENTERLEFT, pos=(115, 0, 290, 0))
        self.schoolTitleLabel = EveCaptionSmall(name='schoolTitleLabel', parent=textCont, align=uiconst.TOTOP)
        self.schoolNameLabel = EveCaptionLarge(name='schoolNameLabel', parent=textCont, align=uiconst.TOTOP, padTop=2)
        self.descriptionLabel = EveLabelLarge(name='descriptionLabel', parent=textCont, align=uiconst.TOTOP, padTop=8)
        if schoolID:
            self._UpdateSchool(schoolID)
            self.opacity = 1.0

    def OnSchoolSelected(self, schoolID):
        uthread.new(self._OnSchoolSelected, schoolID)

    def OnEmpireFactionSelected(self, factionID):
        self.factionID = factionID

    def _OnSchoolSelected(self, schoolID):
        duration = 0.3
        if self.schoolID:
            animations.FadeTo(self, self.opacity, 0.0, duration=duration, sleep=True)
        self.schoolID = schoolID
        if schoolID:
            self._UpdateSchool(schoolID)
            animations.FadeIn(self, duration=duration)

    def _UpdateSchool(self, schoolID):
        self.icon.texturePath = empireSelectionConst.ICONS_BY_SCHOOLID[schoolID]
        self.schoolTitleLabel.text = schools.get_school_title(schoolID)
        self.schoolNameLabel.text = schools.get_school_name(schoolID)
        color = empireSelectionConst.COLOR_BY_FACTIONID[self.factionID]
        self.schoolNameLabel.SetRGBA(*color)
        self.descriptionLabel.text = schools.get_school_description(schoolID)
