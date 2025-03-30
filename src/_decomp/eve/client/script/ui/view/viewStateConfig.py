#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\view\viewStateConfig.py
import logging
from eve.client.script.ui.inflight.shipHud.shipUI import ShipUI
from eve.client.script.ui.services.viewStateSvc import ViewType
from eve.client.script.ui.shared.careerPortal.careerPortalView import CareerPortalView
from eve.client.script.ui.shared.sidePanelsLayer import SidePanels
from eve.client.script.ui.skillPlan.skillPlanView import SkillPlanView
from eve.client.script.ui.skillTree.skillTreeView import SkillTreeView
from eve.client.script.ui.view.aurumstore.aurumStoreView import AurumStoreView
from eve.client.script.ui.view.characterCustomizationView import CharacterCustomizationView
from eve.client.script.ui.view.characterSelectorView import CharacterSelectorView
from eve.client.script.ui.view.hangarView import HangarView
from eve.client.script.ui.view.loginView import LoginView
from eve.client.script.ui.view.paintToolView import PaintToolView
from eve.client.script.ui.view.planetView import PlanetView
from eve.client.script.ui.view.shipSKINRView import ShipSKINRView
from eve.client.script.ui.view.shipTreeView import ShipTreeView
from eve.client.script.ui.view.spaceToSpaceTransition import SpaceToSpaceTransition
from eve.client.script.ui.view.spaceView import SpaceView
from eve.client.script.ui.view.starMapView import StarMapView
from eve.client.script.ui.view.starMapViewNew import StarMapViewNew
from eve.client.script.ui.view.structureView import StructureView
from eve.client.script.ui.view.systemMapView import SystemMapView
from eve.client.script.ui.view.systemMapViewNew import SystemMapViewNew
from eve.client.script.ui.view.transitions import FadeToBlackTransition, SpaceToStationTransition, FadeToBlackLiteTransition, SpaceToStructureTransition, StationToSpaceTransition, CharSelectCreateToSpaceTransition, ToHangarTransition, HangarToHangarTransition, ToCharCreationTransition, ToStructureFromCharCreationTransition, EmptyTransition
from eve.client.script.ui.view.viewStateConst import ViewState, ViewOverlay
logger = logging.getLogger(__name__)
VIEWS_PRIMARY_APPLICATION = (ViewState.Space, ViewState.Hangar, ViewState.Structure)
DOCKABLE_PANEL_VIEWS = (ViewState.ShipTree, ViewState.StarMapNew, ViewState.SystemMapNew)
VIEWS_SECONDARY = DOCKABLE_PANEL_VIEWS + (ViewState.StarMap,
 ViewState.SystemMap,
 ViewState.Planet,
 ViewState.SkillPlan,
 ViewState.CareerPortal,
 ViewState.VirtualGoodsStore,
 ViewState.SkillTree,
 ViewState.PaintTool,
 ViewState.ShipSKINR)

def SetupViewStates(viewSvc, rootViewLayer):
    logger.debug('Configuring view states')
    logger.debug('Initializing view state service')
    viewSvc.Initialize(rootViewLayer)
    AddPrimaryViews(viewSvc)
    AddSecondaryViews(viewSvc)
    AddDynamicViews(viewSvc)
    AddTransitions(viewSvc)
    AddOverlays(viewSvc)
    logger.debug('Done configuring view states')


def AddPrimaryViews(viewSvc):
    logger.debug('Adding primary views')
    viewSvc.AddView(ViewState.Login, LoginView())
    viewSvc.AddView(ViewState.CharacterSelector, CharacterSelectorView())
    viewSvc.AddView(ViewState.Space, SpaceView())
    viewSvc.AddView(ViewState.Hangar, HangarView())
    viewSvc.AddView(ViewState.Structure, StructureView())


