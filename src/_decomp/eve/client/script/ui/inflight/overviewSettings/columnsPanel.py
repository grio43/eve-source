#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\columnsPanel.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.button.group import ButtonGroup
import overviewPresets.overviewSettingsConst as osConst
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelLarge
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.inflight.overview import overviewConst, overviewColumns
from eve.client.script.ui.inflight.overviewSettings.overviewSettingEntries import GetLastEntryToAdd, ColumnEntry
from eve.client.script.ui.inflight.overviewSettings.panelUtils import OnContentDragEnter, OnContentDragExit
from eve.common.lib import appConst as const
from localization import GetByLabel
from utillib import KeyVal

class ColumnsPanel(Container):
    default_name = 'columnsPanel'
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.tabID = attributes.get('tabID', None)
        self.cachedScrollPos = 0.0
        self.presetSvc = sm.GetService('overviewPresetSvc')
        EveLabelLarge(text=GetByLabel('UI/Overview/HintToggleDisplayStateAndOrder'), parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padding=(8, 4, 0, 8))
        colbtns = ButtonGroup(parent=self, idx=0)
        colbtns.AddButton(GetByLabel('UI/Overview/ResetColumns'), self.ResetColumns)
        self.scroll = Scroll(name='columnsScroll', parent=self, padding=const.defaultPadding)
        self.scroll.multiSelect = 0
        self.scroll.sr.content.OnDropData = self.MoveStuff
        self.scroll.sr.content.OnDragEnter = lambda *args: OnContentDragEnter(self.scroll, *args)
        self.scroll.sr.content.OnDragExit = lambda *args: OnContentDragExit(self.scroll, *args)

    def ResetColumns(self, *args):
        self.presetSvc.ResetTabVisibleColumnIDs(self.tabID)
        self.presetSvc.ResetTabColumnOrder(self.tabID)
        self.LoadColumns()
        sm.GetService('stateSvc').NotifyOnStateSetupChange('column reset')

    def LoadColumns(self, selected = None, loadFromTop = False):
        userSet = overviewColumns.GetColumns(self.tabID)
        userSetOrder = overviewColumns.GetColumnOrder(self.tabID)
        missingColumns = [ col for col in overviewConst.ALL_COLUMNS if col not in userSetOrder ]
        userSetOrder += missingColumns
        i = 0
        scrolllist = []
        for columnID in userSetOrder:
            data = KeyVal()
            data.label = overviewColumns.GetColumnLabel(columnID)
            data.checked = columnID in userSet
            data.cfgname = osConst.CONFIG_COLUMNS
            data.retval = columnID
            data.canDrag = True
            data.isSelected = selected == i
            data.OnChange = self.CheckBoxChange
            scrolllist.append(GetFromClass(ColumnEntry, data=data))
            i += 1

        scrolllist += GetLastEntryToAdd(scrolllist)
        scrollTo = 0.0 if loadFromTop else self.cachedScrollPos
        self.scroll.Load(contentList=scrolllist, scrollTo=scrollTo)

    def CheckBoxChange(self, checkbox, node):
        checked = checkbox.checked
        columnID = node.retval
        current = overviewColumns.GetColumns(self.tabID)[:]
        while columnID in current:
            current.remove(columnID)

        if checked:
            current.append(columnID)
        self.presetSvc.SetTabVisibleColumnIDs(self.tabID, current)
        self.DoFullOverviewReload()

    def DoFullOverviewReload(self):
        sm.ScatterEvent('OnFullOverviewReload')

    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        self.MoveColumn(idx)

    def MoveColumn(self, idx = None, *args):
        self.cachedScrollPos = self.scroll.GetScrollProportion()
        selected = self.scroll.GetSelected()
        if selected:
            selected = selected[0]
            if idx is not None:
                if idx != selected.idx:
                    if selected.idx < idx:
                        newIdx = idx - 1
                    else:
                        newIdx = idx
                else:
                    return
            else:
                newIdx = max(0, selected.idx - 1)
            column = selected.retval
            current = overviewColumns.GetColumnOrder(self.tabID)[:]
            while column in current:
                current.remove(column)

            if newIdx == -1:
                newIdx = len(current)
            current.insert(newIdx, column)
            self.presetSvc.SetTabColumnOrder(self.tabID, current)
            self.LoadColumns(newIdx)
            self.DoFullOverviewReload()
