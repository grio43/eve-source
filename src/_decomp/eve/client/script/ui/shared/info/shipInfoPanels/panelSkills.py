#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelSkills.py
import evetypes
import expertSystems.client
import eveicon
import localization
import threadutils
import uthread2
from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
from eve.common.script.sys import idCheckers
from eve.common.lib import appConst
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import IntToRoman
from carbon.common.script.util.commonutils import StripTags
from carbonui.services.setting import UserSettingBool
from carbonui import Align, TextHeadline, TextDetail, TextColor, TextBody, uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.control.contextMenu.menuData import MenuData
from carbonui.control.checkbox import Checkbox
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.infoIcon import CheckMarkGlyphIcon
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.control.toggleButtonGroup import ToggleButtonGroup
from eve.client.script.ui.control.toggleButtonGroupButton import ToggleButtonGroupButtonIcon
from eve.client.script.ui.control.toggleButtonUnderlay import ToggleButtonUnderlay, FrameType
from eve.client.script.ui.shared.info.shipInfoCollapsibleGroup import _CollapsibleGroupBase
from eve.client.script.ui.shared.info.shipInfoConst import UNLOCKED_ICON, MASTERY_ICONS, ANGLE_SKILLS, TAB_SKILLS, get_mastery_level_icon_and_message
from eve.client.script.ui.shared.info.shipInfoListEntries import _ListEntryBase
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from eve.client.script.ui.shared.tooltip.itemObject import ItemObject
from eve.client.script.ui.shared.tooltip.skillBtns import SkillActionContainer
from eve.client.script.ui.shared.tooltip.skill_requirement import OmegaTrainingTimeContainer, AlphaTrainingTimeContainer, GetActivityTextForType
from menu import MenuLabel
from utillib import KeyVal
from skills.client.skillController import SkillController
_filter_acquired_setting = UserSettingBool('masteries_filter_acquired', False)
_collapsed_certificates = set()

