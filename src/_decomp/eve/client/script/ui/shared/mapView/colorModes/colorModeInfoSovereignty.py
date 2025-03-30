#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\mapView\colorModes\colorModeInfoSovereignty.py
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.shared.mapView.colorModes.colorModeInfoBase import ColorModeInfoSearchBase
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_FACTION, STARMODE_FILTER_FACWAR_ALL
import uthread
from eve.common.script.search.const import ResultType

class ColorModeInfoSearch_Faction(ColorModeInfoSearchBase):
    settingsKey = 'Search_Faction'
    searchFor = [ResultType.alliance, ResultType.faction]

    def OnSearchCleared(self):
        from eve.client.script.ui.shared.mapView.mapViewColorHandler import GetColorStarsByFactionSearchArgs, SetColorStarsByFactionSearchArgs
        if GetColorStarsByFactionSearchArgs() != STARMODE_FILTER_FACWAR_ALL:
            SetColorStarsByFactionSearchArgs(STARMODE_FILTER_FACWAR_ALL)
            self._LoadColorMode(STARMODE_FILTER_FACWAR_ALL)

    def OnSearchEntrySelected(self, selectedDataList, *args, **kwds):
        selectedNode = selectedDataList[0]
        self.delaySelectionTimer = AutoTimer(500, self._LoadColorMode, selectedNode.charID)

    def _LoadColorMode(self, filterFactionID, *args, **kwds):
        self.delaySelectionTimer = None
        if not self.mapView:
            return
        mapView = self.mapView()
        if not mapView:
            return
        from eve.client.script.ui.shared.mapView.mapViewColorHandler import SetColorStarsByFactionSearchArgs
        SetColorStarsByFactionSearchArgs(filterFactionID)
        uthread.new(mapView.SetMapFilter, STARMODE_FACTION)
