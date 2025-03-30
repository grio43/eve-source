#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\lobbyWnd.py
import math
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
import eve.client.script.ui.shared.systemMenu.settingCheckers as settingCheckers
import uthread
from carbonui import ButtonFrameType, uiconst
from carbonui.control.window import Window
from carbonui.services.setting import CharSettingBool
from carbonui.util.dpi import reverse_scale_dpi
from carbonui.window.settings import RegisterState
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.flowcontainer import FlowContainer
from carbonui.uicore import uicore
from carbonui.control.tabGroup import TabGroup
from eve.client.script.ui.menuUtil import SHOWINFOGROUP
from eve.client.script.ui.shared.dockedUI.inventory import InventoryPanel
from eve.common.lib import appConst as const
from eve.client.script.ui.control.eveIcon import CheckCorpID, GetLogoIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.dockedUI import ReloadLobbyWnd, controlButton, corvetteButton, modeButton, undockButton
from eve.client.script.ui.shared.dockedUI.agents import AgentsPanel
from eve.client.script.ui.shared.dockedUI.guests import GuestsPanel, GuestsPanelController
from eve.client.script.ui.shared.dockedUI.inControlCont import ConfirmTakeControl
from eve.client.script.ui.shared.dockedUI.offices import OfficesPanel
from eve.client.script.ui.shared.dockedUI.serviceBtn import StationServiceBtn
from eve.client.script.ui.station import stationServiceConst
from localization import GetByLabel
from uihider import UiHiderMixin
BIGBUTTONSIZE = 48
SMALLBUTTONSIZE = 32
BUTTONGAP = 4
DOCKING_BUTTONS_HEIGHT = 40
DOCKING_BUTTONS_WIDTH = 160
AGENTSPANEL = 'agentsPanel'
GUESTSPANEL = 'guestsPanel'
OFFICESPANEL = 'officesPanel'
INVENTORYPANEL = 'inventoryPanel'
show_hangars_tab_setting = CharSettingBool(settings_key='lobby_window_show_items_tab', default_value=lambda : bool(settings.char.windows.Get('dockshipsanditems', True)))