def AddSecondaryViews(viewSvc):
    logger.debug('Adding secondary views')
    viewSvc.AddView(ViewState.StarMap, StarMapView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.SystemMap, SystemMapView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.StarMapNew, StarMapViewNew(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.SystemMapNew, SystemMapViewNew(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.Planet, PlanetView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.ShipTree, ShipTreeView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.VirtualGoodsStore, AurumStoreView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.SkillPlan, SkillPlanView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.SkillTree, SkillTreeView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.CareerPortal, CareerPortalView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.PaintTool, PaintToolView(), viewType=ViewType.Secondary)
    viewSvc.AddView(ViewState.ShipSKINR, ShipSKINRView(), viewType=ViewType.Secondary)


def AddDynamicViews(viewSvc):
    logger.debug('Adding dynamic views')
    viewSvc.AddView(ViewState.CharacterCreation, CharacterCustomizationView(), viewType=ViewType.Dynamic)


def AddTransitions(viewSvc):
    logger.debug('Adding state transitions')
    AddLoginTransitions(viewSvc)
    viewSvc.AddTransitions(fromNames=VIEWS_PRIMARY_APPLICATION, toNames=VIEWS_PRIMARY_APPLICATION, transition=FadeToBlackLiteTransition(fadeTimeMS=100))
    viewSvc.AddTransitions(fromNames=VIEWS_PRIMARY_APPLICATION + VIEWS_SECONDARY, toNames=VIEWS_SECONDARY, transition=EmptyTransition())
    viewSvc.AddTransitions(fromNames=VIEWS_SECONDARY, toNames=VIEWS_PRIMARY_APPLICATION + VIEWS_SECONDARY, transition=EmptyTransition())
    viewSvc.AddTransition(ViewState.Space, ViewState.Space, SpaceToSpaceTransition())
    viewSvc.AddTransition(ViewState.StarMap, ViewState.StarMap)
    viewSvc.AddTransition(ViewState.Space, ViewState.Hangar, SpaceToStationTransition())
    viewSvc.AddTransition(ViewState.Hangar, ViewState.Space, StationToSpaceTransition(fadeTimeMS=500, fadeOutTimeMS=1000))
    AddStructureTransitions(viewSvc)
    AddNESStoreTransitions(viewSvc)
    AddHangarTransitions(viewSvc)
    AddLogOutTransitions(viewSvc)


def AddLoginTransitions(viewSvc):
    viewSvc.AddTransition(None, ViewState.Login)
    viewSvc.AddTransitions((ViewState.Login, None), (ViewState.CharacterSelector, ViewState.CharacterCreation), FadeToBlackTransition(fadeTimeMS=250))
    viewSvc.AddTransitions((ViewState.CharacterSelector,), (ViewState.CharacterCreation, ViewState.VirtualGoodsStore, ViewState.Structure), FadeToBlackTransition(fadeTimeMS=250))
    viewSvc.AddTransitions((ViewState.CharacterSelector, ViewState.CharacterCreation), (ViewState.Space,), CharSelectCreateToSpaceTransition())
    viewSvc.AddTransitions((ViewState.CharacterCreation, ViewState.CharacterSelector), (ViewState.Hangar,), ToHangarTransition(fadeTimeMS=250, allowReopen=False))
    viewSvc.AddTransition(ViewState.CharacterCreation, ViewState.CharacterSelector, FadeToBlackTransition(fadeTimeMS=250, allowReopen=False))


def AddLogOutTransitions(viewSvc):
    viewSvc.AddTransitions(fromNames=VIEWS_PRIMARY_APPLICATION + VIEWS_SECONDARY, toNames=(ViewState.CharacterSelector,), transition=FadeToBlackTransition(fadeTimeMS=1000))


def AddHangarTransitions(viewSvc):
    viewSvc.AddTransition(ViewState.Hangar, ViewState.Hangar, HangarToHangarTransition(fadeTimeMS=500))
    viewSvc.AddTransitions(fromNames=(ViewState.Hangar,) + VIEWS_SECONDARY, toNames=(ViewState.CharacterCreation,), transition=FadeToBlackTransition(fadeTimeMS=200))


def AddNESStoreTransitions(viewSvc):
    viewsToAndFrom = VIEWS_SECONDARY + VIEWS_PRIMARY_APPLICATION + (ViewState.CharacterSelector, ViewState.CharacterCreation)
    viewSvc.AddTransitions((ViewState.VirtualGoodsStore,), viewsToAndFrom, FadeToBlackTransition(fadeTimeMS=250))
    viewSvc.AddTransitions(viewsToAndFrom, (ViewState.VirtualGoodsStore,), FadeToBlackTransition(fadeTimeMS=250))


def AddStructureTransitions(viewSvc):
    viewSvc.AddTransition(ViewState.Structure, ViewState.Space)
    viewSvc.AddTransition(ViewState.Space, ViewState.Structure, SpaceToStructureTransition())
    viewSvc.AddTransition(ViewState.Structure, ViewState.Hangar, FadeToBlackTransition(fadeTimeMS=500))
    viewSvc.AddTransition(ViewState.Hangar, ViewState.Structure, FadeToBlackTransition(fadeTimeMS=500))
    viewSvc.AddTransitions(fromNames=VIEWS_SECONDARY, toNames=(ViewState.CharacterCreation,), transition=ToCharCreationTransition(fadeTimeMS=500))
    viewSvc.AddTransition(ViewState.CharacterCreation, ViewState.Structure, ToStructureFromCharCreationTransition(fadeTimeMS=500))


def AddOverlays(viewSvc):
    logger.debug('Adding view state controlled overlays')
    viewSvc.AddOverlay(ViewOverlay.Target, None)
    viewSvc.AddOverlay(ViewOverlay.ShipUI, ShipUI)
    viewSvc.AddOverlay(ViewOverlay.SidePanels, SidePanels)
