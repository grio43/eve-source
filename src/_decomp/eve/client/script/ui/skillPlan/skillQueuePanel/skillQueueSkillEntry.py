#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\skillPlan\skillQueuePanel\skillQueueSkillEntry.py
import sys
import blue
import evetypes
import gametime
import localization
import log
import trinity
import uthread
from carbon.common.script.util import timerstuff
from carbon.common.script.util.commonutils import GetAttrs
from carbonui import const as uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from clonegrade.const import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.industry.views.errorFrame import ErrorFrame
from eve.client.script.ui.shared.info.panels.panelRequiredFor import RequiredForScrollController
from eve.client.script.ui.skillPlan.skillPlanEditor.skillPlanDropIndicatorCont import IsMultiSkillEntryMove
from skills.client.skillController import SkillController
from eve.client.script.ui.shared.neocom.skillConst import COLOR_SKILL_1, COLOR_MOVE_INDICATOR
from eve.client.script.ui.shared.neocom.skillConst import COLOR_TRAININGALLOWED, COLOR_TRAININGNOTALLOWED
from eve.client.script.ui.shared.neocom.timelineContainer import TimelineContainer
from eve.client.script.ui.skillPlan.skillQueuePanel.baseSkillEntry import BaseSkillEntry
from eveservices.menu import GetMenuService
from fsdBuiltData.common.iconIDs import GetIconFile
from localization import GetByLabel
from menu import MenuLabel
OPACITY_START = 0.3

