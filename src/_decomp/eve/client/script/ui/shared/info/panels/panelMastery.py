#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelMastery.py
import evetypes
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from carbon.common.script.util.format import IntToRoman
from eve.client.script.ui.control.entries.certificate import CertEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButtonIcon
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.shared.shipTree import shipTreeConst
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skillBtns import SkillActionContainer
from eve.client.script.ui.shared.tooltip.skill_requirement import OmegaTrainingTimeContainer, AlphaTrainingTimeContainer
from eve.common.lib import appConst as const
BUTTONS = ((1, 'res:/UI/Texture/classes/Mastery/MasterySmall1.png'),
 (2, 'res:/UI/Texture/classes/Mastery/MasterySmall2.png'),
 (3, 'res:/UI/Texture/classes/Mastery/MasterySmall3.png'),
 (4, 'res:/UI/Texture/classes/Mastery/MasterySmall4.png'),
 (5, 'res:/UI/Texture/classes/Mastery/MasterySmall5.png'))

class PanelMastery(Container):
    __notifyevents__ = ['OnSkillsChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.masteryLevel = 0
        sm.RegisterNotify(self)

    def Load(self):
        self.Flush()
        toggleButtonCont = Container(name='btnGroupCont', parent=self, align=uiconst.TOTOP, height=45)
        btnGroup = ToggleButtonGroup(parent=toggleButtonCont, align=uiconst.CENTER, height=toggleButtonCont.height, width=330, padding=(10, 4, 10, 3), callback=self.LoadMasteryLevel, btnClass=ToggleButtonGroupButtonIcon)
        for level, iconPath in BUTTONS:
            hint = localization.GetByLabel('UI/InfoWindow/MasteryLevelButtonHint', level=level)
            if level == 5:
                color = Color(*shipTreeConst.COLOR_MASTERED).SetBrightness(0.2).GetRGBA()
            else:
                color = Color(*shipTreeConst.COLOR_BG).SetBrightness(0.35).GetRGBA()
            btnGroup.AddButton(btnID=level, iconPath=iconPath, iconSize=45, hint=hint, colorSelected=color)

        self.settingsMenu = UtilMenu(menuAlign=uiconst.TOPLEFT, parent=toggleButtonCont, align=uiconst.BOTTOMLEFT, top=4, left=4, GetUtilMenu=self.GetSettingsMenu, texturePath='res:/UI/Texture/SettingsCogwheel.png', width=16, height=16, iconSize=18)
        self.bottomContainer = ContainerAutoSize(parent=self, align=uiconst.TOBOTTOM, padding=const.defaultPadding)
        self.masteryScroll = Scroll(name='masteryScroll', parent=self, padding=const.defaultPadding)
        level = sm.GetService('certificates').GetCurrCharMasteryLevel(self.typeID)
        level = max(level, 1)
        btnGroup.SelectByID(level)

    def LoadMasteryLevel(self, btnID, *args):
        if getattr(self, 'masteryScroll', None) is None:
            return
        if btnID is None:
            return
        self.masteryLevel = btnID
        entries = self.GetMasteryScrollEntries(btnID)
        self.masteryScroll.Load(contentList=entries)
        self.UpdateTrainingTime(btnID)

    def GetMasteryScrollEntries(self, level):
        certificates = sm.GetService('certificates').GetCertificatesForShipByMasteryLevel(self.typeID, level)
        scrolllist = []
        for cert in certificates:
            data = sm.GetService('info').GetCertEntry(cert, level)
            scrolllist.append((data.get('label', ''), GetFromClass(CertEntry, data)))

        return SortListOfTuples(scrolllist)

    def UpdateTrainingTime(self, masteryLevel):
        certSvc = sm.GetService('certificates')
        trainingTime = certSvc.GetShipTrainingTimeForMasteryLevel(self.typeID, masteryLevel)
        skillSvc = sm.GetService('skills')
        isOmegaRestricted = False
        requiredSkillsList = []
        cloneGradeService = sm.GetService('cloneGradeSvc')
        for skillID, skillLevel in certSvc.GetSkillsRequiredForMasteryLevel(self.typeID, masteryLevel).iteritems():
            skill = skillSvc.GetSkill(skillID)
            if not isOmegaRestricted:
                isOmegaRestricted = cloneGradeService.IsRequirementsRestricted(skillID)
                if not isOmegaRestricted:
                    isOmegaRestricted = cloneGradeService.IsSkillLevelRestricted(skillID, skillLevel)
            if not skill or skill.trainedSkillLevel < skillLevel:
                requiredSkillsList.append((skillID, skillLevel))

        if not isOmegaRestricted:
            isOmegaRestricted = ItemObject(self.typeID).NeedsOmegaUpgrade()
        requiredSkillsList = list(set(requiredSkillsList))
        requiredSkillsList = skillSvc.GetSkillsMissingToUseAllSkillsFromListRecursiveAsList(requiredSkillsList)
        missingSkills = sm.GetService('skills').GetMissingSkillBooksFromList(requiredSkillsList)
        self.bottomContainer.Flush()
        if len(requiredSkillsList) > 0:
            if cloneGradeService.IsOmega():
                OmegaTrainingTimeContainer(parent=self.bottomContainer, omegaTime=long(trainingTime), padBottom=8)
            else:
                omegaTime = long(trainingTime) / 2
                AlphaTrainingTimeContainer(parent=self.bottomContainer, isOmegaRestricted=isOmegaRestricted, alphaTime=long(trainingTime), omegaTime=omegaTime, activityText=localization.GetByLabel('Tooltips/SkillPlanner/ActivityTrainMasteryLevel'), padBottom=8, clipChildren=True)
            if not isOmegaRestricted:
                typeName = evetypes.GetName(self.typeID)
                level = IntToRoman(self.masteryLevel)
                skillPlanName = localization.GetByLabel('UI/SkillPlan/CreateMasterySkillPlanName', typeName=typeName, level=level)
                SkillActionContainer(parent=self.bottomContainer, align=uiconst.TOTOP, requiredSkills=requiredSkillsList, missingSkills=missingSkills, skillPlanName=skillPlanName)

    def GetSettingsMenu(self, parent):
        parent.AddCheckBox(text=localization.GetByLabel('UI/InfoWindow/MasteryFilterAcquired'), checked=bool(settings.user.ui.Get('masteries_filter_acquired', False)), callback=self.ToggleFilterAcquired)

    def ToggleFilterAcquired(self, *args):
        settings.user.ui.Set('masteries_filter_acquired', not settings.user.ui.Get('masteries_filter_acquired', False))
        self.LoadMasteryLevel(self.masteryLevel)

    def OnSkillsChanged(self, *args):
        self.LoadMasteryLevel(self.masteryLevel)