class PanelSkills(PanelBase):
    __notifyevents__ = ['OnSkillsChanged']
    _selectedTabID = None

    def ApplyAttributes(self, attributes):
        super(PanelSkills, self).ApplyAttributes(attributes)
        self._load_task = None
        self.LoadAssociatedExpertSystems()
        self.LoadCurrentMastery()
        self.rightNav.SelectByID(0)
        _filter_acquired_setting.on_change.connect(self._filter_acquired_setting_changed)

    def Close(self):
        super(PanelSkills, self).Close()
        _filter_acquired_setting.on_change.disconnect(self._filter_acquired_setting_changed)

    def _enable_minimized_view(self):
        self.mastery_level_cont_minimized.SetParent(self.minimizedCont, idx=0)
        self.minimizedNav.SetParent(self.minimizedCont, idx=1)
        self._filter_container.SetParent(self.minimizedCont, idx=2)
        self.training_time_cont.SetParent(self.minimizedCont, idx=3)
        self.list_cont.SetParent(self.content_scroll_minimized)

    def _enable_expanded_view(self):
        self.training_time_cont.SetParent(self.rightCont)
        self._filter_container.SetParent(self.rightCont)
        self.list_cont.SetParent(self.scroll_cont)
        self.scroll_cont.SetParent(self.rightCont)

    def _construct_content_minimized(self):
        self.mastery_level_cont_minimized = Container(name='mastery_level_cont_minimized', parent=self.minimizedCont, align=Align.TOTOP, height=32, padBottom=4)
        self.mastery_level_icon_minimized = Sprite(name='mastery_level_sprite', parent=self.mastery_level_cont_minimized, align=Align.CENTERLEFT, width=40, height=32, padLeft=8, texturePath=eveicon.mastery_locked, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.1, state=uiconst.UI_DISABLED)
        self.mastery_level_label_minimized = TextBody(name='masteryLevelLabel', parent=self.mastery_level_cont_minimized, align=Align.CENTERLEFT, padLeft=48, text='You have mastery level 5', state=uiconst.UI_DISABLED)

    def _construct_content(self):
        uthread2.Yield()
        self.right_nav_cont = Container(name='rightNavCont', parent=self.rightCont, align=Align.TOTOP, height=64, padBottom=8)
        self.training_time_cont = ContainerAutoSize(name='trainingTimeCont', parent=self.rightCont, align=Align.TOBOTTOM, padTop=8)
        self._filter_container = Container(parent=self.rightCont, align=Align.TOTOP, height=24, padBottom=4)
        ButtonIcon(parent=self._filter_container, align=Align.TORIGHT, texturePath=eveicon.collapse, hint=localization.GetByLabel('UI/Common/Buttons/CollapseAll'), func=self._collapse_all, opacity=TextColor.NORMAL.opacity)
        checkbox_container = Container(parent=self._filter_container, align=Align.TOALL, clipChildren=True)
        Checkbox(parent=checkbox_container, align=Align.CENTERLEFT, setting=_filter_acquired_setting, text=localization.GetByLabel('UI/InfoWindow/MasteryFilterAcquired'))
        self.scroll_cont = ScrollContainer(name='scrollCont', parent=self.rightCont, align=Align.TOALL)
        self.list_cont = ContainerAutoSize(name='listCont', parent=self.scroll_cont, align=Align.TOTOP)
        self._construct_navigation()
        self._construct_expert_system()
        self._construct_mastery()

    def _construct_navigation(self):
        self.rightNav = ToggleButtonGroup(name='rightNav', parent=self.right_nav_cont, align=uiconst.TOTOP, callback=self.OnNavButtonPressed, height=64, btnClass=SkillPanelToggleButtonLarge)
        self.minimizedNav = ToggleButtonGroup(name='minimizedNav', parent=self.minimizedCont, align=uiconst.TOTOP, idx=0, callback=self.OnNavButtonPressed, height=42, btnClass=SkillPanelToggleButtonSmall, padBottom=8)
        self.nav_buttons = {}
        self.nav_buttons[0] = self.rightNav.AddButton(0, iconPath=UNLOCKED_ICON, iconSize=48, hint=localization.GetByLabel('UI/InfoWindow/TabNames/Requirements'), getMenu=self._get_tab_group_menu)
        self.nav_buttons_minimized = {}
        self.nav_buttons_minimized[0] = self.minimizedNav.AddButton(0, iconPath=UNLOCKED_ICON, iconSize=32, hint=localization.GetByLabel('UI/InfoWindow/TabNames/Requirements'), getMenu=self._get_tab_group_menu)
        for level in range(6):
            if level > 0:
                self.nav_buttons[level] = self.rightNav.AddButton(level, iconPath=MASTERY_ICONS[level], iconSize=48, hint=localization.GetByLabel('UI/InfoWindow/MasteryLevelButtonHint', level=level), getMenu=self._get_tab_group_menu)
                self.nav_buttons_minimized[level] = self.minimizedNav.AddButton(level, iconPath=MASTERY_ICONS[level], iconSize=32, hint=localization.GetByLabel('UI/InfoWindow/MasteryLevelButtonHint', level=level), getMenu=self._get_tab_group_menu)

    def OnNavButtonPressed(self, btnID, oldBtnID):
        self._selectedTabID = btnID
        self.LoadPage()
        self.rightNav.SetSelected(btnID)
        self.minimizedNav.SetSelected(btnID)

    def _get_tab_group_menu(self, btnID):
        if not session.role & ROLE_GML:
            return None
        m = MenuData()
        if btnID == 0:
            m.AddEntry('GM: Give all skills', lambda : _qa_give_required_skills(self.typeID))
        else:
            m.AddEntry('GM: Give all skills', lambda : _qa_give_all_cert_skills(self.typeID, btnID))
        return m

    _MASTERY_CONT_HEIGHT = 140
    _OMEGA_MASTERY_CONT_HEIGHT = 160

    def _construct_mastery(self):
        self.mastery_level_cont = Container(name='masteryLevelCont', parent=self.leftCont, align=Align.TOBOTTOM, height=self._MASTERY_CONT_HEIGHT, padding=(16, 0, 16, 24), state=uiconst.UI_DISABLED)
        self.mastery_level_label = TextHeadline(name='masteryLevelLabel', parent=self.mastery_level_cont, align=Align.CENTERBOTTOM, text='', state=uiconst.UI_DISABLED)
        self.mastery_level_icon = Sprite(name='masteryLevelSprite', parent=self.mastery_level_cont, align=Align.CENTERTOP, width=128, height=128, texturePath=eveicon.mastery_locked, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.1, state=uiconst.UI_DISABLED)

    def _construct_expert_system(self):
        self.expert_system_cont = Container(name='expertSystemCont', parent=self.leftCont, align=Align.TOBOTTOM, height=68, padding=(16, 0, 16, 24))
        TextDetail(name='expertSystemInfoLabel', parent=self.expert_system_cont, align=Align.TOPLEFT, text=localization.GetByLabel('UI/InfoWindow/ExpertSystemAvailable'), color=TextColor.SECONDARY)
        expert_system_subcont = Container(name='expertSystemSubCont', parent=self.expert_system_cont, align=Align.TOBOTTOM, state=uiconst.UI_PICKCHILDREN, height=46)
        expertSystemSprite = Sprite(name='expertSystemIcon', parent=expert_system_subcont, align=Align.CENTERLEFT, state=uiconst.UI_NORMAL, width=46, height=46, texturePath='res:/UI/Texture/Icons/Inventory/ExpertSystems/CoreShipSystems.png')
        splitCont = Container(parent=expert_system_subcont, align=Align.TOALL, padLeft=60, state=uiconst.UI_PICKCHILDREN)
        self.expert_system_label = TextBody(name='expertSystemLabel', parent=Container(parent=splitCont, align=Align.TOTOP_PROP, height=0.5, clipChildren=True), align=Align.BOTTOMLEFT, text=None, autoFadeSides=16, state=uiconst.UI_NORMAL)
        self.expert_system_value_label = TextDetail(name='expertSystemValueLabel', parent=Container(parent=splitCont, align=Align.TOBOTTOM_PROP, height=0.5, clipChildren=True), align=Align.TOPLEFT, color=TextColor.SECONDARY, text=localization.GetByLabel('UI/InfoWindow/ExpertSystemUnlocksShips', num=3), state=uiconst.UI_DISABLED, autoFadeSides=16)
        expertSystemSprite.OnClick = self.on_expert_system_clicked
        self.expert_system_label.OnClick = self.on_expert_system_clicked

    def on_expert_system_clicked(self, *args):
        from eve.client.script.ui.shared.neocom.characterSheetWindow import CharacterSheetWindow
        CharacterSheetWindow.OpenExpertSystems()

    def LoadRequirements(self):
        self.list_cont.Flush()
        requiredSkills = sm.GetService('skills').GetRequiredSkills(self.typeID)
        for typeID, requiredLevel in requiredSkills.iteritems():
            self._DrawSkillTree(typeID, requiredLevel, self.list_cont, 1, 6)

    def _DrawSkillTree(self, skillID, requiredLvl, parent, indentIdx, indentStep):
        ListEntrySkill(skillID=skillID, requiredLevel=requiredLvl, parent=parent, indent=indentIdx * indentStep)
        for prereqId, lvl in sm.GetService('skills').GetRequiredSkills(skillID).iteritems():
            if prereqId == skillID:
                continue
            self._DrawSkillTree(prereqId, lvl, parent, indentIdx + 1, indentStep)

    @threadutils.threaded
    def LoadPage(self):
        pageID = self._selectedTabID
        self.LoadTrainingTimeAndSkillActions(pageID)
        if pageID == 0:
            self._filter_container.display = False
            self.LoadRequirements()
        else:
            self._filter_container.display = True
            self.LoadMasteryLevel(pageID)

    def LoadMasteryLevel(self, level):
        self.list_cont.Flush()
        certificates = [ (cert.GetName(), cert) for cert in sm.GetService('certificates').GetCertificatesForShipByMasteryLevel(self.typeID, level) ]
        for name, certificate in sorted(certificates, key=lambda cert: cert[0]):
            uthread2.Yield()
            if level != self._selectedTabID:
                break
            self.LoadCertificate(certificate, level, name)

    def LoadCertificate(self, certificate, level, name):
        certificateCont = CollapsibleGroupCertificate(name=name, parent=self.list_cont, align=Align.TOTOP, groupIcon=eveicon.skill_book, groupName=name, padBottom=4, certificate=certificate, level=level)
        collapsed = (certificate.certificateID, level) in _collapsed_certificates or certificate.GetLevel() >= level
        if collapsed:
            certificateCont.SetCollapsed(True)
        skillSvc = sm.GetService('skills')
        filter_acquired = _filter_acquired_setting.get()
        for skillID, level in certificate.SkillsByTypeAndLevel(level):
            if filter_acquired:
                skill = skillSvc.GetSkill(skillID)
                if skill and skill.trainedSkillLevel >= level:
                    continue
            ListEntrySkill(skillID=skillID, requiredLevel=level, parent=certificateCont.mainCont, indent=8, hint=skillSvc.GetSkillToolTip(skillID, level))

    def LoadCurrentMastery(self):
        certSvc = sm.GetService('certificates')
        masteryLevel = certSvc.GetCurrCharMasteryLevel(self.typeID)
        canFly = sm.GetService('skills').IsSkillRequirementMet(self.typeID)
        texturePath, message, onClick = get_mastery_level_icon_and_message(self.typeID)
        self.mastery_level_icon.SetTexturePath(texturePath)
        self.mastery_level_icon.OnClick = onClick
        self.mastery_level_label.SetText(message)
        self.mastery_level_icon_minimized.SetTexturePath(texturePath)
        self.mastery_level_icon_minimized.OnClick = onClick
        self.mastery_level_label_minimized.SetText(message)
        if not canFly:
            for lvl, btn in self.nav_buttons.iteritems():
                btn.set_unlocked(False)

            for lvl, btn in self.nav_buttons_minimized.iteritems():
                btn.set_unlocked(False)

        else:
            for lvl, btn in self.nav_buttons.iteritems():
                btn.set_unlocked(masteryLevel >= lvl)

            for lvl, btn in self.nav_buttons_minimized.iteritems():
                btn.set_unlocked(masteryLevel >= lvl)

    def LoadAssociatedExpertSystems(self):
        self.expert_system_cont.display = False
        if not expertSystems.has_associated_expert_system(self.typeID):
            self.mastery_level_cont.padBottom = 56
            return
        associatedExpertSystems = expertSystems.get_associated_expert_systems(self.typeID)
        relevantExpertSystems = filter(lambda system: expertSystems.expert_system_benefits_player(system.type_id), associatedExpertSystems)
        if len(relevantExpertSystems):
            expertSystem = relevantExpertSystems[0]
            self.expert_system_label.text = expertSystem.name
            if expertSystem.associated_type_ids:
                self.expert_system_value_label.text = localization.GetByLabel('UI/InfoWindow/ExpertSystemUnlocksShips', num=len(expertSystem.associated_type_ids))
            else:
                self.expert_system_value_label.Hide()
            self.expert_system_cont.display = True
        else:
            self.mastery_level_cont.padBottom = 56

    def LoadTrainingTimeAndSkillActions(self, level):
        self.training_time_cont.Flush()
        if level == 0:
            self._LoadTrainingTimeAndSkillActionsForRequirements()
        else:
            self._LoadTrainingTimeAndSkillActionsForMastery(level)

    def _LoadTrainingTimeAndSkillActionsForRequirements(self):
        if sm.GetService('skills').IsSkillRequirementMet(self.typeID):
            return
        totalTime = sm.GetService('skills').GetSkillTrainingTimeLeftToUseType(self.typeID, includeBoosters=False)
        omegaRestricted = ItemObject(self.typeID, None).NeedsOmegaUpgrade()
        if sm.GetService('cloneGradeSvc').IsOmega():
            OmegaTrainingTimeContainer(parent=self.training_time_cont, omegaTime=totalTime)
        else:
            omegaTime = totalTime / 2
            AlphaTrainingTimeContainer(parent=self.training_time_cont, isOmegaRestricted=omegaRestricted, alphaTime=totalTime, omegaTime=omegaTime, activityText=GetActivityTextForType(self.typeID))
        if not omegaRestricted:
            SkillActionContainer(parent=self.training_time_cont, padTop=8, align=uiconst.TOTOP, typeID=self.typeID)

    def _LoadTrainingTimeAndSkillActionsForMastery(self, masteryLevel):
        skillSvc = sm.GetService('skills')
        certSvc = sm.GetService('certificates')
        trainingTime = certSvc.GetShipTrainingTimeForMasteryLevel(self.typeID, masteryLevel)
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
        if len(requiredSkillsList) > 0:
            if cloneGradeService.IsOmega():
                OmegaTrainingTimeContainer(parent=self.training_time_cont, omegaTime=long(trainingTime), padBottom=8)
            else:
                omegaTime = long(trainingTime) / 2
                AlphaTrainingTimeContainer(parent=self.training_time_cont, isOmegaRestricted=isOmegaRestricted, alphaTime=long(trainingTime), omegaTime=omegaTime, activityText=localization.GetByLabel('Tooltips/SkillPlanner/ActivityTrainMasteryLevel'), padBottom=8, clipChildren=True)
            if not isOmegaRestricted:
                typeName = evetypes.GetName(self.typeID)
                level = IntToRoman(masteryLevel)
                skillPlanName = localization.GetByLabel('UI/SkillPlan/CreateMasterySkillPlanName', typeName=typeName, level=level)
                SkillActionContainer(parent=self.training_time_cont, align=uiconst.TOTOP, requiredSkills=requiredSkillsList, missingSkills=missingSkills, skillPlanName=skillPlanName)

    @classmethod
    def get_name(cls):
        return localization.GetByLabel('UI/InfoWindow/TabNames/Skills')

    @classmethod
    def get_icon(cls):
        return eveicon.skill_book

    @classmethod
    def is_visible(cls, typeID, itemID = None, rec = None):
        return not idCheckers.IsCapsule(evetypes.GetGroupID(typeID))

    def get_camera_position(self):
        return ANGLE_SKILLS

    def get_tab_type(self):
        return TAB_SKILLS

    def OnSkillsChanged(self, *args):
        self.LoadCurrentMastery()
        self.LoadPage()

    def _filter_acquired_setting_changed(self, *args, **kwargs):
        self.LoadPage()

    def _collapse_all(self):
        for entry in self.list_cont.children:
            if hasattr(entry, 'SetCollapsed'):
                entry.SetCollapsed(True)


