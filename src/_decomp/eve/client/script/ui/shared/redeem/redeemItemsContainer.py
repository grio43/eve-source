#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\redeemItemsContainer.py
import math
import eveformat
import evelink.client
import eveui
import homestation.client
import localization
import redeem.client
import signals
import threadutils
import uthread2
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import ButtonVariant, Color, uiconst
from carbonui.control.button import Button
from carbonui.control.combo import Combo
from carbonui.control.scroll import Scroll
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor, eveThemeColor
from eve.client.script.ui.control import eveLabel, itemIcon
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.message import QuickMessage
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.shared.inventory.invContainers import RedeemItems, GetRedeemSortOptions
from eve.client.script.ui.shared.redeem.redeemItem import RedeemItem, DraggableRedeemItem, REDEEM_ITEM_WIDTH, GetRedeemItemHeight, GetRedeemItemHeightWithoutDescription
from eve.client.script.ui.shared.redeem.redeemUiConst import CREATION_DATE_SORT_KEY
from uihider import CommandBlockerService

def alert_user(text):
    message = QuickMessage(parent=uicore.layer.abovemain, name='RedeemActionAlert')
    message.minTop = uicore.desktop.height / 2 - 56
    msg = u'\n{}\n'.format(text)
    message.ShowMsg(msg)
    uthread2.call_after_wallclocktime_delay(message.Close, 3)


PADDING_NORMAL = 8
PADDING_WIDE = 2 * PADDING_NORMAL
FOOTER_HEIGHT = 50
BUTTON_CONTAINER_HEIGHT = 35
ITEM_ROW_PADDING = 12
INFO_CONTAINER_COLOR = (0.0, 0.0, 0.0, 0.5)
INV_NAME = 'redeemItems'

