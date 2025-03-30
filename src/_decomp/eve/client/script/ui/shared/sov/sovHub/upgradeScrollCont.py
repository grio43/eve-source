#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\upgradeScrollCont.py
from carbonui.control.scroll import Scroll, VERSION
from carbonui.primitives.container import Container
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.scrollUtil import TabFinder
from eve.client.script.ui.shared.sov.sovHub.hubController import NOT_AVAILABLE
from eve.client.script.ui.shared.sov.sovHub.upgradeEntry import UpgradeEntry, UpgradeLastEntry, PosIndicatorLine
import carbonui
from eveexceptions import ExceptionEater
from localization import GetByLabel
MIN_COL_WIDTH = 30

class UpgradeScrollCont(Container):

    def ApplyAttributes(self, attributes):
        self.scroll = None
        self.hubController = attributes.hubController
        super(UpgradeScrollCont, self).ApplyAttributes(attributes)
        self.hubController.on_online_state_changed.connect(self.OnOnlineStateChanged)
        self.scroll = Scroll(name='upgradeScroll', parent=self, id='SovHubUpgradeScroll')
        self.tabFinder = TabFinder()
        self.scroll.GetTabStops = self.GetTabStops
        self.scroll.ChangeSortBy = self.ChangeSortBy
        self.scroll.sr.content.OnDropData = self.DoDropData
        self.scroll.sr.content.OnDragEnter = self.OnContentDragEnter
        self.scroll.sr.content.OnDragExit = self.OnContentDragExit
        self.changeIndicator = PosIndicatorLine(parent=self.scroll, align=carbonui.Align.TOBOTTOM, pickState=carbonui.PickState.OFF, height=2, padTop=-2, opacity=1.0, idx=0)

    def ChangeSortBy(self, *args):
        pass

    def LoadScroll(self):
        self.scroll.ShowLoading()
        try:
            headers = UpgradeEntry.GetHeaders()
            scrollList = self.GetScrollList()
            if self.destroyed:
                return
            if scrollList == NOT_AVAILABLE:
                self.scroll.LoadContent(contentList=[], noContentHint=GetByLabel('UI/Sovereignty/NotAvailable'))
            else:
                if scrollList:
                    lastDropEntry = GetFromClass(UpgradeLastEntry)
                    scrollList.append(lastDropEntry)
                noContentHint = self.hubController.GetNoInstalledUpgradesHint()
                self.scroll.LoadContent(contentList=scrollList, headers=headers, noContentHint=noContentHint)
                self.UpdateHeaderHints()
        finally:
            self.scroll.HideLoading()

    def UpdateHeaderHints(self):
        for i, eachHeaderChild in enumerate(self.scroll.GetHeadersChildren()):
            eachHeaderChild.GetHint = lambda idx = i: self.GetHeaderHint(idx)

    def GetHeaderHint(self, idx, *args):
        hint = None
        textList = [UpgradeEntry.GetHeaderText(idx), UpgradeEntry.GetHeadersHint(idx)]
        textList = filter(None, textList)
        if textList:
            hint = '<br>'.join(textList)
        if hint:
            from carbonui.uicore import uicore
            uicore.uilib.auxiliaryTooltip = None
        return hint

    def GetScrollList(self):
        entryControllers = self.hubController.GetInstalledUpgradesEntryControllers()
        if entryControllers == NOT_AVAILABLE:
            return NOT_AVAILABLE
        scrollList = []
        for data in entryControllers:
            entry = GetFromClass(UpgradeEntry, {'entryController': data,
             'typeID': data.typeID,
             'hubController': self.hubController})
            scrollList.append(entry)

        return scrollList

    def DoDropData(self, dragObj, entries, idx = -1):
        self.hubController.DoDropData(dragObj, entries, idx)
        self.HidePositionIndicator()

    def OnContentDragEnter(self, dragObj, entries, *args):
        dropError = self.hubController.GetDropError(entries[0])
        if dropError:
            color = eveColor.DANGER_RED
        else:
            color = eveColor.ICE_WHITE
        self.ShowPositionIndicator(color)

    def ShowPositionIndicator(self, color = None):
        if not self.scroll.IsScrollbarVisible() and self.scroll.GetNodes():
            lastDropEntry = self.GetLastDropEntry()
            if lastDropEntry:
                lastDropEntry.ShowIndicator(color)
        else:
            self.changeIndicator.ShowPosIndicator(color)
            if self.scroll.GetNodes():
                self.changeIndicator.align = carbonui.Align.TOBOTTOM
            else:
                self.changeIndicator.align = carbonui.Align.TOTOP_NOPUSH

    def OnContentDragExit(self, *args):
        self.HidePositionIndicator()

    def HidePositionIndicator(self):
        self.changeIndicator.HidePosIndicator()
        lastDropEntry = self.GetLastDropEntry()
        if lastDropEntry:
            lastDropEntry.HideIndicator()

    def GetLastDropEntry(self):
        nodes = self.scroll.GetNodes()
        if nodes:
            return nodes[-1].panel

    def OnOnlineStateChanged(self, typeID):
        self.UpdateUpgradeStates()

    def UpdateUpgradeStates(self):
        self.hubController.UpdateEffectiveStatesForSimulatedUpgrades()
        for node in self.scroll.GetNodes():
            panel = node.panel
            if not panel or isinstance(panel, UpgradeLastEntry):
                continue
            panel.UpdateEffectiveState()
            panel.UpdateOnlineState()

    def GetTabStops(self, headertabs, idx = None):
        scrollWidth, h = self.scroll.GetAbsoluteSize()
        contentWidths = self.tabFinder.GetMaxContentWidths(self.scroll.sr.nodes, UpgradeEntry, idx=idx)
        if idx is not None or not contentWidths:
            return contentWidths
        headerWidths = [ MIN_COL_WIDTH for x in contentWidths ]
        upgradeColumnIdx = x = UpgradeEntry.headerInfo.keys().index('upgrade')
        if not scrollWidth:
            return self.tabFinder.GetMaxTabStops(contentWidths, headerWidths)
        tabStops = self._GetUserDefinedTabStops(scrollWidth, contentWidths, headerWidths, upgradeColumnIdx)
        if tabStops is not None:
            return tabStops
        adjustedContentWidth = self._AdjustUpgradeWidth(contentWidths, scrollWidth, upgradeColumnIdx)
        adjustedContentWidth = adjustedContentWidth or contentWidths
        return self._GetTabStopsFromContentWidths(adjustedContentWidth, headerWidths)

    def _GetUserDefinedTabStops(self, scrollWidth, contentWidth, headerWidths, upgradeColumnIdx):
        _, currentSettings = self.GetCurrentSettingsForScroll()
        userDefinedContentWidth = []
        for i, headerInfo in enumerate(UpgradeEntry.headerInfo.itervalues()):
            calcValue = contentWidth[i]
            val = currentSettings.get(headerInfo.columnText, calcValue)
            if headerInfo.useMinWidth:
                val = max(calcValue, val)
            userDefinedContentWidth.append(val)

        adjustedContentWidth = self._AdjustUpgradeWidth(userDefinedContentWidth, scrollWidth, upgradeColumnIdx)
        if adjustedContentWidth is None:
            return
        return self._GetTabStopsFromContentWidths(adjustedContentWidth, headerWidths)

    def _AdjustUpgradeWidth(self, contentWidths, scrollWidth, updateColumnIdx):
        contentSum = sum(contentWidths)
        if scrollWidth < contentSum:
            upgradeWidth = contentWidths[updateColumnIdx]
            widthWithoutUpgrade = contentSum - upgradeWidth
            available = scrollWidth - widthWithoutUpgrade
            if available < MIN_COL_WIDTH:
                return
            contentWidths[updateColumnIdx] = available
        return contentWidths

    def _GetTabStopsFromContentWidths(self, contentWidths, headerWidths):
        self.SetScrollWidthSettings(contentWidths)
        return self.tabFinder.GetMaxTabStops(contentWidths, headerWidths)

    def SetScrollWidthSettings(self, columnWidths):
        currentSettings, scrollSettings = self.GetCurrentSettingsForScroll()
        for i, headerInfo in enumerate(UpgradeEntry.headerInfo.itervalues()):
            scrollSettings[headerInfo.columnText] = columnWidths[i]

        settings.user.ui.Set('columnWidths_%s' % VERSION, currentSettings)

    def GetCurrentSettingsForScroll(self):
        currentSettings = settings.user.ui.Get('columnWidths_%s' % VERSION, {})
        scrollID = self.scroll.sr.id
        currentSettings.setdefault(scrollID, {})
        scrollSettings = currentSettings[scrollID]
        return (currentSettings, scrollSettings)

    def OnWndEndScale(self):
        if self.scroll:
            self.scroll.UpdateTabStops()

    def Close(self):
        with ExceptionEater('Closing UpgradeScrollCont'):
            self.hubController.on_online_state_changed.disconnect(self.OnOnlineStateChanged)
            self.hubController = None
        super(UpgradeScrollCont, self).Close()
