#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\skillImportingMsg.py
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from characterskills import SKILLQUEUE_MAX_NUM_SKILLS
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1
from localization import GetByLabel
from skills.client.skillController import SkillController
import textImporting.importSkillplanConst as importConst
COLOR_GRAY = (1.0, 1.0, 1.0, 0.5)

class SkillImportStatusWindow(Window):
    default_width = 500
    default_height = 540
    default_windowID = 'skillImportStatusWindow'
    default_captionLabelPath = 'UI/SkillQueue/SkillImportHeader'
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_SkillsRemovedFromQueue']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.importingStatus = attributes.importingStatus
        self.failedLines = attributes.failedLines
        self.successfulLabel = EveLabelMedium(parent=self.sr.main, align=uiconst.TOTOP, padding=8)
        self.unsuccessfulLabel = EveLabelMedium(parent=self.sr.main, align=uiconst.TOTOP, padding=8)
        btnGroup = ButtonGroup(parent=self.sr.main, idx=0)
        btnGroup.AddButton(label=GetByLabel('UI/Common/Buttons/Close'), func=self.Close)
        self.scroll = Scroll(parent=self.sr.main, padding=(4, 0, 4, 0))

    def LoadInitialImportingStatus(self, importingStatus, failedLines):
        successFullText = GetByLabel('UI/SkillQueue/SkillsImportedToQueue', numSkills=importingStatus.skillLevelsAdded)
        self.LoadImportingStatus(importingStatus, failedLines, successFullText)

    def LoadImportingStatus(self, importingStatus, failedLines, successFullText = None):
        self.importingStatus = importingStatus
        self.failedLines = failedLines
        if successFullText:
            self.successfulLabel.text = successFullText
            self.successfulLabel.display = True
        else:
            self.successfulLabel.display = False
        somethingFailed = importingStatus.alreadyTrainedLevels or importingStatus.alreadyInQueueLevels or importingStatus.failedLevels or failedLines
        if somethingFailed:
            self.unsuccessfulLabel.text = GetByLabel('UI/SkillQueue/CouldNotBeAddedHeader')
            self.scroll.display = True
            self.width = max(self.width, self.default_width)
            self.height = max(self.height, self.default_height)
        else:
            self.unsuccessfulLabel.text = ''
            self.scroll.display = False
            self.width = 256
            self.height = 128
        if not somethingFailed and not successFullText:
            self.Close()
            return
        scrollList = []
        if importingStatus.alreadyTrainedLevels:
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContent,
             'label': GetByLabel('UI/SkillQueue/SkillsAlreadyTrained'),
             'id': ('alreadyTrained', 0),
             'groupItems': importingStatus.alreadyTrainedLevels,
             'iconMargin': 32,
             'showlen': 1,
             'state': 'locked',
             'BlockOpenWindow': 1}))
        if importingStatus.alreadyInQueueLevels:
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContent,
             'label': GetByLabel('UI/SkillQueue/SkillsAlreadyInQueue'),
             'id': ('alreadyInQueue', 0),
             'groupItems': importingStatus.alreadyInQueueLevels,
             'iconMargin': 32,
             'showlen': 1,
             'state': 'locked',
             'BlockOpenWindow': 1}))
        if importingStatus.failedLevels:
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContent,
             'label': GetByLabel('UI/SkillQueue/FailedToImportSkills'),
             'id': ('failedLevels', 0),
             'groupItems': importingStatus.failedLevels,
             'iconMargin': 32,
             'showlen': 1,
             'state': 'locked',
             'BlockOpenWindow': 1}))
        if failedLines:
            scrollList.append(GetFromClass(ListGroup, {'GetSubContent': self.GetSubContentFailedLines,
             'label': GetByLabel('UI/SkillQueue/CouldNotReadLines'),
             'id': ('failedLevels', 0),
             'groupItems': failedLines,
             'iconMargin': 32,
             'showlen': True,
             'state': 'locked',
             'BlockOpenWindow': 1}))
        self.scroll.Load(contentList=scrollList)

    def GetSubContent(self, nodedata):
        scrollList = []
        for typeID, skillLevel, reason in nodedata.groupItems:
            entry = GetFromClass(MissingSkillEntry, data={'typeID': typeID,
             'sublevel': 1,
             'skillLevel': skillLevel,
             'reason': reason})
            scrollList.append(entry)

        return scrollList

    def GetSubContentFailedLines(self, nodedata):
        scrollList = []
        for text in nodedata.groupItems:
            entry = GetFromClass(Generic, {'label': text,
             'sublevel': 1})
            scrollList.append(entry)

        return scrollList

    def OnSkillsChanged(self, *args):
        self._Update()

    def OnSkillQueueChanged(self):
        self._Update()

    def OnClientEvent_SkillAddedToQueue(self, typeID, level):
        self._Update()

    def OnClientEvent_SkillsRemovedFromQueue(self, skillRequirements):
        self._Update()

    def _Update(self):
        self._UpdateBuffered()

    @uthread2.BufferedCall(500)
    def _UpdateBuffered(self):
        skillQueueSvc = sm.GetService('skillqueue')
        queueLength = skillQueueSvc.GetNumberOfSkillsInQueue()
        if self.importingStatus.failedLevels:
            newFailedLevels = []
            for typeID, skillLevel, reason in self.importingStatus.failedLevels:
                skillController = SkillController(typeID)
                if skillController.IsInjected():
                    if skillController.GetMyLevel() >= skillLevel:
                        continue
                    posInQueue = skillQueueSvc.FindInQueue(typeID, skillLevel)
                    if posInQueue is not None:
                        continue
                    if reason == importConst.FAILED_SKILL_NOT_INJECTED:
                        reason = importConst.FAILED_TOO_MANY_SKILLS if queueLength >= SKILLQUEUE_MAX_NUM_SKILLS else importConst.FAILED_WAS_NOT_INJECTED
                newFailedLevels.append((typeID, skillLevel, reason))

            if newFailedLevels != self.importingStatus.failedLevels:
                self.importingStatus.failedLevels = newFailedLevels
                self.LoadImportingStatus(self.importingStatus, self.failedLines)