class RedeemItemsContainer(Container):
    default_name = 'RedeemItemsContainer'
    default_showHeaderCount = True
    default_showDeliveryInfo = True
    default_showFooter = True
    default_areItemsDraggable = False
    default_sidePadding = 50
    default_topPadding = 4
    default_bottomPadding = 6

    def ApplyAttributes(self, attributes):
        super(RedeemItemsContainer, self).ApplyAttributes(attributes)
        self.isReady = False
        self._is_updating_scroll_selection = False
        self.controller = attributes.controller
        if not self.controller:
            self.controller = Controller(redeem_data=attributes.redeemData, redeem_service=sm.GetService('redeem'), home_station_service=homestation.Service.instance())
        self.onContentUpdateCallback = attributes.get('onContentUpdateCallback', None)
        self.areItemsDraggable = attributes.get('areItemsDraggable', self.default_areItemsDraggable)
        self.showHeaderCount = attributes.get('showHeaderCount', self.default_showHeaderCount)
        self.showDeliveryInfo = attributes.get('showDeliveryInfo', self.default_showDeliveryInfo)
        self.showFooter = attributes.get('showFooter', self.default_showFooter)
        self.sidePadding = attributes.get('sidePadding', self.default_sidePadding)
        self.topPadding = attributes.get('topPadding', self.default_topPadding)
        self.bottomPadding = attributes.get('bottomPadding', self.default_bottomPadding)
        self.redeemItems = None
        self.redeemItemsContainer = None
        self.dragArea = Container(name='dragArea', parent=self, align=uiconst.TOALL)
        if self.showHeaderCount:
            self.ConstructHeader()
        if self.showFooter:
            self.ConstructFooter()
        if self.showDeliveryInfo:
            self.ConstructDeliveryInfo()
        self.redeemItemsContainer = Container(name='redeemItemsContainer', parent=self, align=uiconst.TOALL, padding=(self.sidePadding,
         self.topPadding,
         self.sidePadding,
         self.bottomPadding))
        self.ConstructRedeemItemsContainer()
        self.controller.on_selection_changed.connect(self._OnSelectionChanged)
        self.controller.on_load.connect(self._OnTokensUpdated)
        self.controller.on_redeem.connect(self._OnRedeem)
        self.controller.on_trash.connect(self._OnTrash)
        self.controller.on_refresh_sort.connect(self._RefreshSort)
        self.controller.on_text_filter_changed.connect(self._OnTextFilterChanged)
        self.controller.select_all_triggered.connect(self._SelectAllTriggered)
        uthread2.start_tasklet(self.controller.load)

    def ConstructHeader(self):
        Header(parent=self, align=uiconst.TOTOP, padding=(self.sidePadding,
         PADDING_WIDE,
         self.sidePadding,
         0), controller=self.controller)
        ControlContainer(parent=self, align=uiconst.TOTOP, controller=self.controller, padding=(self.sidePadding,
         10,
         self.sidePadding,
         16))

    def ConstructDeliveryInfo(self):
        if not CommandBlockerService.instance().is_blocked(['redeem_to_home_station']):
            HomeStationSection(parent=self, align=uiconst.TOBOTTOM, padding=(self.sidePadding,
             0,
             self.sidePadding,
             PADDING_NORMAL), controller=self.controller)
        CurrentStationSection(parent=self, align=uiconst.TOBOTTOM, padding=(self.sidePadding,
         0,
         self.sidePadding,
         PADDING_NORMAL), controller=self.controller)
        AutoInjectNotice(parent=self, align=uiconst.TOBOTTOM, padding=(self.sidePadding,
         0,
         self.sidePadding,
         PADDING_NORMAL), controller=self.controller)

    def ConstructFooter(self):
        Footer(parent=self, align=uiconst.TOBOTTOM, controller=self.controller)

    @eveui.skip_if_destroyed
    def ConstructRedeemItemsContainer(self):
        if self.redeemItems and not self.redeemItems.destroyed:
            self.redeemItems.Close()
        self.redeemItems = RedeemItems(name=INV_NAME, parent=self.redeemItemsContainer, showControls=False, state=uiconst.UI_NORMAL, itemID='redeemItems', hasCapacity=False, oneWay=True, viewOnly=True, hasScrollBackground=False, rowPadding=ITEM_ROW_PADDING, shouldAddFinalRowPadding=False, getItemClass=self.GetItemClass, scrollClass=Scroll, shouldShowHint=self.ShouldShowHint(), selectAllOnFirstLoad=True, onSelectionChange=self._OnScrollSelectionChanged)
        self.redeemItems.GetRubberbandParentContainer = self.GetDragArea
        self.OnMouseDown = self.redeemItems.scroll.OnMouseDown
        self.OnMouseUp = self.redeemItems.scroll.OnMouseUp

    def GetDragArea(self):
        return self.dragArea

    def _OnTokensUpdated(self):
        if self.redeemItems and not self.redeemItems.destroyed:
            self.redeemItems.Refresh()
        else:
            self.ConstructRedeemItemsContainer()
        self.isReady = True
        if self.onContentUpdateCallback:
            self.onContentUpdateCallback()

    def _OnScrollSelectionChanged(self, selected_nodes):
        if self._is_updating_scroll_selection:
            return
        self.controller.on_selection_changed.disconnect(self._OnSelectionChanged)
        try:
            selected_tokens = [ node.item for node in selected_nodes ]
            self.controller.select_exclusive(selected_tokens)
        finally:
            self.controller.on_selection_changed.connect(self._OnSelectionChanged)

    def _OnSelectionChanged(self):
        self._is_updating_scroll_selection = True
        try:
            selected_nodes = [ node for node in self.redeemItems.scroll.GetNodes() if token_key(node.item) in self.controller.selected_keys ]
            self.redeemItems.scroll.SelectNodes(selected_nodes)
        finally:
            self._is_updating_scroll_selection = False

    def _SelectAllTriggered(self):
        self.redeemItems.scroll.SelectAll()

    def IsReady(self):
        return self.isReady

    def HasTokens(self):
        return self.controller.tokens_count > 0

    def RedeemAll(self):
        self.controller.redeem_all(destination=Destination.current_station)

    def GetItemClass(self):
        if self.areItemsDraggable:
            return DraggableRedeemItem
        return RedeemItem

    def ShouldShowHint(self):
        return not self.areItemsDraggable

    def _OnRedeem(self, delivery_location_id, redeem_result):
        PlaySound(uiconst.SOUND_ADD_OR_USE)
        alert_message = None
        if redeem_result['itemsCreated']:
            alert_message = localization.GetByLabel('UI/Redeem/RedeemToStationModalConfirmation', station=delivery_location_id)
        elif any((redeem_result[x] for x in ['activated_licenses', 'itemsCreated', 'isk_rewarded'])):
            alert_message = localization.GetByLabel('UI/Redeem/RedeemModalConfirmation')
        if alert_message:
            alert_user(alert_message)

    def _OnTrash(self):
        alert_user(localization.GetByLabel('UI/Redeem/TrashModalConfirmation'))
        PlaySound(uiconst.SOUND_REMOVE)

    def _RefreshSort(self, sortby, direction):
        self.redeemItems.RefreshSort(sortby, direction)

    def _OnTextFilterChanged(self, text):
        self.redeemItems.SetQuickFilterInput(text)


