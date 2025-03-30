#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\solarsysteminterference\client\ui\interference_indicator.py
import localization
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from solarsysteminterference.util import SystemCanHaveInterference

class InterferenceIndicator(ContainerAutoSize):
    default_alignMode = uiconst.TOPLEFT
    LABEL_DISPLAY_INTERFERENCE = 'UI/SolarSystemInterference/DisplayInterferenceLevel'
    ICON_PATH = 'res:/UI/Texture/icons/interference_icon.png'
    ICON_COLOR = '#FFFFFF'
    __notifyevents__ = ['OnSolarsystemInterferenceChanged_Local']

    def ApplyAttributes(self, attributes):
        super(InterferenceIndicator, self).ApplyAttributes(attributes)
        self.systemInterferenceSvc = attributes.get('systemInterferenceSvc')
        self._RefreshInterferenceLevel()
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.infoPanelService = sm.GetService('infoPanel')
        if self.interference_level is not None:
            Sprite(parent=self, align=uiconst.TOPLEFT, texturePath=self.ICON_PATH, width=23, height=23, color=Color.HextoRGBA(self.ICON_COLOR), state=uiconst.UI_NORMAL).hint = localization.GetByLabel(self.LABEL_DISPLAY_INTERFERENCE, interference=round(self.interference_level * 100.0, 2))

    def OnSolarsystemInterferenceChanged_Local(self):
        self._RefreshInterferenceLevel()

    def Refresh(self):
        self._RefreshInterferenceLevel()

    def _RefreshInterferenceLevel(self):
        self.interference_level = None
        self.quiescent_interference_level = None
        self.max_interference_level = None
        if SystemCanHaveInterference(session.solarsystemid2):
            interference_state = self.systemInterferenceSvc.GetLocalInterferenceStateNow()
            if interference_state:
                self.interference_level = interference_state.normalisedInterferenceLevel
        self.Flush()
        self.ConstructLayout()