class ListEntrySkill(_ListEntryBase):
    default_height = 32
    isDragObject = True

    def __init__(self, skillID, requiredLevel, indent = 0, **kw):
        self.skillID = skillID
        self.requiredLevel = requiredLevel
        self.skillController = SkillController(skillID)
        super(ListEntrySkill, self).__init__(indent=indent, **kw)
        self.refresh()

    def construct_layout(self):
        super(ListEntrySkill, self).construct_layout()
        self.iconCont = Container(name='iconCont', parent=self.content, align=Align.TORIGHT, width=16, left=8)
        self.icon = None
        self.completedIcon = None
        skillBarCont = Container(name='skillBarCont', parent=self.content, align=Align.TOLEFT, width=70)
        self.skillBar = SkillBar(name='skillBar', parent=skillBarCont, align=Align.CENTERLEFT, state=uiconst.UI_DISABLED, skillID=self.skillID, boxSize=8)
        skillAndLevelCont = Container(name='skillAndLevelCont', parent=self.content, align=Align.TOALL, padLeft=8, clipChildren=True)
        self.skillAndLevelLabel = TextBody(name='skillAndLevelLabel', parent=skillAndLevelCont, align=Align.CENTERLEFT, autoFadeSides=16)
        self.backgroundFill = None

    def refresh(self):
        text = self.skillController.GetRequiredSkillNameAndLevelComparedToTrainedLevel(self.requiredLevel)
        self.skillAndLevelLabel.SetText(text)
        self.skillBar.SetRequiredLevel(self.requiredLevel)
        if not self.skillController.IsInjected():
            if self.skillController.IsSkillAvailableForPurchase():
                self.set_icon(texturePath='res:/ui/Texture/classes/Skills/SkillBookNotInjected.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/SkillQueue/SkillBookMissing'))
            else:
                self.set_icon(texturePath='res:/ui/Texture/classes/Skills/RareSkillBookNotInjected.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/SkillQueue/RareSkillBookMissing'))
        elif self.skillController.GetMyLevel() >= self.requiredLevel:
            self.set_completed()
            self.skillAndLevelLabel.SetRGBA(1.0, 1.0, 1.0, 0.5)
            self.hide_background()
        else:
            self.set_icon(texturePath='res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png', color=COLOR_SKILL_1, hint=localization.GetByLabel('UI/InfoWindow/SkillNotTrainedToRequiredLevel'))
            self.hide_background()

    def set_completed(self):
        if self.completedIcon is None:
            self.completedIcon = CheckMarkGlyphIcon(parent=self.iconCont, align=Align.CENTER, hint=localization.GetByLabel('UI/InfoWindow/SkillTrainedToRequiredLevel'))
        else:
            self.completedIcon.Show()
        if self.icon:
            self.icon.Hide()

    def set_icon(self, texturePath, color, hint):
        if self.icon is None:
            self.icon = Sprite(parent=self.iconCont, align=Align.CENTER, texturePath=texturePath, width=16, height=16, color=color, hint=hint)
        else:
            self.icon.SetTexturePath(texturePath)
            self.icon.SetRGBA(*color)
            self.icon.hint = hint
        if self.completedIcon:
            self.completedIcon.Hide()

    def hide_background(self):
        if self.backgroundFill is not None:
            self.backgroundFill.Close()
            self.backgroundFill = None

    def GetMenu(self):
        return self.skillController.GetMenu()

    def GetDragData(self):
        return self.skillController.GetDragData()

    def LoadTooltipPanel(self, tooltip_panel, *args):
        LoadSkillEntryTooltip(tooltip_panel, self.skillID, self.requiredLevel)

    def OnDblClick(self, *args, **kwargs):
        self._show_info()

    def _show_info(self):
        sm.GetService('info').ShowInfo(typeID=self.skillID)


