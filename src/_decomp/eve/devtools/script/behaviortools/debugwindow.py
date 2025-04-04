#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\behaviortools\debugwindow.py
from brennivin.itertoolsext import Bundle
from carbon.common.script.util.format import FmtDate
from carbon.common.script.util.timerstuff import AutoTimer
from carbonui.control.dragResizeCont import DragResizeCont
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from carbonui.control.window import Window
import carbonui.const as uiconst
from eve.client.script.ui.util.uiComponents import Component, HoverEffect
import logging
import blue
import math
from eve.client.script.ui.util.uix import HybridWnd
import gametime
logger = logging.getLogger(__name__)
VALUE_COLOR = (0.4, 0.8, 1.0)
ENTRY_HEIGHT = 20
COLOR_INVALID = Color.GRAY3
COLOR_SUCCESS = Color(8, 195, 131).GetRGBA()
COLOR_FAILED = Color(255, 70, 70).GetRGBA()
COLOR_RUNNING = Color(50, 115, 249).GetRGBA()
COLOR_SUSPENDED = Color(209, 51, 243).GetRGBA()
COLOR_MONITORING = Color(253, 225, 1).GetRGBA()
TaskInvalidStatus = 'TaskInvalidStatus'
TaskSuccessStatus = 'TaskSuccessStatus'
TaskFailureStatus = 'TaskFailureStatus'
TaskRunningStatus = 'TaskRunningStatus'
TaskSuspendedStatus = 'TaskSuspendedStatus'
STATUS_MAP = dict(TaskInvalidStatus=Bundle(text='Invalid', color=COLOR_INVALID), TaskSuccessStatus=Bundle(text='Success', color=COLOR_SUCCESS), TaskFailureStatus=Bundle(text='Failure', color=COLOR_FAILED), TaskRunningStatus=Bundle(text='Running', color=COLOR_RUNNING), TaskSuspendedStatus=Bundle(text='Suspended', color=COLOR_SUSPENDED), TaskBlockingStatus=Bundle(text='Blocking', color=Color.YELLOW))

class BehaviorTreeEntry(ContainerAutoSize):
    MAX_WIDTH = 300
    NODE_WIDTH = 250
    PADDING = 5
    default_name = 'BehaviorTreeNode'
    default_height = ENTRY_HEIGHT
    default_align = uiconst.TOTOP

    def ApplyAttributes(self, attributes):
        super(BehaviorTreeEntry, self).ApplyAttributes(attributes)
        self.task = attributes.task
        self.taskID = attributes.taskID
        self.CreateTreeIndent(attributes)
        self.taskNode = TaskNode(name=attributes.text, parent=self, clipChildren=True, task=attributes.task, text=attributes.text, window=attributes.window)

    def CreateTreeIndent(self, attributes):
        Container(name='pad', parent=self, align=uiconst.TOLEFT, width=self.PADDING)
        for x in xrange(attributes.indent):
            c = Container(name='Indent', parent=self, align=uiconst.TOLEFT, width=ENTRY_HEIGHT)
            Line(parent=c, align=uiconst.TOLEFT)

    def SetBgColor(self, alternate = False):
        pass

    def EnableStepped(self):
        self.taskNode.EnableStepped()

    def DisableStepped(self):
        self.taskNode.DisableStepped()

    def SetStatus(self, status):
        self.taskNode.SetStatus(status)

    def ToggleChildren(self):
        self.taskNode.ToggleChildren()


@Component(HoverEffect())

