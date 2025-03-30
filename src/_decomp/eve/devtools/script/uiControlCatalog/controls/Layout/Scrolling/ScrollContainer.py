#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiControlCatalog\controls\Layout\Scrolling\ScrollContainer.py
import carbonui.const as uiconst
import eveicon
from carbonui.control.baseScrollContEntry import BaseScrollContEntry
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLabel import Label
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.frame import Frame
from eve.client.script.ui.control.message import ShowQuickMessage
from eve.devtools.script.uiControlCatalog.sample import Sample

def OnEntryClicked(entry):
    ShowQuickMessage('Entry with value %s clicked' % entry.value)


class Sample1(Sample):
    name = 'Basic'

    def sample_code(self, parent):
        from carbonui.control.scrollContainer import ScrollContainer
        from carbonui.control.baseScrollContEntry import BaseScrollContEntry

        class MyScrollEntry(BaseScrollContEntry):
            default_name = 'MyScrollEntry'
            default_height = 30

            def ApplyAttributes(self, attributes):
                super(MyScrollEntry, self).ApplyAttributes(attributes)
                self.value = attributes.Get('value', 0)
                Label(name='myLabel', parent=self, align=uiconst.CENTERLEFT, text='Entry with value %s' % self.value, left=6)

        myScrollCont = ScrollContainer(name='myScrollCont', parent=parent, showUnderlay=True, align=uiconst.TOPLEFT, width=250, height=200)
        for i in range(10):
            entry = MyScrollEntry(parent=myScrollCont, value=i)
            entry.on_clicked.connect(OnEntryClicked)


class Sample2(Sample):
    name = 'Selectable entries'

    def sample_code(self, parent):
        from carbonui.control.scrollContainer import ScrollContainer
        from carbonui.control.baseScrollContEntry import BaseScrollContEntry

        class MyScrollEntry(BaseScrollContEntry):
            default_height = 30

            def ApplyAttributes(self, attributes):
                super(MyScrollEntry, self).ApplyAttributes(attributes)
                self.value = attributes.Get('value', 0)
                Label(name='myLabel', parent=self, align=uiconst.CENTERLEFT, text='Entry with value %s' % self.value, left=6)

        class MySelectionScrollContainer(ScrollContainer):

            def PopulateScroll(self):
                for i in range(10):
                    entry = MyScrollEntry(parent=self, value=i)
                    entry.on_clicked.connect(self.OnEntrySelected)

            def OnEntrySelected(self, entry):
                self.DeselectAllEntries()
                entry.OnSelect()

            def DeselectAllEntries(self):
                for entry in self.mainCont.children:
                    entry.OnDeselect()

        myScrollCont = MySelectionScrollContainer(name='myScrollCont', parent=parent, showUnderlay=True, align=uiconst.TOPLEFT, width=250, height=200)
        myScrollCont.PopulateScroll()


class Sample3(Sample):
    name = 'Horizontal scrolling'

    def sample_code(self, parent):
        from carbonui.control.scrollContainer import ScrollContainer
        ICONSIZE = 16
        ICONS = list(eveicon.iter_icons())[:40]
        myScrollCont = ScrollContainer(name='myScrollCont', parent=parent, align=uiconst.TOPLEFT, width=200, height=ICONSIZE * 2)
        Frame(bgParent=myScrollCont, opacity=0.05)
        for icon in ICONS:
            Sprite(align=uiconst.TOLEFT, parent=myScrollCont, texturePath=icon.resolve(ICONSIZE), width=ICONSIZE, padLeft=8)


class Sample4(Sample):
    name = 'Lazy Loading'

    def sample_code(self, parent):
        from carbonui.control.scrollContainer import ScrollContainer

        class MyScrollEntry(BaseScrollContEntry):
            default_height = 30

            def ApplyAttributes(self, attributes):
                super(MyScrollEntry, self).ApplyAttributes(attributes)
                self.value = attributes.Get('value', 0)

            def lazy_load(self):
                label = Label(name='myLabel', parent=self, align=uiconst.CENTERLEFT, text='Entry with value %s' % self.value, left=6, opacity=0.0)
                animations.FadeIn(label)

        myScrollCont = ScrollContainer(name='myScrollCont', parent=parent, showUnderlay=True, align=uiconst.TOPLEFT, width=250, height=200)
        for i in range(1000):
            entry = MyScrollEntry(parent=myScrollCont, value=i)
            entry.on_clicked.connect(OnEntryClicked)