class SkillQueueSkillEntry(BaseSkillEntry):
    __guid__ = 'listentry.SkillQueueSkillEntry'
    __nonpersistvars__ = ['selection', 'id']
    isDragObject = True

    def ApplyAttributes(self, attributes):
        self.entryHeight = 0
        self.blinking = 0
        super(SkillQueueSkillEntry, self).ApplyAttributes(attributes)
        self.posIndicatorLine = None
        self.acceleratedSprite = None
        self.skillQueueSvc = sm.GetService('skillqueue')
        self.skills = sm.GetService('skills')
        self.timelineCont = None
        self.flashCont = None
        self.disabledFrame = None
        self.removeButton = None

    def CheckConstructRemoveButton(self):
        if not self.removeButton:
            self.removeButton = ButtonIcon(parent=self, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/Icons/105_32_12.png', pos=(0, 0, 24, 24), iconSize=24, func=self.RemoveFromQueue)

    def CheckConstructAcceleratedSprite(self):
        if not self.acceleratedSprite:
            self.acceleratedSprite = Sprite(name='accelratedTraining', parent=self, align=uiconst.BOTTOMLEFT, state=uiconst.UI_HIDDEN, pos=(2, 4, 16, 16), texturePath='res:/UI/Texture/Crimewatch/booster.png', idx=0, hint=localization.GetByLabel('UI/SkillQueue/Skills/AcceleratedTraining'))

    def Load(self, node):
        BaseSkillEntry.Load(self, node)
        self.controller = SkillController(node.skillID)
        data = node
        self.skillID = data.skillID
        self.UpdateSkillNameLevelLabel()
        self.inQueue = data.Get('inQueue', 0)
        if data.trained:
            queue = self.skillQueueSvc.GetQueue()
            isTypeActive = len(queue) and data.skill.typeID == queue[0].trainingTypeID
            isNextLevel = data.Get('currentLevel', -1) + 1 == data.Get('trainToLevel')
            isNotQueuedRecord = data.Get('inQueue', 0) == 0
            recordNeedsUpdating = isTypeActive and (isNotQueuedRecord or isNextLevel)
            if recordNeedsUpdating:
                uthread.new(self.UpdateTraining, data.skill)
            else:
                skill = data.skill
                spsNextLevel = self.skills.SkillpointsNextLevel(skill.typeID)
                if spsNextLevel is not None:
                    timeLeft = data.timeLeft
                    if timeLeft > 0:
                        timeLeftText = self._GetTimeLeftText(long(timeLeft))
                    else:
                        timeLeftText = ''
                    self.timeLeftText.text = timeLeftText
        self.HidePosIndicator()
        if self.inQueue == 1 and self.inTrainingHilite:
            self.inTrainingHilite.Hide()
        self.UpdateAcceleratedMarker()
        self.ConstructTypeUnlockIcons()
        self.UpdateRemoveButton()
        if self.timeLeftText:
            if self.IsCurrentlyTraining():
                self.StartFlashAnimation()
                self.timeLeftText.opacity = 1.0
            else:
                self.timeLeftText.opacity = 0.5
        if self.IsDisabledForTraining() or self.sr.node.disabledForTraining:
            self.ShowDisabledFrame()
        else:
            self.HideDisabledFrame()

    def GetTypeID(self):
        return self.sr.node.skillID

    def IsCurrentlyTraining(self):
        currSkill = sm.GetService('skillqueue').SkillInTraining()
        isCurrentSkill = currSkill and currSkill.typeID == self.GetTypeID() and currSkill.trainedSkillLevel == self.GetTrainToLevel() - 1
        return isCurrentSkill

    def GetTrainToLevel(self):
        return self.sr.node.trainToLevel

    def HideDisabledFrame(self):
        if self.disabledFrame:
            self.disabledFrame.Hide()

    def ShowDisabledFrame(self):
        if not self.disabledFrame:
            self.disabledFrame = ErrorFrame(bgParent=self, color=COLOR_OMEGA_ORANGE, opacityLow=0.15, padding=2)
        self.disabledFrame.Show()

    def IsDisabledForTraining(self):
        maxLevel = sm.GetService('cloneGradeSvc').GetMaxSkillLevel(self.skillID)
        return maxLevel < self.GetTrainToLevel()

    def DrawTimeline(self, offset, segments, animate = False):
        self._CheckConstructTimeline()
        self.timelineCont.FlushLine()
        for width, color in segments:
            self.timelineCont.AddSegment(width, color)

        self.timelineCont.SetOffset(offset)
        if animate:
            self.timelineCont.opacity = 0.0
            animations.FadeIn(self.timelineCont)
        else:
            self.timelineCont.StopAnimations()
            self.timelineCont.opacity = 1.0

    def HideTimeline(self, animate = False):
        if animate:
            animations.FadeOut(self.timelineCont, callback=self.timelineCont.FlushLine)
        else:
            self.timelineCont.FlushLine()

    def _CheckConstructTimeline(self):
        if self.timelineCont is None:
            self.timelineCont = TimelineContainer(parent=self, idx=0, align=uiconst.TOBOTTOM_NOPUSH, state=uiconst.UI_DISABLED, barHeight=1, height=2, clipChildren=1)

    def RemoveFromQueue(self):
        self.sr.node.RemoveFromQueue(self.sr.node)

    def UpdateRemoveButton(self):
        data = self.sr.node
        skillQueueSvc = sm.GetService('skillqueue')
        isRemovable = skillQueueSvc.IsRemoveAllowed(data.invtype, data.trainToLevel)
        if isRemovable:
            self.CheckConstructRemoveButton()
            self.removeButton.Show()
        elif self.removeButton:
            self.removeButton.Hide()

    def StartFlashAnimation(self):
        if not self.flashCont:
            self.ConstructFlashCont()
        uicore.animations.FadeTo(self.flashSprite, 0.3, 0.5, duration=1.0)
        uicore.animations.MorphScalar(self.flashCont, 'left', -120, 0, duration=4.0, curveType=uiconst.ANIM_LINEAR, loops=uiconst.ANIM_REPEAT)
        uicore.animations.FadeTo(self.flashCont, OPACITY_START, 1.0, duration=5.0, curveType=uiconst.ANIM_WAVE, loops=uiconst.ANIM_REPEAT)

    def StopFlashAnimation(self):
        if self.flashCont:
            self.flashCont.StopAnimations()
            self.flashCont.opacity = OPACITY_START
            self.flashSprite.opacity = 0.0

    def ConstructFlashCont(self):
        color = COLOR_SKILL_1
        self.flashCont = Container(name='flashCont', parent=self, state=uiconst.UI_DISABLED, idx=0, align=uiconst.TOPLEFT, width=self.width, height=self.height, opcaity=OPACITY_START)
        self.flashSprite = Sprite(parent=self.flashCont, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', pos=(0,
         0,
         1000,
         self.height), color=color, opacity=0.2, tileX=True)

    def OnDblClick(self, *args):
        sm.GetService('info').ShowInfo(self.GetTypeID())

    def ConstructTypeUnlockIcons(self):
        from eve.client.script.ui.shared.info.panels.panelRequiredFor import RequiredForScrollController
        controller = RequiredForScrollController()
        typeIDsByMarketGroupID = controller.GetUnlockTypeIDsByMarketGroup(self.GetTypeID(), self.GetTrainToLevel())
        if typeIDsByMarketGroupID:
            iconSize = 24
            cont = Container(parent=self.textCont)
            iconCont = ContainerAutoSize(parent=cont, align=uiconst.CENTERLEFT, height=iconSize, left=8)
            for marketGroupID, typeIDs in typeIDsByMarketGroupID.iteritems():
                TypesUnlockedIcon(parent=iconCont, align=uiconst.TOLEFT, width=iconSize, marketGroupID=marketGroupID, typeIDs=typeIDs)

            iconCont.SetSizeAutomatically()

    def UpdateSkillNameLevelLabel(self):
        self.CheckConstructNameLevelLabel()
        text = self.controller.GetRequiredSkillNameAndLevelComparedToTrainedLevel(self.GetTrainToLevel())
        self.nameLevelLabel.text = text

    def UpdateAcceleratedMarker(self):
        if not self.inQueue:
            return
        data = self.sr.node
        if data.isAccelerated:
            self.CheckConstructAcceleratedSprite()
            self.acceleratedSprite.display = True
        elif self.acceleratedSprite:
            self.acceleratedSprite.display = False

    def FillBoxes(self, currentLevel, trainToLevel):
        inTraining = self.skillQueueSvc.SkillInTraining()
        for i in xrange(currentLevel, 5):
            if inTraining and inTraining.typeID == self.skillID:
                if not self.inQueue:
                    if i == currentLevel:
                        self.blinking = 1
                        continue
                elif currentLevel + 1 == trainToLevel:
                    self.blinking = 1
                    continue
            box = self.sr.Get('box_%s' % i, None)
            if box and i < trainToLevel:
                box.SetRGBA(*self.blueColor)
                box.state = uiconst.UI_DISABLED

    def GetMenu(self):
        m = GetMenuService().GetMenuForSkill(self.rec.typeID)
        selected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        if self.inQueue == 1:
            if GetAttrs(self, 'parent', 'RemoveSkillFromQueue'):
                m.append(None)
                m.append((MenuLabel('UI/Commands/Remove'), self.parent.RemoveSkillFromQueue, ()))
        return m

    def GetHint(self):
        return evetypes.GetDescription(self.skillID)

    def OnClick(self, *args):
        if self.sr.node:
            if self.sr.node.Get('selectable', 1):
                self.sr.node.scroll.SelectNode(self.sr.node)
            eve.Message('ListEntryClick')
            if self.sr.node.Get('OnClick', None):
                self.sr.node.OnClick(self)

    def UpdateTraining(self, skill):
        if not self or self.destroyed:
            return
        currentPoints = self.GetCurrentPoints(skill)
        fill = self.sr.Get('box_%s' % int(skill.trainedSkillLevel))
        if not fill:
            return
        fill.state = uiconst.UI_DISABLED
        if self.blinking == 1:
            fill.SetRGBA(*COLOR_SKILL_1)
            sm.StartService('ui').BlinkSpriteA(fill, 1.0, time=1000.0, maxCount=0, passColor=0, minA=0.5)
        if self.inQueue == 0:
            self.OnSkillpointChange(currentPoints)

    def GetCurrentPoints(self, skill):
        if not self or self.destroyed:
            return
        ETA = sm.GetService('skillqueue').GetEndOfTraining(skill.typeID)
        level = skill.trainedSkillLevel
        if not self or self.destroyed or GetAttrs(self, 'sr', 'node', 'skill', 'typeID') != skill.typeID:
            return
        if ETA:
            time = ETA - gametime.GetWallclockTime()
            secs = time / 10000000L
        else:
            time = 0
            secs = 0
        currentPoints = sm.GetService('skillqueue').GetEstimatedSkillPointsTrained(skill.typeID)
        if GetAttrs(self, 'sr', 'node', 'trainToLevel') != level:
            if GetAttrs(self, 'sr', 'node', 'timeLeft'):
                time = self.sr.node.timeLeft
            else:
                time = None
        self.SetTimeLeft(time)
        if ETA:
            self.endOfTraining = ETA
        else:
            self.endOfTraining = None
        self.lasttime = gametime.GetWallclockTime()
        self.lastsecs = secs
        self.lastpoints = currentPoints
        self.timer = timerstuff.AutoTimer(1000, self.UpdateProgress)
        return currentPoints

    def UpdateProgress(self):
        try:
            if self.endOfTraining is None:
                self.timer = None
                return
            skill = self.rec
            timeLeft = self.endOfTraining - blue.os.GetWallclockTime()
            if self.inQueue == 0:
                currentPoints = self.skillQueueSvc.GetEstimatedSkillPointsTrained(skill.typeID)
                self.OnSkillpointChange(currentPoints)
            else:
                self.SetTimeLeft(timeLeft)
        except:
            self.timer = None
            log.LogException()
            sys.exc_clear()

    def GetDragData(self, *args):
        return self.sr.node.scroll.GetSelectedNodes(self.sr.node)

    def OnDropData(self, dragObj, nodes, *args):
        self.HidePosIndicator()
        if GetAttrs(self, 'parent', 'OnDropData'):
            if self.inQueue:
                self.parent.OnDropData(dragObj, nodes, idx=self.sr.node.idx)
            else:
                node = nodes[0]
                if GetAttrs(node, 'panel', 'inQueue'):
                    self.parent.OnDropData(dragObj, nodes)

    def OnDragEnter(self, dragObj, nodes, *args):
        if not self.inQueue or nodes is None:
            return
        self.ShowPosIndicator(nodes)

    def CheckConstructPosIndicatorLine(self):
        if not self.posIndicatorLine:
            self.posIndicatorLine = Line(parent=self, align=uiconst.TOPLEFT_PROP, pos=(0, 0, 0.99, 2), state=uiconst.UI_DISABLED, opacity=0.0, idx=0)

    def ShowPosIndicator(self, nodes):
        self.CheckConstructPosIndicatorLine()
        if IsMultiSkillEntryMove(nodes):
            color = COLOR_MOVE_INDICATOR
        else:
            firstNode = nodes[0]
            allowedMove = self.skillQueueSvc.IsMoveAllowed(firstNode, self.sr.node.idx)
            if allowedMove:
                color = COLOR_TRAININGALLOWED
            elif self.skillQueueSvc.IsSkillEntry(firstNode):
                color = COLOR_TRAININGNOTALLOWED
            else:
                color = (0, 0, 0, 0)
        self.posIndicatorLine.SetRGBA(*color)

    def OnDragExit(self, *args):
        if not self.inQueue:
            return
        self.HidePosIndicator()

    def HidePosIndicator(self):
        if self.posIndicatorLine:
            self.posIndicatorLine.opacity = 0.0

    def GetDynamicHeight(node, width):
        name = localization.GetByLabel('UI/SkillQueue/Skills/SkillNameAndRankValue', skill=node.skill.typeID, rank=0)
        _, nameHeight = EveLabelLarge.MeasureTextSize(name, maxLines=1)
        return max(32, nameHeight + 8)


