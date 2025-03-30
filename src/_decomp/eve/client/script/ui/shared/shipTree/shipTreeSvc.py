#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeSvc.py
from collections import defaultdict
import evetypes
import geo2
import shipgroup
import uthread
from carbon.common.script.sys.service import Service
from clonegrade.const import CLONE_STATE_ALPHA
from eve.client.script.ui.shared.shipTree import shipTreeConst
from eve.client.script.ui.shared.shipTree.shipTreeConst import NODETYPE_CONNECTOR, NODETYPE_GROUP, NODETYPE_OTHERFACTIONGROUP, NODETYPE_ROOT
from eve.client.script.ui.control.treeData import TreeData
from eve.common.lib import appConst as const
K2 = 1.0 / 2
K3 = 1.0 / 3
K4 = 1.0 / 4
K8 = 1.0 / 8
K12 = 1.0 / 12
K24 = 1.0 / 24

class ShipTree(Service):
    __guid__ = 'svc.shipTree'
    __servicename__ = 'Ship tree service'
    __displayname__ = 'Ship tree service'

    def Run(self, *args):
        self.shipTypeIDsByFactionIDAndGroupID = None
        self.shipGroupIDsByTypeIDs = None
        self._recentlyChangedSkills = None

    def _InitShipTypeIDDict(self):
        self.shipTypeIDsByFactionIDAndGroupID = defaultdict(list)
        for groupID in evetypes.GetGroupIDsByCategory(const.categoryShip):
            if not evetypes.IsGroupPublishedByGroup(groupID):
                continue
            for typeID in evetypes.GetTypeIDsByGroup(groupID):
                try:
                    if evetypes.IsPublished(typeID):
                        key = (evetypes.GetFactionID(typeID), evetypes.GetShipGroupID(typeID))
                        self.shipTypeIDsByFactionIDAndGroupID[key].append(typeID)
                except (KeyError, AttributeError):
                    pass

    def GetShipTypeIDs(self, factionID, isisGroupID):
        if not self.shipTypeIDsByFactionIDAndGroupID:
            self._InitShipTypeIDDict()
        if (factionID, isisGroupID) in self.shipTypeIDsByFactionIDAndGroupID:
            return self.shipTypeIDsByFactionIDAndGroupID[factionID, isisGroupID]
        return []

    def GetShipTypeIDsByGroupID(self, isisGroupID):
        if not self.shipTypeIDsByFactionIDAndGroupID:
            self._InitShipTypeIDDict()
        results = set()
        for factionID, groupID in self.shipTypeIDsByFactionIDAndGroupID:
            if groupID == isisGroupID:
                results.update(self.shipTypeIDsByFactionIDAndGroupID[factionID, isisGroupID])

        return results

    def GetShipGroupID(self, typeID):
        if not self.shipGroupIDsByTypeIDs:
            self._InitShipGroupIDDict()
        return self.shipGroupIDsByTypeIDs.get(typeID, None)

    def _InitShipGroupIDDict(self):
        if not self.shipTypeIDsByFactionIDAndGroupID:
            self._InitShipTypeIDDict()
        self.shipGroupIDsByTypeIDs = {}
        for (_, isisGroupID), typeIDs in self.shipTypeIDsByFactionIDAndGroupID.iteritems():
            for typeID in typeIDs:
                self.shipGroupIDsByTypeIDs[typeID] = isisGroupID

    def GetRootNode(self, factionID):
        if factionID == const.factionORE:
            return self._GetOREData(factionID)
        if factionID == const.factionTriglavian:
            return self._GetTriglavianData(factionID)
        if factionID == const.factionEDENCOM:
            return self._GetEdenComData(factionID)
        if factionID == const.factionCONCORDAssembly:
            return self._GetConcordData(factionID)
        if factionID == const.factionSocietyOfConsciousThought:
            return self._GetSoctData(factionID)
        if factionID in (const.factionGuristasPirates,
         const.factionSanshasNation,
         const.factionTheBloodRaiderCovenant,
         const.factionAngelCartel,
         const.factionSerpentis,
         const.factionSistersOfEVE,
         const.factionMordusLegion,
         const.factionDeathless):
            return self._GetPirateFactionData(factionID)
        return self._GetFactionData(factionID)

    def _GetFactionData(self, factionID):

        def Grp(parent, position, shipGroupID, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, iconsPerRow=iconsPerRow, factionID=factionID, treeID=factionID)

        def Con(parent, position):
            return ConnectorNode(parent=parent, position=position, treeID=factionID)

        root = RootNode(parent=None, position=(0, 0))
        c = Grp(root, (K2, 0), shipgroup.groupRookie)
        cIndustr = Con(c, (0, 3 * K4))
        c = Con(c, (3 * K4, 0))
        c = Con(c, (K12, -K12))
        c = Grp(c, (0, -K2), shipgroup.groupFrigate)
        c2 = Grp(c, (0, -K2), shipgroup.groupNavyFrigate, 4)
        c2 = Con(c2, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupInterceptor, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupAssault, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupCovertOps, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupElectronicAttack, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupLogisticsFrigates, 6)
        c = Grp(c, (5 * K4, 0), shipgroup.groupDestroyer)
        c2 = Grp(c, (0, -K2), shipgroup.groupNavyDestroyers, 4)
        c2 = Con(c2, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupInterdictor)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupCommandDestroyers)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupTacticalDestroyer)
        c = Grp(c, (5 * K4, 0), shipgroup.groupCruiser)
        c2 = Grp(c, (0, -K2), shipgroup.groupNavyCruiser, 4)
        c2 = Con(c2, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupRecon, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupHeavyAssault, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupHeavyInterdictor, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupLogistics, 6)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K2, -K2), shipgroup.groupStrategicCruiser, 6)
        c = Grp(c, (3 * K2, 0), shipgroup.groupBattlecruiser)
        c2 = Grp(c, (0, -K2), shipgroup.groupNavyBattlecruiser)
        c2 = Con(c2, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupCommandship)
        c = Grp(c, (6 * K4, 0), shipgroup.groupBattleship)
        c2 = Grp(c, (0, -K2), shipgroup.groupNavyBattleship)
        c2 = Con(c2, (0, -3 * K8))
        Grp(c2, (K3, -K3), shipgroup.groupBlackOps)
        c2 = Con(c2, (0, -K2))
        Grp(c2, (K3, -K3), shipgroup.groupMarauder)
        c = Con(c, (7 * K4, 0))
        c2 = Grp(c, (K4, 0), shipgroup.groupDreadnought)
        c2 = Grp(c2, (0, -K3 * 2), shipgroup.groupNavyDreadnoughts, 4)
        c2 = Con(c2, (0, -K3 * 1.5))
        Grp(c2, (K3, -K3), shipgroup.groupLancerDreadnought, 4)
        c2 = Con(c, (0, -K3 * 6))
        Grp(c2, (K3, -K3), shipgroup.groupCarrier)
        c2 = Con(c2, (0, -K3 * 2.5))
        Grp(c2, (K3, -K3), shipgroup.groupTitan)
        c = Con(cIndustr, (K12, K12))
        c = Grp(c, (K2, 0), shipgroup.groupShuttle)
        c = Grp(c, (17 * K4, 0), shipgroup.groupIndustrial)
        c2 = Con(c, (0, -K3))
        Grp(c2, (K4, -K4), shipgroup.groupTransport)
        c = Grp(c, (3.0, 0), shipgroup.groupFreighter)
        c2 = Con(c, (0, -K8))
        Grp(c2, (K2, -K2), shipgroup.groupJumpFreighter)
        return root

    def _GetTriglavianData(self, factionID):

        def Grp(parent, position, shipGroupID, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, iconsPerRow=iconsPerRow, factionID=factionID, treeID=factionID)

        def Con(parent, position):
            return ConnectorNode(parent=parent, position=position, treeID=factionID)

        root = RootNode(parent=None, position=(0, 0))
        c = Grp(root, (K2, 0), shipgroup.groupFrigate)
        c2 = Con(c, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupAssault, 6)
        c = Grp(c, (5 * K4, 0), shipgroup.groupDestroyer)
        c2 = Con(c, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupCommandDestroyers)
        c = Grp(c, (5 * K4, 0), shipgroup.groupCruiser)
        c2 = Con(c, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupHeavyAssault)
        c2 = Con(c, (0, -K2))
        c2 = Con(c2, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupLogistics)
        c = Grp(c, (5 * K4, 0), shipgroup.groupBattlecruiser)
        c = Grp(c, (5 * K4, 0), shipgroup.groupBattleship)
        c = Con(c, (5 * K4, 0))
        Grp(c, (K4, 0), shipgroup.groupDreadnought)
        return root

    def _GetEdenComData(self, factionID):

        def Grp(parent, position, shipGroupID, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, iconsPerRow=iconsPerRow, factionID=factionID, treeID=factionID)

        def Con(parent, position):
            return ConnectorNode(parent=parent, position=position, treeID=factionID)

        root = RootNode(parent=None, position=(0, 0))
        c = Con(root, (K2, 0))
        cLeft = Con(c, (0, 0))
        cRight = Con(c, (0, 1.0))
        c = Grp(cLeft, (K2, 0), shipgroup.groupFrigate)
        c = Grp(c, (5 * K4, 0), shipgroup.groupCruiser)
        c = Grp(c, (5 * K4, 0), shipgroup.groupBattleship)
        c = Grp(cRight, (3 * K4, 0), shipgroup.groupIndustrial)
        c2 = Con(c, (0, -K3))
        c3 = Grp(c2, (K4, -K4), shipgroup.groupTransport)
        c = Grp(c, (4 * K2, 0), shipgroup.groupFreighter)
        return root

    def _GetOREData(self, factionID):

        def Grp(parent, position, shipGroupID, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, iconsPerRow=iconsPerRow, factionID=factionID, treeID=factionID)

        def Con(parent, position):
            return ConnectorNode(parent=parent, position=position, treeID=factionID)

        root = RootNode(parent=None, position=(0, 0))
        c = Con(root, (K2, 0))
        cLeft = Con(c, (0, 0))
        cRight = Con(c, (0, 1.0))
        c = Grp(cLeft, (K2, 0), shipgroup.groupMiningFrigate)
        c1 = Con(c, (0, -K2))
        Grp(c1, (K2, -K2), shipgroup.groupExpeditionFrigate)
        c = Grp(c, (1.0, 0), shipgroup.groupMiningBarge)
        c2 = Con(c, (0, -K2))
        Grp(c2, (K2, -K2), shipgroup.groupExhumers)
        c = Grp(cRight, (3 * K2, 0), shipgroup.groupOreIndustrial)
        cDown = Con(c, (0, 1.0))
        c3 = Grp(cDown, (4 * K2, 0), shipgroup.groupFreighter)
        c = Grp(c, (1.0, 0), shipgroup.groupIndustrialCommand)
        c = Grp(c, (1.0, 0), shipgroup.groupCapitalIndustrial)
        return root

    def _GetPirateFactionData(self, factionID):

        def Grp(parent, position, shipGroupID, facID, showLinksTo, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, factionID=facID, showLinksTo=showLinksTo, treeID=factionID, iconsPerRow=iconsPerRow)

        def OtherGrp(parent, position, shipGroupID, facID, showLinksTo, iconsPerRow = 3):
            return OtherFactionGroupNode(parent=parent, position=position, shipGroupID=shipGroupID, factionID=facID, showLinksTo=showLinksTo, treeID=factionID, iconsPerRow=iconsPerRow)

        def Con(parent, position):
            return ConnectorNode(parent=parent, position=position, treeID=factionID)

        factionID1, factionID2 = shipTreeConst.PARENT_FACTIONIDS_BY_FACTIONID[factionID]
        root = c = RootNode(parent=None, position=(0, 0))
        shipTreeSvc = sm.GetService('shipTree')
        i = 0
        for shipGroupID in (shipgroup.groupFrigate,
         shipgroup.groupDestroyer,
         shipgroup.groupCruiser,
         shipgroup.groupBattlecruiser,
         shipgroup.groupBattleship):
            if shipTreeSvc.GetShipTypeIDs(factionID, shipGroupID):
                x = K2 if i == 0 else 3 * K4
                c = Grp(c, (x, 0), shipGroupID, factionID, False)
                top = OtherGrp(root, (K2 + i * x, -0.5), shipGroupID, factionID1, True)
                Grp(top, (0, 0.5), shipGroupID, factionID, False)
                bottom = OtherGrp(root, (K2 + i * x, 0.5), shipGroupID, factionID2, True)
                Grp(bottom, (0, -0.5), shipGroupID, factionID, False)
                i += 1

        i = 0
        for shipGroupID in (shipgroup.groupDreadnought, shipgroup.groupCarrier, shipgroup.groupTitan):
            if shipTreeSvc.GetShipTypeIDs(factionID, shipGroupID):
                h = 0.0 if i == 0 else -0.8
                c = Con(c, (K2, h))
                g = Grp(c, (K2, 0), shipGroupID, factionID, False)
                top = OtherGrp(g, (0, -K2), shipGroupID, factionID1, True)
                Grp(top, (0, K2), shipGroupID, factionID, False)
                bottom = OtherGrp(g, (0, K2), shipGroupID, factionID2, True)
                Grp(bottom, (0, -K2), shipGroupID, factionID, False)
                i += 1

        return root

    def _GetConcordData(self, factionID):

        def Grp(parent, position, shipGroupID, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, iconsPerRow=iconsPerRow, factionID=factionID, treeID=factionID)

        def Con(parent, position):
            return ConnectorNode(parent=parent, position=position, treeID=factionID)

        root = RootNode(parent=None, position=(0, 0))
        c = Grp(root, (K2, 0), shipgroup.groupShuttle)
        c = Grp(c, (2 * K2, 0), shipgroup.groupCovertOps)
        c = Grp(c, (5 * K4, 0), shipgroup.groupRecon)
        c2 = Con(c, (0, -K3))
        Grp(c2, (K3, -K3), shipgroup.groupFlagCruiser)
        c = Grp(c, (5 * K4, 0), shipgroup.groupBlackOps)
        return root

    def _GetSoctData(self, factionID):

        def Grp(parent, position, shipGroupID, iconsPerRow = 3):
            return GroupNode(parent=parent, position=position, shipGroupID=shipGroupID, iconsPerRow=iconsPerRow, factionID=factionID, treeID=factionID)

        root = RootNode(parent=None, position=(0, 0))
        c = Grp(root, (K2, 0), shipgroup.groupShuttle)
        c = Grp(c, (K2 * 2, 0), shipgroup.groupFrigate)
        c = Grp(c, (K2 * 2, 0), shipgroup.groupDestroyer)
        c = Grp(c, (K2 * 2, 0), shipgroup.groupBattlecruiser)
        c = Grp(c, (K2 * 2, 0), shipgroup.groupBattleship)
        return root

    def IsInShipTree(self, typeID):
        hasShipGroup = evetypes.GetShipGroupID(typeID) is not None
        return hasShipGroup and evetypes.GetGroupID(typeID) != const.groupCapsule

    def GetRecentlyChangedSkills(self):
        if self._recentlyChangedSkills is not None:
            return self._recentlyChangedSkills
        uthread.Lock(self, 'GetRecentlyChangedSkills')
        try:
            if self._recentlyChangedSkills is None:
                self._recentlyChangedSkills = sm.GetService('skills').GetRecentlyTrainedSkills()
        finally:
            uthread.UnLock(self, 'GetRecentlyChangedSkills')

        return self._recentlyChangedSkills

    def IsShipMasteryRecentlyIncreased(self, typeID):
        masteryLevel = sm.GetService('certificates').GetCurrCharMasteryLevel(typeID)
        certs = sm.GetService('certificates').GetCertificatesForShipByMasteryLevel(typeID, masteryLevel)
        changed = self.GetRecentlyChangedSkills()
        for cert in certs:
            for skillTypeID, level in changed.iteritems():
                if skillTypeID in cert.skills:
                    currCertSkillLevel = cert.skills[skillTypeID][cert.currentLevel]
                    if currCertSkillLevel > level:
                        return True

        return False

    def IsGroupsRecentlyUnlocked(self, factionID):
        factionData = self.GetRootNode(factionID)
        shipGroups = [ node for node in factionData.GetDescendants().values() if isinstance(node, GroupNode) ]
        for shipGroup in shipGroups:
            if shipGroup.IsRecentlyUnlocked():
                return True

        return False

    def EmptyRecentlyChangedSkillsCache(self):
        self._recentlyChangedSkills = {}

    def FlushRecentlyChangedSkillsCache(self):
        self._recentlyChangedSkills = None