class SkillPanelToggleButtonUnderlay(ToggleButtonUnderlay):

    def _get_texture_path(self):
        if self.frame_type == FrameType.LEFT:
            return 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_left_64px.png'
        if self.frame_type == FrameType.RIGHT:
            return 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_right_64px.png'
        return 'res:/UI/Texture/classes/ToggleButtonGroup/toggle_button_frame_64px.png'


class SkillPanelToggleButtonLarge(ToggleButtonGroupButtonIcon):
    default_clipChildren = True

    def _layout(self):
        self._icon = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.iconPath, color=self._get_icon_color(), pos=(0,
         -8,
         self.iconSize,
         self.iconSize))
        self._underlay = SkillPanelToggleButtonUnderlay(bgParent=self, selected=self.isSelected, enabled=not self.isDisabled, selected_color_override=self.colorSelected)
        self.unlocked_icon = Sprite(parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, pos=(0, 18, 16, 16), texturePath=eveicon.circle_checkmark, color=(1, 1, 1, 0.6))
        self.unlocked_icon.Hide()
        self.locked_icon = Sprite(parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, pos=(0, 18, 12, 12), texturePath='res:/UI/Texture/classes/PieCircle/circle16.png', color=(0, 0, 0, 0.4))

    def set_unlocked(self, unlocked):
        if unlocked:
            self.unlocked_icon.Show()
            self.locked_icon.Hide()
        else:
            self.unlocked_icon.Hide()
            self.locked_icon.Show()


