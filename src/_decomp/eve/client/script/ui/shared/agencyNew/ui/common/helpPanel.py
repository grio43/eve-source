#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\common\helpPanel.py
import carbonui
from carbonui import uiconst
from carbonui.control.baseScrollContEntry import BaseScrollContEntry
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.section import Section
from carbonui.primitives.container import Container
MAIN_CONT_PADDING = 10

class HelpSection:

    def __init__(self, name, panel):
        self.name = name
        self.panel = panel


class HelpPanel(Container):

    def ApplyAttributes(self, attributes):
        super(HelpPanel, self).ApplyAttributes(attributes)
        self.mainCont = Container(parent=self, name='mainCont', align=uiconst.TOALL, padding=32)
        self.sections = attributes.sections
        self.entries = []
        self.ConstructLayout()

    def ConstructLayout(self):
        self.ConstructTopicSelectionColumn()
        self.ConstructTopicDetailsColumn()

    def ConstructTopicSelectionColumn(self):
        topicSelectionColumnCont = Container(parent=self.mainCont, name='topicSelectionColumnCont', align=uiconst.TOLEFT_PROP, width=0.3)
        topicsSection = Section(parent=topicSelectionColumnCont, name='topicsSection', align=uiconst.TOALL, headerText='browse topics', padding=8)
        self.topicSelectionScrollCont = ScrollContainer(parent=topicsSection, align=uiconst.TOALL, showUnderlay=True, name='topicSelectionScrollCont')
        for section in self.sections:
            entry = _ScrollEntry(parent=self.topicSelectionScrollCont, section=section)
            entry.on_clicked.connect(self.SectionSelected)
            entry.on_clicked.connect(self.DeselectAll)
            entry.on_clicked.connect(entry.OnSelect)
            self.entries.append(entry)

    def DeselectAll(self, *args):
        for entry in self.entries:
            entry.OnDeselect()

    def SectionSelected(self, entry):
        for section in self.sections:
            section.panel.Hide()

        entry.section.panel.SetParent(self.detailsSection)
        entry.section.panel.Show()
        self.detailsSection.headerCont.SetText(entry.section.name)

    def ConstructTopicDetailsColumn(self):
        self.topicDetailsColumn = Container(parent=self.mainCont, name='topicDetailsColumn', align=uiconst.TORIGHT_PROP, width=0.7)
        self.detailsSection = Section(parent=self.topicDetailsColumn, name='detailsSection', align=uiconst.TOALL, padding=8)


class _ScrollEntry(BaseScrollContEntry):
    default_height = 30

    def ApplyAttributes(self, attributes):
        super(_ScrollEntry, self).ApplyAttributes(attributes)
        self.section = attributes.section
        self.ConstructLayout()

    def ConstructLayout(self):
        carbonui.TextBody(parent=self, name='label', align=carbonui.Align.TOLEFT, text=self.section.name, padding=5)

    def OnSelect(self, *artgs):
        print '{} selected'.format(self.section.name)
        super(_ScrollEntry, self).OnSelect()
