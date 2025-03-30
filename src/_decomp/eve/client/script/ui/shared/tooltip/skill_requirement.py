#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\skill_requirement.py
import carbonui.uiconst as uiconst
import eveicon
import evetypes
import localization
from carbon.common.script.util.format import IntToRoman
from carbonui import TextBody, TextColor, Align, ButtonStyle, Density, ButtonFrameType
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid, LayoutGridRow
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from clonegrade import COLOR_OMEGA_ORANGE, COLOR_OMEGA_DARK_BG
from eve.client.script.ui.control.infoIcon import WarningGlyphIcon
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SKILLREQ_PANEL
from eve.client.script.ui.shared.neocom import skillConst
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skillBtns import SkillActionContainer
from eveservices.menu import GetMenuService
from localization.formatters.timeIntervalFormatters import TIME_CATEGORY_MINUTE, FormatTimeIntervalShortWritten
from skills.client.skillController import SkillController
from utillib import KeyVal
from inventorycommon import const

class RequiredSkillRow(LayoutGridRow):
    default_state = uiconst.UI_NORMAL
    isDragObject = True
    __notifyevents__ = ['OnSkillQueueRefreshed']

    def ApplyAttributes(self, attributes):
        super(RequiredSkillRow, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.level = attributes.level
        text = localization.GetByLabel('UI/InfoWindow/RequiredSkillNameAndLevel', skill=self.typeID, level=IntToRoman(self.level), levelColor=Color(*skillConst.COLOR_SKILL_1).GetHex())
        label = TextBody(align=uiconst.CENTERLEFT, text=text, padRight=15)
        self.AddCell(label)
        texturePath, hint = self._GetTexturePathAndHint()
        Sprite(name='skillbookStatus', parent=label.parent, align=uiconst.CENTERRIGHT, pos=(-16, 0, 16, 16), texturePath=texturePath, color=TextColor.WARNING, hint=hint)
        self.bar = SkillBar(align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, skillID=self.typeID, requiredLevel=self.level)
        self.AddCell(self.bar, cellPadding=(24, 6, 0, 0))
        sm.RegisterNotify(self)

    def Close(self):
        super(RequiredSkillRow, self).Close()
        sm.UnregisterNotify(self)

    def _GetTexturePathAndHint(self):
        texturePath = hint = ''
        skillController = SkillController(self.typeID)
        if not skillController.IsInjected():
            if skillController.IsSkillAvailableForPurchase():
                texturePath = eveicon.skill_book
                hint = localization.GetByLabel('UI/SkillQueue/SkillBookMissing')
            else:
                texturePath = 'res:/ui/Texture/classes/Skills/RareSkillBookNotInjected.png'
                hint = localization.GetByLabel('UI/SkillQueue/RareSkillBookMissing')
        elif skillController.GetMyLevel() < self.level:
            texturePath = None
            hint = localization.GetByLabel('UI/InfoWindow/SkillNotTrainedToRequiredLevel')
        return (texturePath, hint)

    def GetMenu(self):
        return GetMenuService().GetMenuForSkill(self.typeID)

    def OnClick(self):
        sm.GetService('info').ShowInfo(self.typeID)

    def GetDragData(self):
        data = KeyVal(__guid__='uicls.GenericDraggableForTypeID', typeID=self.typeID, label=evetypes.GetName(self.typeID))
        return (data,)

    def OnSkillQueueRefreshed(self):
        self.bar.Refresh()


class AlphaTrainingTimeContainer(ContainerAutoSize):
    default_name = 'AlphaTrainingCnt'
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_bgColor = COLOR_OMEGA_DARK_BG

    def ApplyAttributes(self, attributes):
        self.isOmegaRestricted = attributes.isOmegaRestricted
        self.alphaTime = attributes.alphaTime
        self.omegaTime = attributes.omegaTime
        self.activityText = attributes.activityText
        self.omega_button = None
        super(AlphaTrainingTimeContainer, self).ApplyAttributes(attributes)
        self.on_click_callback = attributes.get('on_click', None)
        content = ContainerAutoSize(parent=self, align=Align.TOTOP, alignMode=Align.TOTOP, padding=10, clipChildren=True)
        top_container = ContainerAutoSize(parent=content, align=Align.TOTOP, alignMode=Align.CENTERLEFT, padBottom=4)
        TextBody(parent=top_container, align=uiconst.CENTERLEFT, text=localization.GetByLabel('Tooltips/SkillPlanner/TrainingTime'), color=TextColor.SECONDARY, autoFadeSides=True)
        alpha_time_container = ContainerAutoSize(parent=content, align=Align.TOTOP, alignMode=Align.CENTERLEFT, padBottom=4)
        Sprite(parent=alpha_time_container, align=Align.CENTERLEFT, width=16, height=16, texturePath=eveicon.alpha)
        TextBody(parent=alpha_time_container, align=Align.CENTERLEFT, text=self._get_time_formatted(self.alphaTime), color=TextColor.HIGHLIGHT if not self.isOmegaRestricted else TextColor.SECONDARY, padLeft=24, autoFadeSides=True)
        omega_time_container = ContainerAutoSize(parent=content, align=Align.TOTOP, alignMode=Align.CENTERLEFT)
        Sprite(parent=omega_time_container, align=Align.CENTERLEFT, width=16, height=16, texturePath=eveicon.omega)
        TextBody(parent=omega_time_container, align=uiconst.CENTERLEFT, text=self._get_time_formatted(self.omegaTime), color=COLOR_OMEGA_ORANGE, padLeft=24, autoFadeSides=True)
        if self.isOmegaRestricted:
            omega_warning_container = ContainerAutoSize(parent=content, align=Align.TOTOP, alignMode=Align.CENTERLEFT, padTop=4)
            WarningGlyphIcon(parent=omega_warning_container, align=Align.CENTERLEFT, height=18, width=18)
            TextBody(parent=omega_warning_container, align=Align.CENTERLEFT, color=TextColor.HIGHLIGHT, text=localization.GetByLabel('Tooltips/SkillPlanner/OmegaCloneStateRequiredForActivity', doActivity=self.activityText), padLeft=24, autoFadeSides=True)
        Button(parent=content, align=Align.TOTOP, label=localization.GetByLabel('UI/CloneState/Upgrade'), texturePath=eveicon.omega, style=ButtonStyle.MONETIZATION, func=self.on_omega_button_click, density=Density.COMPACT, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT, padTop=8)

    def _get_time_formatted(self, time):
        if time:
            return FormatTimeIntervalShortWritten(time, showTo=TIME_CATEGORY_MINUTE)
        return localization.GetByLabel('Tooltips/SkillPlanner/TrainingComplete')

    def _get_background_color(self):
        return COLOR_OMEGA_DARK_BG

    def on_omega_button_click(self, *args):
        uicore.cmd.OpenCloneUpgradeWindow(origin=ORIGIN_SKILLREQ_PANEL)
        if self.on_click_callback:
            self.on_click_callback()


class AlphaTrainingTimeRow(LayoutGridRow):
    default_state = uiconst.UI_NORMAL
    isDragObject = False
    _OMEGA_RESTRICTED_HEIGHT = 30
    _CONTENT_HEIGHT = 80

    def ApplyAttributes(self, attributes):
        super(AlphaTrainingTimeRow, self).ApplyAttributes(attributes)
        self.isOmegaRestricted = attributes.get('isOmegaRestricted', False)
        self.alphaTime = attributes.get('alphaTime', None)
        self.omegaTime = attributes.get('omegaTime', None)
        self.activityText = attributes.get('activityText', '')
        on_click = attributes.get('on_click', None)
        self.outer_container = AlphaTrainingTimeContainer(isOmegaRestricted=self.isOmegaRestricted, alphaTime=self.alphaTime, omegaTime=self.omegaTime, activityText=self.activityText, on_click=on_click)
        self.AddCell(cellObject=self.outer_container, colSpan=self.columns, cellPadding=(0, 10, 0, 0))

    def _get_height(self):
        if self.isOmegaRestricted:
            return self._CONTENT_HEIGHT + self._OMEGA_RESTRICTED_HEIGHT + 5
        return self._CONTENT_HEIGHT

    def _get_background_color(self):
        return COLOR_OMEGA_DARK_BG


class OmegaTrainingTimeContainer(ContainerAutoSize):
    default_name = 'OmegaTrainingCnt'
    default_align = Align.TOTOP
    default_alignMode = Align.TOTOP
    default_bgColor = (0.1, 0.1, 0.1, 0.7)

    def ApplyAttributes(self, attributes):
        super(OmegaTrainingTimeContainer, self).ApplyAttributes(attributes)
        omegaTime = attributes.get('omegaTime', None)
        TextBody(parent=self, align=uiconst.TOTOP, text=localization.GetByLabel('Tooltips/SkillPlanner/OmegaTrainingTime'), color=TextColor.SECONDARY, maxLines=1, padding=(10, 5, 10, 0))
        TextBody(parent=self, align=uiconst.TOTOP, text=FormatTimeIntervalShortWritten(omegaTime, showTo=TIME_CATEGORY_MINUTE), color=TextColor.HIGHLIGHT, padding=(10, 0, 10, 5))


class OmegaTrainingTimeRow(LayoutGridRow):
    default_state = uiconst.UI_NORMAL
    isDragObject = False

    def ApplyAttributes(self, attributes):
        super(OmegaTrainingTimeRow, self).ApplyAttributes(attributes)
        self.omegaTime = attributes.get('omegaTime', None)
        self.content = OmegaTrainingTimeContainer(omegaTime=self.omegaTime)
        self.AddCell(cellObject=self.content, colSpan=self.columns, cellPadding=(0, 10, 0, 0))


def AddSkillActionAndRequirementsForType(grid, typeID, item = None, origin = None):
    skillSvc = sm.GetService('skills')
    missingSkills = skillSvc.GetTopLevelSkillsMissingToUseItem(typeID)
    if not missingSkills:
        return
    allMissingSkills = skillSvc.GetSkillsMissingToUseItemRecursiveList(typeID)
    totalMissingSkillLevels = skillSvc.GetTotalMissingSkillLevelsToUseItem(typeID)
    missingSkillbooks = skillSvc.GetMissingSkillBooksFromList(allMissingSkills)
    AddSkillRequirements(grid, allMissingSkills, missingSkillbooks, totalMissingSkillLevels)
    AddTrainingTimeForType(grid, typeID, item)
    AddSkillAction(grid, typeID, item)


def AddSkillRequirementLabel(grid, allMissingSkillsCount, missingSkillBooksCount, totalMissingSkillLevels):
    labelCnt = ContainerAutoSize(align=uiconst.CENTERLEFT, minWidth=270, height=25, bgColor=(0.2, 0.2, 0.2, 0))
    spriteCnt = Container(parent=labelCnt, align=uiconst.TOLEFT, width=20)
    Sprite(parent=spriteCnt, align=uiconst.TOPLEFT, width=16, height=16, texturePath=eveicon.skill_book, color=TextColor.NORMAL if not missingSkillBooksCount else TextColor.WARNING)
    TextBody(parent=labelCnt, align=uiconst.TOLEFT, text=localization.GetByLabel('Tooltips/SkillPlanner/SkillsAndSkillLevels', numSkills=allMissingSkillsCount, numLevels=totalMissingSkillLevels), color=skillConst.COLOR_SKILL_1)
    if missingSkillBooksCount > 0:
        TextBody(parent=labelCnt, align=uiconst.TOLEFT, text=localization.GetByLabel('Tooltips/SkillPlanner/MissingSkillBooks', numMissingBooks=missingSkillBooksCount), color=TextColor.WARNING)
    grid.AddRow(rowObjects=[labelCnt], cellPadding=(0, 5, 0, 0))


def AddSkillRequirements(grid, allMissingSkills, missingSkillbooks, totalMissingSkillLevels):
    missingSkillBooksCount = len(missingSkillbooks)
    allMissingSkillsCount = len(allMissingSkills)
    AddSkillRequirementLabel(grid, allMissingSkillsCount, missingSkillBooksCount, totalMissingSkillLevels)
    for skillID, level in allMissingSkills:
        grid.AddRow(rowClass=RequiredSkillRow, typeID=skillID, level=level, cellPadding=(0, 8, 0, 0))


def AddTrainingTimeForType(grid, typeID, item = None, on_click = None):
    isOmega = sm.GetService('cloneGradeSvc').IsOmega()
    isOmegaRestricted = ItemObject(typeID, item).NeedsOmegaUpgrade()
    totalTime = long(sm.GetService('skills').GetSkillTrainingTimeLeftToUseType(typeID, includeBoosters=False))
    if isOmega and totalTime > 0:
        AddTrainingTime(grid, isOmega, isOmegaRestricted, trainingTime=totalTime, on_click=on_click)
    elif totalTime > 0 or isOmegaRestricted:
        AddTrainingTime(grid, isOmega, isOmegaRestricted, trainingTime=totalTime, activityText=GetActivityTextForType(typeID), on_click=on_click)


def AddTrainingTime(grid, isOmega, isOmegaRestricted, trainingTime = None, activityText = None, minWidth = 380, on_click = None):
    if isOmega:
        grid.AddRow(rowClass=OmegaTrainingTimeRow, isOmega=True, omegaTime=trainingTime)
        return
    if trainingTime > 0:
        grid.AddRow(rowClass=AlphaTrainingTimeRow, isOmegaRestricted=isOmegaRestricted, alphaTime=trainingTime, omegaTime=trainingTime / 2, activityText=activityText, on_click=on_click)
    elif isOmegaRestricted:
        grid.AddRow(rowClass=AlphaTrainingTimeRow, isOmegaRestricted=isOmegaRestricted, alphaTime=None, omegaTime=None, activityText=activityText, on_click=on_click)
    grid.AddCell(Container(align=uiconst.CENTERTOP, width=minWidth), colSpan=grid.columns)


def AddSkillAction(grid, typeID, item = None, on_click_callback = None):
    itemObject = ItemObject(typeID, item)
    if itemObject.NeedsOmegaUpgrade():
        return
    if not sm.GetService('skills').IsSkillRequirementMet(typeID):
        btnGroup = SkillActionContainer(align=uiconst.TOTOP, typeID=typeID, item=item, on_click=on_click_callback)
        grid.AddCell(cellObject=btnGroup, colSpan=grid.columns, cellPadding=(0, 10, 0, 0))


def AddSkillActionForList(grid, requiredSkills, missingSkills = None, on_click_callback = None, minWidth = None, skillPlanName = None):
    btnGroup = SkillActionContainer(align=uiconst.TOTOP, requiredSkills=requiredSkills, missingSkills=missingSkills, on_click=on_click_callback, skillPlanName=skillPlanName)
    grid.AddCell(cellObject=btnGroup, colSpan=grid.columns, cellPadding=(0, 10, 0, 0))
    if minWidth:
        grid.AddCell(Container(align=uiconst.CENTERTOP, width=minWidth), colSpan=grid.columns)


def GetActivityTextForType(typeID):
    if evetypes.GetCategoryID(typeID) == const.categoryShip:
        return localization.GetByLabel('Tooltips/SkillPlanner/ActivityFlyShip')
    if evetypes.GetCategoryID(typeID) == const.categorySkill:
        return localization.GetByLabel('Tooltips/SkillPlanner/ActivityTrainSkill')
    return localization.GetByLabel('Tooltips/SkillPlanner/ActivityUseModule')