class Station(object):

    def __init__(self, station_id, type_id):
        self.id = station_id
        self.type_id = type_id

    @staticmethod
    def from_session(session):
        docked_id = get_docked_id(session)
        if docked_id:
            return Station(station_id=docked_id, type_id=sm.GetService('map').GetItem(docked_id).typeID)

    @property
    def name(self):
        return cfg.evelocations.Get(self.id).name

    @property
    def link(self):
        return evelink.location_link(self.id)


def get_docked_id(session):
    station_id = getattr(session, 'stationid', None)
    structure_id = getattr(session, 'structureid', None)
    ship_id = getattr(session, 'shipid', None)
    if station_id is not None:
        return station_id
    if structure_id is not None and structure_id != ship_id:
        return structure_id


class Destination(object):
    current_station = 'current_station'
    home_station = 'home_station'


class Controller(object):
    __notifyevents__ = ('OnRedeemingTokensUpdated', 'OnSessionChanged')

    def __init__(self, redeem_data, redeem_service, home_station_service):
        self._redeem_data = redeem_data
        self._redeem_service = redeem_service
        self._home_station_service = home_station_service
        self._raw_tokens = []
        self._tokens = {}
        self._selected = set()
        self.invName = INV_NAME
        self.on_selection_changed = signals.Signal('on_selection_changed')
        self.on_load = signals.Signal('on_load')
        self.on_station_changed = signals.Signal('on_station_changed')
        self.on_redeem = signals.Signal('on_redeem')
        self.on_trash = signals.Signal('on_trash')
        self.on_refresh_sort = signals.Signal('on_refresh_sort')
        self.on_text_filter_changed = signals.Signal('on_text_filter_changed')
        self.select_all_triggered = signals.Signal('select_all_triggered')
        sm.RegisterNotify(self)

    @property
    def tokens(self):
        return self._tokens.values()

    @property
    def tokens_count(self):
        return len(self._tokens)

    @property
    def selected(self):
        return [ self._tokens[key] for key in self._selected ]

    @property
    def selected_keys(self):
        return [ key for key in self._selected ]

    @property
    def selected_count(self):
        return len(self._selected)

    @property
    def current_station(self):
        return Station.from_session(session)

    @property
    def auto_injected_selected_count(self):
        return len(filter(lambda token: self._redeem_data.is_auto_injected(token), self.selected))

    def load(self):
        self.deselect_all()
        self._raw_tokens = []
        self._tokens = []
        self._raw_tokens = self._redeem_service.GetRedeemTokens()
        self._tokens = {token_key(token):token for token in self._raw_tokens}
        self.on_load()

    def get_by_key(self, key):
        return self._tokens[key]

    def select(self, tokens):
        self._selected = self._selected.union(set((token_key(token) for token in tokens)))
        self.on_selection_changed()

    def select_all(self):
        self.select(self.tokens)

    def select_exclusive(self, tokens):
        self._selected = set((token_key(token) for token in tokens))
        self.on_selection_changed()

    def deselect(self, tokens):
        if any((token_key(token) in self._selected for token in tokens)):
            self._selected = self._selected.difference(set((token_key(token) for token in tokens)))
            self.on_selection_changed()

    def deselect_all(self):
        self.deselect(self.selected)

    def redeem(self, tokens, destination):
        if destination == Destination.current_station:
            delivery_location_id = self.current_station.id
        elif destination == Destination.home_station:
            delivery_location_id = self._home_station_service.get_home_station().id
        else:
            raise RuntimeError('Unknown destination {!r}'.format(destination))
        confirmed = redeem.confirm_redeem(character_id=session.charid, tokens=tokens, delivery_location_id=delivery_location_id, redeem_data=self._redeem_data)
        if not confirmed:
            return
        tokens = [ {'tokenID': token.tokenID,
         'massTokenID': token.massTokenID,
         'typeID': token.typeID} for token in tokens ]
        redeem_result = self._redeem_service.ClaimRedeemTokens(tokens=tokens, charID=session.charid, useHomeStation=destination == Destination.home_station)
        self.on_redeem(delivery_location_id, redeem_result)

    def redeem_all(self, destination):
        self.redeem(self.tokens, destination)

    def redeem_selected(self, destination):
        self.redeem(self.selected, destination)

    def trash(self, tokens):
        if not tokens:
            return
        if not redeem.confirm_trash(tokens):
            return
        token_keys = [ token_key(token) for token in tokens ]
        self._redeem_service.TrashRedeemTokens(token_keys)
        self.on_trash()

    def trash_selected(self):
        self.trash(self.selected)

    def change_sort_order(self, sortby, direction):
        self.on_refresh_sort(sortby, direction)

    def change_text_filter(self, text):
        self.deselect_all()
        self.on_text_filter_changed(text)

    def OnRedeemingTokensUpdated(self):
        uthread2.start_tasklet(self.load)

    def OnSessionChanged(self, is_remote, session, changes):
        docked_or_undocked = any((name in changes for name in ('stationid', 'structureid')))
        took_or_released_structure_control = 'shipid' in changes and session.structureid and session.structureid in changes['shipid']
        if docked_or_undocked or took_or_released_structure_control:
            uthread2.start_tasklet(self.on_station_changed)


