#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\infoBubble.py
import log
import carbonui.const as uiconst
import eveicon
import evelink.client
import evetypes
import inventorycommon.typeHelpers
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.util.format import IntToRoman
from carbonui import Density, TextColor, TextBody, PickState
from carbonui.control.button import Button
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.layoutGrid import LayoutGrid, LayoutGridRow
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.color import Color
from characterdata.factions import get_faction_name
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, EveLabelMedium, Label
from eve.client.script.ui.control.skillBar.skillLevel import SkillLevel
from eve.client.script.ui.shared.cloneGrade import ORIGIN_SHIPTREE
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skill_requirement import AddTrainingTime, AddSkillActionForList
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.pointerPanel import FrameWithPointer
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from eve.client.script.ui.shared.shipTree.shipTreeConst import COLOR_TEXT
from eve.client.script.ui.shared.traits import TraitsContainer, TraitAttributeIcon
from eve.common.script.util.eveFormat import FmtISKAndRound
from eveservices.menu import GetMenuService
import expertSystems.client
from localization import GetByLabel, GetByMessageID
from utillib import KeyVal

class InfoBubble(Container):
    default_name = 'InfoBubble'
    default_align = uiconst.TOPLEFT
    default_state = uiconst.UI_NORMAL
    default_width = 350
    default_height = 200
    default_idx = 0
    default_topOffset = 0
    default_opacity = 0.0

    def __init__(self, **kw):
        Container.__init__(self, **kw)
        self.StartupInfoBubble()

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.parentObj = attributes.parentObj
        self.topOffset = attributes.Get('topOffset', self.default_topOffset)
        self.__isClosing = False
        self.mainCont = Container(name='mainCont', parent=self, padding=20)
        self.bgFrame = Container(name='bgFrame', parent=self, state=uiconst.UI_DISABLED)
        self.pointerFrame = FrameWithPointer(name='pointerFrame', parent=self.bgFrame, align=uiconst.TOALL)
        self.topContainer = ContainerAutoSize(name='topContainer', parent=self.mainCont, align=uiconst.TOTOP, callback=self.OnMainContentSizeChanged)
        self.iconCont = Container(name='iconCont', parent=self.topContainer, align=uiconst.TOPLEFT, width=80, height=80, left=0, top=0)
        self.topRightCont = ContainerAutoSize(name='topRightCont', align=uiconst.TOPLEFT, left=90, width=self.width - 115, parent=self.topContainer, alignMode=uiconst.TOTOP)
        self.caption = EveCaptionMedium(parent=self.topRightCont, align=uiconst.TOTOP)
        self.attributeCont = ContainerAutoSize(name='attributeCont', parent=self.topRightCont, align=uiconst.TOTOP, padTop=5)
        self.mainContent = ContainerAutoSize(name='mainContent', parent=self.mainCont, align=uiconst.TOTOP, callback=self.OnMainContentSizeChanged, padTop=5)

    def StartupInfoBubble(self):
        self.mainContent.SetSizeAutomatically()
        self.OnMainContentSizeChanged()
        self.SetLeftAndTop()

    def SetLeftAndTop(self):
        left, top, width, height = self.parentObj.GetAbsolute()
        if left > self.width:
            self.left = left - self.width - 20
            self.pointerFrame.UpdatePointerPosition(uiconst.POINT_RIGHT_2)
        else:
            self.left = left + width + 20
            self.pointerFrame.UpdatePointerPosition(uiconst.POINT_LEFT_2)
        self.top = top - (self.height - height) / 2

    def OnMainContentSizeChanged(self, *args):
        self.height = self.topContainer.height + self.mainContent.height + 45
        self.SetLeftAndTop()

    def AnimShow(self):
        uicore.animations.FadeIn(self, duration=0.15)
        for i, attrIcon in enumerate(self.attributeCont.children):
            timeOffset = i * 0.05
            uicore.animations.FadeTo(attrIcon, 0.0, 1.0, duration=0.3, timeOffset=timeOffset)
            uicore.animations.MorphScalar(attrIcon, 'left', attrIcon.left + 5, attrIcon.left, duration=0.1, timeOffset=timeOffset)

    def Close(self):
        if self.__isClosing:
            return
        self.__isClosing = True
        uicore.animations.FadeOut(self, duration=0.15, callback=self._Close)

    def _Close(self):
        Container.Close(self)

    def ConstructElements(self, attributeIDsDict):
        attributeIDs = [ x[1] for x in sorted(attributeIDsDict.items(), key=lambda data: int(data[0])) ]
        numInRow = 7
        size = InfoBubbleAttributeIcon.default_width
        for i, attributeID in enumerate(attributeIDs):
            left = i % numInRow * (size + 1)
            top = i / numInRow * (size + 1)
            InfoBubbleAttributeIcon(parent=self.attributeCont, align=uiconst.TOPLEFT, attributeID=attributeID, left=left, top=top)


