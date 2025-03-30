#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\pricehistorychart.py
import localization
import uthread
import utillib
from carbon.common.script.util.format import FmtAmt, FmtDate
from carbonui import uiconst
from carbonui.button.const import HEIGHT_NORMAL
from carbonui.control.combo import Combo
from carbonui.graphs.datafortesting import GetTestData
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import FlushList
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.market.marketGraph import MarketGraph
from eve.common.lib import appConst as const
from eve.common.script.util.eveFormat import FmtCurrency
from eveprefs import prefs

class PriceHistoryParent(Container):
    __guid__ = 'xtriui.PriceHistoryParent'
    __nonpersistvars__ = []
    inited = 0

    def Startup(self):
        self.sr.pricehistory = PriceHistory(name='ph', parent=self, align=uiconst.TOALL, pos=(const.defaultPadding,
         0,
         const.defaultPadding,
         0))
        self.inited = 1

    def LoadType(self, invType):
        self.sr.pricehistory.Render(invType)


class PriceHistory(Container):
    __guid__ = 'xtriui.PriceHistory'
    __nonpersistvars__ = []
    __update_on_reload__ = 1

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.line = None
        self.marker = None
        self.highlow = None
        self.underlay = None
        self.markerparent = None
        self.wantrefresh = 1
        self.rendering = 0
        self.typerecord = None
        self.optionsCont = Container(name='options', parent=self, align=uiconst.TOBOTTOM, height=HEIGHT_NORMAL, padTop=16)
        self.optionsinited = 0
        self.sr.updateTimer = None
        self.currentGraph = None

    def InitOptions(self):
        self.optionsCont.Flush()
        showingPriceHistoryType = settings.user.ui.Get('pricehistorytype', 0)
        if showingPriceHistoryType:
            buttonLabel = localization.GetByLabel('UI/PriceHistory/ShowGraph')
            buttonHint = localization.GetByLabel('Tooltips/Market/MarketDetailsHistoryGraph')
        else:
            buttonLabel = localization.GetByLabel('UI/PriceHistory/ShowTable')
            buttonHint = localization.GetByLabel('Tooltips/Market/MarketDetailsHistoryTable')
        btn = Button(parent=self.optionsCont, label=buttonLabel, align=uiconst.TOLEFT, func=self.ToggleView, args='self', hint=buttonHint)
        timeOptions = [[localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=5), 5],
         [localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=10), 10],
         [localization.GetByLabel('UI/Common/DateWords/Month'), 30],
         [localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Month', months=3), 90],
         [localization.GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Month', months=6), 180],
         [localization.GetByLabel('UI/Common/DateWords/Year'), 365]]
        timeLabel = localization.GetByLabel('/Carbon/UI/Common/Time')
        pos = btn.width + btn.left + 10
        self.timeCombo = Combo(label=timeLabel, parent=self.optionsCont, align=uiconst.TOLEFT, options=timeOptions, name='pricehistorytime', select=settings.user.ui.Get('pricehistorytime', 90), callback=self.ChangeOption, padLeft=8)
        if showingPriceHistoryType:
            self.timeCombo.state = uiconst.UI_NORMAL
        else:
            self.timeCombo.state = uiconst.UI_HIDDEN
        self.optionsinited = 1

    def ToggleView(self, btn, *args):
        settings.user.ui.Set('pricehistorytype', not settings.user.ui.Get('pricehistorytype', 0))
        showingPriceHistoryType = settings.user.ui.Get('pricehistorytype', 0)
        if showingPriceHistoryType:
            btnLabel = localization.GetByLabel('UI/PriceHistory/ShowGraph')
            buttonHint = localization.GetByLabel('Tooltips/Market/MarketDetailsHistoryGraph')
            self.timeCombo.state = uiconst.UI_NORMAL
        else:
            btnLabel = localization.GetByLabel('UI/PriceHistory/ShowTable')
            buttonHint = localization.GetByLabel('Tooltips/Market/MarketDetailsHistoryTable')
            self.timeCombo.state = uiconst.UI_HIDDEN
        btn.hint = buttonHint
        btn.SetLabel(btnLabel)
        btn.width = 100
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)

    def ChangeOption(self, entry, header, value, *args):
        settings.user.ui.Set('pricehistorytime', value)
        self.InitOptions()
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)

    def GetSize(self):
        abswidth, absheight = self.absoluteRight - self.absoluteLeft, self.absoluteBottom - self.absoluteTop
        if not abswidth or not absheight:
            abswidth, absheight = self.absoluteRight - self.absoluteLeft, self.absoluteBottom - self.absoluteTop
        return (abswidth, absheight - self.optionsCont.height)

    def RenderTable(self):
        scroll = eveScroll.Scroll(parent=self, padding=(1, 1, 1, 1))
        scroll.sr.id = 'pricehistoryscroll'
        scroll.smartSort = 0
        scroll.OnColumnChanged = self.OnColumnChanged
        history = sm.GetService('marketQuote').GetPriceHistory(self.typerecord)
        windowData = settings.user.ui.Get('pricehistorytime', 90)
        if len(history) > windowData:
            history = history[-(windowData + 1):]
        scrolllist = []
        for rec in history:
            text = '%s<t>%s<t>%s<t>%s<t>%s<t>%s' % (FmtDate(rec[0]),
             FmtAmt(rec[5]),
             FmtAmt(rec[4]),
             FmtCurrency(rec[1], currency=None),
             FmtCurrency(rec[2], currency=None),
             FmtCurrency(rec[3], currency=None))
            data = utillib.KeyVal()
            data.label = text
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/Quantity'), rec[4])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory'), rec[5])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/LowestPrice'), rec[1])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/HighestPrice'), rec[2])
            data.Set('sort_%s' % localization.GetByLabel('UI/Market/PriceHistory/AveragePrice'), rec[3])
            data.Set('sort_%s' % localization.GetByLabel('UI/Common/Date'), rec[0])
            scrolllist.append(GetFromClass(Generic, data))

        headers = [localization.GetByLabel('UI/Common/Date'),
         localization.GetByLabel('UI/Market/PriceHistory'),
         localization.GetByLabel('UI/Market/PriceHistory/Quantity'),
         localization.GetByLabel('UI/Market/PriceHistory/LowestPrice'),
         localization.GetByLabel('UI/Market/PriceHistory/HighestPrice'),
         localization.GetByLabel('UI/Market/PriceHistory/AveragePrice')]
        scroll.Load(fixedEntryHeight=18, contentList=scrolllist, headers=headers)

    def OnColumnChanged(self, *args):
        if self.typerecord:
            uthread.new(self.Render, self.typerecord)

    def GetGraph(self, typeID):
        if prefs.GetValue('priceHistoryTestData', False):
            data = GetTestData()
        else:
            data = sm.GetService('marketQuote').GetPriceHistory(typeID)
        data = data[-365:]
        graph = MarketGraph(parent=self, data=data, typeID=typeID)
        self.currentGraph = graph
        return graph

    def Render(self, typeRecord):
        if self.rendering:
            return
        self.typerecord = typeRecord
        if not self.optionsinited:
            self.InitOptions()
        FlushList(self.children[1:])
        if settings.user.ui.Get('pricehistorytype', 0):
            self.RenderTable()
            return
        self.rendering = 1
        try:
            self.currentGraph = self.GetGraph(self.typerecord)
        finally:
            self.rendering = 0
