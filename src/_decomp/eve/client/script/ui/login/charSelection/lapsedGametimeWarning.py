#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charSelection\lapsedGametimeWarning.py
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.control.eveIcon import Icon
import carbonui.const as uiconst
import localization

class LapsedGametimeWarning(Container):
    default_state = uiconst.UI_DISABLED
    default_align = uiconst.TOTOP
    default_bgColor = (0.6667, 0.0745, 0.1333, 0.65)
    default_height = 38

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self._ConstructLapsedOmegaTimeWarning()

    def _ConstructLapsedOmegaTimeWarning(self):
        lapsedSubCenterContainer = ContainerAutoSize(name='lapsed_sub_center', parent=self, state=uiconst.UI_NORMAL, align=uiconst.CENTER, height=28)
        Icon(name='omega_warning_icon', parent=lapsedSubCenterContainer, state=uiconst.UI_NORMAL, size=28, align=uiconst.TOLEFT, icon='res:/UI/Texture/Icons/notifications/notificationIcon_OmegaDowngradeToAlpha.png')
        lapsedSubTextCenterContainer = ContainerAutoSize(name='lapsed_sub_center', parent=lapsedSubCenterContainer, state=uiconst.UI_NORMAL, align=uiconst.TOLEFT, height=28, padRight=28, left=10)
        EveLabelLarge(name='omega_warning_label', align=uiconst.CENTER, parent=lapsedSubTextCenterContainer, state=uiconst.UI_NORMAL, text=localization.GetByLabel('UI/CharacterSelection/OmegaLapsed'))