def token_key(token):
    return (token.tokenID, token.massTokenID)


class Header(ContainerAutoSize):

    def __init__(self, controller, **kwargs):
        super(Header, self).__init__(alignMode=uiconst.TOTOP, **kwargs)
        self._controller = controller
        self._label = None
        self.layout()
        self.update()
        self._controller.on_load.connect(self.update)

    def layout(self):
        self._label = eveLabel.EveCaptionLarge(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOTOP)

    @threadutils.threaded
    def update(self):
        text = localization.GetByLabel('UI/RedeemWindow/ReedemNumItems', num=self._controller.tokens_count)
        self._label.SetText(text)


class Footer(Container):

    def __init__(self, controller, **kwargs):
        super(Footer, self).__init__(bgColor=eveColor.BLACK, height=FOOTER_HEIGHT, **kwargs)
        self._controller = controller
        self._label = None
        self.layout()
        self.update()
        self._controller.on_selection_changed.connect(self.update)
        self._controller.on_load.connect(self.update)

    def layout(self):
        ButtonIcon(parent=self, align=uiconst.CENTERLEFT, left=PADDING_WIDE, width=32, height=32, texturePath='res:/UI/Texture/Classes/RedeemPanel/trashcan_icon.png', iconSize=24, func=self._controller.trash_selected, args=(), hint=localization.GetByLabel('UI/RedeemWindow/TrashSelectedItems'))
        self._label = eveLabel.EveLabelMedium(parent=self, align=uiconst.CENTERRIGHT, left=PADDING_WIDE)

    @threadutils.threaded
    def update(self):
        self._label.SetText(localization.GetByLabel('UI/Redeem/RedeemItemsSelected', selected=self._controller.selected_count, total=self._controller.tokens_count))


