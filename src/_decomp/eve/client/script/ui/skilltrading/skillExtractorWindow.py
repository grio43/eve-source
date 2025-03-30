#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skilltrading\skillExtractorWindow.py
import blue
from carbonui import TextColor, uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.color import Color
import contextlib
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import CaptionLabel, EveCaptionMedium, EveHeaderMedium, EveLabelMedium, EveLabelSmall
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from carbonui.control.window import Window
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.skillBar.controller import SkillBarController
from eve.client.script.ui.control.skillBar.skillBar import SkillBar
from eve.client.script.ui.control.skillBar.skillLevel import SkillLevel, COLOR_TRAINED, COLOR_UNTRAINED
from eve.client.script.ui.control.treeData import TreeData
from eve.client.script.ui.control.treeViewEntry import TreeViewEntry
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from inventorycommon.const import groupCapsule
from skills.client.skillController import SkillController
from eve.client.script.ui.shared.neocom.skillConst import COLOR_UNALLOCATED_1
from eve.client.script.ui.skilltrading.skillExtractorController import SkillExtractorController, SkillExtractorError, RESTRICTION_IMPLANT, RESTRICTION_CLONE_STATE, RESTRICTION_JUMP_CLONE, RESTRICTION_PI_COLONY, RESTRICTION_PI_UPGRADE, RESTRICTION_OVER_TRAINED
from eve.client.script.ui.util.uiComponents import ButtonEffect, Component
import evelink.client
import evetypes
from inventorycommon import const as invconst
import itertoolsext
import localization
import signals
import trinity
import uthread
from eveservices.menu import GetMenuService
COLOR_EXTRACTED = (0.871,
 0.118,
 0.0,
 1.0)

