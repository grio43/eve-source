#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\claim_location_prompt.py
import localization
import evetypes
import homestation.client
from eve.common.script.sys.eveCfg import IsDocked
import carbonui
from carbonui.control.window import Window
from carbonui.window.control.action import CloseWindowAction
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.button import Button
from carbonui.primitives.line import Line
from eve.client.script.ui.control.itemIcon import ItemIcon
from jobboard.client.job_board_settings import redeem_to_current_location

def prompt_select_claim_location(item_rewards):
    if not item_rewards:
        return None
    else:
        window = JobBoardClaimLocation.Open(item_rewards=item_rewards)
        if window.ShowDialog(modal=True, closeWhenClicked=True) == 1:
            location_id = window.result
            redeem_to_current_location.set(location_id and location_id in (session.stationid, session.structureid))
            return location_id
        return None


class JobBoardClaimLocation(Window):
    default_name = 'JobBoardClaimLocation'
    default_windowID = 'select_jobboard_claim_location'
    default_captionLabelPath = 'UI/SystemMenu/RedeemItems'
    default_width = 500
    default_height = 160
    default_minSize = (default_width, default_height)
    default_isStackable = False
    default_isCollapseable = False
    default_isCompact = True
    result = None

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.MakeUnResizeable()
        item_rewards = sorted([ (type_id, amount, evetypes.GetName(type_id)) for type_id, amount in attributes['item_rewards'].iteritems() ], key=lambda x: x[2])
        self._main_container = main = ContainerAutoSize(parent=self.content, align=carbonui.Align.TOTOP, callback=self._on_content_size_changed)
        item_container = ScrollContainer(parent=main, align=carbonui.Align.TOTOP, padding=8, height=min(len(item_rewards) * 52, 300))
        for type_id, amount, name in item_rewards:
            self._construct_reward(item_container, type_id, amount, name)

        Line(parent=main, align=carbonui.Align.TOTOP, padding=(8, 12, 8, 16))
        current_station_id = None
        if IsDocked():
            current_station_id = session.stationid or session.structureid
            current_location_type_id = sm.GetService('map').GetItem(current_station_id).typeID
            self._construct_location(main, current_station_id, current_location_type_id, localization.GetByLabel('UI/Generic/CurrentLocation'), localization.GetByLabel('UI/RedeemWindow/RedeemToCurrentStation'))
        home_station = homestation.Service.instance().get_home_station()
        if not current_station_id or home_station.id != current_station_id:
            self._construct_location(main, home_station.id, home_station.type_id, localization.GetByLabel('UI/Map/HomeStationLabel'), localization.GetByLabel('UI/RedeemWindow/RedeemToHomeStation'))

    def _construct_location(self, parent, location_id, type_id, text, button_text):
        container = Container(parent=parent, align=carbonui.Align.TOTOP, height=48, padding=8)
        button_container = ContainerAutoSize(parent=container, align=carbonui.Align.TORIGHT)
        Button(parent=button_container, align=carbonui.Align.CENTERRIGHT, label=button_text, func=lambda *args, **kwargs: self._select_location(location_id))
        ItemIcon(parent=container, align=carbonui.Align.CENTERLEFT, width=48, height=48, typeID=type_id, itemID=location_id)
        text_container = ContainerAutoSize(parent=container, align=carbonui.Align.VERTICALLY_CENTERED, padLeft=56, padRight=8, clipChildren=True)
        carbonui.TextBody(parent=text_container, align=carbonui.Align.TOTOP, text=text, color=carbonui.TextColor.SECONDARY, autoFadeSides=16, maxLines=1)
        carbonui.TextBody(parent=text_container, align=carbonui.Align.TOTOP, text=cfg.evelocations.Get(location_id).name, autoFadeSides=16, maxLines=2)

    def _construct_reward(self, parent, type_id, amount, name):
        container = ContainerAutoSize(parent=parent, align=carbonui.Align.TOTOP, padBottom=4, clipChildren=True)
        ItemIcon(parent=container, align=carbonui.Align.CENTERLEFT, typeID=type_id, height=48, width=48)
        carbonui.TextBody(parent=container, align=carbonui.Align.CENTERLEFT, left=56, text=localization.GetByLabel('UI/InfoWindow/FittingItemLabelWithQuantity', quantity=amount, itemName=name))

    def _select_location(self, location_id):
        self.result = location_id
        self.SetModalResult(1)

    def _on_content_size_changed(self):
        _, self.height = self.GetWindowSizeForContentSize(height=self._main_container.height)

    def _get_window_actions(self):
        return [CloseWindowAction(self)]