class AutoInjectNotice(ContainerAutoSize):
    icon_size = 24
    color = Color.from_hex('#369ebd')

    def __init__(self, controller, **kwargs):
        super(AutoInjectNotice, self).__init__(alignMode=uiconst.TOTOP, minHeight=(self.icon_size + 2 * PADDING_NORMAL), clipChildren=True, **kwargs)
        self.display = False
        self._controller = controller
        self._frame = None
        self._corner = None
        self._icon = None
        self._label = None
        self._padding_before = (self.padTop, self.padBottom)
        self._is_revealed = False
        self.layout()
        self.update(animate=False)
        self._controller.on_selection_changed.connect(self.update)

    def layout(self):
        color = eveThemeColor.THEME_ACCENT
        self._frame = Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, rotation=math.pi, color=color, opacity=0.1)
        self._corner = Sprite(name='AUTOINJECT_SPRITE_A', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/Shared/DarkStyle/cornerTriSmall.png', width=5, height=5, color=color)
        self._icon = Sprite(name='AUTOINJECT_SPRITE_B', parent=self, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, top=PADDING_NORMAL, left=PADDING_NORMAL, width=self.icon_size, height=self.icon_size, texturePath='res:/UI/Texture/classes/RedeemPanel/autoInjectFlat.png', color=color)
        self._label = eveLabel.EveLabelMedium(name='AUTOINJECT_LABEL_A', parent=self, align=uiconst.TOTOP, state=uiconst.UI_DISABLED, padding=(PADDING_NORMAL + self.icon_size + PADDING_NORMAL,
         PADDING_NORMAL,
         PADDING_NORMAL,
         PADDING_NORMAL), color=color)

    def reveal(self):
        self.padTop, self.padBottom = self._padding_before
        self.display = True
        self.EnableAutoSize()

    def anim_reveal(self):
        if self.display:
            return
        self.display = True
        _, height = self.GetAutoSize()
        self.DisableAutoSize()
        duration = 0.2
        animations.FadeIn(self, duration=duration)
        animations.MorphScalar(self, 'height', startVal=0, endVal=height, duration=duration / 2.0, callback=self.EnableAutoSize)
        animations.MorphScalar(self, 'padTop', startVal=0, endVal=self._padding_before[0], duration=duration)
        animations.MorphScalar(self, 'padBottom', startVal=0, endVal=self._padding_before[1], duration=duration)

    def hide(self):
        self.display = False

    def anim_hide(self):
        if not self.display:
            return
        self.DisableAutoSize()
        duration = 0.2
        animations.FadeOut(self, duration=duration)
        animations.MorphScalar(self, 'height', startVal=self.height, endVal=0, duration=duration / 2.0, callback=self.Hide)
        animations.MorphScalar(self, 'padTop', startVal=self._padding_before[0], endVal=0, duration=duration)
        animations.MorphScalar(self, 'padBottom', startVal=self._padding_before[1], endVal=0, duration=duration)

    @threadutils.threaded
    def update(self, animate = True):
        self._label.SetText(localization.GetByLabel('UI/RedeemWindow/AutoInjectNotification', count=self._controller.auto_injected_selected_count))
        if self._controller.auto_injected_selected_count > 0:
            self.anim_reveal() if animate else self.reveal()
        else:
            self.anim_hide() if animate else self.hide()

    def OnColorThemeChanged(self):
        super(AutoInjectNotice, self).OnColorThemeChanged()
        newColor = eveThemeColor.THEME_ACCENT.rgb
        self._frame.SetRGB(*newColor)
        self._corner.SetRGB(*newColor)
        self._icon.SetRGB(*newColor)
        self._label.SetRGB(*newColor)


class StationSection(ContainerAutoSize):
    icon_size = 48
    background_color = INFO_CONTAINER_COLOR

    def __init__(self, button_text, primary = False, **kwargs):
        super(StationSection, self).__init__(bgColor=self.background_color, **kwargs)
        self._button_text = button_text
        self._primary = primary
        self._icon = None
        self._label = None
        self._button = None
        self._feedback = None
        self.layout()
        self.update()

    def redeem(self):
        raise NotImplementedError()

    def get_text(self):
        raise NotImplementedError()

    def update_icon(self, icon):
        raise NotImplementedError()

    def is_enabled(self):
        raise NotImplementedError()

    def layout(self):
        inner = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP, minHeight=self.icon_size + 2 * PADDING_NORMAL)
        self._feedback = Fill(parent=inner, align=uiconst.TOALL, color=(1.0, 1.0, 1.0), opacity=0.0)
        icon_cont = ContainerAutoSize(parent=inner, align=uiconst.TOLEFT, padding=8)
        self._icon = itemIcon.ItemIcon(parent=icon_cont, align=uiconst.TOPLEFT, state=uiconst.UI_DISABLED, width=self.icon_size, height=self.icon_size, showOmegaOverlay=False)
        button_cont = ContainerAutoSize(parent=inner, align=uiconst.TORIGHT, padding=(PADDING_NORMAL,
         0,
         PADDING_NORMAL,
         0))
        if self._primary:
            button_variant = ButtonVariant.PRIMARY
        else:
            button_variant = ButtonVariant.NORMAL
        self._button = Button(parent=button_cont, align=uiconst.CENTER, label=self._button_text, func=self.redeem, args=(), variant=button_variant)
        self._button.Disable()
        label_cont = ContainerAutoSize(parent=inner, align=uiconst.TOTOP, minHeight=self.icon_size, padding=(0,
         PADDING_NORMAL,
         0,
         PADDING_NORMAL))
        self._label = eveLabel.EveLabelMedium(parent=label_cont, align=uiconst.CENTERLEFT, state=uiconst.UI_NORMAL, autoFadeSides=25)

    @threadutils.threaded
    def update(self, animate = False, feedback = False):
        if animate:
            animations.FadeOut(self._icon, duration=0.25)
            animations.FadeOut(self._label, duration=0.25, sleep=True)
        self.update_icon(self._icon)
        self._label.SetText(self.get_text())
        if self.is_enabled():
            self._button.Enable()
        else:
            self._button.Disable()
        if animate:
            animations.FadeIn(self._icon, duration=0.25)
            animations.FadeIn(self._label, endVal=self._label.default_color[3], duration=0.25)
            if feedback:
                animations.FadeTo(self._feedback, endVal=0.5, duration=0.35, timeOffset=0.1, curveType=uiconst.ANIM_WAVE)