class SkillExtractorWindow(Window):
    __guid__ = 'form.SkillExtractorWindow'
    __notifyevents__ = ['OnSessionChanged']
    default_width = 450
    default_height = 700
    default_minSize = (default_width, default_height)
    default_windowID = 'SkillExtractorWindow'
    default_captionLabelPath = 'UI/SkillTrading/SkillExtractorWindowCaption'
    default_iconNum = 'res:/UI/Texture/WindowIcons/augmentations.png'
    default_clipChildren = True
    default_isCollapseable = False
    default_isLightBackgroundConfigurable = False
    default_isStackable = False
    default_isLockable = False
    default_isOverlayable = False

    @classmethod
    def OpenOrReload(cls, *args, **kwargs):
        if cls.IsOpen():
            wnd = cls.GetIfOpen()
            if wnd.controller.isCompleted:
                wnd.Close()
                wnd = cls.Open(*args, **kwargs)
            else:
                wnd.controller.itemID = kwargs.get('itemID')
                wnd.Maximize()
        else:
            cls.Open(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        super(SkillExtractorWindow, self).ApplyAttributes(attributes)
        self.controller = SkillExtractorController(attributes.itemID)
        self.filterSettings = SkillFilterSettings()
        self.Layout()
        self.Reload()
        self.filterSettings.onUpdate.connect(self.UpdateNoContentMessage)
        self.controller.onUpdate.connect(self.OnUpdate)
        self.controller.onSkillListUpdate.connect(self.Reload)
        sm.GetService('audio').SendUIEvent('st_activate_skill_extractor_play')

    def Layout(self):
        self.contentCont = Container(parent=self.GetMainArea(), align=uiconst.TOALL)
        topCont = Container(name='topCont', parent=self.contentCont, align=uiconst.TOTOP, height=128)
        SkillExtractorBar(parent=topCont, align=uiconst.CENTER, state=uiconst.UI_NORMAL, width=300, controller=self.controller)
        middleCont = Container(parent=self.contentCont, align=uiconst.TOALL, padding=(8, 0, 8, 8))
        self.filterCont = Container(name='filterCont', parent=middleCont, align=uiconst.TOTOP, height=HEIGHT_NORMAL, opacity=0.0)
        SkillFilterMenu(parent=self.filterCont, align=uiconst.CENTERRIGHT, settings=self.filterSettings, hint=localization.GetByLabel('UI/SkillTrading/FilterSettings'))
        SkillFilterEdit(parent=self.filterCont, align=uiconst.CENTERRIGHT, left=20, filterSettings=self.filterSettings, isTypeField=True)
        self.skillScroll = ScrollContainer(parent=middleCont, align=uiconst.TOALL, showUnderlay=True, opacity=0.0, padTop=4)
        self.loadingPanel = Container(parent=middleCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=250, height=150)
        LoadingWheel(parent=self.loadingPanel, align=uiconst.CENTERTOP, width=42, height=42)
        text = localization.GetByLabel('UI/SkillTrading/LoadingSkills')
        EveHeaderMedium(parent=self.loadingPanel, align=uiconst.TOTOP, top=50, text='<center>%s</center>' % text)
        self.messagePanel = ContainerAutoSize(parent=self.GetMainArea(), align=uiconst.CENTER, alignMode=uiconst.TOTOP, width=300, opacity=0.0, idx=0)

    def Reload(self):
        uthread.new(self._Reload)

    def _Reload(self):
        self.AnimShowLoading()
        self.CheckShipAndShowMessage()
        self.entryDataList = self._GenerateSkillEntries(self.controller.skills)
        self._FlushAndPopulateSkillScroll(self.entryDataList)
        self.UpdateNoContentMessage()
        self.AnimHideLoading()

    def AnimShowLoading(self):
        self.skillScroll.Disable()
        self.filterCont.Disable()
        animations.FadeIn(self.loadingPanel)
        animations.FadeOut(self.skillScroll, duration=0.3)
        animations.FadeOut(self.filterCont, duration=0.3, sleep=True)

    def AnimHideLoading(self):
        self.skillScroll.Enable()
        self.filterCont.Enable()
        animations.FadeOut(self.loadingPanel)
        animations.FadeIn(self.skillScroll)
        animations.FadeIn(self.filterCont)

    def _GenerateSkillEntries(self, skills):
        skillDataByGroupID = itertoolsext.bucket(skills, keyprojection=lambda s: evetypes.GetGroupID(s.typeID), valueprojection=lambda s: SkillEntryData(s, self.controller, self.filterSettings))
        groups = [ SkillGroupData(gid, self.filterSettings, children=data) for gid, data in skillDataByGroupID.iteritems() ]
        return sorted(groups, key=lambda x: x.GetLabel().lower())

    def _FlushAndPopulateSkillScroll(self, groups):
        self.skillScroll.Flush()
        for groupData in groups:
            SkillGroupEntry(parent=self.skillScroll, data=groupData, defaultExpanded=False)
            blue.pyos.BeNice()

    def OnUpdate(self):
        self.UpdateNoContentMessage()
        self.CheckCompletedAndShowMessage()

    def UpdateNoContentMessage(self):
        self.skillScroll.HideNoContentHint()
        if all((data.isFiltered for data in self.entryDataList)):
            emptyHint = localization.GetByLabel('UI/SkillTrading/NoSkillsHint')
            self.skillScroll.ShowNoContentHint(emptyHint)

    def CheckCompletedAndShowMessage(self):
        if self.controller.isCompleted:
            self.PrepareCompleteMessage()
            self.AnimShowMessage()

    def PrepareCompleteMessage(self):
        self.messagePanel.Flush()
        text = localization.GetByLabel('UI/SkillTrading/CompleteMessageCaption')
        EveCaptionMedium(parent=self.messagePanel, align=uiconst.TOTOP, text='<center>%s</center>' % text)
        text = localization.GetByLabel('UI/SkillTrading/CompleteMessageMain', amount=self.controller.SKILL_POINT_GOAL, injector=invconst.typeSkillInjector)
        EveLabelMedium(parent=self.messagePanel, align=uiconst.TOTOP, top=4, text='<center>%s</center>' % text)
        iconCont = Container(parent=self.messagePanel, align=uiconst.TOTOP, top=8, height=64)
        Icon(parent=iconCont, align=uiconst.CENTER, left=-40, typeID=invconst.typeSkillInjector, size=64, state=uiconst.UI_DISABLED)
        Sprite(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/skilltrading/arrow_right.png', width=32, height=32, opacity=0.6)
        Sprite(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, left=40, texturePath='res:/UI/Texture/WindowIcons/itemHangar.png', width=64, height=64)
        text = localization.GetByLabel('UI/SkillTrading/CompleteMessageTail', injector=invconst.typeSkillInjector)
        EveLabelMedium(parent=self.messagePanel, align=uiconst.TOTOP, top=8, text='<center>%s</center>' % text)
        buttonCont = Container(parent=self.messagePanel, align=uiconst.TOTOP, top=16, height=40)
        Button(parent=buttonCont, align=uiconst.CENTER, label=localization.GetByLabel('UI/Common/Done'), func=self.Close)

    def CheckShipAndShowMessage(self):
        if self.controller.isCompleted:
            return
        ship = sm.GetService('godma').GetItem(session.shipid)
        if ship.groupID != groupCapsule:
            self.PrepareShipMessage()
            self.AnimShowMessage()
        else:
            self.AnimHideMessage()

    def PrepareShipMessage(self):
        self.messagePanel.Flush()
        EveCaptionMedium(parent=self.messagePanel, align=uiconst.TOTOP, text='<center>%s</center>' % localization.GetByLabel('UI/SkillTrading/ShipMessageHeader'))
        EveLabelMedium(parent=self.messagePanel, align=uiconst.TOTOP, top=4, text='<center>%s</center>' % localization.GetByLabel('UI/SkillTrading/ShipMessage'), color=TextColor.SECONDARY)
        buttonCont = Container(parent=self.messagePanel, align=uiconst.TOTOP, top=16, height=40)
        Button(parent=buttonCont, align=uiconst.CENTER, label=localization.GetByLabel('UI/SkillTrading/LeaveShipButtonLabel'), func=self.LeaveShip, args=())

    def AnimShowMessage(self):
        self.contentCont.state = uiconst.UI_DISABLED
        animations.FadeTo(self.contentCont, startVal=self.contentCont.opacity, endVal=0.1)
        animations.FadeIn(self.messagePanel)

    def AnimHideMessage(self):
        self.contentCont.state = uiconst.UI_PICKCHILDREN
        animations.FadeTo(self.contentCont, startVal=self.contentCont.opacity, endVal=1.0)
        animations.FadeOut(self.messagePanel)

    def Close(self, *args, **kwargs):
        super(SkillExtractorWindow, self).Close(*args, **kwargs)
        self.controller.Close()

    def OnSessionChanged(self, isRemote, sess, change):
        if 'stationid' in change:
            self.Close()
        elif 'shipid' in change:
            self.CheckShipAndShowMessage()

    def LeaveShip(self):
        ship = sm.GetService('godma').GetItem(session.shipid)
        sm.StartService('station').TryLeaveShip(ship)
        self.AnimHideMessage()


class SkillFilterEdit(QuickFilterEdit):

    def ApplyAttributes(self, attributes):
        super(SkillFilterEdit, self).ApplyAttributes(attributes)
        self.filterSettings = attributes.filterSettings

    def ReloadFunction(self):
        self.filterSettings.SetNameFilter(self.quickFilterInput)


class SkillFilterSettings(object):
    SHOW_SKILLS_KEY = 'skillExtractorWindow_showSkills'
    HIDE_LOCKED_SKILLS_KEY = 'skillExtractorWindow_hideLockedSkills'
    HIDE_EMPTY_SKILLS_KEY = 'skillExtractorWindow_hideEmptySkills'
    SHOW_ALL_SKILLS = 'all'
    SHOW_EXTRACTED_SKILLS = 'extracted'
    OPTION_DEFAULTS = {SHOW_SKILLS_KEY: SHOW_ALL_SKILLS,
     HIDE_LOCKED_SKILLS_KEY: False,
     HIDE_EMPTY_SKILLS_KEY: False}

    def __init__(self):
        self.onUpdate = signals.Signal(signalName='onUpdate6')
        self._nameFilter = ''

    def GetNameFilter(self):
        return self._nameFilter

    def SetNameFilter(self, name):
        current = self._nameFilter
        self._nameFilter = name.strip().lower() if name is not None else ''
        if current != self._nameFilter:
            self.onUpdate()

    def IsShowAllSkills(self):
        return self.GetOption(self.SHOW_SKILLS_KEY) == self.SHOW_ALL_SKILLS

    def SetShowAllSkills(self):
        self.SetOption(self.SHOW_SKILLS_KEY, self.SHOW_ALL_SKILLS)

    def IsShowExtractedSkills(self):
        return self.GetOption(self.SHOW_SKILLS_KEY) == self.SHOW_EXTRACTED_SKILLS

    def SetShowExtractedSkills(self):
        self.SetOption(self.SHOW_SKILLS_KEY, self.SHOW_EXTRACTED_SKILLS)

    def IsHideLockedSkills(self):
        return self.GetOption(self.HIDE_LOCKED_SKILLS_KEY)

    def ToggleHideLockedSkills(self):
        self.ToggleOption(self.HIDE_LOCKED_SKILLS_KEY)

    def IsHideEmptySkills(self):
        return self.GetOption(self.HIDE_EMPTY_SKILLS_KEY)

    def ToggleHideEmptySkills(self):
        self.ToggleOption(self.HIDE_EMPTY_SKILLS_KEY)

    def GetOption(self, option):
        return settings.user.ui.Get(option, self.OPTION_DEFAULTS[option])

    def SetOption(self, option, value):
        settings.user.ui.Set(option, value)
        self.onUpdate()

    def ToggleOption(self, option):
        current = self.GetOption(option)
        self.SetOption(option, not current)


class SkillFilterMenu(UtilMenu):
    default_texturePath = 'res:/UI/Texture/SettingsCogwheel.png'
    default_width = 16
    default_height = 16
    default_iconSize = 18
    default_menuAlign = uiconst.TOPLEFT

    def ApplyAttributes(self, attributes):
        attributes.GetUtilMenu = self.GetSkillFilterMenu
        super(SkillFilterMenu, self).ApplyAttributes(attributes)
        self.settings = attributes.settings

    def GetSkillFilterMenu(self, menu):
        menu.AddRadioButton(text=localization.GetByLabel('UI/SkillTrading/ShowAllSkills'), checked=self.settings.IsShowAllSkills(), callback=self.settings.SetShowAllSkills)
        menu.AddRadioButton(text=localization.GetByLabel('UI/SkillTrading/ShowExtractedSkills'), checked=self.settings.IsShowExtractedSkills(), callback=self.settings.SetShowExtractedSkills)
        menu.AddDivider()
        menu.AddCheckBox(text=localization.GetByLabel('UI/SkillTrading/HideLockedSkills'), checked=self.settings.IsHideLockedSkills(), callback=self.settings.ToggleHideLockedSkills)
        menu.AddCheckBox(text=localization.GetByLabel('UI/SkillTrading/HideEmptySkills'), checked=self.settings.IsHideEmptySkills(), callback=self.settings.ToggleHideEmptySkills)


class SkillExtractorBar(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        super(SkillExtractorBar, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.Layout()
        self.Update()
        self.controller.onUpdate.connect(self.Update)

    def Layout(self):
        gaugeCont = Container(parent=self, align=uiconst.TOTOP, height=48)
        Frame(parent=gaugeCont, cornerSize=3, opacity=0.5, color=eveThemeColor.THEME_FOCUS)
        self.gaugeBG = Fill(bgParent=gaugeCont, align=uiconst.TOALL, color=eveThemeColor.THEME_FOCUSDARK, opacity=0.2)
        self.extractButton = ExtractButton(parent=gaugeCont, align=uiconst.TOALL, controller=self.controller)
        self.gauge = Gauge(parent=gaugeCont, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, height=gaugeCont.height - 2, gaugeHeight=gaugeCont.height - 2, top=1, color=COLOR_UNALLOCATED_1, backgroundColor=(1.0, 1.0, 0.0, 0.0))
        self.noProgressHint = eveLabel.EveCaptionSmall(parent=gaugeCont, align=uiconst.CENTER, width=self.width, text=localization.GetByLabel('UI/SkillTrading/DropToExtractHint'))
        self.amountLabel = ExtractorBarAmountLabel(parent=self, align=uiconst.TOTOP, padTop=4, goal=self.controller.SKILL_POINT_GOAL)

    def Update(self):
        self.gauge.SetValue(self.controller.progress)
        self.amountLabel.AnimSetAmount(self.controller.extractedPoints)
        opacity = 0.0 if self.controller.progress > 0.0 else TextColor.HIGHLIGHT.opacity
        animations.FadeTo(self.noProgressHint, startVal=self.noProgressHint.opacity, endVal=opacity)
        target = 0.5 - self.controller.progress if self.controller.progress > 0.0 else 0.0
        animations.MorphVector2(self.gaugeBG, 'translationPrimary', startVal=self.gaugeBG.translationPrimary, endVal=(target, 0.0))

    def OnDropData(self, source, data):
        for entry in data:
            skillID = self._GetDropDataSkillID(entry)
            if skillID is not None:
                try:
                    self.controller.ExtractSkill(skillID)
                    sm.GetService('audio').SendUIEvent('st_select_skills_play')
                except SkillExtractorError:
                    pass

    def _GetDropDataSkillID(self, data):
        for attr in ('skillID', 'typeID', 'invtype'):
            skillID = getattr(data, attr, None)
            if skillID is not None:
                return skillID


@Component(ButtonEffect(bgElementFunc=lambda parent, _: parent.frame, opacityIdle=1.0, opacityHover=0.6, opacityMouseDown=0.2))

class ExtractButton(Container):
    default_opacity = 0.0

    def ApplyAttributes(self, attributes):
        super(ExtractButton, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self._processing = False
        self.controller.onUpdate.connect(self.Update)
        self.Layout()
        self.Update()

    def Layout(self):
        self.frame = Frame(bgParent=self, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/buttonBg.png', cornerSize=5, color=Color.GRAY2)
        self.arrows = Sprite(bgParent=self, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrowMask.png', textureSecondaryPath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', translationSecondary=(-0.16, 0), spriteEffect=trinity.TR2_SFX_MODULATE, color=Color.GRAY2, opacity=0.2)
        animations.MorphVector2(self.arrows, 'translationSecondary', startVal=(0.16, 0.0), endVal=(-0.16, 0.0), duration=2.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        self.label = CaptionLabel(parent=self, align=uiconst.CENTER, text=localization.GetByLabel('UI/SkillTrading/Extract'))
        self.spinner = LoadingWheel(parent=self, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=30, height=30, opacity=0.0)

    @property
    def isReady(self):
        return self.controller.progress >= 1.0 and not self.controller.isCompleted

    @property
    def isProcessing(self):
        return self._processing

    def Update(self):
        if self.controller.progress < 1.0:
            self.AnimHide()
        else:
            self.AnimShow()

    def AnimShow(self):
        self.Enable()
        animations.FadeIn(self, timeOffset=0.3, duration=0.5)

    def AnimHide(self):
        self.Disable()
        animations.FadeOut(self, duration=0.2)

    def OnClick(self, *args):
        uthread.new(self._ProcessOnClick)

    def _ProcessOnClick(self):
        if not self.isReady or self.isProcessing:
            return
        with self.processing():
            self.controller.Commit()
            sm.GetService('audio').SendUIEvent('st_confirmed_extraction_play')

    @contextlib.contextmanager
    def processing(self):
        try:
            self._processing = True
            self._AnimShowProcessing()
            yield
        finally:
            self._processing = False
            self._AnimHideProcessing()

    def _AnimShowProcessing(self):
        animations.FadeOut(self.label)
        animations.FadeIn(self.spinner)

    def _AnimHideProcessing(self):
        animations.FadeIn(self.label)
        animations.FadeOut(self.spinner)


class ExtractorBarAmountLabel(Container):
    default_height = 17

    def ApplyAttributes(self, attributes):
        super(ExtractorBarAmountLabel, self).ApplyAttributes(attributes)
        self.goal = attributes.goal
        self._amount = attributes.get('amount', 0)
        self.Layout()

    def Layout(self):
        Frame(parent=self, opacity=0.1)
        Sprite(bgParent=self, align=uiconst.TOALL, padding=(4, 4, 4, 4), texturePath='res:/UI/Texture/classes/skilltrading/checker_bg.png', opacity=0.4, tileX=True, tileY=True)
        self.label = EveLabelSmall(parent=self, align=uiconst.CENTER)
        self.UpdateLabel()

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, value):
        self._amount = int(value)
        self.UpdateLabel()

    def AnimSetAmount(self, amount):
        animations.MorphScalar(self, 'amount', startVal=self.amount, endVal=amount, callback=lambda : setattr(self, 'amount', amount))

    def UpdateLabel(self):
        text = localization.GetByLabel('UI/SkillTrading/ExtractionProgressAndTotal', current=self.amount, total=self.goal)
        self.label.SetText(text)


class SkillEntryData(TreeData):

    def __init__(self, skill, controller, filterSettings, **kw):
        super(SkillEntryData, self).__init__(**kw)
        self.skill = skill
        self.controller = controller
        self.filterSettings = filterSettings

    @property
    def typeID(self):
        return self.skill.typeID

    @property
    def name(self):
        return evetypes.GetName(self.typeID)

    @property
    def isFiltered(self):
        showExtracted = self.filterSettings.IsShowExtractedSkills()
        hideLocked = self.filterSettings.IsHideLockedSkills()
        hideEmpty = self.filterSettings.IsHideEmptySkills()
        nameFilter = self.filterSettings.GetNameFilter()
        if showExtracted and self.skill.points == self.skill.unmodifiedPoints:
            return True
        if nameFilter not in self.name.lower():
            return True
        if hideLocked and self.isLocked:
            return True
        if hideEmpty and self.skill.unmodifiedPoints == 0:
            return True
        return False

    @property
    def isLocked(self):
        return self.skill.IsLocked()

    @property
    def isExtracted(self):
        return self.skill.points != self.skill.unmodifiedPoints

    def ExtractSkill(self):
        if not self.isLocked:
            self.controller.ExtractSkill(self.typeID)

    def Undo(self):
        self.controller.Revert(self.typeID)

    def GetLabel(self):
        color = (1.0, 1.0, 1.0, 0.8)
        if self.skill.points != self.skill.unmodifiedPoints:
            color = COLOR_EXTRACTED
        text = localization.GetByLabel('UI/SkillTrading/SkillEntryLabel', typeID=self.typeID, level=self.skill.level, rank=self.skill.rank, points=self.skill.points, color=Color.RGBtoHex(*color))
        return text

    def GetHint(self):
        if self.skill.isRestricted:
            return self._GetRestrictedSkillHint()
        if self.skill.isRequired:
            return self._GetRequiredSkillHint()
        if self.skill.isQueued:
            return self._GetQueuedSkillHint()

    def _GetRestrictedSkillHint(self):
        if self.skill.restrictionReason is None:
            return
        LABEL_BY_RESTRICTION = {RESTRICTION_IMPLANT: 'UI/SkillTrading/SkillRestrictionImplants',
         RESTRICTION_CLONE_STATE: 'UI/SkillTrading/SkillRestrictionCloneState',
         RESTRICTION_JUMP_CLONE: 'UI/SkillTrading/SkillRestrictionJumpClones',
         RESTRICTION_PI_COLONY: 'UI/SkillTrading/SkillRestrictionInterplanetaryConsolidation',
         RESTRICTION_PI_UPGRADE: 'UI/SkillTrading/SkillRestrictionCommandCenterUpgrade',
         RESTRICTION_OVER_TRAINED: 'UI/SkillTrading/SkillRestrictionOverTrained'}
        label = LABEL_BY_RESTRICTION[self.skill.restrictionReason]
        return localization.GetByLabel(label)

    def _GetRequiredSkillHint(self):
        hint = localization.GetByLabel('UI/SkillTrading/RequiredSkillHintBody')
        dependentSkills = self._GetDependentSkills()
        skillNames = sorted((evetypes.GetName(s) for s in dependentSkills))
        showCount = 5
        rest = len(skillNames) - showCount
        if rest == 1:
            showCount += 1
        for skill in skillNames[:showCount]:
            hint += '<br>%s' % skill

        if rest > 1:
            hint += localization.GetByLabel('UI/SkillTrading/RequiredSkillHintTrail', rest=rest)
        return hint

    def _GetDependentSkills(self):
        mySkills = [ s.typeID for s in self.controller.skills ]
        dependentSkills = []
        for dependentSkillID, requiredLevel in self.skill.dependencies.iteritems():
            if dependentSkillID not in mySkills:
                continue
            dependentSkill = self.controller.skillsByID[dependentSkillID]
            if dependentSkill.points == 0:
                continue
            if self.skill.level <= requiredLevel:
                dependentSkills.append(dependentSkillID)

        return dependentSkills

    def _GetQueuedSkillHint(self):
        return localization.GetByLabel('UI/SkillTrading/QueuedSkillHint')

    def GetDragData(self):
        if self.isLocked:
            return None
        return [SkillDragData(self.typeID)]


class SkillGroupData(TreeData):

    def __init__(self, groupID, filterSettings, **kw):
        label = kw.pop('label', evetypes.GetGroupNameByGroup(groupID))
        super(SkillGroupData, self).__init__(label=label, **kw)
        self.filterSettings = filterSettings
        self.onChildUpdated = signals.Signal(signalName='onChildUpdated')
        for child in self.GetChildren():
            child.skill.onUpdate.connect(self.onChildUpdated)

    @property
    def isFiltered(self):
        return all((child.isFiltered for child in self.GetChildren()))

    def GetChildren(self):
        children = super(SkillGroupData, self).GetChildren()
        return sorted(children, key=lambda x: evetypes.GetName(x.typeID).lower())


class SkillTreeEntry(TreeViewEntry):
    default_height = 26
    tooltipPointer = uiconst.POINT_RIGHT_2

    def ApplyAttributes(self, attributes):
        super(SkillTreeEntry, self).ApplyAttributes(attributes)
        self.modifiedBG = None
        self.lockedIcon = None
        self.undoButton = None
        levelBarCont = Container(parent=self.topRightCont, align=uiconst.TOLEFT, width=70, left=18)
        self.levelBar = SkillBar(parent=levelBarCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, controller=ExtractorSkillBarController(self.data.skill), levelClass=ExtractorSkillLevel)
        self.OnSkillUpdated()
        self.data.filterSettings.onUpdate.connect(self.UpdateVisibility)
        self.data.skill.onUpdate.connect(self.OnSkillUpdated)

    def UpdateAlignment(self, *args, **kwargs):
        alignment = super(SkillTreeEntry, self).UpdateAlignment(*args, **kwargs)
        self.UpdateLabelRightFade()
        return alignment

    def UpdateLabelRightFade(self):
        availableWidth = self.displayWidth - self.label.left
        self.label.SetRightAlphaFade(fadeEnd=availableWidth, maxFadeWidth=20)

    def UpdateBackground(self):
        if self.data.skill.points != self.data.skill.unmodifiedPoints:
            self.CheckConstructModifiedBG()
            self.modifiedBG.opacity = 0.1
        elif self.modifiedBG:
            self.modifiedBG.opacity = 0.0

    def CheckConstructModifiedBG(self):
        if self.modifiedBG is None:
            self.modifiedBG = Fill(bgParent=self, color=COLOR_UNALLOCATED_1, opacity=0.0, padBottom=1)

    def Extract(self):
        if self.data.isLocked:
            return
        try:
            self.data.ExtractSkill()
            sm.GetService('audio').SendUIEvent('st_select_skills_play')
        except SkillExtractorError:
            pass

    def UpdateUndoButton(self):
        self.CheckConstructUndoButton()
        if self.data.isExtracted:
            self.undoButton.Enable()
            animations.MorphScalar(self.undoButton, 'left', startVal=self.undoButton.left, endVal=4, duration=0.3)
        else:
            self.undoButton.Disable()
            animations.MorphScalar(self.undoButton, 'left', startVal=self.undoButton.left, endVal=-self.undoButton.width, duration=0.3)

    def CheckConstructUndoButton(self):
        if self.undoButton is None:
            self.undoButton = ButtonIcon(parent=self.topRightCont, align=uiconst.CENTERRIGHT, left=0, width=17, height=17, iconSize=17, texturePath='res:/UI/Texture/classes/skilltrading/undo.png', func=self.Undo, hint=localization.GetByLabel('UI/SkillTrading/Undo'))

    def Undo(self):
        self.data.Undo()

    def GetDragData(self):
        return self.data.GetDragData()

    def GetSpacerContWidth(self):
        return 88

    def GetMenu(self):
        m = GetMenuService().GetMenuFromItemIDTypeID(None, self.data.typeID)
        extractText = localization.GetByLabel('UI/SkillTrading/ExtractSkill')
        m.append((extractText, self.Extract, ()))
        return m

    def UpdateLabel(self):
        super(SkillTreeEntry, self).UpdateLabel()
        self.label.SetText(self.data.GetLabel())

    def UpdateVisibility(self):
        self.display = not self.data.isFiltered

    def UpdateLockedStatus(self):
        opacity = 0.4 if self.data.isLocked else 1.0
        animations.FadeTo(self.label, startVal=self.opacity, endVal=opacity)
        if self.data.isLocked:
            self.CheckConstructLockIcon()
            animations.FadeIn(self.lockedIcon, duration=0.3)
        elif self.lockedIcon is not None:
            animations.FadeOut(self.lockedIcon, duration=0.3)

    def CheckConstructLockIcon(self):
        if self.lockedIcon is None:
            self.lockedIcon = Sprite(parent=self.topRightCont, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, ignoreSize=True, texturePath='res:/UI/Texture/classes/skilltrading/lock.png', left=3, width=14, height=14, color=Color.GRAY3, opacity=0.0)

    def OnDblClick(self):
        self.Extract()

    def OnSkillUpdated(self):
        self.UpdateVisibility()
        self.UpdateLabel()
        self.UpdateBackground()
        self.UpdateLockedStatus()
        self.UpdateUndoButton()


class SkillGroupEntry(TreeViewEntry):

    def ApplyAttributes(self, attributes):
        super(SkillGroupEntry, self).ApplyAttributes(attributes)
        self.UpdateVisibility()
        self.data.filterSettings.onUpdate.connect(self.UpdateVisibility)
        self.data.onChildUpdated.connect(self.UpdateVisibility)

    def GetTreeViewEntryClassByTreeData(self, data):
        return SkillTreeEntry

    def ShowChild(self, child, show = True):
        if show:
            show = not child.data.isFiltered
        super(SkillGroupEntry, self).ShowChild(child, show=show)

    def UpdateVisibility(self):
        self.display = not self.data.isFiltered

    def OnClick(self, *args):
        self.ToggleChildren()


class SkillDragData(object):
    __guid__ = None

    def __init__(self, typeID):
        self.typeID = typeID

    def get_link(self):
        return evelink.type_link(self.typeID)

    def LoadIcon(self, icon, parent, size):
        icon.LoadIconByTypeID(self.typeID, size=size)


class ExtractorSkillBarController(SkillBarController):

    def __init__(self, skill):
        self._skill = skill
        super(ExtractorSkillBarController, self).__init__(SkillController(skill.typeID))
        self._skill.onUpdate.connect(self.onUpdate)

    @property
    def isExtracted(self):
        return self._skill.points != self._skill.unmodifiedPoints

    def IsLevelExtracted(self, level):
        return self._skill.level < level <= self._skill.unmodifiedLevel

    def IsPartiallyTrained(self, level):
        return self._skill.progress > 0 and self._skill.level + 1 == level

    @property
    def isRestricted(self):
        return False

    @property
    def restrictedLevel(self):
        return 5


class ExtractorSkillLevel(SkillLevel):

    def Layout(self):
        if self.isPartiallyTrained and self.skill.isExtracted:
            self.AddBox(COLOR_UNTRAINED)
            self.AddPartiallyTrained(COLOR_EXTRACTED)
        elif self.skill.IsLevelExtracted(self.level):
            self.AddBox(COLOR_EXTRACTED)
            if self.skill.IsPartiallyTrained(self.level):
                self.AddPartiallyTrained(COLOR_TRAINED)
        else:
            super(ExtractorSkillLevel, self).Layout()


def __SakeReloadHook():
    import log
    try:
        wnd = SkillExtractorWindow.GetIfOpen()
        if wnd is not None:
            itemID = wnd.controller.itemID
            SkillExtractorWindow.CloseIfOpen()
            SkillExtractorWindow.Open(itemID=itemID, useDefaultPos=True)
    except Exception:
        log.LogException()