class ShipTreeNodeBase(TreeData):
    __guid__ = 'shipTree.NodeBase'
    nodeType = None

    def __init__(self, treeID = None, showLinksTo = True, iconsPerRow = 3, *args, **kw):
        TreeData.__init__(self, *args, **kw)
        self._isLocked = None
        self._isRestricted = None
        self._isPathToElite = None
        self.showLinksTo = showLinksTo
        self.treeID = treeID
        self._boundingBox = None
        self._position = (0, 0)
        self._iconsPerRow = iconsPerRow

    def GetNodeType(self):
        return self.nodeType

    def GetDimensions(self):
        p0, p1 = self.GetBoundingBox()
        return geo2.Vec2Subtract(p1, p0)

    def GetCenter(self):
        p0, p1 = self.GetBoundingBox()
        return geo2.Vec3Lerp(p0, p1, 0.5)

    def GetPosition(self):
        return self._position

    def GetPositionProportional(self):
        rootNode = self.GetRootNode()
        (minX, minY), (maxX, maxY) = rootNode.GetBoundingBox()
        x, y = self.GetPosition()
        if minX == maxX:
            x = 0.0
        else:
            x = (x - minX) / (maxX - minX)
        if minY == maxY:
            y = 0.0
        else:
            y = (y - minY) / (maxY - minY)
        return (x, y)

    def SetPosition(self, position):
        self._position = position

    def GetBoundingBox(self):
        if self._boundingBox:
            return self._boundingBox
        minX, minY = self.GetPosition()
        maxX, maxY = self.GetPosition()
        children = self.GetChildren()
        if not children:
            return (self.GetPosition(), self.GetPosition())
        for child in self.GetChildren():
            (x1, y1), (x2, y2) = child.GetBoundingBox()
            minX = min(minX, x1, x2)
            minY = min(minY, y1, y2)
            maxX = max(maxX, x1, x2)
            maxY = max(maxY, y1, y2)

        self._boundingBox = ((minX, minY), (maxX, maxY))
        return self._boundingBox

    def GetGroupNodesByLevel(self):
        nodes = []
        self._GetGroupNodesByLevel(nodes, 0)
        return nodes

    def GetIconsPerRow(self):
        return self._iconsPerRow

    def IsAllChildrenElite(self):
        if not self.children:
            return self.IsElite()
        for child in self.children:
            if child.nodeType == NODETYPE_OTHERFACTIONGROUP:
                continue
            if not child._IsAllChildrenElite(child):
                return False

        return True

    def _IsAllChildrenElite(self, node):
        if not node.IsElite():
            return False
        for child in node.children:
            if not child._IsAllChildrenElite(child):
                return False

        return True

    def IsElite(self):
        return True

    def FlushCache(self):
        self._isLocked = None
        self._isRestricted = None
        self._isPathToElite = None
        for child in self.children:
            child.FlushCache()

    def IsPathToElite(self):
        if self._isPathToElite is not None:
            return self._isPathToElite
        parNode = self
        while True:
            childNode = parNode
            parNode = parNode.parent
            if parNode is None or parNode.nodeType != NODETYPE_CONNECTOR:
                if childNode.nodeType == NODETYPE_CONNECTOR:
                    self._isPathToElite = childNode.IsAllChildrenElite()
                else:
                    self._isPathToElite = childNode.IsElite() and childNode.IsAllChildrenElite()
                return self._isPathToElite

    def IsRestricted(self):
        if self._isRestricted is None:
            self._isRestricted = self._IsRestricted()
        return self._isRestricted

    def _IsRestricted(self):
        return False