class LobbyWnd(UiHiderMixin, Window):
    __guid__ = 'form.LobbyWnd'
    __notifyevents__ = ['OnSetDevice', 'OnStructureServiceUpdated']
    default_windowID = 'lobbyWnd'
    uniqueUiName = pConst.UNIQUE_NAME_LOBBY_WND
    default_top = 16
    default_width = 280
    default_minSize = (270, 495)
    default_captionLabelPath = 'UI/Station/StationServices'
    default_isLightBackground = True
    default_scope = uiconst.SCOPE_DOCKED
    hasWindowIcon = False
    selectedGroupButtonID = None
    _agents_panel = None
    _guests_panel = None
    _guests_panel_controller = None
    _inventory_panel = None
    _offices_panel = None
    _tabs = None

    @staticmethod
    def default_height(*args):
        return uicore.desktop.height - 160

    @staticmethod
    def default_left(*args):
        return uicore.desktop.width - LobbyWnd.default_width - 16

    def __init__(self, **kwargs):
        RegisterState(self.default_windowID, 'compact', False)
        super(LobbyWnd, self).__init__(**kwargs)
        show_hangars_tab_setting.on_change.connect(self._on_show_hangars_tab_setting_changed)

    def OnSetDevice(self):
        bottom = self.top + self.height
        if bottom > uicore.desktop.height:
            self.height = max(self.default_minSize[1], uicore.desktop.height - self.top)
        right = self.left + self.width
        if right > uicore.desktop.width:
            self.width = max(self.default_minSize[0], uicore.desktop.width - self.left)

    def ApplyAttributes(self, attributes):
        self.viewState = sm.GetService('viewState')
        super(LobbyWnd, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.MakeUnKillable()
        self.MakeUnstackable()
        self.BuildTopSection()
        self._AddStationServices()
        self._AddPanelToggleBtnCont()
        self._AddGuestPanel()
        self._AddAgentPanel()
        self._AddOfficePanel()
        activePanel = settings.user.ui.Get('stationsLobbyTabs', AGENTSPANEL)
        if show_hangars_tab_setting.is_enabled():
            self._AddInventoryPanel()
        elif activePanel == INVENTORYPANEL:
            activePanel = AGENTSPANEL
        self._tabs.SelectByID(activePanel)
        self.LoadOwnerInfo()
        self.LoadServiceButtons()
        if self.destroyed:
            return
        sm.RegisterNotify(self)

    def Prepare_Header_(self):
        super(LobbyWnd, self).Prepare_Header_()
        self.header.show_caption = False

    def BuildTopSection(self):
        self.corpLogoParent = Container(name='corpLogoParent', parent=self.content, align=uiconst.TOTOP, height=160)
        self.corpName = Label(name='corpName', parent=self.content, align=uiconst.TOTOP, top=8, fontsize=18)
        StationButtonGrid(parent=self.content, align=uiconst.TOTOP, padTop=16, station_controller=self.controller, view_state_service=self.viewState)

    def _AddStationServices(self):
        padTop = 8
        self.corvetteButtonParent = ContainerAutoSize(parent=self.content, align=uiconst.TOTOP, padTop=16)
        self.serviceButtons = FlowContainer(name='serviceButtons', parent=self.content, align=uiconst.TOTOP, centerContent=True, contentSpacing=(BUTTONGAP, BUTTONGAP), padding=(24, 16, 24, 0), idx=2)

    def _on_guests_panel_guest_count_changed(self, controller):
        if self.destroyed:
            self._guests_panel_controller.on_guest_count_changed.disconnect(self._on_guests_panel_guest_count_changed)
        else:
            self.UpdateGuestTabText()

    def _AddGuestPanel(self):
        self._guests_panel_controller = GuestsPanelController()
        self._guests_panel = GuestsPanel(parent=self.panelsCont, align=uiconst.TOALL, padding=(0, 8, 0, 0), controller=self._guests_panel_controller)
        self._guests_panel.display = False
        self._tabs.AddTab(tabID=GUESTSPANEL, panel=self._guests_panel, label=GetByLabel('UI/Station/Lobby/Guests'), hint=GetByLabel('Tooltips/StationServices/GuestsTab_description'))
        self._guests_panel_controller.on_guest_count_changed.connect(self._on_guests_panel_guest_count_changed)
        uthread.new(self._guests_panel_controller.load)

    def _AddAgentPanel(self):
        self._agents_panel = AgentsPanel(name=AGENTSPANEL, parent=self.panelsCont, align=uiconst.TOALL, padding=(0, 8, 0, 0))
        self._agents_panel.display = False
        tab = self._tabs.AddTab(tabID=AGENTSPANEL, panel=self._agents_panel, label=GetByLabel('UI/Station/Lobby/Agents'), hint=GetByLabel('Tooltips/StationServices/AgentsTab_descrtiption'))
        tab.name = 'stationInformationTabAgents'
        tab.uniqueUiName = pConst.UNIQUE_NAME_AGENTS_TAB

    def _AddPanelToggleBtnCont(self):
        self._tabs = TabGroup(parent=self.content, align=uiconst.TOTOP, padding=(0, 16, 0, 0), callback=self._on_tab_selected)
        self.panelsCont = Container(name='panelsCont', parent=self.content)

    def _on_tab_selected(self, tab_id, old_tab_id):
        if tab_id is not None:
            settings.user.ui.Set('stationsLobbyTabs', tab_id)

    def _AddOfficePanel(self):
        self._offices_panel = OfficesPanel(parent=self.panelsCont, align=uiconst.TOALL, padding=(0, 8, 0, 0), station_controller=self.controller)
        tab = self._tabs.AddTab(tabID=OFFICESPANEL, panel=self._offices_panel, label=GetByLabel('UI/Station/Lobby/Offices'), hint=GetByLabel('Tooltips/StationServices/OfficesTab_description'))
        tab.uniqueUiName = pConst.UNIQUE_NAME_OFFICES_TAB

    def _AddInventoryPanel(self):
        self._inventory_panel = InventoryPanel(parent=self.panelsCont, station_controller=self.controller)
        tab = self._tabs.AddTab(tabID=INVENTORYPANEL, panel=self._inventory_panel, label=GetByLabel('UI/Station/Lobby/Hangars'), hint='<b>%s</b><br>%s' % (GetByLabel('Tooltips/StationServices/Hangars'), GetByLabel('Tooltips/StationServices/Hangars_description')))
        tab.name = 'Button_InventoryPanel'
        tab.uniqueUiName = pConst.UNIQUE_NAME_HANGARS_TAB

    def LoadOwnerInfo(self):
        parent = self.corpLogoParent
        parent.Flush()
        corpID = self.controller.GetOwnerID()
        size = 128 if CheckCorpID(corpID) else 64
        logo = GetLogoIcon(parent=parent, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, itemID=corpID, acceptNone=False, pos=(0,
         0,
         size,
         size))
        parent.height = logo.top + logo.height
        if CheckCorpID(corpID):
            self.corpName.display = False
        else:
            self.corpName.text = '<center>' + cfg.eveowners.Get(corpID).name
            self.corpName.display = True

    def GetServiceBtnSize(self):
        return SMALLBUTTONSIZE

    def LoadServiceButtons(self):
        parent = self.serviceButtons
        parent.Flush()
        corvetteButton.CorvetteButton(parent=self.corvetteButtonParent, align=uiconst.CENTER)
        haveServices = self.GetCurrentStationServices()
        btnsize = self.GetServiceBtnSize()
        for serviceInfo in reversed(haveServices):
            button = StationServiceBtn(name=serviceInfo.name, uniqueUiName=pConst.GetUniqueStationServiceName(serviceInfo.name), parent=parent, align=uiconst.NOALIGN, serviceInfo=serviceInfo, iconSize=btnsize, func=lambda name = serviceInfo.name: self.OnSvcBtnClick(name), args=())
            self.SetServiceButtonState(button, serviceInfo.serviceID)

    def ReloadServiceButtons(self):
        self.controller.GetServices()
        for button in self.serviceButtons.children:
            try:
                serviceID = button.serviceID
            except AttributeError:
                continue

            self.SetServiceButtonState(button, serviceID)

    def SetServiceButtonState(self, button, serviceID):
        currentstate = self.controller.GetCurrentStateForService(serviceID)
        if currentstate is None:
            return
        self.controller.RemoveServiceFromCache(serviceID)
        button.UpdateState(currentstate.isEnabled)

    def OnSvcBtnClick(self, serviceName):
        self.CheckCanAccessService(serviceName)
        sm.GetService('station').LoadSvc(serviceName)

    def CheckCanAccessService(self, serviceName):
        return CheckCanAccessService(self.controller, serviceName)

    def GetCurrentStationServices(self):
        return self.controller.GetServices()

    def OnButtonGroupSelection(self, buttonID, *args):
        settings.user.ui.Set('stationsLobbyTabs', buttonID)
        self.selectedGroupButtonID = buttonID
        functionByButton = {AGENTSPANEL: self.ShowAgents,
         GUESTSPANEL: self.ShowGuests,
         OFFICESPANEL: self.ShowOffices,
         INVENTORYPANEL: self.ShowHangars}
        if buttonID in functionByButton:
            functionByButton[buttonID]()

    def AddControlButton(self):
        if not self.controller.IsControlable():
            return
        control_button_controller = controlButton.Controller(docked_ui_controller=self.controller, confirm_override_control=confirm_override_control)
        controlButton.ControlButton(parent=self.undockparent, align=uiconst.NOALIGN, controller=control_button_controller, fixedheight=DOCKING_BUTTONS_HEIGHT, fixedwidth=DOCKING_BUTTONS_WIDTH, frame_type=ButtonFrameType.RECTANGLE)

    def AddDockedModeButton(self):
        if not self.controller.HasDockModes():
            return
        mode_button_controller = modeButton.Controller(docked_ui_controller=self.controller, view_state_service=self.viewState)
        modeButton.ModeButton(parent=self.undockparent, align=uiconst.NOALIGN, controller=mode_button_controller, fixedheight=DOCKING_BUTTONS_HEIGHT, fixedwidth=DOCKING_BUTTONS_WIDTH, frame_type=ButtonFrameType.RECTANGLE)

    def AddUndockButton(self):
        undock_button_controller = undockButton.Controller(docked_ui_controller=self.controller)
        undockButton.UndockButton(parent=self.undockparent, align=uiconst.NOALIGN, uniqueUiName=pConst.UNIQUE_NAME_UNDOCK_BTN, controller=undock_button_controller, fixedheight=DOCKING_BUTTONS_HEIGHT, fixedwidth=DOCKING_BUTTONS_WIDTH, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)

    def UpdateGuestTabText(self):
        self._tabs.GetTabByID(GUESTSPANEL).SetLabel(u'{tab_name} [{count}]'.format(tab_name=GetByLabel('UI/Station/Lobby/Guests'), count=self._guests_panel_controller.guest_count))

    def ShowOffices(self):
        self._offices_panel.LoadPanel()

    def ShowHangars(self):
        self._inventory_panel.LoadPanel()

    def ShowAgents(self):
        self._agents_panel.LoadPanel()

    def ShowGuests(self, *args):
        self._guests_panel.LoadPanel()

    def OnStructureServiceUpdated(self):
        self.ReloadServiceButtons()

    def StopAllBlinkButtons(self):
        for each in self.serviceButtons.children:
            if hasattr(each, 'Blink'):
                each.Blink(0)

    def BlinkButton(self, whatBtn):
        for each in self.serviceButtons.children:
            if each.name.lower() == whatBtn.lower():
                each.Blink(blinks=40)

    def GetMenuMoreOptions(self):
        menu = super(LobbyWnd, self).GetMenuMoreOptions()
        menu.AddEntry(text=GetByLabel('UI/Station/Lobby/CorpShowInfoButton'), func=self._show_owner_info, menuGroupID=SHOWINFOGROUP)
        menu.AddSeparator()
        menu.AddCheckbox(text=GetByLabel('UI/Station/Lobby/ShowHangarsTab'), setting=show_hangars_tab_setting)
        return menu

    def _show_owner_info(self):
        sm.GetService('info').ShowInfo(typeID=const.typeCorporation, itemID=self.controller.GetOwnerID())

    @staticmethod
    def _on_show_hangars_tab_setting_changed(value):
        ReloadLobbyWnd()


def is_small_buttons_enabled():
    return settingCheckers.get_small_station_buttons_setting()


def CheckCanAccessService(stationController, serviceName):
    serviceData = stationServiceConst.serviceDataByNameID.get(serviceName)
    if serviceData is None:
        return
    for stationServiceID in serviceData.stationServiceIDs:
        result = stationController.PerformAndGetErrorForStandingCheck(stationServiceID)
        if result is not None:
            raise result


def confirm_override_control(docked_ui_controller):
    structure_id = docked_ui_controller.GetItemID()
    current_pilot_id = docked_ui_controller.GetStructurePilot(structure_id)
    ConfirmTakeControl.Open(controller=docked_ui_controller, charInControl=current_pilot_id)


class StationButtonGrid(ContainerAutoSize):
    GAP_SIZE = 8
    _undock_button = None
    _mode_button = None
    _control_button = None

    def __init__(self, station_controller, view_state_service, **kwargs):
        self._controller = station_controller
        self._view_state_service = view_state_service
        super(StationButtonGrid, self).__init__(alignMode=uiconst.TOPLEFT, **kwargs)
        self._load()

    def _load(self):
        if self._controller.IsControlable():
            self._create_control_button()
        if self._controller.HasDockModes():
            self._create_mode_button()
        self._create_undock_button()

    def _create_control_button(self):
        self._control_button = controlButton.ControlButton(parent=self, align=uiconst.TOPLEFT, docked_ui_controller=self._controller, frame_type=ButtonFrameType.RECTANGLE)

    def _create_mode_button(self):
        self._mode_button = modeButton.ModeButton(parent=self, align=uiconst.TOPLEFT, docked_ui_controller=self._controller, view_state_service=self._view_state_service, frame_type=ButtonFrameType.RECTANGLE)

    def _create_undock_button(self):
        self._undock_button = undockButton.UndockButton(parent=self, align=uiconst.TOPLEFT, docked_ui_controller=self._controller, frame_type=ButtonFrameType.CUT_BOTTOM_LEFT_RIGHT)

    def _update_button_alignment(self, budget_width):
        undock_button_top = 0
        if self._control_button and self._mode_button:
            control_button_width = self._control_button.get_intrinsic_width()
            mode_button_width = self._mode_button.get_intrinsic_width()
            total_width = control_button_width + self.GAP_SIZE + mode_button_width
            if total_width > budget_width:
                self._control_button.left = 0
                self._control_button.top = 0
                self._control_button.width = budget_width
                self._mode_button.left = 0
                self._mode_button.top = self._control_button.height + self.GAP_SIZE
                self._mode_button.width = budget_width
            else:
                self._control_button.left = 0
                self._control_button.top = 0
                self._control_button.width = int(math.ceil((budget_width - self.GAP_SIZE) / 2.0))
                self._mode_button.left = self._control_button.width + self.GAP_SIZE
                self._mode_button.top = 0
                self._mode_button.width = budget_width - self._control_button.width - self.GAP_SIZE
            undock_button_top = self._mode_button.top + self._mode_button.height + self.GAP_SIZE
        elif self._control_button:
            self._control_button.left = 0
            self._control_button.top = 0
            self._control_button.width = budget_width
            undock_button_top = self._control_button.height + self.GAP_SIZE
        elif self._mode_button:
            self._mode_button.left = 0
            self._mode_button.top = 0
            self._mode_button.width = budget_width
            undock_button_top = self._mode_button.height + self.GAP_SIZE
        self._undock_button.top = undock_button_top
        self._undock_button.width = budget_width

    def UpdateAlignment(self, budgetLeft = 0, budgetTop = 0, budgetWidth = 0, budgetHeight = 0, updateChildrenOnly = False):
        budget_width = reverse_scale_dpi(budgetWidth)
        self._update_button_alignment(budget_width)
        return super(StationButtonGrid, self).UpdateAlignment(budgetLeft, budgetTop, budgetWidth, budgetHeight, updateChildrenOnly)
