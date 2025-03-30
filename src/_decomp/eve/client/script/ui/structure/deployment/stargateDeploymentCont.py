#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\deployment\stargateDeploymentCont.py
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.util.bunch import Bunch
import eve.client.script.parklife.states as stateConst
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.shared.stateFlag import GetStateFlagFromData
from eve.client.script.ui.structure.deployment.stargateSystemEntry import StargateDestSystemsEntry
from localization import GetByLabel
from localization.formatters import FormatNumeric
from utillib import KeyVal
import carbonui.const as uiconst
OPT_ALL_SYSTEMS = 1
OPT_WITH_GATES_POINTING_HERE = 2

class StargateDeploymentCont(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        solarSystemName = cfg.evelocations.Get(session.solarsystemid2).name
        options = [(GetByLabel('UI/Structures/Deployment/AllSolarsystems'), OPT_ALL_SYSTEMS), (GetByLabel('UI/Structures/Deployment/SystemsLinkedHere', solarSystemName=solarSystemName), OPT_WITH_GATES_POINTING_HERE)]
        topCont = Container(parent=self, align=uiconst.TOTOP, height=20)
        self.filterCombo = Combo(parent=topCont, align=uiconst.TOLEFT, options=options, callback=self.LoadListFromCombo, width=120)
        self.scroll = Scroll(parent=self, padding=const.defaultPadding, id='StargateDeploymentCont')
        self.scroll.multiSelect = False
        self.scroll.GetStringFromNode = self.GetStringsFromNode

    def LoadListFromCombo(self, *args):
        self._LoadList()

    def LoadListAndSetFilter(self, firstTime):
        if firstTime:
            jumpBridgesInRangeBySolarSystemID = sm.GetService('structureDeployment').GetNearbyJumpBridges()
            aBridgePointsToSystem = any((x.alignedToCurrentSystem for x in jumpBridgesInRangeBySolarSystemID.itervalues()))
            if aBridgePointsToSystem:
                self.filterCombo.SetValue(OPT_WITH_GATES_POINTING_HERE)
            else:
                self.filterCombo.SetValue(OPT_ALL_SYSTEMS)
        self._LoadList()

    def _LoadList(self):
        filterCombValue = self.filterCombo.GetValue()
        structureDeploymentSvc = sm.GetService('structureDeployment')
        destinationSolarsystemID = structureDeploymentSvc.GetDestinationSolarsystemID()
        nearbySolarSystemsDict = structureDeploymentSvc.GetSystemsInLightYearDistanceForJumpGateDict(session.solarsystemid)
        cfg.evelocations.Prime(nearbySolarSystemsDict.keys())
        jumpBridgesInRangeBySolarSystemID = sm.GetService('structureDeployment').GetNearbyJumpBridges()
        pathFinderSvc = sm.GetService('clientPathfinderService')
        facwarSvc = sm.GetService('facwar')
        stateSvc = sm.GetService('stateSvc')
        scrollList = []
        for eachSolarSystemID, dist in nearbySolarSystemsDict.iteritems():
            jumpGate = jumpBridgesInRangeBySolarSystemID.get(eachSolarSystemID, None)
            systemName = cfg.evelocations.Get(eachSolarSystemID).name
            distText = GetByLabel('UI/CapitalNavigation/CapitalNavigationWindow/DistanceToSystem', lightYearDistance=dist)
            numJumps = pathFinderSvc.GetJumpCountFromCurrent(eachSolarSystemID)
            jumpsText = FormatNumeric(numJumps, decimalPlaces=0)
            isSelected = eachSolarSystemID == destinationSolarsystemID
            alignedToCurrentSystem = bool(jumpGate and jumpGate.alignedToCurrentSystem)
            if filterCombValue == OPT_WITH_GATES_POINTING_HERE and not alignedToCurrentSystem:
                continue
            if jumpGate:
                structureName = jumpGate.structureName
                corpID = jumpGate.ownerID
            else:
                structureName = ''
                corpID = None
            if corpID:
                warFactionID = facwarSvc.GetCorporationWarFactionID(corpID)
                corpFlag = GetStateFlagFromData(KeyVal(ownerID=corpID, corpID=corpID, warFactionID=warFactionID))
                corpFlagInfo = stateSvc.GetStatePropsColorAndBlink(corpFlag)
            else:
                corpFlag = None
                corpFlagInfo = None
            node = Bunch(solarSystemID=eachSolarSystemID, systemName=systemName, decoClass=StargateDestSystemsEntry, jumpText=jumpsText, distText=distText, charIndex=systemName, OnClick=self.OnEntrySelected, isSelected=isSelected, corpFlagInfo=corpFlagInfo, jumpGate=jumpGate)
            flagSortNumber = GetFlagSortNumber(corpFlag)
            node.sortValues = [systemName,
             dist,
             numJumps,
             (flagSortNumber, structureName.lower()),
             (-alignedToCurrentSystem, -bool(jumpGate), flagSortNumber)]
            scrollList.append(node)

        noContentHint = GetByLabel('UI/Structures/Deployment/NoSolarsystemsFound')
        self.scroll.Load(contentList=scrollList, headers=StargateDestSystemsEntry.GetHeaders(), noContentHint=noContentHint)

    def OnEntrySelected(self, entry):
        selectedNodes = self.scroll.GetSelected()
        if not selectedNodes:
            solarSystemID = None
        else:
            solarSystemID = selectedNodes[0].solarSystemID
        structureDeployment = sm.GetService('structureDeployment')
        structureDeployment.SetDestinationSolarsystemID(solarSystemID)

    def GetStringsFromNode(self, node):
        return StargateDestSystemsEntry.GetStringFromNode(node)


def GetFlagSortNumber(corpFlag):
    if corpFlag in flagOrder:
        return -flagOrder.index(corpFlag)
    return corpFlag


flagOrder = [stateConst.flagStandingHorrible,
 stateConst.flagStandingBad,
 stateConst.flagAlliesAtWar,
 stateConst.flagAtWarMilitia,
 stateConst.flagNoStanding,
 stateConst.flagStandingNeutral,
 stateConst.flagAlliesAtWar,
 stateConst.flagSameMilitia,
 stateConst.flagStandingGood,
 stateConst.flagStandingHigh,
 stateConst.flagSameAlliance,
 stateConst.flagSamePlayerCorp]
