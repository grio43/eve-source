#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelMissions.py
import blue
import carbonui.const as uiconst
from carbonui.control.scrollContainer import ScrollContainer
from eve.client.script.ui.shared.infoPanels.const.infoPanelUIConst import PANELWIDTH, LEFTPAD
from eve.client.script.ui.shared.infoPanels.const import infoPanelConst
from eve.client.script.ui.shared.infoPanels.InfoPanelBase import InfoPanelBase
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_MISSION_INFO_PANEL
from localization import GetByLabel
from missions.client.ui.missionEntry import MissionEntry
MISSION_CONTAINER_WIDTH = PANELWIDTH - LEFTPAD
PADDING_MISSION_TO_MISSION = 12
PADDING_INFO_PANEL_TITLE_TO_HEADER = 4
SCROLL_CONTAINER_HEIGHT_MAX = 450
EXPANDED_MISSION_INDEX = 'ExpandedMissionIndex'
MISSION_INDEX_NONE = None
MISSION_INDEX_UNSET = -1
SCROLL_DATA_SETTING = 'MissionInfoPanelScrollData'

class InfoPanelMissionData(object):
    DEFAULT_ICON_TEXTURE_PATH = None
    DEFAULT_ICON_OPACITY = 0.7
    DEFAULT_ICON_COLOR = None

    def __init__(self, title, icon = None):
        self.title = title
        self.icon = icon or self.DEFAULT_ICON_TEXTURE_PATH
        self._InitializeObjectives()

    def _InitializeObjectives(self):
        self.objectives = []

    def GetObjectives(self):
        return self.objectives

    def GetIcon(self):
        return (self.icon, self.DEFAULT_ICON_OPACITY, self.DEFAULT_ICON_COLOR)

    def GetID(self):
        return self.title

    def GetContextMenu(self):
        return None

    def GetStateColor(self):
        return None

    @property
    def hint(self):
        return self.title


