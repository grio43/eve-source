#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\objectives\client\objective_task\scanning.py
from carbonui.uicore import uicore
from evedungeons.client.data import GetDungeon
import localization
from probescanning.const import probeResultPerfect, probeResultGood
import eveformat
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from objectives.client.objective_task.base import ObjectiveTask
from objectives.client.objective_task.dungeon import InDungeonTask
from objectives.client.ui.objective_task_widget import ProgressBarTaskWidget

class ScanSignatureTask(ObjectiveTask):
    objective_task_content_id = 19
    WIDGET = ProgressBarTaskWidget
    __notifyevents__ = ['OnClientEvent_PerfectScanResultReached', 'OnSystemScanDone']

    def __init__(self, dungeon_id = None, scan_result = None, **kwargs):
        super(ScanSignatureTask, self).__init__(**kwargs)
        self._dungeon_id = None
        self._scan_result = None
        self._update_highlight()
        self.dungeon_id = dungeon_id
        self.scan_result = scan_result

    def get_values(self):
        result = super(ScanSignatureTask, self).get_values()
        result['scan_result'] = self.scan_result
        result['progress'] = self.progress
        return result

    @property
    def dungeon_id(self):
        return self._dungeon_id

    @dungeon_id.setter
    def dungeon_id(self, value):
        if self._dungeon_id == value:
            return
        self._dungeon_id = value
        if self._dungeon_id:
            dungeon_data = GetDungeon(self.dungeon_id)
            self._title = localization.GetByMessageID(dungeon_data.dungeonNameID)
            self.update()

    @property
    def scan_result(self):
        return self._scan_result

    @scan_result.setter
    def scan_result(self, value):
        if self._scan_result == value:
            return
        self._scan_result = value
        self.update()
        if self._scan_result:
            self.completed = self._scan_result.certainty >= probeResultPerfect
        else:
            self.completed = False
        self._update_highlight()

    def _update_highlight(self):
        from nodegraph.client.actions.blinks import BlinkUiElement, BlinkUiElementByUniqueName
        if self._scan_result:
            self.highlight = BlinkUiElement(ui_element_path='scan_result_{}'.format(self._scan_result.id))
        else:
            self.highlight = BlinkUiElementByUniqueName(unique_ui_name=pConst.UNIQUE_NAME_PROBE_REFRESH, chain_blinks=True)

    def _update_title(self):
        if self.dungeon_id:
            dungeon_data = GetDungeon(self.dungeon_id)
            title = localization.GetByMessageID(dungeon_data.dungeonNameID)
            if self.scan_result:
                title = u'{} {}'.format(self.scan_result.id, title)
            self._title = title

    @property
    def value(self):
        if self.scan_result:
            return self.scan_result.id
        return u'{}%'.format(eveformat.number(self.progress * 100, decimal_places=1))

    @property
    def progress(self):
        if self._scan_result:
            return self._scan_result.certainty
        return 0.0

    def _start(self):
        super(ScanSignatureTask, self)._start()
        self.OnSystemScanDone()

    def OnSystemScanDone(self):
        if self.completed:
            return
        results, _, _, _ = sm.GetService('scanSvc').GetResults()
        matching_results = self._get_matching_results(results)
        max_certainty = self.scan_result.certainty if self.scan_result else -1
        scan_result = None
        for result in matching_results:
            if result.certainty >= probeResultPerfect:
                scan_result = result
                break
            if result.certainty > max_certainty:
                scan_result = result
                max_certainty = result.certainty

        if scan_result and scan_result.certainty >= probeResultGood:
            self.scan_result = scan_result

    def _get_matching_results(self, results):
        matching = []
        for result in results:
            if self.dungeon_id:
                if result.dungeonID == self.dungeon_id:
                    matching.append(result)

        return matching

    def double_click(self, *args):
        if not self.completed:
            uicore.cmd.OpenProbeScanner()


class WarpToScanResult(InDungeonTask):
    objective_task_content_id = 20

    def __init__(self, scan_result = None, **kwargs):
        super(WarpToScanResult, self).__init__(**kwargs)
        self._scan_result = None
        self.scan_result = scan_result

    @property
    def scan_result(self):
        return self._scan_result

    @scan_result.setter
    def scan_result(self, value):
        if self._scan_result == value:
            return
        self._scan_result = value
        if self._scan_result:
            self.dungeon_id = self.scan_result.dungeonID
        else:
            self.dungeon_id = None

    def double_click(self, *args):
        if self.scan_result:
            sm.GetService('menu').WarpToScanResult(self.scan_result.id)

    def get_context_menu(self):
        pass
