#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\squadrons\squadronMenu.py
from collections import defaultdict
from eve.common.script.mgt.fighterConst import TUBE_STATE_EMPTY
from eve.common.script.sys.eveCfg import IsDocked
from eveservices.menu import GetMenuService
from fighters import SquadronIsSupport, SquadronIsLight, SquadronIsHeavy
from localization import GetByLabel
from menu import MenuLabel
from carbonui.control.contextMenu.menuData import MenuData

def GetSquadronMenu(cont):
    ship = sm.GetService('godma').GetItem(session.shipid)
    if ship is None:
        return []
    tubeStatus = cont.shipFighterState.GetTubeStatus(cont.tubeFlagID)
    if tubeStatus.statusID == TUBE_STATE_EMPTY:
        return GetSquadronMenuForEmptyTube(cont)
    m = MenuData()
    fighterInTube = cont.shipFighterState.GetFightersInTube(cont.tubeFlagID)
    if fighterInTube is not None:
        if not IsDocked():
            m.AddEntry(MenuLabel('UI/Inventory/Fighters/LaunchToSpace'), cont.LaunchFightersFromTube)
        m.AddEntry(MenuLabel('UI/Inventory/Fighters/UnloadFromLaunchTube'), cont.UnloadTubeToFighterBay)
        m += GetMenuService().CelestialMenu(fighterInTube.itemID, typeID=fighterInTube.typeID)
    fighterInSpace = cont.shipFighterState.GetFightersInSpace(cont.tubeFlagID)
    if fighterInSpace is not None:
        m.AddEntry(MenuLabel('UI/Inventory/Fighters/RecallToLaunchTube'), cont.RecallFighterToTube)
        m.AddEntry(MenuLabel('UI/Drones/ReturnDroneAndOrbit'), cont.ReturnAndOrbit)
        m.AddEntry(MenuLabel('UI/Fighters/AbandonFighter'), cont.AbandonFighter)
        m += GetMenuService().CelestialMenu(fighterInSpace.itemID, typeID=fighterInSpace.typeID)
    return m


def GetSquadronMenuForEmptyTube(cont):
    HEAVY = 0
    LIGHT = 1
    SUPPORT = 2
    OTHER = 3
    fightersInBay = sm.GetService('invCache').GetInventoryFromId(session.shipid).ListFighterBay()
    optionsByClass = defaultdict(list)
    for fighter in fightersInBay:
        typeID = fighter.typeID
        if SquadronIsHeavy(typeID):
            fighterClass = HEAVY
        elif SquadronIsLight(typeID):
            fighterClass = LIGHT
        elif SquadronIsSupport(typeID):
            fighterClass = SUPPORT
        else:
            fighterClass = OTHER
        fighterLabel = GetByLabel('UI/Inflight/Drone/DroneBayEntryWithStacksize', drone=fighter.typeID, stacksize=fighter.stacksize)
        optionsByClass[fighterClass].append((fighterLabel, fighter.itemID))

    m = MenuData()
    for fighterClass in (HEAVY,
     LIGHT,
     SUPPORT,
     OTHER):
        options = optionsByClass.get(fighterClass, [])
        if not options:
            continue
        sortedOptions = sorted(options, key=lambda x: x[0])
        for fighter in sortedOptions:
            fighterName, fighterID = fighter
            m.AddEntry(fighterName, lambda fID = fighterID: cont.LoadFighterToTube(fID))

        m.AddSeparator()

    return m
