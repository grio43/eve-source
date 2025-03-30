#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\statistics.py
import uthread2
from carbonui import uiconst, fontconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from fwwarzone.client.dashboard.collapsingSections import CollapsableSectionsContainer
from fwwarzone.client.dashboard.statisticsController import StatisticsController
from localization import GetByLabel

class FWStatisticsPanel(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.layoutRoom = 0.8
        self.scrolls = []
        self.sections = []
        self.mainCont = None

    def LoadPanel(self, *args, **kwargs):
        if self.mainCont:
            return
        uthread2.start_tasklet(self.ConstructLayout)

    def ConstructLayout(self):
        loadingWheel = LoadingWheel(width=64, height=64, parent=self, align=uiconst.CENTER)
        self.mainCont = Container(parent=self, padding=80, align=uiconst.TOALL, state=uiconst.UI_HIDDEN)
        self.scrolls = [('personal', GetByLabel('UI/Generic/Personal')), ('corp', GetByLabel('UI/Generic/Corporation')), ('militia', GetByLabel('UI/FactionWarfare/Militia'))]
        if session.allianceid is not None:
            self.scrolls.append(('alliance', GetByLabel('UI/Common/Alliance')))
        for key, text in self.scrolls:
            cont = Container(align=uiconst.TOALL)
            self.infoScroll = eveScroll.Scroll(parent=cont, padBottom=5, rowPadding=5, headerFontSize=fontconst.EVE_LARGE_FONTSIZE)
            self.infoScroll.ChangeSortBy = lambda *args: None
            statisticsController = StatisticsController(self.infoScroll)
            statisticsController.LoadStatisticsScrollData(key)
            self.sections.append((cont, text, False))

        CollapsableSectionsContainer(parent=self.mainCont, align=uiconst.TOALL, sections=self.sections, layoutRoom=0.8)
        loadingWheel.Hide()
        self.mainCont.Show()