class TaskNode(Container):
    default_align = uiconst.TOLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(TaskNode, self).ApplyAttributes(attributes)
        self.isCollapsed = False
        self.window = attributes.window
        self.task = attributes.task
        self.CreateLayout(attributes)
        self.SetStatus(attributes.task.status)

    def CreateLayout(self, attributes):
        self.stepFrame = Frame(name='myFrame', bgParent=self, frameConst=uiconst.FRAME_BORDER2_CORNER9, padding=(1, 1, 1, 1))
        self.mainFrame = Frame(name='myFrame', bgParent=self, frameConst=uiconst.FRAME_FILLED_SHADOW_CORNER9, padding=(1, 1, 1, 1))
        self.collapsedFrame = Sprite(name='myFrame', bgParent=self, texturePath='res:/UI/Texture/Classes/Industry/Output/hatchPattern.png', padding=(1, 1, 1, 1), tileX=True, tileY=True)
        self.collapsedFrame.display = False
        label = eveLabel.EveLabelSmall(parent=self, text=attributes.text, align=uiconst.CENTER, color=Color.WHITE)
        self.width = max(100, label.textwidth + 16)

    def EnableStepped(self):
        self.stepFrame.Show()

    def DisableStepped(self):
        self.stepFrame.Hide()

    def SetStatus(self, status):
        self.task.status = status
        self.mainFrame.SetRGBA(*STATUS_MAP[status].color[:3])
        self.mainFrame.opacity = 0.4
        self.stepFrame.SetRGBA(*STATUS_MAP[status].color[:3])
        self.stepFrame.opacity = 0.5
        self.collapsedFrame.SetRGBA(*STATUS_MAP[status].color[:3])
        self.collapsedFrame.opacity = 0.3

    def OnClick(self, *args):
        self.ToggleChildren()

    def ToggleChildren(self):
        self.SetCollapsed(not self.isCollapsed)

    def SetCollapsed(self, isCollapsed):
        self.collapsedFrame.display = isCollapsed
        self.isCollapsed = isCollapsed
        if hasattr(self.task, 'subtasks'):
            for taskID in self.task.subtasks:
                e = self.window.taskMap[taskID]
                e.display = not isCollapsed
                e.taskNode.SetCollapsed(isCollapsed)

    def GetTooltipDelay(self):
        return 500

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.AddLabelLarge(text=self.task.attributes.get('name', self.task.type), colSpan=2, bold=True, bgColor=(1, 1, 1, 0.1), align=uiconst.CENTER)
        tooltipPanel.AddLabelValue('Type', self.task.type, VALUE_COLOR)
        tooltipPanel.AddLabelValue('ID', self.task.id, VALUE_COLOR)
        tooltipPanel.AddLabelValue('Status', self.task.status, STATUS_MAP[self.task.status].color)
        tooltipPanel.AddLabelLarge(text='Attributes', colSpan=2, bold=True, bgColor=(1, 1, 1, 0.1), align=uiconst.CENTER)
        for attributeName, attributeValue in sorted(self.task.attributes.iteritems()):
            tooltipPanel.AddLabelValue(attributeName, str(attributeValue), VALUE_COLOR)


def get_trimmed_value(message):
    if len(message) > 30:
        return message[:30] + ' ... '
    else:
        return message