class CurrentStationSection(StationSection):

    def __init__(self, controller, **kwargs):
        self._controller = controller
        super(CurrentStationSection, self).__init__(button_text=localization.GetByLabel('UI/RedeemWindow/RedeemToCurrentStation'), primary=True, **kwargs)
        self._controller.on_station_changed.connect(self.handle_station_changed)
        self._controller.on_selection_changed.connect(self.update)

    def is_enabled(self):
        return self._controller.current_station is not None and self._controller.selected_count > 0

    def get_text(self):
        current_station = self._controller.current_station
        if current_station is None:
            return u'{}<br>{}'.format(localization.GetByLabel('UI/RedeemWindow/CurrentStationHeader'), eveformat.color(localization.GetByLabel('UI/RedeemWindow/NotDocked'), eveColor.WARNING_ORANGE))
        else:
            return u'{}<br>{}'.format(localization.GetByLabel('UI/RedeemWindow/CurrentStationHeader'), current_station.link)

    def update_icon(self, icon):
        current_station = self._controller.current_station
        if current_station is None:
            icon.SetTexturePath('res:/UI/Texture/Icons/5_64_11.png')
            icon.opacity = 0.5
        else:
            icon.SetTypeIDandItemID(typeID=current_station.type_id, itemID=current_station.id)
            icon.opacity = 1.0

    def redeem(self):
        self._controller.redeem_selected(Destination.current_station)

    def handle_station_changed(self):
        self.update(animate=True, feedback=True)


