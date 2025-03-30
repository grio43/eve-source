#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\overviewSettings\historyPanel.py
from carbon.common.script.util.format import FmtDate
from carbonui.primitives.container import Container
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.control.button import Button
from eve.client.script.ui.control.eveEditPlainText import EditPlainText
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelSmall
from localization import GetByLabel
from overviewPresets.client.link import overview_preset_link
import overviewPresets.overviewSettingsConst as oConst

class HistoryPanel(Container):
    default_name = 'HistoryPanel'
    default_state = uiconst.UI_HIDDEN

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.presetSvc = sm.GetService('overviewPresetSvc')
        historyCont = Container(name='historyCont', parent=self, align=uiconst.TOALL)
        self.restoreCont = ContainerAutoSize(name='historyCont', parent=historyCont, align=uiconst.TOBOTTOM, left=const.defaultPadding, width=const.defaultPadding, alignMode=uiconst.TOTOP)
        Line(parent=historyCont, align=uiconst.TOBOTTOM, color=(1, 1, 1, 0.1))
        restoreButton = Button(parent=self.restoreCont, label=GetByLabel('UI/Overview/RestoreProfile'), func=self.RestoreOldOverview, left=10, align=uiconst.CENTERRIGHT)
        restoreLabel = EveLabelMedium(text=GetByLabel('UI/Overview/AutomaticallyStoredOverviewHeader'), parent=self.restoreCont, align=uiconst.TOTOP, padding=(10,
         3,
         restoreButton.width + 10,
         0), state=uiconst.UI_DISABLED)
        self.restoreOverviewNameLabel = EveLabelSmall(text='', parent=self.restoreCont, align=uiconst.TOTOP, padding=(10,
         0,
         restoreButton.width + 10,
         2), state=uiconst.UI_DISABLED)
        historyText = EveLabelMedium(text=GetByLabel('UI/Overview/HistoryText'), parent=historyCont, align=uiconst.TOTOP, padding=(10, 3, 10, 0), state=uiconst.UI_DISABLED)
        historyText.SetRGBA(1, 1, 1, 0.8)
        self.historyEdit = EditPlainText(setvalue='', parent=historyCont, align=uiconst.TOALL, readonly=True, pos=(10, -2, 10, 0))
        self.historyEdit.HideBackground()
        self.historyEdit.RemoveActiveFrame()
        return historyCont

    def RestoreOldOverview(self, *args):
        self.presetSvc.RestoreAutoSavedOverviewProfile()
        self.UpdateRestoreCont()

    def LoadHistory(self):
        presetHistoryKeys = settings.user.overview.Get(oConst.SETTING_HISTORY_KEYS, {})
        textList = []
        for eachKey, eachValue in presetHistoryKeys.iteritems():
            overviewName = eachValue.get('overviewName', 'overview_name')
            presetKey = eachValue.get('presetKey')
            timestamp = eachValue.get('timestamp')
            link = overview_preset_link(presetKey, overviewName)
            text = GetByLabel('UI/Overview/ProfileLinkWithTimestamp', profileLink=link, timestamp=FmtDate(timestamp))
            textList.append((timestamp, text))

        textList = SortListOfTuples(textList, reverse=True)
        allText = '<br>'.join(textList[:15])
        self.historyEdit.SetValue(allText)
        self.UpdateRestoreCont()

    def UpdateRestoreCont(self):
        restoreData = settings.user.overview.Get(oConst.SETTING_RESTORE_DATA, {})
        if not restoreData:
            self.restoreCont.display = False
            return
        self.restoreCont.display = True
        overviewName = restoreData['name']
        timestamp = restoreData['timestamp']
        self.restoreOverviewNameLabel.text = GetByLabel('UI/Overview/StoredOverviewBasedOn', overviewName=overviewName, timestamp=FmtDate(timestamp))
