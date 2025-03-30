#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillPlanEditor\skillPlanEditorContents.py
import blue
import evetypes
import itertoolsext
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, fontconst
from carbonui.control.dragdrop import dragdata, dragDropUtil
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.skillPlan import skillPlanUISignals, skillPlanUtil
from eve.client.script.ui.skillPlan.controls.skillPlanLine import SkillPlanLine
from eve.client.script.ui.skillPlan.skillPlanConst import NO_REQ
from eve.client.script.ui.skillPlan.skillPlanEditor.dragIndicatorLine import DragIndicatorLine
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanDropIndicatorCont import SkillPlanDropIndicatorCont
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanEditorSkillEntry import INVALID_LINE_COLOR, SkillPlanEditorSkillEntry, VALID_LINE_COLOR
from eve.client.script.ui.skillPlan.skillPlanUtil import GetPreReqsAndRequiredForSkillLevel, GetRequirementStateForEntry, IsTypeValidMilestone
from eve.common.lib import appConst
from eve.common.lib import appConst as const
from eveui import clipboard
from localization import GetByLabel
from shipfitting import INVALID_FITTING_ID
from shipfitting.client.link import parse_fitting_url
from skills.skillConst import skill_max_level
SCROLL_LOADING_OPACITY = 0.5
ASYNC_LOAD_THRESHOLD = 30

