#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\jobboard\client\ui\solar_system_chip.py
from evePathfinder.core import IsUnreachableJumpCount
import carbonui
import eveui
import eveicon
import inventorycommon.const as invConst
from eve.common.script.sys import idCheckers
import localization
import uthread2
from carbonui import TextColor, uiconst
from eveformat.client.location import get_security_status, solar_system_with_security
from security.client.securityColor import get_security_status_color

class SolarSystemChip(eveui.ContainerAutoSize):
    default_state = eveui.State.normal
    default_alignMode = eveui.Align.to_left
    default_height = 20
    compact_icon = eveicon.jump_to
    __notifyevents__ = ['OnAutopilotUpdated', 'OnSessionChanged']

    def __init__(self, solar_system_id, compact = False, *args, **kwargs):
        super(SolarSystemChip, self).__init__(*args, **kwargs)
        self._solar_system_id = solar_system_id
        self._compact = compact
        self._layout()
        sm.RegisterNotify(self)
        uthread2.start_tasklet(self._update_jumps)

    def Close(self):
        sm.UnregisterNotify(self)
        super(SolarSystemChip, self).Close()

    def OnAutopilotUpdated(self, *args, **kwargs):
        self._update_jumps()

    def OnSessionChanged(self, _is_remote, _session, change):
        if 'solarsystemid2' in change:
            self._update_jumps()

    def set_solar_system_id(self, solar_system_id):
        if solar_system_id == self._solar_system_id:
            return
        self._solar_system_id = solar_system_id
        self._location_label.text = cfg.evelocations.Get(self._solar_system_id).locationName
        security_status = get_security_status(self._solar_system_id)
        security_status_color = get_security_status_color(security_status)[:3]
        self._hover_fill.SetRGB(*security_status_color)
        self._frame.SetRGB(*security_status_color)
        self._security_status_label.text = str(security_status)
        self._update_jumps()

    def _update_jumps(self):
        jumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, self._solar_system_id)
        if self._compact:
            jumps_label = '-' if IsUnreachableJumpCount(jumps) else str(jumps)
        elif not jumps:
            jumps_label = localization.GetByLabel('UI/Generic/CurrentSystem')
        elif IsUnreachableJumpCount(jumps):
            jumps_label = localization.GetByLabel('UI/Generic/NoGateToGateRouteShort')
        else:
            jumps_label = localization.GetByLabel('UI/Common/NumJumps', numJumps=jumps)
        self._jump_label.text = jumps_label

    def _layout(self):
        security_status = get_security_status(self._solar_system_id)
        security_status_color = get_security_status_color(security_status)
        container = eveui.ContainerAutoSize(parent=self, align=eveui.Align.to_left, alignMode=carbonui.Align.TOLEFT, padding=2)
        jumps_container = eveui.ContainerAutoSize(parent=container, align=carbonui.Align.TOLEFT, alignMode=eveui.Align.center_left, padLeft=2, padRight=2)
        if self._compact:
            eveui.Sprite(name='numJumps', parent=jumps_container, align=eveui.Align.center_right, texturePath=self.compact_icon, height=16, width=16, color=TextColor.SECONDARY)
        self._jump_label = carbonui.TextDetail(name='numJumps', parent=jumps_container, align=eveui.Align.center_left, text='', padding=(4, 0, 18, 0) if self._compact else (4, 0, 4, 0), color=TextColor.SECONDARY)
        location_cotainer = eveui.ContainerAutoSize(parent=container, align=carbonui.Align.TOLEFT, alignMode=eveui.Align.to_left, padLeft=2, padRight=2)
        self._location_label_container = eveui.ContainerAutoSize(parent=location_cotainer, align=eveui.Align.to_left, alignMode=eveui.Align.center_left, maxWidth=80 if self._compact else None, padding=4)
        self._location_label = carbonui.TextDetail(name='locationName', parent=self._location_label_container, align=eveui.Align.center_left, text=cfg.evelocations.Get(self._solar_system_id).locationName, maxLines=1, autoFadeSides=16)
        self._hover_fill = eveui.Frame(bgParent=self._location_label_container, color=security_status_color, opacity=0.2, frameConst=uiconst.FRAME_FILLED_CORNER1, padding=-4)
        security_status_container = eveui.ContainerAutoSize(parent=location_cotainer, align=eveui.Align.to_left, alignMode=eveui.Align.center_left)
        self._security_status_label = carbonui.TextDetail(name='securityStatus', parent=security_status_container, align=eveui.Align.center_left, text=str(security_status), padding=4)
        self._frame = eveui.Frame(bgParent=security_status_container, color=security_status_color, opacity=0.5, frameConst=uiconst.FRAME_FILLED_CORNER1)
        eveui.Frame(bgParent=self, color=(0, 0, 0), opacity=0.5, frameConst=uiconst.FRAME_FILLED_CORNER1)

    def OnClick(self, *args):
        sm.GetService('info').ShowInfo(itemID=self._solar_system_id, typeID=invConst.typeSolarSystem)

    def GetMenu(self):
        return sm.GetService('menu').GetMenuFromItemIDTypeID(itemID=self._solar_system_id, typeID=invConst.typeSolarSystem)

    def OnMouseEnter(self, *args):
        super(SolarSystemChip, self).OnMouseEnter(*args)
        eveui.fade(self._hover_fill, end_value=0.3, duration=0.2)

    def OnMouseExit(self, *args):
        super(SolarSystemChip, self).OnMouseExit(*args)
        eveui.fade(self._hover_fill, end_value=0.2, duration=0.2)


class ClosestSolarSystemChip(SolarSystemChip):
    compact_icon = eveicon.location

    def __init__(self, solar_system_id, location_ids, compact = False, *args, **kwargs):
        self._location_ids = location_ids
        super(ClosestSolarSystemChip, self).__init__(solar_system_id=solar_system_id, compact=compact, *args, **kwargs)

    def _update_jumps(self):
        num_locations = len(self._location_ids)
        if self._compact:
            self._jump_label.text = str(num_locations)
        else:
            self._jump_label.text = localization.GetByLabel('UI/Opportunities/NumLocations', num_locations=num_locations)

    def LoadTooltipPanel(self, tooltip_panel, *args):
        tooltip_panel.LoadStandardSpacing()
        tooltip_panel.columns = 1
        for location_id in self._location_ids:
            if idCheckers.IsSolarSystem(location_id):
                text = solar_system_with_security(location_id)
                subtext = None
                icon = eveicon.solar_system
            elif idCheckers.IsConstellation(location_id):
                text = cfg.evelocations.Get(location_id).locationName
                icon = eveicon.constellation
                subtext = localization.GetByLabel('UI/Common/LocationTypes/Constellation')
            elif idCheckers.IsRegion(location_id):
                text = cfg.evelocations.Get(location_id).locationName
                icon = eveicon.region
                subtext = localization.GetByLabel('UI/Common/LocationTypes/Region')
            else:
                continue
            if subtext:
                text = u'<color={}>[{}]</color> {}'.format(TextColor.SECONDARY, subtext, text)
            tooltip_panel.AddSpriteLabel(icon, text, iconSize=16, iconColor=TextColor.NORMAL)
