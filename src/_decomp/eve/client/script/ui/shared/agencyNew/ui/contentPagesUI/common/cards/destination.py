#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\common\cards\destination.py
import math
from carbonui import uiconst, TextBody
from carbonui.primitives.container import Container
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.utilButtons.showInfoButton import ShowInfoButton
from eve.client.script.ui.control.statefulButton import StatefulButton
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece
from eve.client.script.ui.shared.agencyNew.ui import agencyUIConst
from eve.client.script.ui.shared.agencyNew.ui.controls.agencySolarSystemMapIcon import AgencySolarSystemMapIcon
from eve.common.lib.appConst import typeSolarSystem
from localization import GetByLabel

class SetDestinationCard(Container):
    default_width = agencyUIConst.CONTENTCARD_WIDTH
    default_height = agencyUIConst.CONTENTCARD_HEIGHT

    def __init__(self, solar_system_id, *args, **kwargs):
        super(SetDestinationCard, self).__init__(*args, **kwargs)
        self._content_container = None
        self._controller = BaseContentPiece(solarSystemID=solar_system_id, typeID=typeSolarSystem)
        self._construct_layout()

    def _construct_layout(self):
        self._content_container = Container(name='stationContainer', parent=self, align=uiconst.TOALL)
        self._construct_frame()
        self._construct_system_icon()
        self._construct_system_info()

    def _construct_frame(self):
        Sprite(name='corner_top_left', parent=self._content_container, align=uiconst.TOTOP_NOPUSH, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', opacity=agencyUIConst.OPACITY_SLANTS, height=11)
        Sprite(name='corner_bottom_right', parent=self._content_container, align=uiconst.TOBOTTOM_NOPUSH, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/Agency/contentCardTop.png', opacity=agencyUIConst.OPACITY_SLANTS, rotation=math.pi, height=11)
        Frame(name='frame', bgParent=self._content_container, texturePath='res:/UI/Texture/Shared/DarkStyle/panel2Corner_Solid.png', cornerSize=9, color=Color.BLACK, opacity=0.75)

    def _construct_system_icon(self):
        system_icon_container = Container(name='system_icon_container', parent=self._content_container, align=uiconst.TOLEFT, width=76, height=76, left=5)
        AgencySolarSystemMapIcon(name='system_icon', parent=system_icon_container, align=uiconst.TOALL, contentPiece=self._controller)

    def _construct_system_info(self):
        system_info_container = Container(name='system_info_container', parent=self._content_container, padding=(10, 5, 0, 5))
        ShowInfoButton(name='info_button', parent=system_info_container, align=uiconst.TOPRIGHT, typeID=self._controller.typeID, itemID=self._controller.solarSystemID, left=5)
        solar_system_name = self._controller.GetSolarSystemName()
        header_label = TextBody(name='header_label', parent=system_info_container, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text=GetByLabel('UI/Agency/Common/DestinationCardTitle', solar_system_name=solar_system_name), singleline=True)
        header_label.SetRightAlphaFade(fadeEnd=180, maxFadeWidth=10)
        solar_system_text = sm.GetService('infoPanel').GetSolarSystemText(solarSystemID=self._controller.solarSystemID, solarSystemAlt='')
        num_jumps = self._controller.GetJumpsToSelfFromCurrentLocation()
        num_jumps_text = GetByLabel('UI/Common/numberOfJumps', numJumps=num_jumps)
        EveLabelMedium(name='solar_system_label', parent=system_info_container, align=uiconst.TOTOP, state=uiconst.UI_NORMAL, text='%s - %s' % (solar_system_text, num_jumps_text), top=3)
        StatefulButton(name='destination_button', parent=system_info_container, align=uiconst.BOTTOMLEFT, iconAlign=uiconst.TORIGHT, label=self._get_button_label(), func=self._set_destination, controller=self._controller)

    def _get_button_label(self):
        if self._controller.solarSystemID == session.solarsystemid2:
            return GetByLabel('UI/Agency/Common/DestinationCardAlreadyInSystem')
        else:
            return GetByLabel('UI/Commands/SetDestination')

    def _set_destination(self):
        if self._controller.solarSystemID == session.solarsystemid2:
            return
        sm.GetService('starmap').SetWaypoint(destinationID=self._controller.solarSystemID, clearOtherWaypoints=True)
