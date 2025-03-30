#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\infoPanels\infoPanelAirNpe.py
from eve.client.script.ui.shared.infoPanels.const.infoPanelConst import PANEL_AIR_NPE
from eve.client.script.ui.shared.infoPanels.infoPanelObjectiveTracker import InfoPanelObjectiveTracker
from eve.client.script.ui.shared.pointerTool.pointerToolConst import UNIQUE_NAME_AIR_NPE_INFO_PANEL
from storylines.client.objectives.trackers.airnpetracker import AirNpeObjectiveTracker
import localization
from carbonui.uicore import uicore
import carbonui.const as uiconst
SKIP_ICON_PATH = 'res:/UI/Texture/Icons/38_16_201.png'

class InfoPanelAirNpe(InfoPanelObjectiveTracker):
    default_name = 'InfoPanelAirNpe'
    uniqueUiName = UNIQUE_NAME_AIR_NPE_INFO_PANEL
    panelTypeID = PANEL_AIR_NPE
    label = 'UI/Shared/Tutorial'
    default_iconTexturePath = 'res:/ui/Texture/Classes/InfoPanels/opportunitiesTreeIcon.png'
    featureID = 'air_npe'
    OBJECTIVE_TRACKER_CLASS = AirNpeObjectiveTracker

    @staticmethod
    def IsAvailable():
        return bool(AirNpeObjectiveTracker().get_objectives())

    def HasOptionsMenu(self):
        return True

    def GetOptionsMenu(self, menuParent, *args, **kwargs):
        menuParent.AddIconEntry(icon=SKIP_ICON_PATH, text=localization.GetByLabel('UI/SystemMenu/SkipTutorial'), callback=self._Skip, name='utilmenu_SkipTutorial')

    def _Skip(self, *args, **kwargs):
        if uicore.Message('SkipTutorialOffer', buttons=uiconst.YESNO) == uiconst.ID_YES:
            self.objective_tracker.skip_mission()
