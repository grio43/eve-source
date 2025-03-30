#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoPanels\panelSkin.py
import carbonui.const as uiconst
import eveicon
import localization
import logging
import uthread2
from carbonui import Align
from carbonui.uianimations import animations
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.shared.info.shipInfoConst import TAB_SKINS, ANGLE_SKINS
from eve.client.script.ui.shared.info.shipInfoPanels.panelBase import PanelBase
from eve.client.script.ui.shared.skins.controller import ShipInfoSkinPanelController
from eve.client.script.ui.shared.skins.skinPanel import SkinPanel
logger = logging.getLogger(__name__)
PANEL_WIDTH = 416

class PanelSkins(PanelBase):

    @classmethod
    def get_name(cls):
        return localization.GetByLabel('UI/InfoWindow/TabNames/Skins')

    @classmethod
    def get_icon(cls):
        return eveicon.skins

    def get_tab_type(self):
        return TAB_SKINS

    def get_camera_position(self):
        return ANGLE_SKINS

    def _construct_content(self):
        uthread2.Yield()
        self.skinPanel = ShipInfoSkinPanel(parent=self.rightCont, align=uiconst.TOALL, controller=self._controller.skin_controller, settingsPrefix='Preview_SkinPanel', logContext='PreviewWindow')
        self.loadingWheel = LoadingWheel(parent=self.rightCont, align=Align.CENTER, opacity=0.0)
        uthread2.StartTasklet(self._load_panel_task)

    def _load_panel_task(self):
        selectedSkin = None
        if self._params:
            selectedSkin = self._params.get('skin', None)
        animations.FadeIn(self.loadingWheel)
        self.skinPanel.SetPreviewType(self.typeID)
        self.skinPanel.Load(selectedSkin)
        if selectedSkin:
            self._controller.skin_controller.SetPreviewed(selectedSkin)
        animations.FadeOut(self.loadingWheel)

    def _enable_expanded_view(self):
        self.skinPanel.SetParent(self.rightCont)
        self.skinPanel.SetCompactMode(False)

    def show_minimized_view(self, is_compact):
        super(PanelSkins, self).show_minimized_view(True)
        self.skinPanel.SetParent(self.minimizedCont)
        self.skinPanel.SetCompactMode(True)

    def _construct_minimized_content_scroll(self):
        pass

    def on_reset(self, initialize):
        if initialize:
            return
        self._controller.reset_skin()

    def _on_skin_controller_on_change(self):
        skin = self.skinController.previewed or self.skinController.pending or self.skinController.applied
        self._controller.change_skin(skin)

    def _get_compact_top_padding(self):
        return 200


class ShipInfoSkinPanel(SkinPanel):

    def Close(self):
        super(SkinPanel, self).Close()