class InfoBubbleShipGroup(InfoBubble):
    default_name = 'InfoBubbleShipGroup'
    default_topOffset = 0

    def ApplyAttributes(self, attributes):
        self.default_width = 420
        InfoBubble.ApplyAttributes(self, attributes)
        self.node = attributes.node
        factionName = ''
        factionID = attributes.get('factionID', None)
        if factionID:
            factionName = get_faction_name(factionID)
        infoBubbleGroup = cfg.infoBubbleGroups[self.node.shipGroupID]
        self.caption.text = GetByMessageID(infoBubbleGroup['nameID'])
        Frame(bgParent=self.iconCont, texturePath='res:/UI/Texture/Classes/ShipTree/Groups/groupIconFrame.png', opacity=0.15)
        self.icon = Sprite(name='icon', parent=self.iconCont, pos=(0, 0, 64, 64), align=uiconst.CENTER, texturePath=infoBubbleGroup['iconLarge'])
        self.ConstructElements(infoBubbleGroup['elements'])
        Label(parent=self.mainContent, align=uiconst.TOTOP, text=GetByMessageID(infoBubbleGroup['descriptionID']), padTop=5)
        skillSvc = sm.GetService('skills')
        if self.node.IsLockedWithoutExpertSystem():
            layoutGrid = LayoutGrid(parent=self.mainContent, align=uiconst.TOTOP, padTop=12)
            caption = InfoBubbleCaption(align=uiconst.TOPLEFT, text=GetByLabel('UI/ShipTree/SkillsRequiredToUnlock'), padding=(0, 12, 0, 2), width=self.width - 40)
            requiredSkills = self.node.GetRequiredSkillsSorted()
            cloneGradeService = sm.GetService('cloneGradeSvc')
            isOmegaRestricted = False
            layoutGrid.AddCell(caption, colSpan=2)
            for typeID, level in requiredSkills:
                if not isOmegaRestricted:
                    isOmegaRestricted = cloneGradeService.IsRequirementsRestricted(typeID)
                    if not isOmegaRestricted:
                        isOmegaRestricted = cloneGradeService.IsSkillLevelRestricted(typeID, level)
                layoutGrid.AddRow(rowClass=SkillEntry, typeID=typeID, level=level)

            isOmega = sm.GetService('cloneGradeSvc').IsOmega()
            trainingTime = self.node.GetTimeToUnlock()
            AddTrainingTime(layoutGrid, isOmega=isOmega, isOmegaRestricted=isOmegaRestricted, trainingTime=trainingTime, activityText=GetByLabel('Tooltips/SkillPlanner/ActivityUnlockShipGroup'), minWidth=370)
            isOmegaLocked = isOmegaRestricted and not isOmega
            if not isOmegaLocked:
                skillPlanName = '%s %s' % (factionName, GetByMessageID(infoBubbleGroup['nameID']))
                allRequiredSkills = skillSvc.GetSkillsMissingToUseAllSkillsFromListRecursiveAsList(requiredSkills)
                missingSkills = skillSvc.GetMissingSkillBooksFromList(allRequiredSkills)
                AddSkillActionForList(layoutGrid, allRequiredSkills, missingSkills, skillPlanName=skillPlanName, on_click_callback=self.Close)
        else:
            bonusSkills = self.node.GetBonusSkillsSorted()
            if bonusSkills:
                layoutGrid = LayoutGrid(parent=self.mainContent, align=uiconst.TOTOP)
                caption = InfoBubbleCaption(align=uiconst.TOPLEFT, text=GetByLabel('UI/ShipTree/ShipBonusSkills'), padding=(0, 12, 0, 2), width=self.width - 40)
                layoutGrid.AddCell(caption, colSpan=2)
                indentForButton = False
                for typeID, level in bonusSkills:
                    if skillSvc.GetSkill(typeID).trainedSkillLevel < 5:
                        indentForButton = True

                for typeID, level in bonusSkills:
                    showButton = indentForButton
                    if showButton and skillSvc.GetSkill(typeID).trainedSkillLevel >= 5:
                        showButton = False
                    layoutGrid.AddRow(rowClass=SkillEntry, typeID=typeID, level=level, showLevel=False, showButton=showButton, indentForButton=indentForButton)

                layoutGrid.AddRow(rowClass=BonusSkillInfoRow, plural=len(bonusSkills) > 1)
        self.AnimShow()