class SkillPlanEditorContents(Container):

    def ApplyAttributes(self, attributes):
        super(SkillPlanEditorContents, self).ApplyAttributes(attributes)
        self.skillPlan = None
        self.entries = set()
        skillPlanUISignals.on_skill_requirements_changed.connect(self.OnSkillRequirementsChanged)
        skillPlanUISignals.on_skill_plan_cleared.connect(self.OnSkillPlanCleared)
        self.topCont = Container(name='topCont', parent=self, align=uiconst.TOTOP, height=70)
        self._ConstructTopCont()
        SkillPlanLine(parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padTop=6)
        self.dropIndicatorCont = SkillPlanDropIndicatorCont(parent=self, align=uiconst.TOBOTTOM)
        self.dropIndicatorCont.OnDragEnter = self.OnDropContDragEnter
        self.dropIndicatorCont.OnDropData = self.OnDropContDropData
        self.scroll = ScrollContainer(parent=self, showUnderlay=False, align=uiconst.TOALL, state=uiconst.UI_DISABLED, opacity=SCROLL_LOADING_OPACITY, padTop=20)
        self.loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER)
        self.scroll.onDropDataSignal.connect(self.OnDropData)
        self.scroll.onDragEnterSignal.connect(self.OnScrollDragEnter)
        self.scroll.onDragExitSignal.connect(self.OnScrollDragExit)
        self.dragIndicator = None
        SkillPlanLine(parent=self, align=uiconst.TOBOTTOM, idx=0, state=uiconst.UI_DISABLED)
        self.CheckShowNoContentHint()

    def Close(self):
        super(SkillPlanEditorContents, self).Close()
        skillPlanUISignals.on_skill_requirements_changed.disconnect(self.OnSkillRequirementsChanged)
        skillPlanUISignals.on_skill_plan_cleared.disconnect(self.OnSkillPlanCleared)

    def _ConstructTopCont(self):
        self.caption = EveCaptionLarge(parent=self.topCont, name='skillPlanOverviewLabel', align=uiconst.TOPLEFT, text=GetByLabel('UI/SkillPlan/SkillPlan'))
        UtilMenu(parent=self.topCont, align=uiconst.TOPRIGHT, texturePath='res:/UI/Texture/Icons/77_32_49.png', pos=(-4, 4, 24, 24), GetUtilMenu=self.GetUtilMenu, iconSize=24)
        self.quickFilterEdit = QuickFilterEdit(parent=self.topCont, align=uiconst.BOTTOMRIGHT, width=120, height=30, top=4, callback=self.OnQuickFilterEdit)

    def OnQuickFilterEdit(self):
        self.ReconstructScrollEntries()

    def GetUtilMenu(self, menuParent):
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=GetByLabel('UI/SkillPlan/CopySkillsToClipboard'), callback=self.CopySkillsToClipboard)
        hint = GetByLabel('UI/SkillQueue/ImportSkillplanFormatHint', typeID=appConst.typeSpaceshipCommand)
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=GetByLabel('UI/SkillPlan/ImportSkillsFromClipboard'), hint=hint, callback=self.ImportSkillsFromClipboard)
        menuParent.AddIconEntry(icon='res:/UI/Texture/classes/UtilMenu/BulletIcon.png', text=GetByLabel('UI/SkillPlan/ClearSkills'), callback=self.ClearSkills)

    def ClearSkills(self):
        self.skillPlan.ClearSkillRequirements()
        self.skillPlan.ClearMilestones()
        skillPlanUISignals.on_skill_plan_cleared(self.skillPlan.GetID())

    def ImportSkillsFromClipboard(self):
        skillplanImporter = sm.GetService('skillqueue').GetSkillPlanImporter()
        skillRequirements, failedLines = skillplanImporter.GetSkillsAndLevelsFromText(clipboard.get())
        if skillRequirements:
            self.skillPlan.AppendSkillRequirements(skillRequirements)

    def CopySkillsToClipboard(self):
        clipboard.set(self.skillPlan.GetRequirementsClipboardText())

    def OnSkillRequirementsChanged(self, skillPlanID):
        if skillPlanID == self.skillPlan.GetID():
            self.ReconstructScrollEntries()
            self.UpdateSkillCountTotal()

    def OnSkillPlanCleared(self, skillPlanID):
        if self.skillPlan and self.skillPlan.GetID() == skillPlanID:
            self.entries.clear()
            self.scroll.Flush()
            self.CheckShowNoContentHint()

    def CheckShowNoContentHint(self):
        numShown = len([ entry for entry in self.entries if entry.display ])
        if not self.skillPlan:
            return
        if not self.skillPlan.GetSkillRequirements():
            self.scroll.ShowNoContentHint(GetByLabel('UI/SkillPlan/NoSkillsInPlanHint'))
        elif not numShown:
            self.scroll.ShowNoContentHint(GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/NoSkillsMatchingFilters'))
        else:
            self.scroll.HideNoContentHint()

    def OnDropData(self, dropObj, entries):
        dragData = entries[0]
        guid = getattr(dragData, '__guid__', None)
        if isinstance(dragData, dragdata.SkillLevelDragData):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                if dragData.level < skill_max_level:
                    PlaySound(uiconst.SOUND_ADD_OR_USE)
                    self.skillPlan.AppendSkillRequirement(dragData.typeID)
            else:
                self._MoveEntryToBottom(dragData.typeID, dragData.level)
        elif isinstance(dragData, dragdata.TypeDragData) and evetypes.IsSkill(dragData.typeID):
            PlaySound(uiconst.SOUND_ADD_OR_USE)
            self.skillPlan.AppendSkillRequirement(dragData.typeID)
        elif guid is not None and guid == 'listentry.FittingEntry':
            self._OnDropFitting(dragData.fitting)
        elif guid is not None and guid == 'TextLink':
            fittingString, _ = parse_fitting_url(dragData.url)
            fitting, _ = sm.GetService('fittingSvc').GetFittingFromString(fittingString)
            if fitting != INVALID_FITTING_ID:
                self._OnDropFitting(fitting)
        else:
            self._OnTypeDropData(dragData)
        self.HideDragIndicator()

    def _OnDropFitting(self, fitting):
        typeIDs = [fitting.shipTypeID]
        rackTypes = sm.GetService('fittingSvc').GetTypesByRack(fitting)

        def _ExtractTypeIDsFromCategory(categoryName):
            if categoryName in rackTypes:
                for typeID, _ in rackTypes[categoryName].iteritems():
                    if typeID not in typeIDs:
                        typeIDs.append(typeID)

                rackTypes.pop(categoryName)

        _ExtractTypeIDsFromCategory('subSystems')
        _ExtractTypeIDsFromCategory('hiSlots')
        _ExtractTypeIDsFromCategory('medSlots')
        _ExtractTypeIDsFromCategory('lowSlots')
        _ExtractTypeIDsFromCategory('rigSlots')
        _ExtractTypeIDsFromCategory('charges')
        _ExtractTypeIDsFromCategory('fighters')
        _ExtractTypeIDsFromCategory('drones')
        _ExtractTypeIDsFromCategory('implants')
        _ExtractTypeIDsFromCategory('modules')
        for rack, contents in rackTypes.iteritems():
            if len(contents) > 0:
                for typeID, _ in contents.iteritems():
                    if typeID not in typeIDs:
                        typeIDs.append(typeID)

        self.BulkAddSkillRequirements(typeIDs)

    def _OnTypeDropData(self, dragData):
        typeID = dragDropUtil.GetTypeID(dragData)
        if typeID:
            self._AddRequirementsForType(typeID)

    def _AddRequirementsForType(self, typeID):
        if not IsTypeValidMilestone(typeID):
            return
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        if self.skillPlan.HasEmptyMilestoneSlots():
            if evetypes.GetCategoryID(typeID) == const.categorySkill:
                self.skillPlan.AddAllSkillsRequiredFor(typeID, 1)
                self.skillPlan.AddSkillRequirementMilestone(typeID, 1)
            else:
                self.skillPlan.AddTypeIDMilestone(typeID)
        else:
            self.skillPlan.AddAllSkillsRequiredFor(typeID)

    def BulkAddSkillRequirements(self, typeIDs):
        if not self.skillPlan:
            return
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        uthread2.start_tasklet(self._BulkAddSkillRequirements, typeIDs)

    def _BulkAddSkillRequirements(self, typeIDs):
        if not self.skillPlan:
            return
        self._ShowLoadingWheel()
        self.skillPlan.BulkAddAllSkillsRequiredFor(typeIDs)
        self._HideLoadingWheel()

    def SetSkillPlan(self, skillPlan):
        self.skillPlan = skillPlan
        uthread2.start_tasklet(self.ConstructScrollEntries)
        self.UpdateSkillCountTotal()

    def ConstructScrollEntries(self):
        requiresAsyncLoading = len(self.skillPlan.GetSkillRequirements()) > ASYNC_LOAD_THRESHOLD
        if requiresAsyncLoading:
            skillPlanUISignals.on_contents_list_started_reconstructing()
        for typeID, level in self.skillPlan.GetSkillRequirements():
            entry = self.ConstructScrollEntry(typeID, level)
            self.entries.add(entry)
            if requiresAsyncLoading:
                blue.pyos.BeNice()

        self.CheckShowNoContentHint()
        self.scroll.state = uiconst.UI_NORMAL
        self._HideLoadingWheel()
        if requiresAsyncLoading:
            skillPlanUISignals.on_contents_list_finished_reconstructing()

    def ReconstructScrollEntries(self):
        currentLen = len(self.entries)
        newLen = len(self.skillPlan.GetSkillRequirements())
        requiresAsyncLoading = newLen - currentLen > ASYNC_LOAD_THRESHOLD
        if requiresAsyncLoading:
            skillPlanUISignals.on_contents_list_started_reconstructing()
        selectedEntry = itertoolsext.first_or_default(self.entries, lambda x: x.isSelected)
        if selectedEntry and (selectedEntry.typeID, selectedEntry.level) in self.skillPlan.GetSkillRequirements():
            selectedTypeID, selectedLevel = selectedEntry.typeID, selectedEntry.level
            prereqs, reqForTypeIDs = GetPreReqsAndRequiredForSkillLevel(selectedEntry.typeID, selectedEntry.level)
        else:
            selectedTypeID = selectedLevel = None
            prereqs, reqForTypeIDs = {}, set()
        entriesToReUse = {(entry.typeID, entry.level):entry for entry in self.entries}
        for entry in self.entries:
            if entry.GetParent() == self.scroll:
                entry.SetParent(None)

        self.entries.clear()
        for typeID, level in self.skillPlan.GetSkillRequirements():
            entry = entriesToReUse.pop((typeID, level), None)
            if entry:
                if entry.GetParent() != self.scroll:
                    entry.SetParent(self.scroll)
                entry.UpdatePrimaryButton()
            else:
                entry = self.ConstructScrollEntry(typeID, level)
            if selectedEntry:
                reqState = GetRequirementStateForEntry(selectedTypeID, selectedLevel, entry, prereqs, reqForTypeIDs)
            else:
                reqState = NO_REQ
            entry.UpdateReqState(reqState)
            self.entries.add(entry)
            entry.display = self.IsEntryShown(entry)
            if requiresAsyncLoading:
                self._UpdateSkillCountPartial()
                blue.pyos.BeNice()

        for entry in entriesToReUse.itervalues():
            entry.Close()

        self.CheckShowNoContentHint()
        if requiresAsyncLoading:
            skillPlanUISignals.on_contents_list_finished_reconstructing()

    def IsEntryShown(self, entry):
        filterTxt = self.quickFilterEdit.GetValue()
        if not filterTxt:
            return True
        return filterTxt.lower() in evetypes.GetName(entry.typeID).lower()

    def ConstructScrollEntry(self, typeID, level, index = -1):
        entry = SkillPlanEditorSkillEntry(parent=self.scroll, typeID=typeID, level=level, idx=index, skillPlan=self.skillPlan, padBottom=8)
        entry.onClickSignal.connect(self.OnEntryClicked)
        entry.onDblClickSignal.connect(self.OnEntryDblClicked)
        entry.onDropDataSignal.connect(self.OnEntryDropData)
        entry.onDragEnterSignal.connect(self.OnEntryDragEnter)
        return entry

    def OnEntryDblClicked(self, entry):
        return self.skillPlan.AppendSkillRequirement(entry.typeID)

    def GetEntry(self, typeID, level):
        for entry in self.entries:
            if entry.typeID == typeID and entry.level == level:
                return entry

    def OnEntryClicked(self, clickedEntry):
        prereqs, reqForTypeIDs = GetPreReqsAndRequiredForSkillLevel(clickedEntry.typeID, clickedEntry.level)
        if uicore.uilib.Key(uiconst.VK_CONTROL):
            deselectEntry = itertoolsext.first_or_default(self.entries, lambda x: x.isSelected) == clickedEntry
        else:
            deselectEntry = False
        for entry in self.entries:
            if entry == clickedEntry:
                if deselectEntry:
                    entry.SetDeselected()
                else:
                    entry.SetSelected()
                entry.UpdateReqState(NO_REQ)
            else:
                entry.SetDeselected()
                if deselectEntry:
                    entry.UpdateReqState(NO_REQ)
                else:
                    reqState = GetRequirementStateForEntry(clickedEntry.typeID, clickedEntry.level, entry, prereqs, reqForTypeIDs)
                    entry.UpdateReqState(reqState)

    def OnEntryDragEnter(self, dragEntry, dragData):
        isValidMove = True
        if isinstance(dragData, dragdata.SkillLevelDragData):
            potentialDropIndex = self.skillPlan.GetSkillRequirementIndex(dragEntry.typeID, dragEntry.level)
            originalIndex = self.skillPlan.GetSkillRequirementIndex(dragData.typeID, dragData.level)
            isValidMove = self.skillPlan.IsSkillRequirementMoveValid(originalIndex, potentialDropIndex)
        dragEntry.ShowIndicatorLine(isValidMove)

    def OnEntryDropData(self, dropEntry, entries):
        dragData = entries[0]
        guid = getattr(dragData, '__guid__', None)
        if isinstance(dragData, dragdata.SkillLevelDragData):
            if uicore.uilib.Key(uiconst.VK_SHIFT):
                if dragData.level < skill_max_level:
                    index = self.skillPlan.GetSkillRequirementIndex(dropEntry.typeID, dropEntry.level)
                    nextLevel = self.skillPlan.GetNextLevel(dragData.typeID)
                    if nextLevel and self.skillPlan.IsSkillInsertionValid(dragData.typeID, nextLevel, index):
                        self.skillPlan.InsertSkillRequirement(dragData.typeID, level=nextLevel, aboveTypeID=dropEntry.typeID, aboveLevel=dropEntry.level)
            else:
                self._MoveEntryAbove(dragData.typeID, dragData.level, dropEntry.typeID, dropEntry.level)
        elif isinstance(dragData, dragdata.TypeDragData) and evetypes.IsSkill(dragData.typeID):
            PlaySound(uiconst.SOUND_ADD_OR_USE)
            self.skillPlan.InsertSkillRequirement(dragData.typeID, aboveTypeID=dropEntry.typeID, aboveLevel=dropEntry.level)
        elif guid is not None and guid == 'listentry.FittingEntry':
            self._OnDropFitting(dragData.fitting)
        elif guid is not None and guid == 'TextLink':
            fittingString, _ = parse_fitting_url(dragData.url)
            fitting, _ = sm.GetService('fittingSvc').GetFittingFromString(fittingString)
            if fitting != INVALID_FITTING_ID:
                self._OnDropFitting(fitting)
        else:
            self._OnTypeDropData(dragData)

    def _MoveEntryAbove(self, typeID, level, aboveTypeID = None, aboveLevel = None):
        self.skillPlan.MoveSkillRequirement(typeID, level, aboveTypeID, aboveLevel)

    def _MoveEntryToBottom(self, typeID, level):
        self._MoveEntryAbove(typeID, level)

    def OnDropContDragEnter(self, dragObject, entries):
        uthread2.StartTasklet(self.dropIndicatorCont.OnDragEnterFromParent, entries, self.skillPlan, self.scroll)

    def OnDropContDropData(self, dropObj, entries):
        if self.scroll.IsVerticalScrollBarVisible() and self.scroll.GetPositionVertical() >= 1.0:
            self.OnDropData(dropObj, entries)
        self.dropIndicatorCont.HideIndicator()

    def OnScrollDragEnter(self, dragObject, entries):
        dragData = entries[0]
        if isinstance(dragData, dragdata.SkillLevelDragData):
            originalIndex = self.skillPlan.GetSkillRequirementIndex(dragData.typeID, dragData.level)
            dropIndex = len(self.skillPlan.GetSkillRequirements())
            isValidMove = self.skillPlan.IsSkillRequirementMoveValid(originalIndex, dropIndex)
            self.ShowDragIndicator(isValidMove)
        elif skillPlanUtil.IsValidContentsDragData(dragData):
            self.ShowDragIndicator()

    def ShowDragIndicator(self, isValid = True):
        if not self.dragIndicator:
            self.dragIndicator = DragIndicatorLine(parent=self.scroll, align=uiconst.TOTOP)
        self.dragIndicator.color = VALID_LINE_COLOR if isValid else INVALID_LINE_COLOR

    def OnScrollDragExit(self, dragObject, entries):
        self.HideDragIndicator()

    def HideDragIndicator(self):
        if self.dragIndicator:
            self.dragIndicator.Close()
            self.dragIndicator = None

    def _UpdateSkillCountPartial(self):
        numSkills = len(self.entries)
        self._SetSkillCount(numSkills)

    def UpdateSkillCountTotal(self):
        if self.skillPlan:
            numSkills = len(self.skillPlan.GetSkillRequirements())
            self._SetSkillCount(numSkills)

    def _SetSkillCount(self, numSkills):
        numSkillsTxt = ' <color=%s><fontsize=%s>%s</fontsize></color>' % (eveColor.LED_GREY_HEX, fontconst.EVE_LARGE_FONTSIZE, str(numSkills))
        self.caption.SetText(GetByLabel('UI/SkillPlan/SkillPlan') + numSkillsTxt)

    def _HideLoadingWheel(self):
        animations.FadeTo(self.scroll, self.scroll.opacity, 1.0, duration=0.3)
        self.loadingWheel.Hide()

    def _ShowLoadingWheel(self):
        self.loadingWheel.Show()
        animations.FadeTo(self.scroll, self.scroll.opacity, SCROLL_LOADING_OPACITY, duration=0.3)
