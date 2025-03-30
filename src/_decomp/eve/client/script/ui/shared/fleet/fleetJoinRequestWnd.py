#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fleet\fleetJoinRequestWnd.py
import localization
from carbonui import const as uiconst
from carbonui.control.button import Button
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control import eveScroll
from eve.client.script.ui.control.entries.util import GetFromClass
from carbonui.control.window import Window
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.shared.fleet.entries import JoinRequestField
MIN_WINDOW_WIDTH = 310

def get_character_name_width(charID):
    return EveLabelMedium(text=localization.GetByLabel('UI/Common/CharacterNameLabel', charID=charID)).width


class FleetJoinRequestWindow(Window):
    default_windowID = 'FleetJoinRequestWindow'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fleet.png'
    default_captionLabelPath = 'UI/Fleet/FleetWindow/JoinRequests'
    default_iconNum = 'res:/ui/Texture/WindowIcons/fleet.png'

    def ApplyAttributes(self, attributes):
        super(FleetJoinRequestWindow, self).ApplyAttributes(attributes)
        self.join_request = EveLabelMedium(text=localization.GetByLabel('UI/Fleet/FleetWindow/JoinRequestsHelp'), parent=self.content, align=uiconst.TOTOP, padBottom=uiconst.defaultPadding)
        self.sr.scroll = eveScroll.Scroll(parent=self.content)
        self.sr.scroll.multiSelect = 0
        self.LoadJoinRequests()

    def LoadJoinRequests(self):
        scrolllist = []
        fleet_svc = sm.GetService('fleet')
        for joinRequest in fleet_svc.GetJoinRequests().itervalues():
            if joinRequest is None:
                continue
            name = localization.GetByLabel('UI/Common/CharacterNameLabel', charID=joinRequest.charID)
            scrolllist.append((name, GetFromClass(JoinRequestField, {'label': name,
              'height': Button.default_height,
              'props': None,
              'checked': False,
              'charID': joinRequest.charID,
              'retval': None,
              'hint': None})))

        join_requests = filter(None, fleet_svc.GetJoinRequests().values())
        character_name_widths = [ get_character_name_width(request.charID) for request in join_requests ]
        max_text_width = max(character_name_widths or [0])
        window_min_width = max(MIN_WINDOW_WIDTH, max_text_width + Button.default_width * 2)
        self.SetMinSize(size=(window_min_width, 145), refresh=True)
        scrolllist = SortListOfTuples(scrolllist)
        self.sr.scroll.Load(contentList=scrolllist)
