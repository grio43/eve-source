#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\shipInfoWindow.py
import eveicon
import evetypes
import localization
import uthread
import uthread2
import trinity
from eve.client.script.ui.shared.skins.controller import ShipInfoSkinPanelController
from eveservices.menu import GetMenuService
import eveui
from eveui import CharacterPortrait
from carbon.common.script.sys.serviceConst import ROLE_QA
from carbonui import uiconst, Align, TextBody, TextDetail, PickState, TextColor
from carbonui.control.dragdrop.dragdata import ShipDragData
from carbonui.control.sideNavigation import SideNavigationSplitView, SideNavigation, SideNavigationEntry, SideNavigationEntryInterface
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import SessionSettingBool, SessionSettingEnum
from carbonui.uianimations import animations
from carbonui.window.control.action import WindowMenuAction, WindowActionImportance
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control.scenecontainer import SceneContainerBaseNavigation
from eve.client.script.ui.services.menuSvcExtras.openFunctions import SimulateFitting
from eve.client.script.ui.shared.fittingScreen.tryFit import GetParentShipInfo
from eve.client.script.ui.shared.info.baseInfoWindow import BaseInfoWindow
from eve.client.script.ui.shared.info.shipInfoConst import GetAnimDuration, TOP_DOWN_NOSE_UP_ALT, get_sound_by_type_id, GetMassBasedSoundOffset, INFO_TABS, FULLY_MINIMIZED, MINIMIZED, EXPANDED, CONTENT_PADDING
from eve.client.script.ui.shared.info.shipInfoPanels.panelConst import SHIP_INFO_PANELS, TAB_OVERVIEW, TAB_FITTING, TAB_SKINS
from eve.client.script.ui.shared.info.shipInfoPreviewScene import ShipInfoPreviewSceneContainer
from inventorycommon.typeHelpers import GetHoloIconPath, GetIconFile
from inventorycommon.util import GetSubSystemTypeIDs, IsModularShip, IsSubsystemFlag
from inventorycommon.const import flagCargo, flagShipHangar, groupCapsule
from inventoryrestrictions import can_view_market_details
from carbonui.uicore import uicore
from eve.common.script.sys.eveCfg import InShipInSpace
from eve.common.script.sys import idCheckers
from utillib import KeyVal
import shipgroup
is_expanded_setting = SessionSettingBool(False)
EXPANDED_WIDTH = 640
MINIMIZED_ZOOM = 0.1
EXPANDED_ZOOM = 0.3
MINIMIZED_ZOOM_RANGE = [1.6, 3.5]
EXPANDED_ZOOM_RANGE = [1.5, 3.5]
MINIMIZED_BG_COLOR = (0,
 0,
 0,
 1)
MINIMIZED_BG_OPACITY = 0.9
MINIMIZED_POSITION_OVERRIDE = TOP_DOWN_NOSE_UP_ALT
LAST_TAB_SETTING = SessionSettingEnum(TAB_OVERVIEW, INFO_TABS)

