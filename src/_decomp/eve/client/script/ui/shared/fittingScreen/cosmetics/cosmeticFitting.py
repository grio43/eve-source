#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\cosmeticFitting.py
import uthread2
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.shared.fitting.cleanShipButton import CleanShipButton
from eve.client.script.ui.shared.fittingScreen.cosmetics.cosmeticFittingCenter import CosmeticFittingCenter
from eve.client.script.ui.shared.fittingScreen.cosmetics.cosmeticFittingErrorScreen import CosmeticFittingErrorScreen
from eve.client.script.ui.shared.fittingScreen.cosmetics.logos import LogoSelectionPanel
from eve.client.script.ui.shared.skins.controller import FittingSkinPanelController
from eve.client.script.ui.shared.skins.skinPanel import SkinPanel
from localization import GetByLabel
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
PANEL_WIDTH = 416
TAB_ID_SKINS = 'skins'
TAB_ID_EMBLEMS = 'emblems'

class CosmeticFitting(Container):
    __notifyevents__ = ['OnCurrentStructureStateChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.cosmeticController = attributes.cosmeticController
        self.controller = attributes.controller
        self.skinPanel = None
        self._loadingWheel = None
        sm.RegisterNotify(self)
        self.ConstructLayout()
        self.controller.on_new_itemID.connect(self.UpdateShipType)

    def Close(self):
        sm.UnregisterNotify(self)
        self.controller.on_new_itemID.disconnect(self.UpdateShipType)
        super(CosmeticFitting, self).Close()

    def ConstructLayout(self):
        self.ConstructLeftPanel()
        self.centerParent = Container(name='centerParent', parent=self, align=uiconst.TOALL)
        self.cosmeticFittingCenter = CosmeticFittingCenter(parent=self.centerParent, controller=self.cosmeticController)
        Sprite(parent=self.centerParent, name='bg', align=uiconst.TOALL, texturePath='res:/UI/Texture/classes/Fitting/Cosmetics/cosmeticFittingBackground.png', state=uiconst.UI_DISABLED, padding=(-16, -16, -16, -16))
        self.cleanShipButton = CleanShipButton(name='cleanShipButton', parent=self, align=uiconst.BOTTOMRIGHT, controller=self.controller, display=not self.controller.ControllerForCategory() == const.categoryStructure)

    def ConstructLeftPanel(self):
        self.leftPanelContainer = Container(name='leftPanelContainer', parent=self, align=uiconst.TOLEFT, width=PANEL_WIDTH, padLeft=-8, padBottom=-8)
        self.ConstructCosmeticTypeTabGroup()
        self.ConstructSkinPanel()
        self._loadingWheel = LoadingWheel(parent=self.leftPanelContainer, align=uiconst.CENTER, width=64, height=64, state=uiconst.UI_HIDDEN)
        self.errorScreen = CosmeticFittingErrorScreen(name='errorScreen', parent=self.logosTabContainer, align=uiconst.TOALL, centralContWidth=PANEL_WIDTH)
        self.errorScreen.CloseScreen(animate=False)
        self.logoSelectionPanel = LogoSelectionPanel(name='logoSelectionPanel', parent=self.logosTabContainer, align=uiconst.TOLEFT, width=PANEL_WIDTH, fittingErrorCallback=self._OnEnableCosmeticsFailedCallback, controller=self.cosmeticController)

    def ConstructCosmeticTypeTabGroup(self):
        self.cosmeticTypeTabGroup = TabGroup(name='cosmeticTypeTabGroup', parent=self.leftPanelContainer, align=uiconst.TOTOP, groupID='CosmeticType', analyticID='CosmeticTypeTabGroup', callback=self.OnCosmeticTypeTabChange, padLeft=16)
        self.skinsTabContainer = Container(name='skinsTabContainer', parent=self.leftPanelContainer, align=uiconst.TOLEFT, width=PANEL_WIDTH, bgColor=(1.0, 1.0, 1.0, 0.05))
        self.logosTabContainer = Container(name='logosTabContainer', parent=self.leftPanelContainer, align=uiconst.TOALL, bgColor=(1.0, 1.0, 1.0, 0.05))
        self.cosmeticTypeTabGroup.AddTab(label=GetByLabel('UI/ShipCosmetics/Skins'), panel=self.skinsTabContainer, tabID=TAB_ID_SKINS, uniqueName=pConst.UNIQUE_NAME_FITTING_SKIN_BROWSER)
        self.cosmeticTypeTabGroup.AddTab(label=GetByLabel('UI/ShipCosmetics/Emblems'), panel=self.logosTabContainer, tabID=TAB_ID_EMBLEMS)
        self.cosmeticTypeTabGroup.AutoSelect()

    def ConstructSkinPanel(self):
        self.skinPanel = SkinPanel(name='skinPanel', parent=self.skinsTabContainer, align=uiconst.TOALL, controller=FittingSkinPanelController(fitting=self.cosmeticController), settingsPrefix='Fitting_SkinPanel', padding=12)

    def PopulateSkinPanel(self):
        if not self.skinPanel:
            return
        if not self.cosmeticTypeTabGroup.GetSelectedID() == TAB_ID_SKINS:
            return
        self.ShowLoadingWheel()
        self.skinPanel.SetPreviewType(self.controller.typeID)
        self.skinPanel.Load()
        self.HideLoadingWheel()

    def UpdateShipType(self, *args, **kwargs):
        self.skinPanel.SetPreviewType(self.controller.typeID)

    def ShowLoadingWheel(self):
        if self._loadingWheel:
            self._loadingWheel.state = uiconst.UI_DISABLED

    def HideLoadingWheel(self):
        if self._loadingWheel:
            self._loadingWheel.state = uiconst.UI_HIDDEN

    def OnCosmeticTypeTabChange(self, newTabID, _oldTabID):
        if newTabID == TAB_ID_SKINS:
            self.PopulateSkinPanel()

    def GoToTab(self, tabID):
        self.cosmeticTypeTabGroup.SelectByID(tabID)

    def OnCurrentStructureStateChanged(self, _solarSystemID, structureID, _state):
        if structureID != session.shipid:
            return
        uthread2.call_after_simtime_delay(self.skinPanel.Reload, 3)

    def AdjustErrorScreenPadding(self, padding):
        self.errorScreen.padding = (-padding[0],
         -padding[1],
         -padding[2],
         -padding[3])

    def _OnEnableCosmeticsFailedCallback(self):
        self.errorScreen.ShowScreen(GetByLabel('UI/Fitting/FittingWindow/Cosmetic/FittingFailedErrorMessage'), GetByLabel('UI/Fitting/FittingWindow/Cosmetic/FittingFailedButton'), self._CloseErrorScreen)

    def _CloseErrorScreen(self):
        self.errorScreen.CloseScreen(True)