class TypesUnlockedIcon(Sprite):
    default_spriteEffect = trinity.TR2_SFX_SOFTLIGHT
    default_saturation = 0.0
    default_effectOpacity = 0.0
    default_opacity = 0.85

    def ApplyAttributes(self, attributes):
        Sprite.ApplyAttributes(self, attributes)
        self.typeIDs = attributes.typeIDs
        marketGroupID = attributes.marketGroupID
        self.marketGroup = cfg.GetMarketGroup(marketGroupID)
        self.texturePath = GetIconFile(self.marketGroup.iconID, 'res:/ui/Texture/WindowIcons/smallfolder.png')

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.state = uiconst.UI_NORMAL
        text = GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkillTabs/TypesUnlockedCaption', groupName=self.marketGroup.marketGroupName)
        tooltipPanel.AddLabelLarge(text=text, cellPadding=(0, 4, 0, 6))
        controller = RequiredForScrollController()
        scrollList = controller.GetTypeScrollList(self.typeIDs)
        maxWidth = max((EveLabelLarge.MeasureTextSize(x.label)[0] for x in scrollList))
        maxWidth = max(maxWidth + 60, 250)
        maxHeight = 205
        height = min(maxHeight, len(scrollList) * 30 + 3)
        scroll = Scroll(align=uiconst.TOPLEFT, pos=(0,
         0,
         maxWidth,
         height))
        scroll.HideBackground()
        scroll.Load(fixedEntryHeight=27, contentList=scrollList)
        tooltipPanel.AddCell(scroll)
