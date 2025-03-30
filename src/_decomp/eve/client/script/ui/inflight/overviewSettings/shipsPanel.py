#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\shipsPanel.py
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveIcon import MenuIcon
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.inflight.overview import overviewConst
from eve.client.script.ui.inflight.bracketsAndTargets.bracketNameFormatting import GetAllowedLabelTypes
from eve.client.script.ui.inflight.overviewSettings.overviewBracketLabelPreview import OverviewBracketLabelPreview
from eve.client.script.ui.inflight.overviewSettings.overviewSettingEntries import OverviewLastDropEntry, ShipEntryLinebreak, GetLastEntryToAdd, ShipEntry
from eve.client.script.ui.inflight.overviewSettings.panelUtils import OnContentDragEnter, OnContentDragExit, ResetCbOnReloadingOverviewProfile
from eve.client.script.ui.inflight.overviewShipLabelObject import ShipLabel
from localization import GetByLabel
import overviewPresets.overviewSettingsConst as oConst
from utillib import KeyVal

class ShipsPanel(Container):
    default_name = 'shipsPanel'
    default_state = uiconst.UI_HIDDEN
    __notifyevents__ = ['OnReloadingOverviewProfile']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.cachedScrollPos = 0.0
        self.overviewPresetSvc = sm.GetService('overviewPresetSvc')
        self.settingCheckboxes = []
        labelPreview = OverviewBracketLabelPreview(parent=self, lineBreakFunc=self.AddLineBreak)
        shiptop = Container(name='filtertop', parent=self, align=uiconst.TOTOP, height=57)
        cb = Checkbox(text=GetByLabel('UI/Overview/HideTickerIfInAlliance'), parent=shiptop, settingsKey=oConst.SETTING_HIDE_CORP_TICKER, checked=self.overviewPresetSvc.GetSettingValueOrDefaultFromName(oConst.SETTING_HIDE_CORP_TICKER, False), callback=self.CheckBoxChange, settingsPath=('user', 'overview'), align=uiconst.TOTOP, pos=(0, 30, 0, 16))
        cb.padLeft = 8
        self.hideTickerIfInAlliance = cb
        self.settingCheckboxes.append(cb)
        self.ConstructPresetMenu(shiptop)
        self.ConstructScroll()
        sm.RegisterNotify(self)

    def ConstructPresetMenu(self, shiptop):
        presetMenu = MenuIcon()
        presetMenu.GetMenu = self.GetShipLabelMenu
        presetMenu.left = 6
        presetMenu.top = 10
        presetMenu.hint = ''
        shiptop.children.append(presetMenu)

    def ConstructScroll(self):
        self.scroll = Scroll(name='shipPanelScroll', parent=self)
        self.scroll.multiSelect = 0
        self.scroll.sr.content.OnDropData = self.MoveStuff
        self.scroll.sr.content.OnDragEnter = lambda *args: OnContentDragEnter(self.scroll, *args)
        self.scroll.sr.content.OnDragExit = lambda *args: OnContentDragExit(self.scroll, *args)

    def CheckBoxChange(self, checkbox, node = None):
        settingsKey = checkbox.GetSettingsKey()
        if settingsKey == oConst.SETTING_HIDE_CORP_TICKER:
            sm.GetService('bracket').UpdateLabels()
        elif settingsKey == 'shiplabels' and node:
            sm.GetService('stateSvc').ChangeShipLabels(node.flag, checkbox.checked)

    def GetShipLabelMenu(self):
        return [(GetByLabel('UI/Overview/ShipLabelFormatPilotCC'), self.SetDefaultShipLabel, ('default',)), (GetByLabel('UI/Overview/ShipLabelFormatPilotCCAA'), self.SetDefaultShipLabel, ('ally',)), (GetByLabel('UI/Overview/ShipLabelFormatCCPilotAA'), self.SetDefaultShipLabel, ('corpally',))]

    def SetDefaultShipLabel(self, setting):
        sm.GetService('stateSvc').SetDefaultShipLabel(setting)
        self.LoadShips()

    def LoadShips(self, selected = None):
        shipLabels = sm.GetService('stateSvc').GetShipLabels()
        allLabels = sm.GetService('stateSvc').GetAllShipLabels()
        corpTickerHidden = sm.GetService('overviewPresetSvc').GetSettingValueOrDefaultFromName(oConst.SETTING_HIDE_CORP_TICKER, False)
        self.hideTickerIfInAlliance.SetChecked(corpTickerHidden)
        hints = {overviewConst.LABEL_TYPE_NONE: '',
         overviewConst.LABEL_TYPE_CORP: GetByLabel('UI/Common/CorpTicker'),
         overviewConst.LABEL_TYPE_ALLIANCE: GetByLabel('UI/Shared/AllianceTicker'),
         overviewConst.LABEL_TYPE_PILOT: GetByLabel('UI/Common/PilotName'),
         overviewConst.LABEL_TYPE_SHIP_NAME: GetByLabel('UI/Common/ShipName'),
         overviewConst.LABEL_TYPE_SHIP_TYPE: GetByLabel('UI/Common/ShipType')}
        comments = {overviewConst.LABEL_TYPE_NONE: GetByLabel('UI/Overview/AdditionalTextForCorpTicker'),
         overviewConst.LABEL_TYPE_CORP: GetByLabel('UI/Overview/OnlyShownForPlayerCorps'),
         overviewConst.LABEL_TYPE_ALLIANCE: GetByLabel('UI/Overview/OnlyShownWhenAvailable')}
        newlabels = [ label for label in allLabels if label[overviewConst.LABEL_TYPE] not in [ alabel[overviewConst.LABEL_TYPE] for alabel in shipLabels ] ]
        shipLabels += newlabels
        scrolllist = []
        allowedLabelTypes = GetAllowedLabelTypes()
        for i, flag in enumerate(shipLabels):
            data = KeyVal()
            labelType = flag[overviewConst.LABEL_TYPE]
            if labelType not in allowedLabelTypes:
                continue
            if labelType == overviewConst.LABEL_TYPE_LINEBREAK:
                data.canDrag = True
                data.label = GetByLabel('UI/Overview/Linebreak')
                data.removeFunc = self.RemoveLinebreak
                scrolllist.append(GetFromClass(ShipEntryLinebreak, data))
                continue
            hint = hints[labelType]
            data.label = hint
            data.checked = flag[overviewConst.LABEL_STATE]
            data.cfgname = 'shiplabels'
            data.retval = flag
            data.flag = flag
            data.canDrag = True
            data.hint = hint
            data.comment = comments.get(labelType, '')
            data.OnChange = self.CheckBoxChange
            data.isSelected = selected == i
            scrolllist.append(GetFromClass(ShipEntry, data))

        scrolllist += GetLastEntryToAdd(scrolllist)
        self.scroll.Load(contentList=scrolllist, scrollTo=self.cachedScrollPos)
        maxLeft = 140
        for shipEntry in self.scroll.GetNodes():
            if shipEntry.panel and not isinstance(shipEntry.panel, OverviewLastDropEntry):
                postLeft = shipEntry.panel.sr.label.left + shipEntry.panel.sr.label.textwidth + 4
                maxLeft = max(maxLeft, postLeft)

        for shipEntry in self.scroll.GetNodes():
            if shipEntry.panel and not isinstance(shipEntry.panel, (OverviewLastDropEntry, ShipEntryLinebreak)):
                shipEntry.panel.postCont.left = maxLeft

    def AddLineBreak(self, *args):
        shipLabels = sm.GetService('stateSvc').GetShipLabels()
        x = ShipLabel(labelType=overviewConst.LABEL_TYPE_LINEBREAK).GetDict()
        shipLabels.insert(0, x)
        settings.user.overview.Set(oConst.SETTINGS_SHIP_LABELS, shipLabels)
        self.RefreshShipLabels()

    def RefreshShipLabels(self):
        sm.GetService('stateSvc').cachedStateSettings = {}
        sm.GetService('bracket').UpdateLabels()
        sm.ScatterEvent('OnShipLabelsUpdated')
        self.LoadShips()

    def RemoveLinebreak(self, idx):
        shipLabels = sm.GetService('stateSvc').GetShipLabels()
        if len(shipLabels) - 1 < idx:
            return
        if shipLabels[idx][overviewConst.LABEL_TYPE] == overviewConst.LABEL_TYPE_LINEBREAK:
            shipLabels.pop(idx)
            settings.user.overview.Set(oConst.SETTINGS_SHIP_LABELS, shipLabels)
            self.RefreshShipLabels()

    def MoveStuff(self, dragObj, entries, idx = -1, *args):
        self.MoveShipLabel(idx)

    def MoveShipLabel(self, idx = None, *args):
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
            sm.GetService('stateSvc').ChangeLabelOrder(selected.idx, newIdx)
            self.LoadShips(newIdx)

    def OnReloadingOverviewProfile(self):
        ResetCbOnReloadingOverviewProfile(self.overviewPresetSvc, self.settingCheckboxes)