class BehaviorDebugWindow(Window):
    default_windowID = 'BehaviorDebugWindow'
    default_caption = 'Behavior Debug Tool'
    default_width = 600
    default_height = 500
    default_stackID = 'BehaviorDebugStack'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.taskMap = {}
        self.controller = None
        self.buttonCont = Container(parent=self.sr.main, name='buttonbar', align=uiconst.TOTOP, height=24, clipChildren=True)
        GradientSprite(bgParent=self.buttonCont, rotation=-math.pi / 2, rgbData=[(0, (1.0, 1.0, 1.3))], alphaData=[(0.6, 0.0), (1.0, 0.05)])
        self.clockCont = Container(parent=self.sr.main, name='clockbar', align=uiconst.TOTOP, height=24, clipChildren=True)
        GradientSprite(bgParent=self.buttonCont, rotation=-math.pi / 2, rgbData=[(0, (1.0, 1.0, 1.3))], alphaData=[(0.6, 0.0), (1.0, 0.05)])
        self.lastUpdateTime = gametime.GetWallclockTime()
        self.lastResetTime = gametime.GetWallclockTime()
        self.currentTimeLabel = eveLabel.EveLabelMedium(parent=self.clockCont, text='', left=8)
        self.lastUpdateTimeLabel = eveLabel.EveLabelMedium(parent=self.clockCont, text='', left=158)
        self.lastResetTimeLabel = eveLabel.EveLabelMedium(parent=self.clockCont, text='', left=258)
        self.leftCont = DragResizeCont(name='leftCont', parent=self.sr.main, align=uiconst.TOLEFT_PROP, settingsID='BehaviorDebugWindowLeftContent', minSize=0.2, maxSize=0.8, defaultSize=0.5)
        GradientSprite(bgParent=self.leftCont, rotation=0, rgbData=[(0, (1.0, 1.0, 1.3))], alphaData=[(0.8, 0.0), (1.0, 0.05)])
        self.mainScroll = ScrollContainer(name='behaviortree', parent=self.leftCont.mainCont, align=uiconst.TOALL, padding=(4, 4, 4, 4))
        self.blackboardScroll = ScrollContainer(name='blackboards', parent=self.sr.main, padding=(4, 4, 4, 4))
        GradientSprite(bgParent=self.blackboardScroll, rotation=0, rgbData=[(0, (1.0, 1.0, 1.3))], alphaData=[(0.8, 0.0), (1.0, 0.05)])
        self.timeUpdateTimer = AutoTimer(1000, self._TimeUpdater)

    def _TimeUpdater(self):
        self.currentTimeLabel.SetText('Time:  current: %s' % FmtDate(gametime.GetWallclockTime(), 'nl'))
        self.lastUpdateTimeLabel.SetText('tick: %s' % FmtDate(self.lastUpdateTime, 'nl'))
        self.lastResetTimeLabel.SetText('reset: %s' % FmtDate(self.lastResetTime, 'nl'))

    def Reset(self):
        self.taskMap = {}
        self.nodeCount = 0
        self.mainScroll.Flush()

    def CreateToolbarButton(self, func, label):
        Button(name=label, label=label, parent=self.buttonCont, align=uiconst.TOLEFT, padding=(8, 4, 0, 4), height=16, func=func)

    def CreateToolbar(self):
        self.CreateToolbarButton(self.OnClickReset, 'Reset Tree')
        self.CreateToolbarButton(self.OnClickUnblockReset, 'Unblock Reset')
        if not isinstance(self.controller.entryKey, tuple):
            self.CreateToolbarButton(self.OnClickClearItemBB, 'Clear Item Blackboard')
        self.CreateToolbarButton(self.OnClickClearGroupBB, 'Clear Group Blackboard')

    def GetEntryKeyForSlashCommand(self):
        if isinstance(self.controller.entryKey, tuple):
            return '%s=%s' % self.controller.entryKey
        else:
            return str(self.controller.entryKey)

    def OnClickReset(self, _):
        sm.GetService('slash').SlashCmd('/behavior reset %s' % self.GetEntryKeyForSlashCommand())

    def _clear_blackboard(self, scope_type):
        sm.GetService('slash').SlashCmd('/behavior blackboard clear scope=%s id=%s '.format(scope_type, self.GetEntryKeyForSlashCommand()))

    def OnClickClearItemBB(self, _):
        self._clear_blackboard('item')

    def OnClickClearGroupBB(self, _):
        self._clear_blackboard('entity_group')

    def OnClickUnblockReset(self, _):
        sm.GetService('slash').SlashCmd('/behavior unblock %s' % self.GetEntryKeyForSlashCommand())

    def SetBlackboardValue(self, blackboardScope, messageName, messageValue):
        scopeText = blackboardScope[0]
        window_format = [{'type': 'textedit',
          'setvalue': str(messageValue),
          'label': 'Value',
          'key': 'value',
          'setfocus': 1,
          'frame': 0,
          'height': 136}]
        returnValue = HybridWnd(window_format, 'Set Blackboard Value', 'setBlackboardValue', modal=1, buttons=uiconst.OKCANCEL, icon=uiconst.OKCANCEL, minW=300, minH=120, unresizeAble=False)
        if returnValue is not None:
            messageValue = returnValue['value']
            slash_command = '/behavior blackboard set scope={scope} id={id} message={message} value={value}'.format(scope=scopeText, id=blackboardScope[1], message=messageName, value=''.join(messageValue.split()))
            sm.GetService('slash').SlashCmd(slash_command)

    def SetController(self, controller):
        self.controller = controller
        self.SetCaption(str(self.controller.entryKey))
        self.CreateToolbar()

    def LoadBehaviorTree(self, treeData):
        self.Reset()
        for taskData in treeData:
            self.AddEntry(taskData)

    def UpdateStatuses(self, taskStatuses):
        for taskId, entry in self.taskMap.iteritems():
            entry.SetStatus(taskStatuses[taskId])

    def UpdateTasksSeen(self, tasksSeen):
        for taskId, entry in self.taskMap.iteritems():
            if taskId in tasksSeen:
                entry.EnableStepped()
            else:
                entry.DisableStepped()

    def LoadEvents(self, events):
        doReset = False
        for time, name, data in events:
            if name == 'Reset':
                doReset = True

        if doReset:
            self.ResetStatusToInvalid()
        self.lastUpdateTime = gametime.GetWallclockTime()

    def ResetStatusToInvalid(self):
        for entry in self.taskMap.itervalues():
            entry.SetStatus(TaskInvalidStatus)

        self.lastResetTime = gametime.GetWallclockTime()

    def LoadBlackboard(self, blackboards):
        self.blackboardScroll.Flush()
        for scopeType, scopeText in [('item', 'Item Blackboard: <color=lightgreen>%d</color>'),
         ('entity_group', 'Entity Group Blackboard: <color=lightgreen>%d</color>'),
         ('dungeon', 'Dungeon Blackboard (spawn): <color=lightgreen>%d</color>'),
         ('tale', 'Tale Blackboard: <color=lightgreen>%d</color>'),
         ('spawn_point_pool', 'Spawn Point Pool Blackboard: <color=lightgreen>%d</color>'),
         ('node_graph', 'Node Graph Blackboard: <color=lightgreen>%s</color>')]:
            for scope, channels in blackboards.iteritems():
                if scopeType == scope[0]:
                    self.CreateBlackboard(scopeText % scope[1], channels, scope)

    def CloseByUser(self, *args):
        logger.debug('closing debugger')
        self.controller.Disconnect()
        self.Close()

    def AddEntry(self, taskDict):
        task = Bundle(taskDict)
        task.attributes = Bundle(taskDict['attributes'])
        entry = BehaviorTreeEntry(parent=self.mainScroll, indent=task.depth, text='<color=lightgreen>%s</color> %s' % (task.attributes.name, task.type) if 'name' in task.attributes else task.type, color=STATUS_MAP[task.status].color, taskID=task.id, task=task, window=self)
        entry.SetBgColor(len(self.mainScroll.mainCont.children) % 2 == 0)
        entry.DisableStepped()
        self.taskMap[entry.taskID] = entry

    def CreateBlackboard(self, scopeText, channels, scope):
        grid = LayoutGrid(columns=3, parent=self.blackboardScroll, align=uiconst.TOTOP, cellPadding=3, cellSpacing=4)
        row = grid.AddRow(bgColor=(1, 1, 1, 0.1))
        headerLabel = ScopeHeaderLabel(text=scopeText, align=uiconst.CENTERLEFT, blackboardScope=scope)
        row.AddCell(cellObject=headerLabel, colSpan=3, bpColor=(1, 1, 1, 0.05))
        for message, time, value in sorted(channels):
            row = grid.AddRow(bgColor=(1, 1, 1, 0.05))
            row.AddCell(cellObject=CopyLabelSmallBold(text=message, align=uiconst.CENTERLEFT, color=(0.4, 0.8, 1.0), messageName=message, messageValue=value, wnd=self, blackboardScope=scope))
            row.AddCell(cellObject=eveLabel.EveLabelSmallBold(text=FmtDate(time, 'nl') if time else str(time), align=uiconst.CENTERLEFT))
            row.AddCell(cellObject=CopyLabelSmallBold(text=get_trimmed_value(str(value)), align=uiconst.CENTERLEFT, color=(0.4, 0.8, 1.0), messageName=message, messageValue=value, wnd=self, blackboardScope=scope))

        Container(parent=self.blackboardScroll, height=16, align=uiconst.TOTOP)