class BonusSkillInfoRow(LayoutGridRow):
    default_name = 'BonuSkillInfoRow'

    def ApplyAttributes(self, attributes):
        super(BonusSkillInfoRow, self).ApplyAttributes(attributes)
        plural = attributes.get('plural', False)
        mainCont = ContainerAutoSize(align=uiconst.TOTOP, padding=(5, 10, 5, 5))
        icon = Sprite(parent=mainCont, align=uiconst.CENTERLEFT, color=eveColor.AURA_PURPLE, texturePath='res:/UI/Texture/classes/careerPortal/aura/aura_icon_16x16.png', width=16, height=16, left=8)
        if plural:
            labelText = GetByLabel('UI/ShipTree/ShipBonusSkillsInfoPlural')
        else:
            labelText = GetByLabel('UI/ShipTree/ShipBonusSkillsInfoSingular')
        label = TextBody(parent=mainCont, align=uiconst.CENTERLEFT, width=280, text=labelText, color=eveColor.AURA_PURPLE, left=35)
        Container(bgParent=mainCont, bgColor=eveColor.AURA_PURPLE, opacity=0.2, padding=-5)
        self.AddCell(mainCont, colSpan=self.columns)


class AddSkillToQueueButton(Button):

    def ApplyAttributes(self, attributes):
        self.default_func = self.ClickFunc
        super(AddSkillToQueueButton, self).ApplyAttributes(attributes)
        self._callback = attributes.get('callback', None)
        self.skillID = attributes.skillID

    def ClickFunc(self, *args):
        skillQueueSvc = sm.GetService('skillqueue')
        skillQueueSvc.AddSkillsToQueue(skills=[(self.skillID, None)], ignoreAlreadyPresent=True)
        self.UpdateState()
        if self._callback:
            self._callback()

    def UpdateState(self):
        skillQueueSvc = sm.GetService('skillqueue')
        skillLevelInQueue = skillQueueSvc.GetSkillLevelsInQueue().get(self.skillID, 0)
        if skillLevelInQueue >= 5:
            self.Disable()


