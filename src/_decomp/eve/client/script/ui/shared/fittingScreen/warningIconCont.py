#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\warningIconCont.py
import threadutils
import uthread2
from carbonui.primitives.container import Container
from carbonui import const as uiconst
from carbonui.primitives.sprite import Sprite
import shipfitting.fittingWarnings as fittingWarnings
from eve.client.script.ui.control.eveLabel import EveLabelMediumBold
from eve.client.script.ui.shared.fittingScreen.skillRequirements import GetMissingSkills_HighestLevelByTypeID, GetSkillTooltip, GetAllTypeIDsMissingSkillsForShipAndContent
from eve.client.script.ui.shared.fittingScreen.warningIconTooltip import EvaluateFitAndPopulateTooltip
from shipfitting.fittingWarningConst import WARNING_LEVEL_HIGH, WARNING_LEVEL_MEDIUM, WARNING_LEVEL_LOW, WARNING_LEVEL_SKILL

class WarningIconCont(Container):
    default_name = 'warningIconCont'
    default_width = 0
    default_height = 60
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.fittingController = attributes.fittingController
        self.currentTooltipPanel = None
        ICON_SIZE = 26
        contSize = ICON_SIZE + 4
        row1 = Container(name='row1', parent=self, height=contSize, align=uiconst.TOTOP)
        row2 = Container(name='row2', parent=self, height=contSize, align=uiconst.TOTOP)
        self.height = 2 * contSize
        self.redWarning = WarningIcon(parent=row1, warningLevel=WARNING_LEVEL_HIGH, tooltipFunc=self.LoadWarningTooltipPanel, width=contSize, iconSize=ICON_SIZE)
        self.yellowWarning = WarningIcon(parent=row1, warningLevel=WARNING_LEVEL_MEDIUM, tooltipFunc=self.LoadWarningTooltipPanel, width=contSize, iconSize=ICON_SIZE)
        self.whiteWarning = WarningIcon(parent=row1, warningLevel=WARNING_LEVEL_LOW, tooltipFunc=self.LoadWarningTooltipPanel, width=contSize, iconSize=ICON_SIZE)
        self.skillWarning1 = SkillWarningIcon(parent=row1, warningLevel=WARNING_LEVEL_SKILL, tooltipFunc=self.LoadSkillTooltip, width=contSize, iconSize=ICON_SIZE)
        self.skillWarning2 = SkillWarningIcon(parent=row2, warningLevel=WARNING_LEVEL_SKILL, tooltipFunc=self.LoadSkillTooltip, width=contSize, iconSize=ICON_SIZE)
        for eachWarningIcon in (self.skillWarning1,
         self.skillWarning2,
         self.redWarning,
         self.yellowWarning,
         self.whiteWarning):
            eachWarningIcon.display = False

    def GetFitName(self):
        itemID = self.fittingController.GetItemID()
        if isinstance(itemID, long):
            return cfg.evelocations.Get(itemID).name
        else:
            return sm.GetService('ghostFittingSvc').GetShipName()

    def LoadSkillTooltip(self, tooltipPanel, *args):
        self.currentTooltipPanel = tooltipPanel
        GetSkillTooltip(tooltipPanel, self.fittingController, fitName=self.GetFitName())
        allTypeIDs = GetAllTypeIDsMissingSkillsForShipAndContent(self.fittingController.GetDogmaLocation())
        _, missingSkillsForTypeID = GetMissingSkills_HighestLevelByTypeID(allTypeIDs)
        warningSlotDict = fittingWarnings.GetSlotsMissingSkills(missingSkillsForTypeID)
        self.fittingController.ChangeFittingWarningDisplay(warningSlotDict)
        tooltipPanel.beingDestroyedCallback = self.SkillTooltipPanelBeingDestroyed
        sm.ScatterEvent('OnSkillMissingTooltipShown')

    def SkillTooltipPanelBeingDestroyed(self, tooltipPanel, *args):
        self.TooltipPanelBeingDestroyed(tooltipPanel, *args)
        sm.ScatterEvent('OnSkillMissingTooltipClosed')

    def LoadWarningTooltipPanel(self, tooltipPanel, owner):
        self.currentTooltipPanel = tooltipPanel
        warningLevel = owner.GetWarningLevel()
        tooltipPanel.state = uiconst.UI_NORMAL
        tooltipPanel.LoadGeneric4ColumnTemplate()
        tooltipPanel.margin = (8, 4, 8, 4)
        EvaluateFitAndPopulateTooltip(tooltipPanel, self.fittingController, warningLevel, True)
        tooltipPanel.beingDestroyedCallback = self.TooltipPanelBeingDestroyed

    def TooltipPanelBeingDestroyed(self, tooltipPanel, *args):
        if self.currentTooltipPanel is None or self.currentTooltipPanel.destroyed:
            self.fittingController.ChangeFittingWarningDisplay({})
            return
        if self.currentTooltipPanel == tooltipPanel and self.currentTooltipPanel.beingDestroyed:
            self.fittingController.ChangeFittingWarningDisplay({})

    @threadutils.throttled(0.5)
    def _UpdateIcon(self):
        uthread2.StartTasklet(self.__UpdateIcon_thread)

    def __UpdateIcon_thread(self):
        activeWarningsByLevel = fittingWarnings.GetActiveWarningsByLevel(self.fittingController)
        for eachIcon in (self.redWarning, self.yellowWarning, self.whiteWarning):
            warningLevel = eachIcon.GetWarningLevel()
            numActiveWarnings = activeWarningsByLevel.get(warningLevel, 0)
            if numActiveWarnings:
                eachIcon.display = True
                eachIcon.SetCounter(numActiveWarnings)
            else:
                eachIcon.display = False

        dogmaLocation = self.fittingController.GetDogmaLocation()
        allTypeIDs = GetAllTypeIDsMissingSkillsForShipAndContent(dogmaLocation)
        highestLevelByTypeID, _ = GetMissingSkills_HighestLevelByTypeID(allTypeIDs)
        if dogmaLocation != self.fittingController.GetDogmaLocation():
            return
        self.skillWarning1.display = self.skillWarning2.display = False
        if highestLevelByTypeID:
            mySkillIcon = self.skillWarning1 if len(activeWarningsByLevel) < 3 else self.skillWarning2
            mySkillIcon.display = True
            mySkillIcon.SetCounter(len(highestLevelByTypeID))

    def ChangeController(self, newController):
        self.fittingController = newController

    def UpdateIcon(self, *args):
        self._UpdateIcon()

    def Close(self):
        self.currentTooltipPanel = None
        Container.Close(self)


class WarningIcon(Container):
    default_width = 28
    default_height = 0
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL
    default_iconSize = 24
    texturePath = 'res:/UI/Texture/classes/Fitting/warningGroup.png'

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        iconSize = attributes.get('iconSize', self.default_iconSize)
        self.warningLevel = attributes.warningLevel
        self.LoadTooltipPanel = attributes.tooltipFunc
        color = fittingWarnings.GetColorForLevel(self.warningLevel)
        warningIcon = Sprite(name='warningIcon', parent=self, align=uiconst.BOTTOMLEFT, texturePath=self.texturePath, pos=(0,
         0,
         iconSize,
         iconSize), state=uiconst.UI_DISABLED)
        warningIcon.SetRGBA(*color)
        self.counterLabel = EveLabelMediumBold(parent=self, align=uiconst.TOPRIGHT, left=2)
        self.counterLabel.SetRGBA(*color)

    def SetCounter(self, number):
        self.counterLabel.text = number

    def GetWarningLevel(self):
        return self.warningLevel

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_1


class SkillWarningIcon(WarningIcon):
    texturePath = 'res:/ui/Texture/classes/Fitting/warningSkills.png'