class CopyLabelSmallBold(eveLabel.EveLabelSmallBold):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(CopyLabelSmallBold, self).ApplyAttributes(attributes)
        self.messageName = attributes.get('messageName')
        self.messageValue = str(attributes.get('messageValue'))
        self.blackboardScope = attributes.get('blackboardScope')
        self.wnd = attributes.get('wnd')

    def GetMenu(self):
        return [('Copy', self.CopyText, []), ('Set Value In Blackboard', self.SetBlackboardValue, [])]

    def CopyText(self):
        blue.pyos.SetClipboardData(self.messageValue)

    def SetBlackboardValue(self):
        self.wnd.SetBlackboardValue(self.blackboardScope, self.messageName, self.messageValue)


class ScopeHeaderLabel(eveLabel.EveLabelMediumBold):
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        super(ScopeHeaderLabel, self).ApplyAttributes(attributes)
        self.blackboardScope = attributes.get('blackboardScope')
        self.wnd = attributes.get('wnd')

    def GetMenu(self):
        return [('Copy', self.CopyText, []), ('Copy ID', self.CopyId, []), ('Connect to behavior', self.ConnectToBehavior, [])]

    def CopyText(self):
        blue.pyos.SetClipboardData(str(self.blackboardScope))

    def ConnectToBehavior(self):
        if 'entity_group' in self.blackboardScope:
            sm.GetService('slash').SlashCmd('/behavior debug connect group=%s' % self.blackboardScope[1])

    def CopyId(self):
        blue.pyos.SetClipboardData(str(self.blackboardScope[1]))
