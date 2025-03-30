#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\entries.py
import localization
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveIcon
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.shared.maps import maputils
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from eveservices.menu import GetMenuService

class BracketSelectorEntry(Generic):
    __guid__ = 'listentry.BracketSelectorEntry'
    __update_on_reload__ = 1

    def Startup(self, *args):
        Generic.Startup(self, *args)
        props = {'parent': self,
         'align': uiconst.CENTERRIGHT,
         'idx': 0}
        pos = (18, 0, 0, 0)
        eye = eveIcon.Icon(icon='ui_38_16_110', pos=pos, name='eye', hint=localization.GetByLabel('UI/Map/MapPallet/hintShow'), **props)
        eye.OnClick = self.ToggleVisibility
        self.sr.eyeoff = eveIcon.Icon(icon='ui_38_16_111', pos=pos, **props)
        hint = eveIcon.Icon(icon='ui_38_16_109', name='hint', hint=localization.GetByLabel('UI/Map/MapPallet/hintShowHint'), **props)
        hint.OnClick = self.ToggleBubbleHint
        self.sr.hintoff = eveIcon.Icon(icon='ui_38_16_111', **props)

    def Load(self, node):
        Generic.Load(self, node)
        if node.visible:
            self.sr.eyeoff.state = uiconst.UI_HIDDEN
        else:
            self.sr.eyeoff.state = uiconst.UI_DISABLED
        if node.showhint:
            self.sr.hintoff.state = uiconst.UI_HIDDEN
        else:
            self.sr.hintoff.state = uiconst.UI_DISABLED

    def ToggleVisibility(self, *args):
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        visible = not self.sr.node.visible
        wantedGroups = maputils.GetVisibleSolarsystemBrackets()[:]
        for node in sel:
            node.visible = visible
            if node.groupID not in wantedGroups and visible:
                wantedGroups.append(node.groupID)
            elif node.groupID in wantedGroups and not visible:
                wantedGroups.remove(node.groupID)
            if node.panel:
                node.panel.Load(node)

        settings.user.ui.Set('groupsInSolarsystemMap', wantedGroups)
        sm.ScatterEvent('OnSolarsystemMapSettingsChange', 'brackets')

    def ToggleBubbleHint(self, *args):
        sel = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        showhint = not self.sr.node.showhint
        wantedHints = maputils.GetHintsOnSolarsystemBrackets()[:]
        for node in sel:
            node.showhint = showhint
            if node.groupID not in wantedHints and showhint:
                wantedHints.append(node.groupID)
            elif node.groupID in wantedHints and not showhint:
                wantedHints.remove(node.groupID)
            if node.panel:
                node.panel.Load(node)

        settings.user.ui.Set('hintsInSolarsystemMap', wantedHints)
        sm.ScatterEvent('OnSolarsystemMapSettingsChange', 'brackets')


class LegendEntry(Generic):
    __guid__ = 'listentry.LegendEntry'

    def Startup(self, *args):
        Generic.Startup(self, args)
        Line(parent=self, align=uiconst.TOBOTTOM)
        self.sr.legendColor = Container(name='legendColor', parent=self, align=uiconst.TOPLEFT, pos=(2, 2, 12, 12), idx=0)
        self.sr.colorFill = Fill(parent=self.sr.legendColor)
        Frame(parent=self.sr.legendColor, color=(0.25, 0.25, 0.25), idx=0)

    def Load(self, node):
        Generic.Load(self, node)
        self.sr.label.left = 18
        if not isinstance(node.legend.color, tuple):
            c = (node.legend.color.r,
             node.legend.color.g,
             node.legend.color.b,
             node.legend.color.a)
            node.legend.color.a = 1.0
        else:
            c = node.legend.color
            node.legend.color = (c[0],
             c[1],
             c[2],
             1.0)
        self.sr.colorFill.SetRGBA(*c)
        self.key = node.key
        self.legend = node.legend
        self.sr.label.Update()

    def GetMenu(self):
        m = []
        if self.legend.data is not None:
            m += GetMenuService().GetGMMenu(itemID=self.legend.data)
        if self.legend.data is not None:
            if idCheckers.IsFaction(self.legend.data):
                m += GetMenuService().GetMenuFromItemIDTypeID(self.legend.data, const.typeFaction)
            elif idCheckers.IsRegion(self.legend.data):
                m += GetMenuService().CelestialMenu(self.legend.data)
            else:
                m += GetMenuService().GetMenuFromItemIDTypeID(self.legend.data, const.typeAlliance)
        return m


class LocationSearchItem(Item):
    __guid__ = 'listentry.LocationSearchItem'
    isDragObject = True