class SkillPanelToggleButtonSmall(ToggleButtonGroupButtonIcon):

    def _layout(self):
        self._icon = Sprite(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath=self.iconPath, color=self._get_icon_color(), pos=(0,
         -8,
         self.iconSize,
         self.iconSize))
        self._underlay = ToggleButtonUnderlay(bgParent=self, selected=self.isSelected, enabled=not self.isDisabled, selected_color_override=self.colorSelected)
        self.unlocked_icon = Sprite(parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, pos=(0, 10, 16, 16), texturePath=eveicon.circle_checkmark, color=(1, 1, 1, 0.6))
        self.unlocked_icon.Hide()
        self.locked_icon = Sprite(parent=self, align=Align.CENTER, state=uiconst.UI_DISABLED, pos=(0, 10, 12, 12), texturePath='res:/UI/Texture/classes/PieCircle/circle16.png', color=(0, 0, 0, 0.4))

    def set_unlocked(self, unlocked):
        if unlocked:
            self.unlocked_icon.Show()
            self.locked_icon.Hide()
        else:
            self.unlocked_icon.Hide()
            self.locked_icon.Show()


class CollapsibleGroupCertificate(_CollapsibleGroupBase):
    default_expanderAlign = Align.TOLEFT
    default_expanderWidth = 20
    default_expanderPadding = (4, 0, 0, 0)
    isDragObject = True

    def ApplyAttributes(self, attributes):
        self.certificate = attributes.certificate
        self.level = attributes.level
        self.label = self.certificate.GetLabel(self.level)
        super(CollapsibleGroupCertificate, self).ApplyAttributes(attributes)
        self.update_progress()

    def SetCollapsed(self, collapsed):
        if collapsed:
            _collapsed_certificates.add((self.certificate.certificateID, self.level))
        else:
            _collapsed_certificates.discard((self.certificate.certificateID, self.level))
        super(CollapsibleGroupCertificate, self).SetCollapsed(collapsed)

    def _construct_expander(self):
        super(CollapsibleGroupCertificate, self)._construct_expander()
        certLevelCont = Container(name='certLevelCont', parent=self.headerCont, align=Align.TOLEFT, width=22, padLeft=4)
        Sprite(name='certLevelIcon', parent=certLevelCont, align=Align.CENTER, width=22, height=22, texturePath=_get_certificate_level_icon(self.level), state=uiconst.UI_DISABLED)
        progressCont = Container(name='progressCont', parent=self.headerCont, align=Align.TORIGHT, width=16, padRight=8)
        self.completedIcon = CheckMarkGlyphIcon(parent=progressCont, align=Align.CENTER, hint=localization.GetByLabel('UI/InfoWindow/TrainedAndOfRequiredLevel'))
        self.progressIcon = Sprite(name='progressIcon', parent=progressCont, align=Align.CENTER, width=16, height=16, texturePath='res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png', hint=localization.GetByLabel('UI/InfoWindow/NotTrained'))
        self.completedIcon.Hide()
        self.progressIcon.Hide()
        titleCont = ContainerAutoSize(name='titleCont', parent=self.headerCont, align=Align.TOALL, padLeft=4, clipChildren=True)
        self.titleLabel = TextBody(name='title', parent=titleCont, align=Align.CENTERLEFT, text=self.label, autoFadeSides=16)

    def update_progress(self):
        currLevel = self.certificate.GetLevel()
        if currLevel >= self.level:
            self.completedIcon.Show()
            self.progressIcon.Hide()
        else:
            self.completedIcon.Hide()
            self.progressIcon.Show()

    def GetMenu(self):
        m = MenuData()
        m.AddEntry(MenuLabel('UI/Commands/ShowInfo'), self._show_info)
        if session.role & ROLE_GML == ROLE_GML:
            m.AddEntry('GM: Give all skills', lambda : _qa_give_cert_skills(self.certificate.certificateID, self.level))
        return m

    def _show_info(self, *args, **kwargs):
        abstractinfo = KeyVal(certificateID=self.certificate.certificateID, level=self.level)
        sm.GetService('info').ShowInfo(appConst.typeCertificate, abstractinfo=abstractinfo)

    def GetHint(self):
        return self.certificate.GetDescription()

    def GetDragData(self, *args):
        entry = KeyVal()
        entry.__guid__ = 'listentry.CertEntry'
        entry.typeID = appConst.typeCertificate
        entry.certID = self.certificate.certificateID
        entry.level = self.level
        entry.genericDisplayLabel = StripTags(self.certificate.GetName())
        return [entry]

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2


