#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\maps\browser.py
import localization
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uicore import uicore
from carbonui.util.various_unsorted import FlushList
from eve.client.script.ui.control import eveLabel
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.shared.infoPanels.listSurroundingsBtn import ListSurroundingsBtn
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
from eve.client.script.ui.shared.maps.map2D import Map2D
from eve.common.lib import appConst as const
from eveexceptions import UserError
DRAWLVLREG = 1
DRAWLVLCON = 2
DRAWLVLSOL = 3
DRAWLVLSYS = 4

class MapBrowser(Container):
    __guid__ = 'xtriui.MapBrowser'
    __nonpersistvars__ = []
    __notifyevents__ = ['ProcessSessionChange', 'DoBallsAdded']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        sm.RegisterNotify(self)
        self.ids = [[],
         [],
         [],
         []]
        self.loadingMap = 0

    def ProcessSessionChange(self, isRemote, session, change):
        if 'regionid' in change and change['regionid'][0] == self.ids[1][0]:
            self.LoadIDs([(const.locationUniverse,
              0,
              DRAWLVLREG,
              eve.session.regionid),
             (eve.session.regionid,
              1,
              DRAWLVLCON,
              eve.session.constellationid),
             (eve.session.constellationid,
              2,
              DRAWLVLSOL,
              eve.session.solarsystemid2),
             (eve.session.solarsystemid2,
              3,
              DRAWLVLSYS,
              None)])
        elif 'constellationid' in change and change['constellationid'][0] == self.ids[2][0]:
            self.LoadIDs([(eve.session.regionid,
              1,
              DRAWLVLCON,
              eve.session.constellationid), (eve.session.constellationid,
              2,
              DRAWLVLSOL,
              eve.session.solarsystemid2), (eve.session.solarsystemid2,
              3,
              DRAWLVLSYS,
              None)])
        elif 'solarsystemid' in change and change['solarsystemid'][0] == self.ids[3][0]:
            self.LoadIDs([(eve.session.constellationid,
              2,
              DRAWLVLSOL,
              eve.session.solarsystemid2), (eve.session.solarsystemid2,
              3,
              DRAWLVLSYS,
              None)])

    def Startup(self):
        pass

    def LoadCurrent(self):
        self.LoadIDs([(const.locationUniverse,
          0,
          DRAWLVLREG,
          eve.session.regionid),
         (eve.session.regionid,
          1,
          DRAWLVLCON,
          eve.session.constellationid),
         (eve.session.constellationid,
          2,
          DRAWLVLSOL,
          eve.session.solarsystemid2),
         (eve.session.solarsystemid2,
          3,
          DRAWLVLSYS,
          None)])

    def LoadIDs(self, ids):
        for id, idlevel, drawlevel, selected in ids:
            if self.destroyed:
                return
            if self.ids[idlevel] == [id]:
                if selected and len(self.children) > idlevel:
                    self.children[idlevel].SetSelected([selected])
                continue
            self.GetMap([id], idlevel, drawlevel, selected)

    def Prepare():
        pass

    def GetMap(self, ids, idlevel, drawlevel, selected = None):
        if getattr(self, 'loadingMap', 0):
            return
        self.loadingMap = 1
        FlushList(self.children[idlevel:])
        self.ids[idlevel] = ids
        cfg.evelocations.Prime(ids)
        l, t, absWidth, absHeight = self.GetAbsolute()
        pilmap = Map2D(name='map', align=uiconst.TOTOP, state=uiconst.UI_NORMAL, height=absWidth)
        pilmap.OnSelectItem = self.OnMapSelection
        pilmap.GetParentMenu = self.GetMenu
        pilmapList = []
        basesize = self.absoluteRight - self.absoluteLeft
        if drawlevel == DRAWLVLSYS:
            pilmap.width = pilmap.height = basesize
            pilmap.left = pilmap.top = (pilmap.width - basesize) / 2
            pilmap.align = uiconst.RELATIVE
            pilmap.dragAllowed = 1
            mapparent = Container(name='mapparent', align=uiconst.TOTOP, lockAspect=1, parent=self, clipChildren=1, height=absWidth)
            LineThemeColored(parent=mapparent, align=uiconst.TOBOTTOM)
            pilmapList = mapparent.children
            self.SetLoadExternalPointer(mapparent, self.ids[idlevel][0])
            addstuff = mapparent
        else:
            LineThemeColored(parent=pilmap.overlays, align=uiconst.TOBOTTOM)
            pilmapList = self.children
            self.SetLoadExternalPointer(pilmap, self.ids[idlevel][0])
            addstuff = pilmap.overlays
        pilmap.Draw(ids, idlevel, drawlevel, basesize)
        uicore.animations.FadeIn(pilmap, duration=0.3)
        pilmapList.append(pilmap)
        listicon = ListSurroundingsBtn(parent=addstuff, align=uiconst.TOPLEFT, state=uiconst.UI_NORMAL, pos=(0, 3, 16, 16), idx=0, showIcon=True)
        locConsts = {0: {const.typeUniverse: ''},
         1: {const.typeRegion: localization.GetByLabel('UI/Common/LocationTypes/Region')},
         2: {const.typeConstellation: localization.GetByLabel('UI/Common/LocationTypes/Constellation')},
         3: {const.typeSolarSystem: localization.GetByLabel('UI/Common/LocationTypes/SolarSystem')}}
        levelName = locConsts.get(idlevel, '').values()[0]
        levelID = locConsts.get(idlevel, '').keys()[0]
        for id in ids:
            if levelID != const.typeUniverse:
                locName = cfg.evelocations.Get(id).name

        hintStr = ''
        buttonStr = ''
        if levelID == const.typeUniverse:
            buttonStr = localization.GetByLabel('UI/Common/LocationTypes/Universe')
            hintStr = localization.GetByLabel('UI/Map/MapBrowser/ListRegions')
        elif levelID == const.typeRegion:
            buttonStr = localization.GetByLabel('UI/Map/MapBrowser/NameRegion', name=locName)
            hintStr = localization.GetByLabel('UI/Map/MapBrowser/ListConstellations', name=locName)
        elif levelID == const.typeConstellation:
            buttonStr = localization.GetByLabel('UI/Map/MapBrowser/NameConstellation', name=locName)
            hintStr = localization.GetByLabel('UI/Map/MapBrowser/ListSolarSystems', name=locName)
        elif levelID == const.typeSolarSystem:
            buttonStr = localization.GetByLabel('UI/Map/MapBrowser/NameSolarSystem', name=locName)
            hintStr = localization.GetByLabel('UI/Map/MapBrowser/ListCelestials', name=locName)
        listbtn = eveLabel.EveLabelMedium(text=buttonStr, parent=addstuff, left=listicon.left + listicon.width + 4, top=5, color=(1.0, 1.0, 1.0, 0.75), idx=0, state=uiconst.UI_NORMAL)
        listbtn.expandOnLeft = True
        listbtn.GetMenu = listicon.GetMenu
        for id in ids:
            if id != const.typeUniverse:
                listicon.sr.typeID = listbtn.sr.typeID = levelID
                listicon.sr.itemID = listbtn.sr.itemID = id

        listbtn.sr.hint = hintStr
        if self.destroyed:
            return
        if drawlevel == DRAWLVLSYS:
            listbtn.sr.groupByType = listicon.sr.groupByType = 1
            listbtn.sr.mapitems = listicon.sr.mapitems = pilmap.mapitems
        elif drawlevel in (DRAWLVLCON, DRAWLVLSOL):
            listbtn.sr.mapitems = listicon.sr.mapitems = pilmap.mapitems[1:]
        else:
            listbtn.sr.mapitems = listicon.sr.mapitems = pilmap.mapitems
        listbtn.solarsystemid = listicon.solarsystemid = ids[0]
        if selected:
            pilmap.SetSelected([selected])
        self.Refresh()
        self.loadingMap = 0

    def GetMenu(self):
        return []

    def ShowOnMap(self, itemID, *args):
        if itemID >= const.mapWormholeRegionMin and itemID <= const.mapWormholeRegionMax or itemID >= const.mapWormholeConstellationMin and itemID <= const.mapWormholeConstellationMax or itemID >= const.mapWormholeSystemMin and itemID <= const.mapWormholeSystemMax:
            raise UserError('MapShowWormholeSpaceInfo', {'char': eve.session.charid})
        if eve.session.stationid:
            sm.GetService('station').CleanUp()
        OpenMap(interestID=itemID)

    def SetLoadExternalPointer(self, where, id, func = None, args = None, hint = None):
        pointer = Sprite(parent=where, name='pointer', align=uiconst.BOTTOMLEFT, pos=(2, 2, 16, 16), texturePath='res:/UI/Texture/Shared/arrowLeft.png', color=(1.0, 1.0, 1.0, 0.5))
        pointer.hint = hint if hint is not None else localization.GetByLabel('UI/Map/MapBrowser/ShowInWorldMap')
        pointer.OnClick = (self.ShowOnMap, id)

    def OnMapSelection(self, themap, itemID):
        if themap.drawlevel == DRAWLVLSYS:
            return
        sm.GetService('loading').Cycle('Loading map')
        mapidx = self.children.index(themap)
        ids = [itemID]
        idlevel = mapidx + 1
        drawlevel = mapidx + 2
        shift = uicore.uilib.Key(uiconst.VK_SHIFT)
        if drawlevel > DRAWLVLSYS:
            sm.GetService('loading').StopCycle()
            return
        if drawlevel == DRAWLVLSYS:
            if shift:
                uthread.new(eve.Message, 'CustomInfo', {'info': localization.GetByLabel('UI/Map/MapBrowser/CannotShiftSelect')})
        elif shift and len(self.children) > idlevel:
            currentids = self.children[idlevel].ids
            ids += currentids
            if itemID in currentids:
                while itemID in ids:
                    ids.remove(itemID)

        if not len(ids):
            return
        themap.SetSelected(ids)
        if mapidx < 3:
            uthread.new(self.GetMap, ids, idlevel, drawlevel)
        sm.GetService('loading').StopCycle()

    def Refresh(self, update = 0):
        for each in self.children:
            if hasattr(each, 'RefreshSize'):
                each.RefreshSize()
            if hasattr(each, 'RefreshOverlays'):
                each.RefreshOverlays()

    def SetTempAngle(self, angle):
        if len(self.children) == 4 and len(self.children[-1].children):
            if hasattr(self.children[-1].children[-1], 'SetTempAngle'):
                self.children[-1].children[-1].SetTempAngle(angle)

    def DoBallsAdded(self, *args, **kw):
        import stackless
        import blue
        t = stackless.getcurrent()
        timer = t.PushTimer(blue.pyos.taskletTimer.GetCurrent() + '::mapBrowser')
        try:
            return self.DoBallsAdded_(*args, **kw)
        finally:
            t.PopTimer(timer)

    def DoBallsAdded_(self, lst):

        def PassEventToChild(childItem):
            if hasattr(childItem, 'CheckMyLocation'):
                childItem.CheckMyLocation()
            if hasattr(childItem, 'CheckDestination'):
                childItem.CheckDestination()

        for ball, slimItem in lst:
            if slimItem.itemID == eve.session.shipid:
                for childMap in self.children:
                    PassEventToChild(childMap)
                    if hasattr(childMap, 'children'):
                        for grandchildItem in childMap.children:
                            PassEventToChild(grandchildItem)

                break