class MissingSkillEntry(Generic):
    __guid__ = 'listentry.SkillTreeEntry'
    default_showHilite = True
    isDragObject = True

    def ApplyAttributes(self, attributes):
        Generic.ApplyAttributes(self, attributes)
        self.missingSkillCont = None
        self.initialized = False
        self.skillService = sm.GetService('skills')
        self.infoService = sm.GetService('info')

    def Load(self, data):
        Generic.Load(self, data)
        if not self.missingSkillCont or self.missingSkillCont.destroyed:
            self.missingSkillCont = MissingSkillCont(parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, typeID=data.typeID, requiredLevel=data.skillLevel, indent=data.sublevel * 16, reason=data.reason)

    def GetHeight(self, *args):
        return 28

    def OnDblClick(self, *args):
        self.missingSkillCont.OnDblClick()

    def GetMenu(self):
        return self.missingSkillCont.GetMenu()

    def GetDragData(self, *args):
        return self.missingSkillCont.GetDragData()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        self.missingSkillCont.LoadTooltipPanel(tooltipPanel)

    def UpdateTimeToTrainLabel(self):
        pass


class MissingSkillCont(Container):
    default_name = 'MissingSkillCont'
    isDragObject = True
    default_align = uiconst.TOTOP
    default_state = uiconst.UI_NORMAL
    default_height = 0
    __notifyevents__ = ['OnSkillsChanged',
     'OnSkillQueueChanged',
     'OnClientEvent_SkillAddedToQueue',
     'OnClientEvent_SkillsRemovedFromQueue']
    reasonsDict = {importConst.FAILED_TOO_MANY_SKILLS: GetByLabel('UI/SkillQueue/TooManySkillsInQueue'),
     importConst.FAILED_SKILL_NOT_INJECTED: GetByLabel('UI/SkillQueue/SkillNotInjected'),
     importConst.FAILED_INCORRECT_ORDER: GetByLabel('UI/SkillQueue/IncorrectOrder'),
     importConst.FAILED_MISSING_PREREQ: GetByLabel('UI/SkillQueue/MissingPrereqs'),
     importConst.FAILED_SKILL_IN_QUEUE: GetByLabel('UI/SkillQueue/AlreadyInQueue'),
     importConst.FAILED_OMEGA_RESTRICTION: GetByLabel('UI/SkillQueue/SkillRequiresCloneStateUpgrade'),
     importConst.FAILED_PREVIOUSLY_TRAINED: GetByLabel('UI/SkillQueue/AlreadyTrained'),
     importConst.FAILD_QUEUE_TOO_LONG: GetByLabel('UI/SkillQueue/QueueTooLong'),
     importConst.FAILED_WAS_NOT_INJECTED: ''}

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        typeID = attributes.typeID
        self.requiredLevel = attributes.requiredLevel
        self.reason = attributes.reason
        indent = attributes.get('indent', 0)
        self.tooltipPointerDirection = attributes.get('tooltipPointerDirection', None)
        self.ConstructLayout(indent=indent)
        self.skillController = SkillController(typeID)
        self.UpdateTextAndIcon()

    def ConstructLayout(self, indent):
        iconCont = Container(parent=self, align=uiconst.TOLEFT, width=16, left=indent)
        self.icon = Sprite(parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 16, 16))
        self.reasonLabelCont = ContainerAutoSize(name='reasonLabelCont', parent=self, align=uiconst.TORIGHT, left=8)
        self.reasonLabel = EveLabelMedium(name='reasonLabel', parent=self.reasonLabelCont, left=8, align=uiconst.CENTERRIGHT, opacity=0.5, text='')
        self.skillLabelCont = Container(name='skillLabelCont', parent=self, align=uiconst.TOALL, left=5)
        self.skillLabel = EveLabelMedium(name='skillLabel', parent=self.skillLabelCont, align=uiconst.CENTERLEFT)

    def UpdateTextAndIcon(self):
        self.UpdateIcon()
        self.UpdateSkillLabel()
        self.UpdateReason()

    def UpdateSkillLabel(self):
        if self.requiredLevel is not None:
            if self.skillController.GetMyLevel() >= self.requiredLevel:
                self.skillLabel.opacity = 0.5
            text = self.skillController.GetRequiredSkillNameAndLevelComparedToTrainedLevel(self.requiredLevel)
        else:
            text = self.skillController.GetName()
        self.skillLabel.SetText(text)

    def UpdateReason(self):
        if self.reason == importConst.FAILED_WAS_NOT_INJECTED and self.skillController.IsInjected():
            text = ''
        else:
            text = self.reasonsDict.get(self.reason, None) or GetByLabel('UI/SkillQueue/UnknownReason')
        self.reasonLabel.text = text

    def SetIcon(self, texturePath, color, hint):
        self.icon.SetTexturePath(texturePath)
        self.icon.SetRGBA(*color)
        self.icon.hint = hint

    def UpdateIcon(self):
        if self.requiredLevel is None:
            texturePath = 'res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png'
            color = COLOR_GRAY
            hint = None
        elif not self.skillController.IsInjected():
            texturePath = 'res:/ui/Texture/classes/Skills/SkillBookNotInjected.png'
            color = COLOR_SKILL_1
            hint = GetByLabel('UI/SkillQueue/SkillBookMissing')
        elif self.skillController.GetMyLevel() >= self.requiredLevel:
            texturePath = 'res:/ui/Texture/classes/Skills/SkillRequirementMet.png'
            color = COLOR_GRAY
            hint = GetByLabel('UI/InfoWindow/SkillTrainedToRequiredLevel')
        else:
            texturePath = 'res:/ui/Texture/classes/Skills/SkillRequirementNotMet.png'
            color = COLOR_SKILL_1
            hint = GetByLabel('UI/InfoWindow/SkillNotTrainedToRequiredLevel')
        self.SetIcon(texturePath=texturePath, color=color, hint=hint)

    def OnDblClick(self, *args):
        sm.GetService('info').ShowInfo(self.skillController.GetTypeID())

    def GetMenu(self):
        return self.skillController.GetMenu()

    def GetDragData(self, *args):
        return self.skillController.GetDragData()

    def LoadTooltipPanel(self, tooltipPanel, *args):
        if uicore.uilib.tooltipHandler.IsUnderTooltip(self):
            return
        from eve.client.script.ui.shared.tooltip.skill import LoadSkillEntryTooltip
        LoadSkillEntryTooltip(tooltipPanel, self.skillController.GetTypeID(), self.requiredLevel)

    def GetTooltipPointer(self):
        return self.tooltipPointerDirection

    def OnSkillsChanged(self, *args):
        self._Update()

    def OnSkillQueueChanged(self):
        self._Update()

    def OnClientEvent_SkillAddedToQueue(self, typeID, level):
        if typeID == self.skillController.GetTypeID():
            self._Update()

    def OnClientEvent_SkillsRemovedFromQueue(self, skillRequirements):
        for typeID, level in skillRequirements:
            if typeID == self.skillController.GetTypeID():
                self._Update()
                return

    def _Update(self):
        self._UpdateBuffered()

    @uthread2.BufferedCall(200)
    def _UpdateBuffered(self):
        if not self or self.destroyed:
            return
        self.UpdateTextAndIcon()
