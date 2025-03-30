#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\skyBoxEffectDebugger.py
import logging
import fsdBuiltData.client.skyBoxEffects as data
import geo2
from carbonui import uiconst
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.primitives.container import Container
from carbonui.primitives.line import Line
from eve.client.script.ui.control import eveScroll
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelSmallBold, EveLabelSmall
from carbonui.control.window import Window
from eve.common.lib.appConst import LIGHTYEAR
from eve.common.script.sys.idCheckers import IsKnownSpaceSystem
from evegraphics.skyBoxEffects.skyBoxEffectManager import SkyBoxEffectManager
SOLARSYSTEM_POSITIONS = {}
log = logging.getLogger(__name__)

def GetPositions():
    global SOLARSYSTEM_POSITIONS
    if len(SOLARSYSTEM_POSITIONS) == 0:
        SOLARSYSTEM_POSITIONS = {ssid:(system.center.x, system.center.y, system.center.z) for ssid, system in cfg.mapSystemCache.iteritems() if IsKnownSpaceSystem(ssid)}
    return SOLARSYSTEM_POSITIONS


class SkyBoxEffectDebugger(object):
    __notifyevents__ = ['OnSessionChanged']
    WINDOW_ID = 'SkyBoxEffectDebugger'

    def __init__(self):
        self.name = 'Sky Box Effect Debugger'
        self.windowID = self.WINDOW_ID
        self.overviewContainer = None
        sm.RegisterNotify(self)

    def OnClose(self, *args):
        sm.UnregisterNotify(self)

    def ShowUI(self):
        wnd = Window.ToggleOpenClose(windowID=self.windowID)
        if wnd is None:
            return
        wnd.SetMinSize([400, 250])
        wnd.SetCaption(self.name)
        wnd._OnClose = self.OnClose
        main = wnd.GetMainArea()
        self.reloadButton = Button(name='reload', align=uiconst.TOBOTTOM, parent=main, label='Reload Data', func=self.ReloadData)
        self.overviewContainer = ScrollContainer(name='myScrollCont', parent=main, align=uiconst.TOALL, padding=5)
        self.SetupData()

    def ReloadData(self, *args):
        scene = sm.GetService('sceneManager').GetActiveScene()
        sm.GetService('environment').skyBoxEffectManager.ClearEffects(scene=scene)
        sm.GetService('environment').skyBoxEffectManager.EnterSolarSystem(session.solarsystemid, scene, force_load_effects=True)
        self.SetupData()

    def SetupData(self):
        self.overviewContainer.Flush()
        if not IsKnownSpaceSystem(session.solarsystemid):
            log.error('Trying to see skybox effect in unknown space, not showing you anything...')
            return
        for effect_id in reversed(data.GetSkyBoxEffects().keys()):
            SkyBoxEffectContainer(align=uiconst.TOTOP, parent=self.overviewContainer, effectid=effect_id)

    def OnSessionChanged(self, *args):
        self.SetupData()