class ShipInfoWindowController(object):

    def __init__(self, select_tab, get_ship_length, reset_skin):
        self._select_tab = select_tab
        self._get_ship_length = get_ship_length
        self._skin_controller = None
        self._type_id = None
        self._item_id = None
        self._item = None
        self._parent_id = None
        self._abstract_info = None
        self._owner_id = None
        self._owner_data = None
        self._ship_contents = None
        self._fetching_owner_data = False
        self._reset_skin = reset_skin

    def set_values(self, type_id, item_id, item, parent_id, abstract_info):
        self._type_id = type_id
        self._item_id = item_id
        self._item = item
        self._parent_id = parent_id
        self._abstract_info = abstract_info
        self._owner_id = self._get_owner_id()
        self._owner_data = None
        self._ship_contents = None
        if self._owner_id and not self.is_owned_by_me:
            self._fetching_owner_data = True
            uthread2.start_tasklet(self._update_owner)

    def set_skin_controller(self, skin_controller):
        self._skin_controller = skin_controller

    def select_tab(self, tab_id):
        self._select_tab(tab_id)

    def reset_skin(self):
        self._reset_skin()

    @property
    def skin_controller(self):
        return self._skin_controller

    @property
    def item_id(self):
        return self._item_id

    @property
    def item(self):
        return self._item

    @item.setter
    def item(self, value):
        if value:
            self._item = value

    @property
    def type_id(self):
        return self._type_id

    @property
    def group_id(self):
        return evetypes.GetGroupID(self.type_id)

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def owner_corporation_id(self):
        if not self.owner_id:
            return None
        if self.is_owned_by_me:
            return session.corpid
        owner_data = self.get_owner_data()
        if owner_data:
            return owner_data.corpID

    @property
    def long_axis_length(self):
        return self._get_ship_length()

    @property
    def is_assembled(self):
        return self.item_id == session.shipid or self._item and self._item.singleton

    @property
    def is_owned_by_me(self):
        return self.owner_id == session.charid

    @property
    def is_simulated(self):
        return self.item_id is not None and isinstance(self.item_id, basestring)

    def get_custom_name(self):
        if self.owner_id and self.item_id in cfg.evelocations.data:
            return cfg.evelocations.Get(self.item_id).name

    def get_ship_name(self):
        return self.get_custom_name() or evetypes.GetName(self.type_id)

    def get_type_name(self):
        return evetypes.GetName(self.type_id)

    def get_class_name(self):
        return shipgroup.get_ship_group_name(self.type_id)

    def get_description(self):
        return evetypes.GetDescription(self.type_id)

    def get_owner_name(self):
        owner_id = self.owner_id
        if owner_id:
            return cfg.eveowners.Get(owner_id).name
        return ''

    def get_owner_data(self):
        while self._fetching_owner_data:
            uthread2.Yield()

        return self._owner_data

    def _get_owner_id(self):
        if not self.item_id:
            return
        if self.item_id == session.shipid:
            return session.charid
        if InShipInSpace():
            owner_id = sm.GetService('michelle').GetCharIDFromShipID(self.item_id)
            if owner_id:
                return owner_id
        owner_id = None
        if self._item and self._item.ownerID and self._item.singleton:
            owner_id = self._item.ownerID
        elif self._abstract_info:
            try:
                owner_id = self._abstract_info.ownerID
            except:
                pass

        if owner_id and idCheckers.IsEvePlayerCharacter(owner_id):
            return owner_id

    def _update_owner(self):
        self._owner_data = sm.GetService('crimewatchSvc').GetSlimItemDataForCharID(self.owner_id)
        self._fetching_owner_data = False

    def get_subsystems(self):
        if not IsModularShip(self.type_id) or not self.item_id:
            return None
        if InShipInSpace() and self.item_id != session.shipid:
            slimItem = sm.GetService('michelle').GetItem(self.item_id)
            if slimItem and slimItem.modules:
                return [ type_id for item_id, type_id, flag_id in slimItem.modules if IsSubsystemFlag(flag_id) ]
        return GetSubSystemTypeIDs(self.item_id, self.type_id)

    def get_ship_contents(self):
        if self._ship_contents is None or self.item_id == session.shipid:
            self._ship_contents = self._get_ship_contents()
        return self._ship_contents

    def _get_ship_contents(self):
        if self.item_id is None:
            return []
        if session.shipid == self.item_id:
            shipinfo = sm.GetService('godma').GetItem(self.item_id)
            if shipinfo is not None and getattr(shipinfo, 'inventory', None) is not None:
                return shipinfo.inventory.List()
        if self.item is None:
            return []
        if not self.item.singleton:
            return []
        if self.item.ownerID == session.charid and self.item.locationID:
            dockable_location_id = self.item.locationID
            solar_system_id = None
            if self.item.flagID in (flagCargo, flagShipHangar):
                parent_ship_info = GetParentShipInfo(self.item)
                if parent_ship_info:
                    dockable_location_id, solar_system_id = parent_ship_info
            inventoryMgr = sm.GetService('invCache').GetInventoryMgr()
            try:
                return inventoryMgr.GetContainerContents(self.item.itemID, dockable_location_id, solar_system_id)
            except AttributeError:
                pass
            except RuntimeError as e:
                if e[0] == 'InvalidLocationID':
                    pass
                else:
                    raise e

        return []

    def get_fitting_data(self, put_ammo_in_cargo = True):
        fitting_svc = sm.GetService('fittingSvc')
        inventory = self.get_ship_contents()
        fitting = KeyVal()
        fitting.shipTypeID = self.type_id
        fitting.fitData = fitting_svc.CreateFittingData(inventory, putModuleAmmoInCargo=put_ammo_in_cargo)
        fitting.fittingID = None
        fitting.description = ''
        shipName = self.get_ship_name()
        fitting.name = shipName
        fitting.ownerID = 0
        return fitting

    def open_simulation(self):
        fitting_svc = sm.GetService('fittingSvc')
        fitting = self.get_fitting_data(False)
        inventory = self.get_ship_contents()
        charges_to_load = fitting_svc.GetLoadedChargeTypes(inventory)
        SimulateFitting(fitting, charges_to_load)


