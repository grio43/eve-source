#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\entries\universe.py
from carbonui.primitives.sprite import Sprite
from evePathfinder.core import IsUnreachableJumpCount
import utillib
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.util.color import Color
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.header import Header
from eve.client.script.ui.control.entries.label_text import LabelTextTop
from eve.client.script.ui.control.entries.text import Text
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.shared.maps import maputils
from localization import GetByLabel
from structures import UPKEEP_STATE_ABANDONED, UPKEEP_STATE_LOW_POWER

class SolarSystem(Generic):
    __params__ = ['label', 'solarSystemID']
    isDragObject = True

    def Startup(self, *args):
        Generic.Startup(self, args)
        self.labelCont = Container(name='labelCont', parent=self, padRight=16)
        self.sr.label.SetParent(self.labelCont)
        self.sr.label.autoFadeSides = 16

    def _GetText(self):
        node = self.sr.node
        security = sm.GetService('map').GetSystemSecurityValue(node.solarSystemID)
        securityModificationIconText = sm.GetService('securitySvc').get_security_modifier_icon_text(node.solarSystemID)
        text = maputils.GetSecurityStatusText(security) + securityModificationIconText
        numJumps = sm.GetService('clientPathfinderService').GetAutopilotJumpCount(session.solarsystemid2, node.solarSystemID)
        if IsUnreachableJumpCount(numJumps):
            numJumps = sm.GetService('clientPathfinderService').GetNoRouteFoundText(node.solarSystemID)
        else:
            numJumps = GetByLabel('UI/Fleet/FleetRegistry/NumberOfJumps', numJumps=numJumps)
        return '%s %s (%s)' % (text, node.label, numJumps)

    def GetDragData(self, *args):
        selectedNodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        retNodes = []
        for node in selectedNodes:
            fakeNode = utillib.KeyVal(__guid__='xtriui.ListSurroundingsBtn', typeID=node.Get('typeID', None), itemID=node.Get('itemID', None), label=node.label)
            retNodes.append(fakeNode)

        return retNodes


class SolarSystemStructure(SolarSystem):

    def Startup(self, *args):
        SolarSystem.Startup(self, args)
        self.sr.icon = ItemIcon(parent=self, pos=(1, 2, 24, 24), align=uiconst.TOPLEFT, idx=0)

    def Load(self, node):
        SolarSystem.Load(self, node)
        self.sr.icon.SetTypeIDandItemID(self.typeID, self.itemID)
        self.sr.icon.left = node.get('sublevel', 0) * 16
        self.sr.label.left = self.height + 4 + node.get('sublevel', 0) * 16

    def GetHeight(self, *args):
        node, width = args
        node.height = 29
        return node.height


class LocationTextEntry(Text):
    __guid__ = 'listentry.LocationTextEntry'
    isDragObject = True
    default_showHilite = True

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes


class LabelLocationTextTop(LabelTextTop):
    __guid__ = 'listentry.LabelLocationTextTop'
    isDragObject = True

    def GetDragData(self, *args):
        nodes = [self.sr.node]
        return nodes


class LocationGroup(ListGroup):
    __guid__ = 'listentry.LocationGroup'
    COLOR_BY_STRUCTURE_POWER_LEVEL = {UPKEEP_STATE_LOW_POWER: eveColor.WARNING_ORANGE,
     UPKEEP_STATE_ABANDONED: eveColor.CHERRY_RED}
    isDragObject = True

    def _ConstructLabel(self):
        self.rightSpriteCont = Container(parent=self, align=uiconst.TORIGHT, pos=(0, 0, 20, 20))
        self.rightSpriteCont.display = False
        self.rightSprite = Sprite(parent=self.rightSpriteCont, align=uiconst.CENTER, pos=(0, 0, 16, 16), opacity=0.75)
        super(LocationGroup, self)._ConstructLabel()

    def GetDragData(self, *args):
        dragDataFunc = self.sr.node.get('GetDragDataFunc', None)
        if dragDataFunc:
            return dragDataFunc(self.sr.node)
        nodes = [self.sr.node]
        return nodes

    def Load(self, node):
        super(LocationGroup, self).Load(node)
        if node.inMyPath:
            self.sr.label.color = Color.YELLOW
        if node.upkeepState in (UPKEEP_STATE_LOW_POWER, UPKEEP_STATE_ABANDONED):
            texturePath = 'res:/UI/Texture/classes/StructureBrowser/bolt.png'
            self.sr.icon.state = uiconst.UI_NORMAL
            self.sr.icon.SetTexturePath(texturePath)
            self.sr.icon.SetSize(9, 9)
            self.sr.label.left = self.sr.icon.left + self.sr.icon.width + 4
            color = self.COLOR_BY_STRUCTURE_POWER_LEVEL.get(node.upkeepState, None)
            if color is not None:
                self.sr.icon.SetRGBA(*color)
            if node.upkeepState == UPKEEP_STATE_LOW_POWER:
                self.sr.icon.hint = GetByLabel('UI/Structures/LowPowerStructureModeHint')
            elif node.upkeepState == UPKEEP_STATE_ABANDONED:
                self.sr.icon.hint = GetByLabel('UI/Structures/AbandonedStructureModeHint')
        rightIconInfo = node.get('rightIconInfo', None)
        if rightIconInfo:
            path, hint = rightIconInfo
            self.rightSprite.SetTexturePath(path)
            self.rightSprite.hint = hint
            self.rightSpriteCont.display = True
        else:
            self.rightSpriteCont.display = False


class SystemNameHeader(Header):

    def Load(self, node):
        super(SystemNameHeader, self).Load(node)
        if node.tabs:
            self.sr.label.tabs = node.tabs
        labelState = uiconst.UI_NORMAL
        if node.labelState:
            labelState = node.labelState
        self.sr.label.state = labelState

    def GetMenu(self):
        if self.sr.get('node', None) and self.sr.node.get('OnGetMenu', None):
            return self.sr.node.OnGetMenu(self)
        return []