class GroupNode(ShipTreeNodeBase):
    nodeType = NODETYPE_GROUP

    def __init__(self, shipGroupID, factionID, position, *args, **kw):
        ShipTreeNodeBase.__init__(self, *args, **kw)
        self.shipGroupID = shipGroupID
        self.factionID = factionID
        if self.parent:
            self.SetPosition(geo2.Add(self.parent.GetPosition(), position))
        else:
            self.SetPosition(position)

    def GetID(self):
        return self.shipGroupID

    def IsLocked(self):
        if self._isLocked is not None:
            return self._isLocked
        mySkills = sm.GetService('skills').GetSkill
        for skillTypeID, data in self._LoopInfoBubbleGroupsPreReqSkills():
            mySkill = mySkills(skillTypeID)
            if mySkill is None or mySkill.effectiveSkillLevel < data['level']:
                self._isLocked = True
                return self._isLocked

        self._isLocked = False
        return self._isLocked

    def IsLockedWithoutExpertSystem(self):
        mySkills = sm.GetService('skills').GetSkill
        for skillTypeID, data in self._LoopInfoBubbleGroupsPreReqSkills():
            mySkill = mySkills(skillTypeID)
            if mySkill is None or mySkill.trainedSkillLevel < data['level']:
                return True

        return False

    def IsRecentlyUnlocked(self):
        if self.IsLocked():
            return False
        oldSkills = sm.GetService('shipTree').GetRecentlyChangedSkills()
        for skillTypeID, data in self._LoopInfoBubbleGroupsPreReqSkills():
            myOldLevel = oldSkills.get(skillTypeID, None)
            if myOldLevel is not None and myOldLevel < data['level']:
                return True

        return False

    def IsBeingTrained(self):
        skillQueue = sm.GetService('skillqueue').GetQueue()
        requiredSkills = self.GetRequiredSkills()
        for trainingRecord in skillQueue:
            if trainingRecord.trainingTypeID in requiredSkills:
                return True

        return False

    def GetSkillLevel(self):
        lowest = 5
        skillSvc = sm.GetService('skills')
        for skillTypeID, _ in self._LoopInfoBubbleGroupsPreReqSkills():
            mySkill = skillSvc.GetSkill(skillTypeID)
            if not mySkill:
                return 0
            if mySkill.skillLevel < lowest:
                lowest = mySkill.skillLevel

        return lowest

    def GetRequiredSkills(self, onlyVisible = False):
        skillsWithLevel = {}
        for skillTypeID, data in self._LoopInfoBubbleGroupsPreReqSkills():
            if onlyVisible and not data['display']:
                continue
            skillsWithLevel[skillTypeID] = data['level']

        return skillsWithLevel

    def GetRequiredSkillsSorted(self, onlyVisible = False):

        def Compare(x, y):
            typeID1, level1 = x
            typeID2, level2 = y
            if level1 != level2:
                return level2 - level1
            typeName1 = evetypes.GetName(typeID1)
            typeName2 = evetypes.GetName(typeID2)
            if typeName1 > typeName2:
                return 1
            else:
                return -1

        skills = self.GetRequiredSkills(onlyVisible)
        skills = [ (typeID, level) for typeID, level in skills.iteritems() ]
        return sorted(skills, cmp=Compare)

    def _LoopInfoBubbleGroupsPreReqSkills(self):
        infoBubbleGroupPreReqSkills = {int(k):v for k, v in cfg.infoBubbleGroups[self.shipGroupID]['preReqSkills'].items()}
        if self.factionID in infoBubbleGroupPreReqSkills:
            skillData = {int(k):v for k, v in infoBubbleGroupPreReqSkills[self.factionID]['skills'].items()}
            for skillTypeID, data in skillData.iteritems():
                yield (skillTypeID, data)

    def GetBonusSkills(self):
        return self.GetRequiredSkills(onlyVisible=True)

    def GetBonusSkillsSorted(self):
        return self.GetRequiredSkillsSorted(onlyVisible=True)

    def _GetGroupNodesByLevel(self, nodes, level):
        if len(nodes) <= level:
            nodes.append([])
        nodes[level].append(self)
        for child in self.GetChildren():
            child._GetGroupNodesByLevel(nodes, level + 1)

    def GetIconSize(self):
        if self.shipGroupID in (shipgroup.groupJumpFreighter, shipgroup.groupFreighter):
            rigSize = 4
        else:
            typeIDs = self.GetShipTypeIDs()
            if typeIDs:
                rigSize = sm.GetService('godma').GetType(typeIDs[0]).rigSize
            else:
                rigSize = 0
        return 82 + 16 * rigSize

    def IsElite(self):
        if self.IsLocked():
            return False
        for typeID in self.GetShipTypeIDs():
            masteryLevel = sm.GetService('certificates').GetCurrCharMasteryLevel(typeID)
            if masteryLevel != 5:
                return False

        return True

    def GetShipTypeIDs(self):
        return sm.GetService('shipTree').GetShipTypeIDs(self.factionID, self.shipGroupID)

    def GetTimeToUnlock(self):
        typeIDs = self.GetShipTypeIDs()
        if typeIDs:
            return sm.GetService('skills').GetSkillTrainingTimeLeftToUseType(typeIDs[0], includeBoosters=False)
        return 0

    def GetGroupWidth(self):
        numIcons = min(len(self.GetShipTypeIDs()), self.GetIconsPerRow())
        return (self.GetIconSize() + 1) * numIcons

    def _IsRestricted(self):
        cloneGradeSvc = sm.GetService('cloneGradeSvc')
        requiredSkills = self.GetRequiredSkills()
        for skillID, requiredLevel in requiredSkills.iteritems():
            if cloneGradeSvc.GetMaxSkillLevel(skillID, CLONE_STATE_ALPHA) < requiredLevel:
                return True

        return super(GroupNode, self)._IsRestricted()