class ShipInfoWindow(BaseInfoWindow):
    __guid__ = 'form.shipinfowindow'
    __notifyevents__ = []
    SIDE_PANEL_WIDTH = 58
    default_width = 960
    default_height = 656
    default_minSize = (325, 450)
    default_name = 'shipInfoWindow'
    default_windowID = 'shipInfoWindow'
    default_iconNum = eveicon.spaceship_command
    default_scope = uiconst.SCOPE_INGAME
    default_apply_content_padding = False
    default_extend_content_into_header = True
    default_isCompactable = True

    def ApplyAttributes(self, attributes):
        self._selectedTab = TAB_OVERVIEW
        self._initialized = False
        self._current_panel = None
        self._load_tasklet = None
        self._live_preview = None
        self._dynamic_state = 0
        self._skin_controller = None
        self._controller = ShipInfoWindowController(select_tab=self.open_tab_by_id, get_ship_length=self._get_ship_length, reset_skin=self._reset_skin)
        super(ShipInfoWindow, self).ApplyAttributes(attributes)
        self._dynamic_state = self._get_dynamic_state()
        self.on_stacked_changed.connect(self._on_stacked_changed_callback)
        self.on_header_height_changed.connect(self._on_header_height_changed)
        self._last_tab_setting = LAST_TAB_SETTING

    def Close(self, *args, **kwargs):
        super(ShipInfoWindow, self).Close(*args, **kwargs)
        if self._skin_controller:
            self._skin_controller.Close()

    def _on_header_height_changed(self, *args, **kwargs):
        self.split_view.padTop = self.sr.headerParent.height

    def OnCompactModeEnabled(self):
        self.OnResizeUpdate()
        self._close_live_preview()
        self._update_preview_display_state()
        self.split_view.set_force_compact(True)
        self.side_navigation.set_force_compact(True)

    def OnCompactModeDisabled(self):
        self.OnResizeUpdate()
        self._construct_live_preview()
        self._load_ship()
        self._update_preview_display_state()
        self.split_view.set_force_compact(False)
        self.side_navigation.set_force_compact(False)

    def ConstructLayout(self):
        self.content.clipChildren = True
        self.split_view = SideNavigationSplitView(parent=self.content, align=uiconst.TOALL, is_always_expanded_setting=is_expanded_setting, expanded_panel_width=200, padTop=self.sr.headerParent.height, clipChildren=False, force_compact=self.compact)
        self.side_navigation = ShipInfoSideNavigation(controller=self._controller, parent=self.split_view.panel, is_expanded_func=self.split_view.is_expanded, expand_func=self.split_view.expand_panel, force_compact=self.compact)
        self.split_view.on_expanded_changed.connect(self.side_navigation.on_expanded_changed)
        self.mainContent = Container(parent=self.split_view.content, align=Align.TOALL, padding=16)
        self.previewCont = Container(parent=self.split_view.content, align=Align.TOALL)
        self.bgFade = Fill(parent=self.content, align=Align.TOALL, state=uiconst.UI_DISABLED, color=MINIMIZED_BG_COLOR, opacity=0, pickState=PickState.OFF, display=not self.compact)
        self._black_bg = Fill(parent=self.content, align=Align.TOALL, state=uiconst.UI_DISABLED, color=(0, 0, 0, 1), opacity=0.0)
        self._construct_live_preview()

    def _construct_live_preview(self, forced = False):
        if self._live_preview or self.compact and not forced:
            return
        sceneNavigation = SceneContainerBaseNavigation(name='preview_navigation', parent=self.previewCont, align=Align.TOALL, state=uiconst.UI_NORMAL, pickRadius=0)
        self._live_preview = ShipInfoPreviewSceneContainer(parent=self.content, align=Align.TOALL, state=uiconst.UI_DISABLED, opacity=0.0)
        self._live_preview.on_load_complete.connect(self._on_model_load_complete)
        sceneNavigation.Startup(self._live_preview)
        self._update_preview_display_state()

    def _close_live_preview(self):
        if not self._live_preview or self._selectedTab == TAB_SKINS:
            return
        self._live_preview.on_load_complete.disconnect(self._on_model_load_complete)
        self._live_preview.Close()
        self._live_preview = None
        self.previewCont.Flush()

    def _ReconstructInfoWindow(self, typeID, itemID = None, rec = None, parentID = None, abstractinfo = None, tabNumber = None, branchHistory = True, selectTabType = None, params = None):
        self._initialized = False
        if self.typeID:
            self.UpdateHistoryData()
        self._controller.set_values(type_id=typeID, item_id=itemID, item=rec, parent_id=parentID, abstract_info=abstractinfo)
        if self._skin_controller:
            self._skin_controller.onChange.disconnect(self._change_skin)
            self._skin_controller.Close()
        self._skin_controller = ShipInfoSkinPanelController(itemID=itemID, ownerID=self._controller.owner_id, hullTypeID=typeID)
        self._skin_controller.onChange.connect(self._change_skin)
        self._controller.set_skin_controller(self._skin_controller)
        self.typeID = typeID
        self.itemID = itemID
        self.rec = rec
        self.parentID = parentID
        self.abstractinfo = abstractinfo
        skin_state = None
        if params:
            skin = params.get('skin', None)
            if skin:
                skin_state = skin
        self._load_ship(skin_state)
        self.groupID = evetypes.GetGroupID(typeID)
        self.categoryID = evetypes.GetCategoryID(typeID)
        if branchHistory:
            self.history.Append(self.GetHistoryData())
        self.update_window_controls()
        self._update_caption()
        visible_tabs = self.get_visible_tabs(typeID, itemID, rec)
        nav_tabs = [ (tabID, self.get_tab_class_by_type(tabID)) for tabID in visible_tabs ]
        self.side_navigation.reconstruct(nav_tabs, self._selectedTab)
        if selectTabType:
            selectedTabID = selectTabType
        elif tabNumber and tabNumber < len(visible_tabs):
            selectedTabID = visible_tabs[tabNumber - 1]
        elif self._current_panel and self._current_panel.is_visible(self.typeID):
            selectedTabID = self._current_panel.get_tab_type()
        else:
            selectedTabID = self._last_tab_setting.get()
        if selectedTabID not in visible_tabs:
            selectedTabID = TAB_OVERVIEW
        self.open_tab_by_id(selectedTabID, params, initialize=True)
        uthread2.Yield()
        self._set_dynamic_state(self._get_dynamic_state(), initial=True)
        self._initialized = True
        self._do_fade_in()

    def _load_ship(self, skin_state = None):
        if not self._live_preview:
            return
        animations.StopAllAnimations(self._black_bg)
        self._black_bg.opacity = 1
        if skin_state is None:
            skin_state = self._get_skin_state()
        self._live_preview.preview_ship(self._controller.type_id, subSystems=self._controller.get_subsystems(), skin_state=skin_state, snap=True, skip_animation=False)

    def _on_model_load_complete(self, snap = True, skip_animation = False):
        if skip_animation or not self._live_preview:
            return
        mass = evetypes.GetMass(self.typeID)
        animDuration = GetAnimDuration(mass)
        self._live_preview.position_ship(self._get_camera_position(), animDuration, snap, get_sound_by_type_id(self.typeID), GetMassBasedSoundOffset(mass))
        self._set_dynamic_state(self._get_dynamic_state(), initial=snap)
        self._do_fade_in()

    def _update_caption(self):
        infoObject = u'%s (%s)' % (evetypes.GetName(self.typeID), shipgroup.get_ship_group_name(self.typeID))
        caption = localization.GetByLabel('UI/InfoWindow/InfoWindowCaption', infoObject=infoObject)
        self.SetCaption(caption)

    def GetPanelByTabType(self, tabType):
        pass

    def GetNeocomGroupLabel(self):
        return localization.GetByLabel('UI/InfoWindow/ShipInformationNeocomGroup')

    def GetHistoryData(self):
        return {'typeID': self.typeID,
         'itemID': self.itemID,
         'rec': self.rec,
         'parentID': self.parentID,
         'abstractinfo': self.abstractinfo,
         'selectTabType': self.GetSelectedTabIdx()}

    def GetCustomHeaderButtons(self):
        return [WindowMenuAction(window=self, icon=eveicon.navigate_forward, label=localization.GetByLabel('UI/Control/EveWindow/Next'), callback=self.OnForward, ui_name='ForwardButton', enabled_check=lambda window: window.history.IsForwardEnabled(), importance=WindowActionImportance.content), WindowMenuAction(window=self, icon=eveicon.navigate_back, label=localization.GetByLabel('UI/Control/EveWindow/Previous'), callback=self.OnBack, ui_name='BackButton', enabled_check=lambda window: window.history.IsBackEnabled(), importance=WindowActionImportance.content)]

    def GetMenuMoreOptions(self):
        menuData = super(ShipInfoWindow, self).GetMenuMoreOptions()
        if bool(session.role & ROLE_QA):
            menuData.AddEntry('QA: OPEN OLD WINDOW', self._qa_open_old_window)
        menuData.extend(GetMenuService().GetMenuFromItemIDTypeID(self.itemID, self.typeID, invItem=self.rec, includeMarketDetails=True).filter([localization.GetByLabel('UI/Commands/ShowInfo'), 'UI/Commands/ShowInfo']))
        return menuData

    def GetWindowLinkData(self):
        if not self._controller.type_id:
            return []
        return ShipDragData(typeID=self._controller.type_id, itemID=self._controller.item_id, ownerID=self._controller.owner_id)

    def OnBack(self, *args):
        self.UpdateHistoryData()
        infoWndData = self.history.GoBack()
        if infoWndData:
            self.ReconstructInfoWindow(branchHistory=False, **infoWndData)

    def OnForward(self, *args):
        self.UpdateHistoryData()
        infoWndData = self.history.GoForward()
        if infoWndData:
            self.ReconstructInfoWindow(branchHistory=False, **infoWndData)

    def get_visible_tabs(self, typeID, itemID = None, rec = None):
        ret = []
        for tabID, panelCls in SHIP_INFO_PANELS.iteritems():
            if panelCls.is_visible(typeID, itemID, rec):
                ret.append(tabID)

        return ret

    def get_tab_class_by_type(self, tabID):
        if tabID in SHIP_INFO_PANELS:
            return SHIP_INFO_PANELS[tabID]

    def open_tab_by_id(self, tabID, params = None, initialize = False):
        panelCls = self.get_tab_class_by_type(tabID)
        if not panelCls:
            raise RuntimeError('No class found for tab type {tabID}'.format(tabID=tabID))
        if not initialize and not panelCls.is_visible(self.typeID, self.itemID, self.rec):
            return
        self._selectedTab = tabID
        if self._current_panel:
            self._current_panel.on_reset(initialize)
        self._last_tab_setting.set(tabID)
        self.mainContent.Flush()
        self.side_navigation.set_entry_selected(tabID)
        self._current_panel = panelCls(parent=self.mainContent, controller=self._controller, params=params, opacity=0)
        self._set_dynamic_state(self._get_dynamic_state())
        if self._dynamic_state == EXPANDED:
            self._current_panel.show_expanded_view()
        else:
            self._current_panel.show_minimized_view(self._dynamic_state == FULLY_MINIMIZED)
        animations.FadeIn(self._current_panel, duration=0.4)
        if tabID == TAB_SKINS and not self._live_preview:
            self._construct_live_preview(True)
            self._load_ship()
        self._update_preview_display_state()
        if self._live_preview and self._live_preview.display:
            self._live_preview.set_ship_state(tabID)
            mass = evetypes.GetMass(self.typeID)
            animDuration = GetAnimDuration(mass)
            self._live_preview.position_ship(self._get_camera_position(), animDuration, initialize, get_sound_by_type_id(self.typeID), GetMassBasedSoundOffset(mass))
            self._update_offset()
            self._update_zoom(duration=animDuration)

    def _get_skin_state(self):
        skin_state = self._skin_controller.previewed or self._skin_controller.pending or self._skin_controller.applied
        return skin_state

    def _change_skin(self):
        if not self._live_preview:
            return
        skin_state = self._get_skin_state()
        try:
            if skin_state == self._live_preview.skin_state:
                return
        except:
            pass

        self._live_preview.preview_skin(self.typeID, subSystems=self._controller.get_subsystems(), skin_state=skin_state, skip_repositioning=True, snap=False, skip_animation=True)
        uthread2.Yield()

    def _reset_skin(self):
        if not self._live_preview:
            return
        self._skin_controller.SetPreviewed(None)
        self._change_skin()

    def _get_ship_length(self):
        if not self._live_preview:
            return 0
        return self._live_preview.get_bounding_sphere_radius() * 2

    def _get_camera_position(self):
        if self._current_panel is not None and (self._get_dynamic_state() == EXPANDED or self._selectedTab == TAB_SKINS):
            return self._current_panel.get_camera_position()
        return MINIMIZED_POSITION_OVERRIDE

    def _get_dynamic_state(self):
        _, _, width, _ = self.displayRect
        if width >= uicore.ScaleDpi(EXPANDED_WIDTH):
            if self.compact and not self._selectedTab == TAB_SKINS:
                return MINIMIZED
            return EXPANDED
        return MINIMIZED

    def _set_dynamic_state(self, state, initial = False):
        if self._dynamic_state == state and not initial:
            return
        self.mainContent.padding = CONTENT_PADDING[state]
        is_compact = state == FULLY_MINIMIZED
        if state == EXPANDED:
            animations.FadeOut(self.bgFade, duration=0.4)
            if self._current_panel:
                self._current_panel.show_expanded_view()
        elif state == MINIMIZED or is_compact:
            animations.FadeIn(self.bgFade, endVal=MINIMIZED_BG_OPACITY, duration=0.4)
            if self._current_panel:
                self._current_panel.show_minimized_view(is_compact)
        self.split_view.set_minimized(is_compact)
        if is_compact:
            self.hasWindowIcon = False
            self.on_compact_mode_changed(self)
        else:
            self.hasWindowIcon = True
            self.on_compact_mode_changed(self)
        self._dynamic_state = state
        if self._live_preview:
            mass = evetypes.GetMass(self.typeID)
            animDuration = GetAnimDuration(mass)
            self._live_preview.position_ship(self._get_camera_position(), animDuration, initial, get_sound_by_type_id(self.typeID), GetMassBasedSoundOffset(mass))
            self._update_offset(initial)
            self._update_zoom(initial, animDuration)
        self._update_preview_display_state()

    def OnResizeUpdate(self, *args):
        state = self._get_dynamic_state()
        if state != self._dynamic_state:
            self._set_dynamic_state(state)
        self._update_offset()

    def _update_preview_display_state(self):
        display_preview = not self.compact
        if self.bgFade:
            self.bgFade.display = display_preview
        if not self._live_preview:
            return
        if self._selectedTab == TAB_SKINS:
            self.bgFade.display = False
            self._live_preview.display = True
            self.previewCont.pickState = PickState.ON
        else:
            self._live_preview.display = display_preview
            self.previewCont.pickState = PickState.ON if display_preview and self._dynamic_state == EXPANDED else PickState.OFF

    def _update_offset(self, initial = False):
        if self._current_panel is None or not self._live_preview:
            return
        centerOffset = 0
        verticalOffset = 0
        if self._dynamic_state == EXPANDED:
            leftIndent = self._current_panel.leftCont.GetAbsoluteSize()[0] / 2 + self.split_view.content.padLeft + self.mainContent.padLeft / 2 + 2
            previewCenter = self.GetAbsoluteSize()[0] / 2
            if previewCenter:
                centerOffset = 1 - float(leftIndent) / previewCenter
            else:
                centerOffset = 0
        elif self._selectedTab == TAB_SKINS:
            centerOffset = 0
        else:
            centerOffset = -1
        self._live_preview.centerOffset = centerOffset
        if self._selectedTab == TAB_SKINS and self._dynamic_state != EXPANDED:
            verticalOffset = -0.6
        self._live_preview.verticalOffset = verticalOffset

    def _update_zoom(self, initial = False, duration = 0):
        if self._dynamic_state == EXPANDED:
            if self._current_panel:
                target_zoom = self._current_panel.get_zoom()
            else:
                target_zoom = EXPANDED_ZOOM
        elif self._selectedTab == TAB_SKINS:
            target_zoom = 2
        else:
            target_zoom = MINIMIZED_ZOOM
        if initial:
            self._live_preview.SetZoom(target_zoom)
        else:
            self._live_preview.zoom_to(target_zoom, duration)

    def _on_stacked_changed_callback(self, *args):
        if self.stacked:
            self.split_view.padTop = 0
        else:
            self.split_view.padTop = 40

    def GetSelectedTabIdx(self):
        if self._current_panel:
            return self._current_panel.get_tab_type()
        return 0

    def _do_fade_in(self):
        if not self._initialized:
            return
        if not self._live_preview or not self._live_preview.loaded:
            return
        if self._black_bg.opacity:
            animations.FadeOut(self._black_bg, duration=0.8, timeOffset=0.1)

    def _qa_open_old_window(self, *args, **kwargs):
        from eve.client.script.ui.shared.info.infoWindow import InfoWindow
        import gametime
        InfoWindow.Open(windowInstanceID=gametime.GetWallclockTime(), typeID=self.typeID, itemID=self.itemID, rec=self.rec, parentID=self.parentID, abstractinfo=self.abstractinfo)

    def OnStartMinimize_(self, *args):
        if self._live_preview:
            self._live_preview.Hide()

    def OnStartMaximize_(self, *args):
        if self._live_preview:
            self._live_preview.Show()


