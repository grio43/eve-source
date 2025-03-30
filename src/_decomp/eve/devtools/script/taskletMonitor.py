#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\taskletMonitor.py
import traceback
import blue
import bluepy
from carbonui import uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveLabel, eveScroll
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window
from carbonui.control.tabGroup import TabGroup
__author__ = 'snorri.sturluson'

class RunningTasklets(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.selectedNode = None
        self.settingsContainer = Container(parent=self, align=uiconst.TOTOP, height=24, padding=10)
        self.countLabel = eveLabel.Label(parent=self.settingsContainer, align=uiconst.TOLEFT, text='', width=200, height=30, padLeft=2, padTop=2)
        Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Refresh', width=120, height=30, func=self.PopulateScroll)
        self.killButton = Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Kill Tasklet', width=120, height=30, padLeft=2, padRight=2, func=self.KillTasklet)
        self.killButton.Disable()
        self.highlightToggle = Checkbox(parent=self.settingsContainer, align=uiconst.TORIGHT, text='Show only highlighted tasklets', callback=self.PopulateScroll, width=240)
        self.scroll = eveScroll.Scroll(parent=self, id='taskletsScroll', align=uiconst.TOTOP, height=350)
        self.callstack = eveScroll.Scroll(parent=self, align=uiconst.TOALL)
        self.PopulateScroll()

    def _SetCountLabel(self):
        self.countLabel.text = '%d tasklets' % self.taskletCount

    def PopulateScroll(self, *args):
        contentList = []
        for t in bluepy.tasklets.keys():
            if not t.alive:
                continue
            if self.highlightToggle.checked and not t.highlighted:
                continue
            callstack = traceback.extract_stack(t.frame)
            ctx = getattr(t, 'context', '(unknown)').replace('<', '&lt;').replace('>', '&gt;')
            runtime = getattr(t, 'runTime', 0)
            color = '<color=0xff00ff00>' if t.highlighted else ''
            label = '%s%d<t>%f<t>%s' % (color,
             t.tasklet_id,
             runtime,
             ctx)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, taskletId=t.tasklet_id, context=ctx, callstack=callstack, runTime=runtime, label=label, OnClick=self.OnListEntryClicked, tasklet=t)
            contentList.append(listEntry)

        self.scroll.Load(contentList=contentList, headers=['ID', 'Runtime', 'Context'], noContentHint='No Data available')
        self.taskletCount = len(contentList)
        self._SetCountLabel()

    def KillTasklet(self, *args):
        if not self.selectedNode:
            return
        self.selectedNode.tasklet.kill()
        self.scroll.RemoveNodes([self.selectedNode])
        self.selectedNode = None
        self.killButton.Disable()
        self.taskletCount -= 1
        self._SetCountLabel()

    def OnListEntryClicked(self, listEntry):
        self.selectedNode = listEntry.sr.node
        self.killButton.Enable()
        contentList = []
        entryNo = 1
        for each in self.selectedNode.callstack:
            filename, line, function_name, code = each
            label = '%d<t>%s<t>%d<t>%s<t>%s' % (entryNo,
             filename,
             line,
             function_name,
             code)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, entryNo=entryNo, filename=filename, line=line, function_name=function_name, code=code, label=label)
            contentList.append(listEntry)
            entryNo += 1

        self.callstack.Load(contentList=contentList, headers=['Entry',
         'File name',
         'Line',
         'Function name',
         'Code'], noContentHint='No Data available')


class TimesliceWarnings(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.settingsContainer = Container(parent=self, align=uiconst.TOTOP, height=24, padding=10)
        self.countLabel = eveLabel.Label(parent=self.settingsContainer, align=uiconst.TOLEFT, text='', height=30, padLeft=2, padTop=2)
        Button(parent=self.settingsContainer, align=uiconst.TORIGHT, label='Refresh', width=120, height=30, func=self.PopulateScroll)
        self.scroll = eveScroll.Scroll(parent=self, id='timesliceWarningsScroll', align=uiconst.TOALL)
        self.PopulateScroll()

    def PopulateScroll(self, *args):
        totalWarnings = 0
        contentList = []
        for ctx, v in blue.pyos.taskletTimer.taskletWarnings.iteritems():
            maxValue, count = v
            ctx = str(ctx).replace('<', '&lt;').replace('>', '&gt;')
            label = '%d<t>%d<t>%s' % (maxValue, count, ctx)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, maxValue=maxValue, count=count, context=ctx, label=label)
            contentList.append(listEntry)
            totalWarnings += count

        self.scroll.Load(contentList=contentList, headers=['Max value', 'Count', 'Context'], noContentHint='No Data available')
        self.countLabel.text = '%d warnings' % totalWarnings


class TaskletMonitor(Window):
    default_caption = 'Tasklet Monitor'
    default_minSize = (800, 500)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        runningTaskletsPanel = RunningTasklets(parent=self.sr.main)
        timesliceWarningsPanel = TimesliceWarnings(parent=self.sr.main)
        TabGroup(parent=self.sr.main, groupID='TaskletsGroupID', idx=0, tabs=(('Running tasklets',
          runningTaskletsPanel,
          self.sr.main,
          'taskletsID1'), ('Timeslice warnings',
          timesliceWarningsPanel,
          self.sr.main,
          'taskletsID2')))