class OtherFactionGroupNode(GroupNode):
    nodeType = NODETYPE_OTHERFACTIONGROUP


class ConnectorNode(ShipTreeNodeBase):
    nodeType = NODETYPE_CONNECTOR

    def __init__(self, position, *args, **kw):
        ShipTreeNodeBase.__init__(self, *args, **kw)
        self._skillLevel = None
        if self.parent:
            self.SetPosition(geo2.Add(self.parent.GetPosition(), position))
        else:
            self.SetPosition(position)

    def GetID(self):
        return '%s_%s' % self.GetPosition()

    def IsLocked(self):
        if self._isLocked is not None:
            return self._isLocked
        for child in self.GetChildren():
            if not child.IsLocked():
                self._isLocked = False
                return self._isLocked

        self._isLocked = True
        return self._isLocked

    def GetSkillLevel(self):
        if self._skillLevel is not None:
            return self._skillLevel
        self._skillLevel = max([ child.GetSkillLevel() for child in self.GetChildren() ])
        return self._skillLevel

    def _GetGroupNodesByLevel(self, nodes, level):
        for child in self.GetChildren():
            child._GetGroupNodesByLevel(nodes, level)

    def _IsRestricted(self):
        return all((c.IsRestricted() for c in self.GetChildren()))


class RootNode(ConnectorNode):
    nodeType = NODETYPE_ROOT

    def _IsRestricted(self):
        return False