class HomeStationSection(StationSection):

    def __init__(self, controller, **kwargs):
        super(HomeStationSection, self).__init__(button_text=localization.GetByLabel('UI/RedeemWindow/RedeemToHomeStation'), **kwargs)
        self._controller = controller
        homestation.Service.instance().on_home_station_changed.connect(self.handle_home_station_changed)
        self._controller.on_selection_changed.connect(self.update)

    @property
    def home_station(self):
        return homestation.Service.instance().get_home_station()

    def is_enabled(self):
        return self._controller.selected_count > 0

    def get_text(self):
        try:
            return u'{}<br>{}'.format(localization.GetByLabel('UI/RedeemWindow/HomeStationHeader'), self.home_station.link)
        except homestation.NotLoggedInError:
            return ''

    def update_icon(self, icon):
        try:
            icon.SetTypeIDandItemID(itemID=self.home_station.id, typeID=self.home_station.type_id)
        except homestation.NotLoggedInError:
            pass

    def redeem(self):
        self._controller.redeem_selected(destination=Destination.home_station)

    def handle_home_station_changed(self):
        self.update(animate=True, feedback=True)


class ControlContainer(ContainerAutoSize):
    __notifyevents__ = ('OnInvContRefreshed',)
    default_height = 30
    default_availableSpace = None

    def __init__(self, controller, **kwargs):
        super(ControlContainer, self).__init__(alignMode=uiconst.TOLEFT, **kwargs)
        self._controller = controller
        self.availableSpace = kwargs.get('availableSpace', None)
        self.sortCombo = None
        self.layout()
        sm.RegisterNotify(self)

    def layout(self):
        options = []
        for eachOption in GetRedeemSortOptions():
            if eachOption is None:
                continue
            labelPath, value = eachOption
            options.append((localization.GetByLabel(labelPath), value))

        selectedValue = self.GetSelectedOptionFromSettings()
        labelCont = ContainerAutoSize(name='labelCont', parent=self, align=uiconst.TOLEFT)
        text = localization.GetByLabel('UI/Common/SortBy')
        label = eveLabel.EveLabelMedium(parent=labelCont, align=uiconst.CENTERRIGHT, left=uiconst.CENTERLEFT, text=text)
        comboCont = ContainerAutoSize(name='comboCont', parent=self, align=uiconst.TOLEFT)
        self.sortCombo = Combo(name='myCombo', parent=comboCont, label='', options=options, align=uiconst.CENTER, callback=self.OnSortOrderChanged, select=selectedValue, width=100)
        buttonCont = ContainerAutoSize(name='buttonCont', parent=self, align=uiconst.TOLEFT, left=10)
        btn = Button(parent=buttonCont, align=uiconst.CENTERRIGHT, label=localization.GetByLabel('UI/RedeemWindow/SelectAll'), func=self._controller.select_all_triggered, args=())
        filterAlign = uiconst.TORIGHT if self.align == uiconst.TOTOP else uiconst.TOLEFT
        filtCont = ContainerAutoSize(name='filtCont', parent=self, align=filterAlign, left=10)
        self.quickFilter = QuickFilterEdit(parent=filtCont, align=uiconst.CENTERRIGHT, width=190)
        self.quickFilter.ReloadFunction = self.OnQuickFilter
        self.height = max(label.height, self.sortCombo.height, btn.height)
        if self.availableSpace is not None:
            self.AdjustWidths()

    def AdjustWidths(self):
        if self.availableSpace is None:
            return
        if self.availableSpace < self.width + 50:
            self.quickFilter.width = 100

    def GetSelectedOptionFromSettings(self):
        return settings.user.ui.Get('containerSortIconsBy_%s' % self._controller.invName, (CREATION_DATE_SORT_KEY, 1))

    def OnInvContRefreshed(self, invCont):
        if invCont.name == self._controller.invName:
            if self.sortCombo and not self.sortCombo.destroyed:
                selectedValue = self.GetSelectedOptionFromSettings()
                self.sortCombo.SelectItemByValue(selectedValue)

    def OnSortOrderChanged(self, cb, key, value):
        self._controller.on_refresh_sort(*value)

    def OnQuickFilter(self, *args):
        text = self.quickFilter.GetValue()
        self._controller.change_text_filter(text)