class InfoPanelMissions(InfoPanelBase):
    default_state = uiconst.UI_PICKCHILDREN
    uniqueUiName = UNIQUE_NAME_MISSION_INFO_PANEL
    default_are_objectives_collapsable = True
    hasSettings = False
    MAINPADTOP = 4
    featureID = None
    __notifyevents__ = InfoPanelBase.__notifyevents__ + ['OnExpandedMissionChanged']

    def ApplyAttributes(self, attributes):
        self.missions = []
        self.missionContainers = {}
        self.header = None
        self.scrollContainer = None
        self.expandedMissionIndex = None
        InfoPanelBase.ApplyAttributes(self, attributes)
        self._ConstructHeader()

    def GetTitle(self):
        if self.label:
            return GetByLabel(self.label)
        return ''

    def ConstructNormal(self):
        self.missions = self.GetMissions()
        self.mainCont.Flush()
        self.scrollContainer = ScrollContainer(name='missions_scroll_container', parent=self.mainCont, align=uiconst.TOTOP, height=0)
        for missionIndex, mission in enumerate(self.missions):
            objectives = mission.GetObjectives()
            top = self._GetMissionContainerTop(missionIndex)
            missionContainer = MissionEntry(name='mission_container_%s' % mission.GetID(), parent=self.scrollContainer, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN, width=MISSION_CONTAINER_WIDTH, top=top, missionIndex=missionIndex, mission=mission, objectives=objectives, HasOptionsMenu=self.HasOptionsMenu, GetOptionsMenu=self.GetOptionsMenu, UpdateExpandedStateForMission=self.UpdateExpandedStateForMission, callback=self.UpdateScrollHeight, isCollapsable=self.default_are_objectives_collapsable)
            self.missionContainers[missionIndex] = missionContainer

        self.InitializeExpandedStates()
        self.UpdateScrollHeight()
        self.UpdateScrollPosition()

    def Hide(self, *args):
        self.SaveScrollData()
        super(InfoPanelMissions, self).Hide(*args)

    def Close(self):
        self.SaveScrollData()
        super(InfoPanelMissions, self).Close()

    def OnBeforeModeChanged(self, oldMode):
        self.SaveScrollData()
        super(InfoPanelMissions, self).OnBeforeModeChanged(oldMode)

    def _ConstructHeader(self):
        self.header = self.headerCls(name='missions_container', parent=self.headerCont, align=uiconst.CENTERLEFT, text=self.GetTitle())

    def _GetMissionContainerTop(self, missionIndex):
        if missionIndex > 0:
            return PADDING_MISSION_TO_MISSION
        return 0

    def UpdateScrollHeight(self):
        if self.scrollContainer and not self.scrollContainer.destroyed:
            totalHeight = self.scrollContainer.mainCont.height
            self.scrollContainer.height = min(totalHeight, SCROLL_CONTAINER_HEIGHT_MAX)
            self.scrollContainer.clipCont.clipChildren = totalHeight > SCROLL_CONTAINER_HEIGHT_MAX

    def UpdateScrollPosition(self):
        blue.synchro.Yield()
        if self.scrollContainer and not self.scrollContainer.destroyed:
            scrollFraction, scrollHeight = self.GetScrollDataSetting()
            currentScrollHeight = self.scrollContainer.height
            if scrollFraction and scrollHeight and 0.0 <= scrollFraction <= 1.0 and scrollHeight == currentScrollHeight:
                self.scrollContainer.ScrollToVertical(scrollFraction)

    def SaveScrollData(self):
        if self.scrollContainer and not self.scrollContainer.destroyed:
            scrollFraction = self.scrollContainer.GetPositionVertical()
            currentScrollHeight = self.scrollContainer.height
            self.SetScrollDataSetting((scrollFraction, currentScrollHeight))

    def ScrollToMission(self, missionIndex):
        missionContainer = self.missionContainers[missionIndex]
        _, topContainer, _, heightContainer = missionContainer.GetAbsolute()
        _, topScroll, _, heightScroll = self.scrollContainer.GetAbsolute()
        heightDifference = heightScroll - heightContainer
        if heightDifference > 0:
            scrollFraction = float(topContainer - topScroll) / heightDifference
            self.scrollContainer.ScrollToVertical(scrollFraction)

    def OnStartModeChanged(self, oldMode):
        if not self.featureID or not oldMode:
            return
        self._UpdateExpandedState()

    def InitializeExpandedStates(self):
        if not self.featureID:
            missionIndex = self.GetExpandedMissionIndex()
            self.UpdateExpandedStateForMission(missionIndex)
            return
        self._UpdateExpandedState()

    def _UpdateExpandedState(self):
        if self.mode == infoPanelConst.MODE_NORMAL:
            expandedMission = sm.GetService('infoPanel').GetExpandedMission()
            missionIndex = None
            if not expandedMission or expandedMission['missionID'] == -1:
                missionIndex = self.GetExpandedMissionIndex()
                if missionIndex in (None, -1):
                    missionIndex = self.GetDefaultExpandedMissionIndex()
                if missionIndex is not None:
                    self._CacheExpandedMission(missionIndex)
            elif expandedMission['featureID'] == self.featureID:
                missionIndex = self.GetIndexForMissionID(expandedMission['missionID'])
            if missionIndex is not None:
                self.TurnOnExpandedMissionIndex(missionIndex)
        else:
            self._CacheExpandedMission(-1)

    def OnExpandedMissionChanged(self, featureID = None, missionID = None):
        if not self.featureID or not featureID or featureID == self.featureID:
            return
        self.expandedMissionIndex = -1
        self.UpdateExpandedStates()

    def UpdateExpandedStateForMissionID(self, missionID):
        self.UpdateExpandedStateForMission(missionID)

    def UpdateExpandedStateForMission(self, missionIndex):
        indexToExpand = MISSION_INDEX_UNSET if missionIndex == self.expandedMissionIndex else missionIndex
        self.TurnOnExpandedMissionIndex(indexToExpand)
        self._CacheExpandedMission(indexToExpand)

    def TurnOnExpandedMissionIndex(self, missionIndex):
        self.SetExpandedMissionIndex(missionIndex)
        self.UpdateExpandedStates()

    def GetMissionIDForIndex(self, index):
        return index

    def GetIndexForMissionID(self, missionID):
        return missionID

    def _CacheExpandedMission(self, index):
        if not self.featureID:
            return
        if index == -1:
            expandedMission = sm.GetService('infoPanel').GetExpandedMission()
            if expandedMission.get('featureID') != self.featureID:
                return
        if index != -1:
            index = self.GetMissionIDForIndex(index)
        sm.GetService('infoPanel').SetExpandedMission(self.featureID, index)

    def UpdateExpandedStates(self):
        for missionIndex, missionContainer in self.missionContainers.items():
            if missionIndex == self.expandedMissionIndex:
                missionContainer.ShowObjectives()
            else:
                missionContainer.HideObjectives()

    def GetDefaultExpandedMissionIndex(self):
        if len(self.missions) > 0:
            return 0
        return MISSION_INDEX_NONE

    def GetExpandedMissionIndexSettingName(self):
        return '%s_%s' % (EXPANDED_MISSION_INDEX, self.panelTypeID)

    def GetExpandedMissionIndex(self):
        settingName = self.GetExpandedMissionIndexSettingName()
        return settings.char.ui.Get(settingName, self.GetDefaultExpandedMissionIndex())

    def SetExpandedMissionIndex(self, missionIndex):
        self.expandedMissionIndex = missionIndex
        settingName = self.GetExpandedMissionIndexSettingName()
        settings.char.ui.Set(settingName, missionIndex)

    def GetScrollDataSettingName(self):
        return '%s_%s' % (SCROLL_DATA_SETTING, self.panelTypeID)

    def GetScrollDataSetting(self):
        settingName = self.GetScrollDataSettingName()
        return settings.char.ui.Get(settingName, (None, None))

    def SetScrollDataSetting(self, scrollData):
        settingName = self.GetScrollDataSettingName()
        return settings.char.ui.Set(settingName, scrollData)

    def GetMissions(self):
        raise NotImplementedError('InfoPanelMissions::GetMissions must be implemented in derived classes.')

    def HasOptionsMenu(self):
        return False

    def GetOptionsMenu(self, menuParent, mission):
        raise NotImplementedError('InfoPanelMissions::GetOptionsMenu must be implemented in derived classes.')
