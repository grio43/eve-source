#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\scannerFiles\scanResults.py
import blue
from carbon.common.script.sys.service import ROLE_QA
from carbon.common.script.util.timerstuff import AutoTimer
import carbonui.const as uiconst
from carbonui.control.basicDynamicScroll import BasicDynamicScroll
from carbonui.uianimations import animations
from eve.common.script.sys.eveCfg import IsControllingStructure
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.scrollColumnHeader import ScrollColumnHeader
from eve.client.script.ui.inflight.scannerFiles.swipeAnimation import SwipeAnimator
from eve.client.script.ui.inflight.scannerListEntries import ScanResultNew
from eve.client.script.ui.shared.mapView.markers.mapMarkerUtil import GetResultTexturePath
from gametime import GetSimTime, GetTimeDiff
from localization import GetByLabel
from logging import getLogger
from menu import MenuLabel
from probescanning.const import probeScanGroupAnomalies
from sensorsuite.overlay.controllers.probescanner import SiteDataFromScanResult
from uthread2 import call_after_wallclocktime_delay
from utillib import KeyVal
logger = getLogger(__name__)

class ScanResults(BasicDynamicScroll):
    __notifyevents__ = ['OnSiteSelectionChanged', 'OnCosmicAnomalyAdded', 'OnCosmicSignatureAdded']

    def ApplyAttributes(self, attributes):
        self._scan_service = None
        self._michelle = None
        super(ScanResults, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.palette = attributes.palette
        self.swipe_animator = SwipeAnimator(parent=self, name='scanAnimator', align=uiconst.TOLEFT_PROP, clipChildren=True)
        self.sort_headers = ScrollColumnHeader(parent=self, settingsID='probescannerwindow_resultScrollList', idx=0, scroll=self, entryClass=ScanResultNew, padBottom=4)
        for header in self.sort_headers.headers:
            header.OnClick = (self.on_header_clicked, header)

        self.highlighted_target_ids = set()
        self.update_timer = AutoTimer(interval=1500, method=self.update_results)

    def Close(self, *args):
        sm.UnregisterNotify(self)
        if self.update_timer:
            self.update_timer.KillTimer()
            self.update_timer = None
        super(ScanResults, self).Close(*args)

    @property
    def scan_service(self):
        if self._scan_service is None:
            self._scan_service = sm.GetService('scanSvc')
        return self._scan_service

    @property
    def michelle(self):
        if self._michelle is None:
            self._michelle = sm.GetService('michelle')
        return self._michelle

    def OnSelectionChange(self, *args):
        selected = self.GetSelected()
        self.scan_service.SetSelectedSites([ site.id for site in selected ])

    def OnSiteSelectionChanged(self):
        nodes = self.GetNodes()
        for node in nodes:
            if not node.panel:
                continue
            if self.scan_service.IsSiteSelected(node.id):
                node.panel.Select()
            else:
                node.panel.Deselect()

    def on_system_scan_started(self):
        current_scan = self.scan_service.GetCurrentScan()
        if current_scan is None:
            return
        dilation_multiplier = 1.0 / max(blue.os.desiredSimDilation, 0.1)
        swipe_duration = dilation_multiplier * current_scan.duration / 1000 + 0.5
        self._start_animation(resultsFadeDuration=0.5, swipeDuration=swipe_duration, swipeFadeInDuration=0.5, swipeFadeOutDuration=0.5, swipeHighlightDuration=0.3)

    def on_system_scan_ended(self):
        self._end_animation(resultsFadeDuration=0.7)

    def OnCosmicAnomalyAdded(self, anomaly):
        target_id = anomaly.targetID
        self.highlight_entry(target_id)

    def OnCosmicSignatureAdded(self, target_id):
        self.highlight_entry(target_id)

    def highlight_entry(self, target_id):
        self._add_highlight(target_id)
        if self.IsVisible():
            self._show_quick_swipe(callback=self.palette.Refresh)
        else:
            self.palette.Refresh()

    def _show_quick_swipe(self, callback = None):
        swipe_duration = 1.0
        results_fade_in_duration = 0.15 * swipe_duration
        results_fade_out_duration = 0.21 * swipe_duration
        end_delay = 0.8 * swipe_duration
        callback_delay = 0.6 * swipe_duration
        self._start_animation(results_fade_in_duration, swipe_duration)
        call_after_wallclocktime_delay(self._end_animation, delay=end_delay, resultsFadeDuration=results_fade_out_duration)
        if callable(callback):
            call_after_wallclocktime_delay(callback, delay=callback_delay)

    def _start_animation(self, resultsFadeDuration, swipeDuration, swipeFadeInDuration = None, swipeFadeOutDuration = None, swipeHighlightDuration = None):
        animations.FadeTo(self, duration=resultsFadeDuration, startVal=1.0, endVal=0.5)
        self.swipe_animator.start(swipeDuration, swipeFadeInDuration, swipeHighlightDuration, swipeFadeOutDuration)

    def _end_animation(self, resultsFadeDuration):
        animations.FadeIn(self, duration=resultsFadeDuration, curveType=uiconst.ANIM_OVERSHOT5)

    def on_header_clicked(self, header):
        self.load_results()
        self.sort_headers.ClickHeader(header)

    def get_result_entry(self, columnWidths, myPos, result):
        displayName = self.scan_service.GetDisplayName(result)
        scanGroupName = self.scan_service.GetScanGroupName(result)
        groupName = self.scan_service.GetGroupName(result)
        typeName = self.scan_service.GetTypeName(result)
        distance = result.GetDistance(myPos)
        sortValues = [GetResultTexturePath(result),
         distance,
         result.id,
         displayName,
         groupName,
         min(1.0, result.certainty)]
        data = KeyVal()
        data.sortValues = sortValues
        data.columnID = 'probeResultColumn'
        data.displayName = displayName
        data.scanGroupName = scanGroupName
        data.groupName = groupName
        data.typeName = typeName
        data.result = result
        data.GetMenu = self.result_menu
        data.distance = distance
        data.newResult = True
        data.columnWidths = columnWidths
        data.itemID = result.itemID
        data.id = result.id
        data.isSelected = self.scan_service.IsSiteSelected(result.id)
        entry = GetFromClass(ScanResultNew, data)
        return entry

    def result_menu(self, panel, *args):
        result = panel.sr.node.result
        menu = []
        siteData = SiteDataFromScanResult(result)
        menu.extend(self.scan_service.GetScanResultMenuWithoutIgnore(siteData))
        nodes = self.GetSelected() or [panel.sr.node]
        idList = []
        nonAnomalyIdList = []
        for node in nodes:
            if hasattr(node.result, 'id'):
                idList.append(node.result.id)
                if node.result.scanGroupID != probeScanGroupAnomalies:
                    nonAnomalyIdList.append(node.result.id)

        menu.append((MenuLabel('UI/Inflight/Scanner/IngoreResult'), self.scan_service.IgnoreResult, idList))
        menu.append((MenuLabel('UI/Inflight/Scanner/IgnoreOtherResults'), self.scan_service.IgnoreOtherResults, idList))
        if session.role & ROLE_QA:
            menu.append(('QA', [('Scan selected sites', self.scan_service.QAScanSites, idList),
              None,
              ('Dungeon ID: {}'.format(result.dungeonID), None),
              ('Archetype ID: {}'.format(result.archetypeID), None)]))
        return menu

    def load_results(self):
        if self.destroyed:
            return
        current_scan = self.scan_service.GetCurrentScan()
        scanning_probes = self.scan_service.GetScanningProbes()
        my_position = sm.GetService('michelle').GetMyPosition()
        if not my_position:
            return
        results, ignored, filtered, filtered_anomalies = self.scan_service.GetResults()
        column_widths = self.sort_headers.GetColumnWidths()
        resultList = []
        if current_scan and GetTimeDiff(current_scan.startTime, GetSimTime()) < current_scan.duration:
            return
        if scanning_probes and session.shipid not in scanning_probes:
            return
        if results:
            for result in results:
                entry = self.get_result_entry(column_widths, my_position, result)
                resultList.append(entry)

        scroll_position = self.GetScrollProportion()
        self.Clear()
        sorted_results = self.get_sorted_results(resultList)
        if IsControllingStructure():
            self.ShowHint(hint=GetByLabel('UI/Inflight/Scanner/ProbeScanDisabledInStructure'))
        else:
            self.AddNodes(0, sorted_results)
            self._apply_highlights(sorted_results)
            if scroll_position:
                self.ScrollToProportion(scroll_position)
            if sorted_results:
                self.ShowHint()
                self.sort_headers.Show()
            else:
                self.sort_headers.Hide()
                self.ShowHint(hint=self.get_no_scan_results_text(filtered, ignored, filtered_anomalies))
            self.palette.ShowFilteredAndIgnored(filtered, ignored, filtered_anomalies)
        self.palette.RefreshProbeResults()

    def _apply_highlights(self, results):
        for result in results:
            self._apply_highlight(result)

    def _apply_highlight(self, result):
        result_id = getattr(result, 'id', None)
        if result_id and result_id in self.highlighted_target_ids:
            panel = getattr(result, 'panel', None)
            if panel:
                panel.ShowNewResultHighlight()
                panel.RegisterForMouseExit(self._remove_highlight)
                logger.debug('Scan result highlights: {} had highlight applied'.format(result_id))

    def _add_highlight(self, result_id):
        self.highlighted_target_ids.add(result_id)
        logger.debug('Scan result highlights: {} added to the list to highlight'.format(result_id))

    def _remove_highlight(self, panel, result_id):
        self.highlighted_target_ids.discard(result_id)
        panel.UnregisterForMouseExit(self._remove_highlight)
        logger.debug('Scan result highlights: {} had highlight removed'.format(result_id))

    def update_results(self):
        if not self.michelle.InWarp():
            return
        nodes = self.GetNodes()
        my_position = self.michelle.GetMyPosition()
        if not nodes or not my_position:
            return
        for node in nodes:
            if not node or not node.result:
                continue
            distance = node.result.GetDistance(my_position)
            node.distance = distance
            node.sortValues[1] = distance
            if not node.panel:
                continue
            node.panel.UpdateDistanceText()

        sorted_results = self.get_sorted_results(nodes)
        self.SetOrderedNodes(sorted_results)

    def get_sorted_results(self, results):
        _, column_direction = self.sort_headers.GetActiveColumnAndDirection()
        sorted_results = sorted(results, key=self.get_sort_value, reverse=not column_direction)
        return sorted_results

    def get_sort_value(self, node):
        columns = ScanResultNew.GetColumns()
        active_column, _ = self.sort_headers.GetActiveColumnAndDirection()
        active_colum_index = columns.index(active_column) if active_column else 0
        return node.sortValues[active_colum_index]

    def get_no_scan_results_text(self, filtered, ignored, filteredAnomalies):
        if IsControllingStructure():
            return GetByLabel('UI/Inflight/Scanner/ProbeScanDisabledInStructure')
        if ignored and (filtered or filteredAnomalies):
            text = GetByLabel('UI/Inflight/Scanner/FilteredAndIgnoredResults')
        elif ignored:
            text = GetByLabel('UI/Inflight/Scanner/IgnoredResults')
        elif filtered or filteredAnomalies:
            text = GetByLabel('UI/Inflight/Scanner/FilteredResults')
        else:
            text = GetByLabel('UI/Inflight/Scanner/NoScanResults')
        return text
