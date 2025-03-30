#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\fwwarzone\client\dashboard\shipCasterVisualization.py
from collections import namedtuple
import eveformat
from carbonui import uiconst, TextColor
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveLabel import EveLabelLarge
from eve.client.script.ui.skillPlan.skillPlanInfoIcon import SkillPlanInfoIcon
from evelink import Link
from localization import GetByLabel

class _ShipCasterVisualization(Container):
    default_width = 309
    default_height = 99

    def ApplyAttributes(self, attributes):
        super(_ShipCasterVisualization, self).ApplyAttributes(attributes)
        self.factionID = attributes.get('factionID')
        self.ConstructLayout()

    def ConstructSolarSystemMenuFunction(self, solarSystemID):

        def fun(*args):
            return sm.GetService('menu').CelestialMenu(solarSystemID)

        return fun

    def ConstructShipCasterNotBuiltYetView(self, factionID, hqSystemId):
        shipCasterVisCont = Container(name='shipCasterVisCont', parent=self, align=uiconst.TOTOP, top=6, height=99)
        gateSystemNameCont = ContainerAutoSize(parent=shipCasterVisCont, name='gateSystemNameCont', align=uiconst.TOLEFT)
        casterSystem = EveLabelLarge(parent=gateSystemNameCont, text=cfg.eveowners.Get(hqSystemId).name, align=uiconst.TOLEFT, top=36, color=TextColor.DISABLED, state=uiconst.UI_NORMAL)
        casterSystem.GetDragData = lambda *args: None
        casterSystem.GetMenu = self.ConstructSolarSystemMenuFunction(hqSystemId)
        iconCont = Container(parent=shipCasterVisCont, name='iconCont', align=uiconst.TOLEFT, width=60)
        Sprite(parent=iconCont, texturePath='res:/UI/Texture/classes/frontlines/shipcaster/shipcaster_icon_40.png', align=uiconst.CENTER, color=TextColor.DISABLED, width=40, height=40, state=uiconst.UI_DISABLED)
        landingPadsContainer = Container(name='landingPadsContainer', parent=shipCasterVisCont, align=uiconst.TOLEFT, width=40, left=-15, top=-4)
        textAlignCont = Container(name='textAlignCont', parent=shipCasterVisCont, align=uiconst.TOALL)
        SkillPlanInfoIcon(parent=textAlignCont, align=uiconst.TOPLEFT, hint=GetByLabel('UI/FactionWarfare/frontlinesDashboard/needToConstructShipcasterTooltip', factionName=cfg.eveowners.Get(self.factionID).name), top=38)
        EveLabelLarge(parent=ContainerAutoSize(parent=textAlignCont, align=uiconst.CENTER, width=150, left=15, top=-2), align=uiconst.TOTOP, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/shipcasterUnavailable'))
        LandingPadRow = namedtuple('LandingPadRow', ['left', 'top', 'texturePath'])
        rows = [LandingPadRow(0, 21, 'res:/UI/Texture/classes/frontlines/shipcaster/line_segment_top.png'), LandingPadRow(12, 40, 'res:/UI/Texture/classes/frontlines/shipcaster/line_segment_middle.png'), LandingPadRow(0, 63, 'res:/UI/Texture/classes/frontlines/shipcaster/line_segment_bottom.png')]
        for row in rows:
            Sprite(parent=landingPadsContainer, texturePath=row.texturePath, useSizeFromTexture=True, top=row.top, left=row.left, color=TextColor.DISABLED, state=uiconst.UI_DISABLED)

    def ConstructLayout(self):
        landingPads = sm.GetService('shipcaster').GetFactionLandingPads(self.factionID)
        landingPads = sorted(landingPads, key=lambda pad: pad.isBuilt and not pad.isDisrupted, reverse=True)
        hqSystemId = sm.GetService('fwWarzoneSvc').GetFactionHQSystem(self.factionID)
        factionsWithShipcaster = sm.GetService('shipcaster').GetFactionsWithShipcaster()
        self.Flush()
        if self.factionID not in factionsWithShipcaster:
            self.ConstructShipCasterNotBuiltYetView(self.factionID, hqSystemId)
            return
        shipCasterVisCont = Container(name='shipCasterVisCont', parent=self, align=uiconst.TOTOP, top=6, height=99)
        gateSystemNameCont = ContainerAutoSize(parent=shipCasterVisCont, name='gateSystemNameCont', align=uiconst.TOLEFT)
        systemLink = Link(url='fwSystemLink:{}:{}'.format(self.factionID, hqSystemId), text=cfg.eveowners.Get(hqSystemId).name)
        casterSystem = EveLabelLarge(parent=gateSystemNameCont, text=systemLink, align=uiconst.TOLEFT, top=36, color=TextColor.NORMAL, state=uiconst.UI_NORMAL)
        casterSystem.GetDragData = lambda *args: None
        casterSystem.GetMenu = self.ConstructSolarSystemMenuFunction(hqSystemId)
        iconCont = Container(parent=shipCasterVisCont, name='iconCont', align=uiconst.TOLEFT, width=60)
        Sprite(parent=iconCont, texturePath='res:/UI/Texture/classes/frontlines/shipcaster/shipcaster_icon_40.png', align=uiconst.CENTER, color=TextColor.HIGHLIGHT, width=40, height=40, state=uiconst.UI_DISABLED)
        landingPadsContainer = Container(name='landingPadsContainer', parent=shipCasterVisCont, align=uiconst.TOLEFT, width=60, left=-15, top=-4)
        landingPadSystemsCont = Container(name='landingPadSystemsCont', parent=shipCasterVisCont, align=uiconst.TOLEFT, width=200, left=-62, top=15)
        LandingPadRow = namedtuple('LandingPadRow', ['left',
         'top',
         'texturePath',
         'landingPad'])
        rows = [LandingPadRow(0, 21, 'res:/UI/Texture/classes/frontlines/shipcaster/line_segment_top.png', None if len(landingPads) == 0 else landingPads[0]), LandingPadRow(12, 40, 'res:/UI/Texture/classes/frontlines/shipcaster/line_segment_middle.png', None if len(landingPads) < 2 else landingPads[1]), LandingPadRow(0, 63, 'res:/UI/Texture/classes/frontlines/shipcaster/line_segment_bottom.png', None if len(landingPads) < 3 else landingPads[2])]
        for row in rows:
            sprite = Sprite(parent=landingPadsContainer, texturePath=row.texturePath, useSizeFromTexture=True, top=row.top, left=row.left, color=TextColor.SECONDARY)
            if row.landingPad and row.landingPad.isLinked:
                secStatusText = eveformat.client.hint(hint=GetByLabel('UI/Map/StarMap/SecurityStatus'), text=eveformat.client.solar_system_security_status(row.landingPad.solarSystemID))
                systemName = cfg.evelocations.Get(row.landingPad.solarSystemID).name
                landingPadSystemNameCont = Container(parent=landingPadSystemsCont, height=21, align=uiconst.TOTOP, left=40)
                systemLink = Link(url='fwSystemLink:{}:{}'.format(self.factionID, row.landingPad.solarSystemID), text=u'%s %s' % (systemName, secStatusText))
                text = EveLabelLarge(parent=landingPadSystemNameCont, align=uiconst.TOLEFT, text=systemLink, color=TextColor.SECONDARY, state=uiconst.UI_NORMAL)
                text.GetMenu = self.ConstructSolarSystemMenuFunction(row.landingPad.solarSystemID)
                text.GetDragData = lambda *args: None
                if not row.landingPad.isDisrupted:
                    sprite.color = eveColor.SUCCESS_GREEN
                    text.color = TextColor.NORMAL
            else:
                EveLabelLarge(parent=landingPadSystemsCont, align=uiconst.TOTOP, left=40, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/unlinkedLandingPad'), color=TextColor.SECONDARY)