class ShipInfoSideNavigation(SideNavigation):

    def __init__(self, controller, is_expanded_func, expand_func = None, is_always_expanded_setting = None, **kwargs):
        super(ShipInfoSideNavigation, self).__init__(is_expanded_func, expand_func, is_always_expanded_setting, **kwargs)
        self._controller = controller

    def Flush(self):
        super(ShipInfoSideNavigation, self).Flush()
        self.bottomControls.Flush()

    def reconstruct(self, tabs, selectedTabID):
        self.Flush()
        typeID = self._controller.type_id
        if can_view_market_details(typeID):
            self.add_bottom_entry(texturePath=eveicon.market_details, text=localization.GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails'), on_click=self.on_market_button_click)
        if self._should_show_ship_tree_button():
            self.add_bottom_entry(texturePath=eveicon.ship_tree, text=localization.GetByLabel('UI/InfoWindow/ShowInISIS'), on_click=self.on_ship_tree_button_click)
        if TAB_FITTING in [ tab[0] for tab in tabs ]:
            if self._controller.is_owned_by_me and self._controller.is_assembled:
                label = 'UI/Fitting/FittingWindow/SimulateShipFitting'
            else:
                label = 'UI/Fitting/FittingWindow/SimulateShip'
            self.add_bottom_entry(texturePath=eveicon.simulate_fitting, text=localization.GetByLabel(label), on_click=self._on_simulate_button_clicked)
        self._add_top_entry()
        for tabID, panelCls in tabs:
            self.add_entry(entry_id=tabID, text=panelCls.get_name(), icon=panelCls.get_icon(), on_click=self._open_tab)

    def _open_tab(self, tab):
        self._controller.select_tab(tab.entry_id)

    def _layout_footer(self, main):
        super(ShipInfoSideNavigation, self)._layout_footer(main)
        self.bottomControls = ContainerAutoSize(parent=main, align=Align.TOBOTTOM)

    def _construct_background(self):
        self.panelBackground = Fill(bgParent=self, color=(0, 0, 0), opacity=0)

    def on_expanded_changed(self, expanded, animate = True):
        super(ShipInfoSideNavigation, self).on_expanded_changed(expanded, animate)
        duration = 0.2 if animate else 0
        if not expanded:
            animations.FadeOut(self.panelBackground, duration=duration)
        else:
            animations.FadeIn(self.panelBackground, endVal=0.9, duration=duration)

    def add_bottom_entry(self, texturePath, text, on_click, icon_size = 16):
        entry = SideNavigationEntry(icon=texturePath, text=text, on_click=on_click, icon_size=icon_size, parent=self.bottomControls, align=Align.TOBOTTOM, icon_color=TextColor.SECONDARY, force_compact=self._force_compact, on_hover=self._on_entry_hover)
        entry.on_expanded_changed(self.is_expanded_func(), animate=False)
        self._connect_to_expand(entry)

    def _add_top_entry(self):
        entry = TopSideNavigationEntry(parent=self._body, controller=self._controller, padBottom=4, on_hover=self._on_entry_hover, force_compact=self._force_compact)
        entry.on_expanded_changed(self.is_expanded_func(), animate=False)
        self._connect_to_expand(entry)

    def _on_entry_hover(self, entry):
        if not self.is_expanded_func() and self.expand_func is not None:
            self.expand_func(True)

    def _should_show_ship_tree_button(self):
        return sm.GetService('shipTree').IsInShipTree(self._controller.type_id)

    def on_ship_tree_button_click(self, *args):
        sm.GetService('shipTreeUI').OpenAndShowShip(self._controller.type_id)

    def on_market_button_click(self, *args):
        uthread.new(sm.StartService('marketutils').ShowMarketDetails, self._controller.type_id, None)

    def _on_simulate_button_clicked(self, *args, **kwargs):
        self._controller.open_simulation()

    def set_force_compact(self, force_compact):
        super(ShipInfoSideNavigation, self).set_force_compact(force_compact)
        for entry in self.bottomControls.children:
            if isinstance(entry, SideNavigationEntryInterface):
                entry.set_force_compact(force_compact)

    def OnMouseEnter(self, *args):
        super(ShipInfoSideNavigation, self).OnMouseEnter(*args)
        if not self._force_compact:
            animations.FadeIn(self.panelBackground, endVal=0.9, duration=0.2)

    def OnMouseExit(self, *args):
        super(ShipInfoSideNavigation, self).OnMouseExit(*args)
        animations.FadeOut(self.panelBackground, duration=0.2)


class TopSideNavigationEntry(Container, SideNavigationEntryInterface):
    default_state = uiconst.UI_NORMAL
    default_align = Align.TOTOP
    default_height = 40
    default_padRight = 10
    default_bgColor = eveThemeColor.THEME_FOCUSDARK
    isDragObject = True
    __notifyevents__ = ['OnSessionChanged']

    def __init__(self, controller, force_compact = False, on_hover = None, **kwargs):
        super(TopSideNavigationEntry, self).__init__(**kwargs)
        self.controller = controller
        self.character_id = self.controller.owner_id
        self._force_compact = force_compact
        self._on_hover = on_hover
        self._is_interactable = True
        sm.RegisterNotify(self)
        type_id = self.controller.type_id
        text = self.controller.get_owner_name() or self.controller.get_type_name()
        if self.character_id:
            subtext = ''
        else:
            subtext = self.controller.get_class_name()
            self._is_interactable = False
        self.bgFill.opacity = 0
        content = Container(parent=self, align=Align.TOALL, padding=(4, 2, 4, 2))
        icon_container = Container(parent=content, align=Align.CENTERLEFT, width=32, height=32)
        icon_container.pickState = PickState.OFF
        if self.character_id:
            self._construct_owner(self.controller.item_id, icon_container)
        else:
            self._consruct_type_icon(type_id, icon_container)
        self._text_container = Container(parent=content, align=Align.TOALL, padLeft=40, padRight=8, clipChildren=True, opacity=0)
        text_inner_container = ContainerAutoSize(parent=self._text_container, align=Align.VERTICALLY_CENTERED)
        self._text = TextBody(parent=text_inner_container, name='character_name_text', align=Align.TOTOP, text=text, maxLines=1, autoFadeSides=16, color=TextColor.SECONDARY)
        self._subtext = TextDetail(parent=text_inner_container, name='detail_text', align=Align.TOTOP, text=subtext, maxLines=1, autoFadeSides=16, color=TextColor.DISABLED)
        if self.character_id:
            uthread2.start_tasklet(self._update_owner_subtext)

    def _update_owner_subtext(self):
        owner_corporation_id = self.controller.owner_corporation_id
        if not owner_corporation_id:
            return
        corp_info = cfg.eveowners.Get(owner_corporation_id)
        if corp_info:
            self._subtext.text = corp_info.name

    def _construct_owner(self, ship_id, icon_container):
        icon = CharacterPortrait(parent=icon_container, align=Align.CENTER, size=32, character_id=self.character_id, textureSecondaryPath='res:/UI/Texture/circle_full.png', spriteEffect=trinity.TR2_SFX_MODULATE, pickState=PickState.OFF)
        self.OnClick = icon.OnClick
        self.GetMenu = icon.GetMenu
        self.GetDragData = icon.GetDragData
        if ship_id == session.shipid:
            Sprite(parent=icon_container, align=Align.CENTER, texturePath='res:/UI/Texture/classes/ShipInfo/circle_outer_34.png', height=34, width=34, color=eveColor.COPPER_OXIDE_GREEN)
            Frame(bgParent=self, align=Align.TOALL, texturePath='res:/UI/Texture/classes/ShipInfo/portrait_corner_frame_36.png', cornerSize=9, color=TextColor.SUCCESS, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3, padding=2)

    def _consruct_type_icon(self, type_id, icon_container):
        type_icon = GetHoloIconPath(type_id) or GetIconFile(type_id)
        Sprite(parent=icon_container, align=Align.CENTER, texturePath=type_icon, height=32, width=32, blendMode=trinity.TR2_SBM_ADD, ignoreColorBlindMode=True)
        Sprite(parent=icon_container, align=Align.CENTER, texturePath='res:/UI/Texture/Shared/windowFrame.png', height=36, width=36, color=TextColor.DISABLED)

    def on_expanded_changed(self, expanded, animate = True):
        if expanded:
            self.set_expanded(animate)
        else:
            self.set_collapsed(animate)

    def set_expanded(self, animate = True):
        if animate:
            eveui.animation.fade_in(self._text_container, duration=0.2)
        else:
            self._text_container.opacity = 1.0

    def set_collapsed(self, animate = True):
        if animate:
            eveui.animation.fade_out(self._text_container, duration=0.2)
        else:
            self._text_container.opacity = 0.0

    def OnMouseEnter(self, *args):
        super(TopSideNavigationEntry, self).OnMouseEnter(*args)
        if self._is_interactable:
            eveui.Sound.button_hover.play()
            eveui.animation.fade_in(self.bgFill, end_value=0.15, duration=0.05)
        if self._on_hover:
            self._on_hover(self)

    def OnMouseExit(self, *args):
        super(TopSideNavigationEntry, self).OnMouseExit(*args)
        if self._is_interactable:
            eveui.animation.fade_out(self.bgFill, duration=0.2)

    def OnSessionChanged(self, _isRemote, _session, change):
        if not self.character_id or self.character_id != session.charid:
            return
        if 'corpid' in change:
            self._update_owner_subtext()

    def set_force_compact(self, force_compact):
        self._force_compact = force_compact

    def GetHint(self):
        if not self._force_compact:
            return ''
        title = self._text.text
        subtitle = self._subtext.text
        if subtitle:
            return u'<b>{}</b>\n{}'.format(title, subtitle)
        else:
            return title

    def GetTooltipPointer(self):
        return uiconst.POINT_RIGHT_2

    def GetTooltipDelay(self):
        if self._force_compact:
            return 0