class SkillEntry(LayoutGridRow):
    default_name = 'SkillEntryLayoutGridRow'
    default_state = uiconst.UI_NORMAL
    default_showLevel = True
    isDragObject = True
    default_skillBarPadding = (24, 8, 8, 8)
    default_textPadding = (0, 3, 0, 3)

    def ApplyAttributes(self, attributes):
        LayoutGridRow.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.level = attributes.level
        self.showLevel = attributes.Get('showLevel', self.default_showLevel)
        self.skillBarPadding = attributes.Get('skillBarPadding', self.default_skillBarPadding)
        self.textPadding = attributes.Get('textPadding', self.default_textPadding)
        self.indentForButton = attributes.Get('indentForButton', False)
        self.showTrainButton = attributes.Get('showButton', False)
        self.addToQueueButton = None
        self._hiliteFill = None
        leftCont = ContainerAutoSize(padding=self.textPadding, align=uiconst.CENTERLEFT)
        self.label = Label(name='label', parent=leftCont, align=uiconst.CENTERLEFT)
        self.AddCell(leftCont, cellPadding=self.cellPadding)
        skillQueueSvc = sm.GetService('skillqueue')
        skillLevelInQueue = skillQueueSvc.GetSkillLevelsInQueue().get(self.typeID, 0)
        if skillLevelInQueue >= 5:
            self.showTrainButton = self.indentForButton = False
        skillBarPadding = (0, 0, 0, 0) if self.showTrainButton else self.textPadding
        skillBarContainer = ContainerAutoSize(name='skillBarCont', padding=skillBarPadding, align=uiconst.CENTERRIGHT)
        self.AddCell(skillBarContainer, cellPadding=self.skillBarPadding)
        self.buttonContainer = Container(parent=skillBarContainer, align=uiconst.CENTERRIGHT, height=18, width=20)
        self.omegaIconButton = ButtonIcon(name='omegaButton', parent=self.buttonContainer, align=uiconst.CENTER, density=Density.COMPACT, texturePath=eveicon.omega, iconSize=16, func=self._OnOmegaButton)
        self.addToQueueButton = AddSkillToQueueButton(name='addToQButton', skillID=self.typeID, parent=self.buttonContainer, align=uiconst.CENTER, density=Density.COMPACT, texturePath=eveicon.add, callback=self.UpdateState)
        skillBarIndent = 30 if self.indentForButton else 0
        self.skillBar = SkillBar(parent=skillBarContainer, align=uiconst.CENTERRIGHT, state=uiconst.UI_DISABLED, skillID=self.typeID, requiredLevel=self.level if self.showLevel else None, pos=(skillBarIndent,
         0,
         SkillBar.default_width,
         SkillBar.default_height))
        self.icon = Sprite(name='icon', parent=skillBarContainer, align=uiconst.CENTERRIGHT, pos=(self.skillBar.width + 5,
         0,
         16,
         16), state=uiconst.UI_NORMAL if self.showLevel else uiconst.UI_HIDDEN)
        self.UpdateState()

    def GetMyLevel(self):
        return sm.GetService('skills').GetMyLevelIncludingLapsed(self.typeID)

    def UpdateState(self):
        myLevel = self.GetMyLevel()
        if self.showTrainButton:
            self.buttonContainer.Show()
            cloneGradeSvc = sm.GetService('cloneGradeSvc')
            skillQueueSvc = sm.GetService('skillqueue')
            skillLevelInQueue = skillQueueSvc.GetSkillLevelsInQueue().get(self.typeID, 0)
            if not cloneGradeSvc.IsOmega() and cloneGradeSvc.IsSkillLevelRestricted(self.typeID, max(myLevel + 1, skillLevelInQueue + 1)):
                self.omegaIconButton.Show()
                self.addToQueueButton.Hide()
            else:
                self.omegaIconButton.Hide()
                self.addToQueueButton.Show()
        else:
            self.buttonContainer.Hide()
        if myLevel and myLevel >= 5:
            if self.addToQueueButton:
                self.addToQueueButton.Hide()
        if self.skillBar:
            self.skillBar.Update()
        if self.showLevel:
            if myLevel and self.level <= myLevel:
                color = TextColor.SECONDARY
                levelColor = TextColor.SECONDARY
            else:
                color = TextColor.NORMAL
                levelColor = TextColor.NORMAL
            text = GetByLabel('UI/InfoWindow/RequiredSkillNameAndLevel', skill=self.typeID, level=IntToRoman(self.level), levelColor=Color(*levelColor).GetHex())
            self.label.SetRGBA(*color)
            self.label.left = 10
            self.icon.state = uiconst.UI_NORMAL
            if myLevel and myLevel >= self.level:
                self.icon.SetTexturePath('res:/ui/Texture/classes/Skills/SkillRequirementMet.png')
                self.icon.hint = GetByLabel('UI/InfoWindow/SkillTrainedToRequiredLevel')
                self.icon.SetRGBA(1.0, 1.0, 1.0, 0.5)
            else:
                self.icon.SetRGBA(*TextColor.WARNING)
                if not sm.GetService('skills').HasSkill(self.typeID):
                    self.icon.SetTexturePath(eveicon.skill_book)
                    self.icon.hint = GetByLabel('UI/SkillQueue/SkillBookMissing')
                else:
                    self.icon.SetTexturePath('res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png')
                    self.icon.hint = GetByLabel('UI/InfoWindow/SkillNotTrainedToRequiredLevel')
        else:
            text = evetypes.GetName(self.typeID)
            self.label.SetRGBA(*TextColor.NORMAL)
            self.label.left = 10
            self.icon.state = uiconst.UI_HIDDEN
        self.label.SetText(text)

    def GetMenu(self):
        return GetMenuService().GetMenuForSkill(self.typeID)

    def OnClick(self):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        sm.GetService('info').ShowInfo(self.typeID)

    def OnMouseEnter(self, *args):
        self.ShowHilite()
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def GetDragData(self):
        ret = KeyVal(__guid__='uicls.GenericDraggableForTypeID', typeID=self.typeID, label=evetypes.GetName(self.typeID))
        return (ret,)

    def ConstructHiliteFill(self):
        if not self._hiliteFill:
            self._hiliteFill = ListEntryUnderlay(bgParent=self)

    def ShowHilite(self, animate = True):
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(True, animate)

    def HideHilite(self, animate = True):
        self.ConstructHiliteFill()
        self._hiliteFill.set_hovered(False, animate)

    def OnMouseExit(self, *args):
        self.HideHilite()

    def _OnOmegaButton(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        uicore.cmd.OpenCloneUpgradeWindow(ORIGIN_SHIPTREE, self.typeID)


class ExpertSystemIcon(Sprite):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        self.infoSvc = sm.GetService('info')
        Sprite.ApplyAttributes(self, attributes)
        self.shipID = attributes.get('shipID', None)

    def OnClick(self, *args):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.OpenExpertSystems()


class ExpertSystemInfoRow(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    default_padding = 10

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        expertSystemTypeID = attributes.expertSystemTypeID
        link = evelink.type_link(expertSystemTypeID)
        EveLabelMedium(parent=self, align=uiconst.TOPLEFT, text=link, maxWidth=150, state=uiconst.UI_NORMAL)
        expertSystems.ViewExpertSystemInStoreButton(parent=self, align=uiconst.CENTERRIGHT, left=20, expert_system_type_id=expertSystemTypeID)


class InfoBubbleShip(InfoBubble):
    default_name = 'InfoBubbleShip'
    default_topOffset = 20

    def ApplyAttributes(self, attributes):
        InfoBubble.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.expertSystems = attributes.expertSystems
        self.caption.text = evetypes.GetName(self.typeID)
        self.icon = ItemIcon(name='icon', parent=self.iconCont, pos=(0, 0, 80, 80), typeID=self.typeID, cursor=uiconst.UICURSOR_MAGNIFIER)
        self.icon.OnClick = self._OnIconClick
        if self.typeID in cfg.infoBubbleTypeElements:
            self.ConstructElements(cfg.infoBubbleTypeElements[self.typeID])
        try:
            TraitsContainer(parent=self.mainContent, typeID=self.typeID)
        except StandardError:
            log.LogException()
            self.Close()
            return

        if self.expertSystems:
            expertSystemsInfoCont = ContainerAutoSize(parent=self.mainContent, align=uiconst.TOTOP, padTop=20)
            expertSystemSpriteLabelCont = ContainerAutoSize(parent=expertSystemsInfoCont, align=uiconst.TOTOP, alignMode=uiconst.TOPLEFT)
            expertSystemIconSize = 24
            ExpertSystemIcon(parent=expertSystemSpriteLabelCont, align=uiconst.TOPLEFT, texturePath='res:/UI/Texture/classes/ExpertSYstems/logo_simple_24.png', width=expertSystemIconSize, height=expertSystemIconSize)
            EveLabelMedium(text=GetByLabel('UI/ShipTree/ExpertSystemsCanHelpFlyShip'), align=uiconst.CENTERLEFT, parent=expertSystemSpriteLabelCont, padLeft=expertSystemIconSize + 4)
            for esTypeID in self.expertSystems:
                ExpertSystemInfoRow(parent=expertSystemsInfoCont, align=uiconst.TOTOP, expertSystemTypeID=esTypeID)

        price = inventorycommon.typeHelpers.GetAveragePrice(self.typeID) or 0
        text = GetByLabel('UI/Inventory/EstIskPrice', iskString=FmtISKAndRound(price, False))
        Label(parent=self.topRightCont, text=text, align=uiconst.TOTOP, padTop=7)
        uicore.animations.FadeTo(self.icon, 1.5, 1.0, duration=0.6)
        self.AnimShow()

    def _AtLeastOneExpertSystemBenefitsPlayer(self, expertSystemIDs):
        for expertSystemID in expertSystemIDs:
            if expertSystems.expert_system_benefits_player(expertSystemID):
                return True

        return False

    def AnimShow(self):
        InfoBubble.AnimShow(self)
        for i, obj in enumerate(self.mainContent.children):
            timeOffset = i * 0.015
            uicore.animations.FadeTo(obj, 0.0, 1.0, duration=0.3, timeOffset=timeOffset)

    def SetLeftAndTop(self):
        left, top, width, height = self.parentObj.GetAbsolute()
        self.left = left - (self.width - width) / 2
        if top > self.height:
            self.top = top - self.height - self.topOffset
            self.pointerFrame.UpdatePointerPosition(uiconst.POINT_BOTTOM_2)
        else:
            self.top = top + height + 2 + self.topOffset
            self.pointerFrame.UpdatePointerPosition(uiconst.POINT_TOP_2)

    def _OnIconClick(self, *args, **kwargs):
        self.Close()
        sm.GetService('info').ShowInfo(self.typeID)


class InfoBubbleCaption(Label):
    default_color = COLOR_TEXT
    default_bold = True
    default_padTop = 8


class InfoBubbleAttributeIcon(TraitAttributeIcon):
    default_name = 'InfoBubbleAttributeIcon'
    default_padRight = 1
    default_opacity = 0.0