class SkyBoxEffectContainer(Container):
    default_height = 200
    default_padding = 30
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.effect_id = attributes.Get('effectid', 0)
        Line(parent=self, align=uiconst.TOBOTTOM, opacity=0.05)
        nearDist = data.GetSkyBoxEffectNearDistInLightYears(self.effect_id)
        farDist = data.GetSkyBoxEffectFarDistInLightYears(self.effect_id)
        sourceSystem = data.GetSkyBoxEffectSourceSolarSystem(self.effect_id)
        if sourceSystem is not None:
            sourceCenter = GetPositions()[sourceSystem]
        else:
            sourceCenter = data.GetSkyBoxEffectWorldPosition(self.effect_id)
        currentCenter = GetPositions()[session.solarsystemid]
        mainContainer = Container(name='mainContainer', parent=self, align=uiconst.TOALL)
        nameContainer = Container(name='nameContainer', parent=mainContainer, align=uiconst.TOTOP, height=30)
        EveCaptionLarge(name='name', parent=nameContainer, align=uiconst.CENTERLEFT, text='%s' % data.GetSkyBoxEffectName(self.effect_id), left=4)
        Button(name='LookAtButton', align=uiconst.CENTERRIGHT, parent=nameContainer, label="Can't Look (in same system)" if sourceSystem == session.solarsystemid2 else 'Look!', func=lambda x: self.LookTowards(sourceCenter), state=uiconst.UI_DISABLED if sourceSystem == session.solarsystemid2 else uiconst.UI_NORMAL)
        distance_from_current = geo2.Vec3DistanceD(currentCenter, sourceCenter) / LIGHTYEAR
        self.CreateInfoContainer(mainContainer, distance_from_current, SkyBoxEffectManager.CalculateScale(distance_from_current, self.effect_id), 'Current')
        self.CreateInfoContainer(mainContainer, nearDist, data.GetSkyBoxEffectNearScale(self.effect_id), 'Near')
        self.CreateInfoContainer(mainContainer, farDist, data.GetSkyBoxEffectFarScale(self.effect_id), 'Far')
        tableContainer = Container(name='scrollContainer', parent=mainContainer, align=uiconst.TOTOP, height=100)
        scroll = eveScroll.Scroll(parent=tableContainer, multiSelect=False)
        scroll.sr.id = 'scroller'
        layout = '%s<t>%s<t>%s<t>%s'
        headers = ['System',
         'SystemID',
         'Dist (LY)',
         'Scale']
        content = set()
        distSortedSystems = [ (geo2.Vec3DistanceD(center, sourceCenter) / LIGHTYEAR, ssid) for ssid, center in GetPositions().iteritems() ]
        distSortedSystems.sort(key=lambda x: x[0])
        closestDist, closestSsid = distSortedSystems[0]
        content.add((cfg.evelocations.Get(closestSsid).name,
         closestSsid,
         closestDist,
         SkyBoxEffectManager.CalculateScale(closestDist, self.effect_id)))
        for index, (dist, ssid) in enumerate(distSortedSystems):
            if index == 0:
                continue
            prevdist, prevsystem = distSortedSystems[index - 1]
            if dist >= nearDist > prevdist:
                if index != 1:
                    scale = SkyBoxEffectManager.CalculateScale(prevdist, self.effect_id)
                    content.add((cfg.evelocations.Get(prevsystem).name,
                     prevsystem,
                     prevdist,
                     scale))
                scale = SkyBoxEffectManager.CalculateScale(dist, self.effect_id)
                content.add((cfg.evelocations.Get(ssid).name,
                 ssid,
                 dist,
                 scale))
            elif dist >= farDist > prevdist:
                if index != 1:
                    scale = SkyBoxEffectManager.CalculateScale(prevdist, self.effect_id)
                    content.add((cfg.evelocations.Get(prevsystem).name,
                     prevsystem,
                     prevdist,
                     scale))
                scale = SkyBoxEffectManager.CalculateScale(dist, self.effect_id)
                content.add((cfg.evelocations.Get(ssid).name,
                 ssid,
                 dist,
                 scale))
            if dist > farDist and prevdist > farDist:
                break

        furthestDist, furthestSsid = distSortedSystems[len(distSortedSystems) - 1]
        content.add((cfg.evelocations.Get(furthestSsid).name,
         furthestSsid,
         furthestDist,
         SkyBoxEffectManager.CalculateScale(furthestDist, self.effect_id)))
        contentList = []
        for info in content:
            label = layout % info
            entry = ScrollEntryNode(decoClass=SE_GenericCore, label=label, OnGetMenu=self.RightClickMenuCmd(info[0], info[1]))
            contentList.append(entry)

        scroll.Load(contentList=contentList, headers=headers, fixedEntryHeight=18)

    def RightClickMenuCmd(self, systemName, solarSystemID):
        return lambda x: self.RightClickMenu(systemName, solarSystemID)

    def RightClickMenu(self, systemName, solarSystemID):
        m = [('TR me to %s' % systemName, self.TR, (solarSystemID,))]
        return m

    def TR(self, solarSystemID):
        sm.GetService('slash').SlashCmd('tr me %s' % solarSystemID)

    def CreateInfoContainer(self, parent, dist, scale, label):
        currentProperties = Container(name='currentProperties', parent=parent, align=uiconst.TOTOP, height=20)
        EveLabelSmallBold(name='curr_dist_label', parent=currentProperties, align=uiconst.TOLEFT, text='%s Dist:' % label, left=4)
        EveLabelSmall(name='curr_dist', parent=currentProperties, align=uiconst.TOLEFT, text='%.3fLY' % dist, left=4)
        EveLabelSmall(name='curr_scale', parent=currentProperties, align=uiconst.TORIGHT, text='%.3f' % scale, left=4)
        EveLabelSmallBold(name='curr_scale_label', parent=currentProperties, align=uiconst.TORIGHT, text='%s Scale:' % label, left=4)

    def LookTowards(self, target):
        current = GetPositions()[session.solarsystemid]
        direction = geo2.Vec3SubtractD(current, target)
        direction = (direction[0], direction[1], -direction[2])
        direction = geo2.Vec3Normalize(direction)
        cam = sm.GetService('space').GetCamera()
        newDir = geo2.Vec3Scale(direction, 10000)
        newPos = geo2.Vec3Scale(direction, -10000)
        cam.TransitTo(newDir, newPos)
