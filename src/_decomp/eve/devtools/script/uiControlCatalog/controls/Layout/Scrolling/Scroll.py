#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Scrolling\Scroll.py
from carbonui import uiconst
from eve.devtools.script.uiControlCatalog.sample import Sample

class Sample1(Sample):
    name = '2 Columns'
    description = 'The Scroll class should only be used if you are in need of sortable columns, otherwise use ScrollContainer, which is much, much simpler'

    def sample_code(self, parent):
        from eve.client.script.ui.control.eveScroll import Scroll
        from eve.client.script.ui.control.entries.generic import Generic
        from eve.client.script.ui.control.entries.util import GetFromClass

        def get_scroll_entries():
            entries = []
            for i in xrange(10):
                data = {'label': '%s<t>%s' % (i, i ** 2)}
                entry = GetFromClass(Generic, data)
                entries.append(entry)

            return entries

        myScroll = Scroll(name='myScroll', parent=parent, align=uiconst.TOPLEFT, id='myScrollUniqueID', hasUnderlay=True, width=200, height=200)
        myScroll.Load(contentList=get_scroll_entries(), headers=('Value 1', 'Value 2'))