def _get_certificate_level_icon(level):
    return 'res:/UI/Texture/Classes/Certificates/level%sSmall.png' % level


def _qa_give_required_skills(type_id):
    from collections import defaultdict
    train_skills = defaultdict(int)

    def add_skills(skill_type_id, required_level):
        if sm.GetService('skills').MySkillLevel(skill_type_id) < required_level:
            train_skills[skill_type_id] = max(train_skills[skill_type_id], required_level)
        for skill_id, level in sm.GetService('skills').GetRequiredSkills(skill_type_id).iteritems():
            if skill_id == skill_type_id:
                continue
            add_skills(skill_id, level)

    required_skills = sm.GetService('skills').GetRequiredSkills(type_id)
    for skill_type_id, required_level in required_skills.iteritems():
        add_skills(skill_type_id, required_level)

    _qa_give_skills(train_skills)


def _qa_give_all_cert_skills(type_id, mastery_level):
    from collections import defaultdict
    train_skills = defaultdict(int)
    certificates = sm.GetService('certificates').GetCertificatesForShipByMasteryLevel(type_id, mastery_level)
    for cert in certificates:
        skills = sm.GetService('certificates').GetCertificate(cert.certificateID).SkillsByTypeAndLevel(mastery_level)
        for skill_type_id, required_level in skills:
            if sm.GetService('skills').MySkillLevel(skill_type_id) < required_level:
                train_skills[skill_type_id] = max(train_skills[skill_type_id], required_level)

    _qa_give_skills(train_skills)


def _qa_give_cert_skills(certificate_id, certificate_level):
    from collections import defaultdict
    train_skills = defaultdict(int)
    skills = sm.GetService('certificates').GetCertificate(certificate_id).SkillsByTypeAndLevel(certificate_level)
    for skill_type_id, required_level in skills:
        if sm.GetService('skills').MySkillLevel(skill_type_id) < required_level:
            train_skills[skill_type_id] = max(train_skills[skill_type_id], required_level)

    _qa_give_skills(train_skills)


def _qa_give_skills(skills):
    cntFrom = 1
    cntTo = len(skills) + 1
    sm.GetService('loading').ProgressWnd('GM Skill Gift', '', cntFrom, cntTo)
    for typeID, level in skills.iteritems():
        cntFrom = cntFrom + 1
        sm.GetService('loading').ProgressWnd('GM Skill Gift', 'Training of the skill %s to level %d has been completed' % (evetypes.GetName(typeID), level), cntFrom, cntTo)
        sm.RemoteSvc('slash').SlashCmd('/giveskill me %s %s' % (typeID, level))

    sm.GetService('loading').ProgressWnd('Done', '', cntTo, cntTo)
    sm.GetService('skills').ForceRefresh()
