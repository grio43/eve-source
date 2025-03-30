#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\dockedUI\corvetteButton.py
import functools
import blue
import carbonui.control.button
import localization
import signals
import uthread
from carbonui import ButtonVariant
from eve.common.script.sys import idCheckers
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst

class CorvetteButtonBase(carbonui.control.button.Button):
    default_name = 'corvetteButton'
    uniqueUiName = pConst.UNIQUE_NAME_CORVETTE_BTN
    default_variant = ButtonVariant.GHOST

    def ApplyAttributes(self, attributes):
        self.controller = Controller()
        attributes.func = self.controller.click
        attributes.args = ()
        super(CorvetteButtonBase, self).ApplyAttributes(attributes)
        self._update_enabled()
        self.controller.on_enabled_changed.connect(self._update_enabled)

    def Close(self):
        self.controller.close()
        super(CorvetteButtonBase, self).Close()

    def LoadTooltipPanel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        add_tooltip_title(panel)
        add_tooltip_description(panel)
        add_tooltip_error_message(panel, self.controller)

    def _update_enabled(self):
        if self.controller.is_enabled:
            self.Enable()
        else:
            self.Disable()


class CorvetteButton(CorvetteButtonBase):
    default_fixedheight = 24

    @property
    def default_label(self):
        return localization.GetByLabel('UI/Station/CreateNewbieShipButton')

    def LoadTooltipPanel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        add_tooltip_description(panel)
        add_tooltip_error_message(panel, self.controller)


class CorvetteIconButton(CorvetteButtonBase):
    default_texturePath = 'res:/UI/Texture/classes/ShipTree/groupIcons/rookie.png'

    def LoadTooltipPanel(self, panel, owner):
        panel.LoadGeneric1ColumnTemplate()
        add_tooltip_title(panel)
        add_tooltip_description(panel)
        add_tooltip_error_message(panel, self.controller)


def add_tooltip_title(panel):
    panel.AddLabelMedium(text=localization.GetByLabel('UI/Station/CreateNewbieShipButton'), wrapWidth=220, bold=True)


def add_tooltip_description(panel):
    panel.AddLabelMedium(text=localization.GetByLabel('UI/Station/CreateNewbieShipTooltip'), wrapWidth=220, color=(0.6, 0.6, 0.6, 1.0))


def add_tooltip_error_message(panel, controller):
    if controller.is_aboard_corvette:
        panel.AddSpacer(height=8)
        panel.AddLabelMedium(text=localization.GetByLabel('UI/Station/AlreadyInNewbieShip'), wrapWidth=220, color=(1.0, 0.0, 0.0, 1.0))


def threaded(f):

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        uthread.new(f, *args, **kwargs)

    return wrapper


class Controller(object):
    __notifyevents__ = ['ProcessActiveShipChanged']
    default_enabled = False

    def __init__(self):
        self.on_enabled_changed = signals.Signal(signalName='on_enabled_changed')
        self._is_clicking = False
        self._is_enabled = self.default_enabled
        self._update_when_ship_is_ready()
        self.clickLock = False
        sm.RegisterNotify(self)

    @property
    def godma_service(self):
        return sm.GetService('godma')

    @property
    def is_aboard_corvette(self):
        ship_item = self.godma_service.GetItem(session.shipid)
        if ship_item is not None:
            return idCheckers.IsNewbieShip(ship_item.groupID)
        else:
            return False

    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, is_enabled):
        was_enabled = self.is_enabled
        self._is_enabled = is_enabled
        if was_enabled != is_enabled:
            self.on_enabled_changed()

    @property
    def station_service(self):
        return sm.GetService('station')

    @property
    def is_ship_ready(self):
        return self.godma_service.IsItemReady(session.shipid)

    def click(self):
        if self._is_clicking or self.clickLock:
            return
        self._is_clicking = True
        try:
            self.clickLock = True
            self._remove_click_lock_in_500_ms()
            self.on_clicked()
        finally:
            self._is_clicking = False

    @threaded
    def _remove_click_lock_in_500_ms(self):
        blue.synchro.SleepWallclock(500)
        self.clickLock = False

    def close(self):
        sm.UnregisterNotify(self)

    def on_clicked(self):
        self.station_service.CreateNewbieShip()

    def _update_enabled(self):
        self.is_enabled = not self.is_aboard_corvette

    @threaded
    def _update_when_ship_is_ready(self):
        while not self.is_ship_ready:
            blue.synchro.SleepWallclock(100)

        self._update_enabled()

    def ProcessActiveShipChanged(self, ship_id, old_ship_id):
        self._update_enabled()
