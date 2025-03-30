#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\bdqmonitor.py
import blue
import carbonui.const as uiconst
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
import remotefilecache
import uthread
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from carbonui.control.window import Window

class BackgroundDownloadQueueMonitor(Window):
    default_caption = 'Background Download Queue Monitor'
    default_minSize = (800, 500)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        topPanel = Container(parent=self.sr.main, align=uiconst.TOTOP, height=30, padding=10)
        Button(parent=topPanel, align=uiconst.TOLEFT, label='Pause', width=120, func=self.Pause, padding=5)
        Button(parent=topPanel, align=uiconst.TOLEFT, label='Resume', width=120, func=self.Resume, padding=5)
        self.mainQueue = eveScroll.Scroll(parent=self.sr.main, id='mainQueueScroll', align=uiconst.TOLEFT, width=300)
        self.subQueue = eveScroll.Scroll(parent=self.sr.main, id='subQueueScroll', align=uiconst.TOALL)
        self.queue = []
        uthread.new(self.PopulateMainQueueScrollTasklet)

    def PopulateMainQueueScrollTasklet(self):
        while not self.destroyed:
            self.PopulateMainQueueScroll()
            blue.synchro.Sleep(333)

    def PopulateMainQueueScroll(self, *args):
        self.queue = remotefilecache.get_queue()
        contentList = []
        index = 1
        for item in self.queue:
            label = '%d<t>%s<t>%d' % (index, item.key, len(item.fileset))
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, label=label)
            contentList.append(listEntry)
            index += 1

        self.mainQueue.Load(contentList=contentList, headers=['#', 'Key', 'Files'], noContentHint='Queue is empty')
        if self.queue:
            self.PopulateSubQueue(self.queue[0])

    def PopulateSubQueue(self, item):
        itemList = list(item.fileset)
        if len(itemList) > 50:
            itemList = itemList[0:49]
            itemList.append('...')
        contentList = []
        index = 1
        for each in itemList:
            label = '%d<t>%s' % (index, each)
            listEntry = ScrollEntryNode(decoClass=SE_GenericCore, id=id, label=label)
            contentList.append(listEntry)
            index += 1

        self.subQueue.Load(contentList=contentList, headers=['#', 'Resource file'], noContentHint='Queue is empty')

    def OnListEntryClicked(self, listEntry):
        node = listEntry.sr.node
        item = node.item
        self.selected_item = item
        self.PopulateSubQueue(item)

    def Pause(self, *args):
        remotefilecache.pause()

    def Resume(self, *args):
        remotefilecache.resume()
