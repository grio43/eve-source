#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\sys\eveCfg.py
import cPickle
import copy
import logging
import math
import random
import re
import sqlite3
import sys
import types
import blue
import carbon.common.script.sys.cfg as sysCfg
import carbon.common.script.util.format as formatUtil
import eve.common.script.util.eveFormat as evefmtutil
import evetypes
import fsd.schemas.binaryLoader as fsdBinaryLoader
import fsdlite
import industry
import localization
import pytelemetry.zoning as telemetry
import remotefilecache
import uthread
import utillib
from caching.memoize import Memoize
from carbon.common.script.sys.crowset import CRowset
from characterdata.factions import iter_factions, get_faction_name
from characterdata.npccharacters import get_npc_character_name, iter_npc_characters
from eve.common.lib import appConst as const
from eve.common.script.util import standingUtil
from eveprefs import boot
from evestations.const import DOOMHEIM_STATION, NPCStation, NPCStationProps
from evestations.data import LOCATION_NPC_STATION_FORMATTER_NO_OP_NAME_RAW, LOCATION_NPC_STATION_FORMATTER_RAW, get_station_operation_name
from inventorycommon.const import CONTAINER_GROUPS
from inventorycommon.util import IsSubsystemFlagVisible, IsTypeContainer
from marketgroups.data import MarketGroupObject
from npcs.npccorporations import CorporationTicker, CorporationTickerProps, get_corporation_ticker_name, get_npc_corporation_name, iter_npc_corporation_ids, iter_npc_corporations
from spacecomponents.common.helper import HasCargoBayComponent
import eve.common.script.sys.idCheckers as idCheckers
OWNER_AURA_IDENTIFIER = -1
OWNER_SYSTEM_IDENTIFIER = -2
logger = logging.getLogger(__name__)

class Standings():
    __guid__ = 'eveCfg.Standings'
    __passbyvalue__ = 1

    def __init__(self, fromID, fromFactionID, fromCorpID, fromCharID, toID, toFactionID, toCorpID, toCharID):
        self.fromID, self.fromFactionID, self.fromCorpID, self.fromCharID, self.toID, self.toFactionID, self.toCorpID, self.toCharID = (fromID,
         fromFactionID,
         fromCorpID,
         fromCharID,
         toID,
         toFactionID,
         toCorpID,
         toCharID)
        self.faction = utillib.KeyVal(faction=0.0, corp=0.0, char=0.0)
        self.corp = utillib.KeyVal(faction=0.0, corp=0.0, char=0.0)
        self.char = utillib.KeyVal(faction=0.0, corp=0.0, char=0.0)

    def __str__(self):
        return 'Standing from %s toward %s: faction:(%s,%s,%s), corp:(%s,%s,%s), char:(%s,%s,%s)' % (self.fromID,
         self.toID,
         self.faction.faction,
         self.faction.corp,
         self.faction.char,
         self.corp.faction,
         self.corp.corp,
         self.corp.char,
         self.char.faction,
         self.char.corp,
         self.char.char)

    def __repr__(self):
        return self.__str__()

    def CanUseAgent(self, level, agentTypeID = None, noL1Check = 1):
        return CanUseAgent(level, agentTypeID, self.faction.char, self.corp.char, self.char.char, self.fromCorpID, self.fromFactionID, {}, noL1Check)

    def __getattr__(self, theKey):
        if theKey == 'minimum':
            m = None
            for each in (self.faction, self.corp, self.char):
                for other in (each.faction, each.corp, each.char):
                    if other != 0.0 and (m is None or other < m):
                        m = other

            if m is None:
                return 0.0
            return m
        if theKey == 'maximum':
            m = None
            for each in (self.faction, self.corp, self.char):
                for other in (each.faction, each.corp, each.char):
                    if other != 0.0 and (m is None or other > m):
                        m = other

            if m is None:
                return 0.0
            return m
        if theKey == 'direct':
            if self.fromID == self.fromFactionID:
                tmp = self.faction
            elif self.fromID == self.fromCorpID:
                tmp = self.corp
            elif self.fromID == self.fromCharID:
                tmp = self.char
            if self.toID == self.toFactionID:
                return tmp.faction
            elif self.toID == self.toCorpID:
                return tmp.corp
            elif self.toID == self.toCharID:
                return tmp.char
            else:
                return 0.0
        else:
            if theKey == 'all':
                return [(self.fromFactionID, self.toFactionID, self.faction.faction),
                 (self.fromFactionID, self.toCorpID, self.faction.corp),
                 (self.fromFactionID, self.toCharID, self.faction.char),
                 (self.fromCorpID, self.toFactionID, self.corp.faction),
                 (self.fromCorpID, self.toCorpID, self.corp.corp),
                 (self.fromCorpID, self.toCharID, self.corp.char),
                 (self.fromCharID, self.toFactionID, self.char.faction),
                 (self.fromCharID, self.toCorpID, self.char.corp),
                 (self.fromCharID, self.toCharID, self.char.char)]
            raise AttributeError(theKey)


def CanUseAgent(level, agentTypeID, fac, coc, cac, fromCorpID, fromFactionID, skills, noL1Check = 1):
    if agentTypeID == const.agentTypeAura:
        return True
    elif level == 1 and agentTypeID != const.agentTypeResearchAgent and noL1Check:
        return 1
    m = (level - 1) * 2.0 - 1.0
    if boot.role == 'client':
        if not skills:
            mySkills = sm.GetService('skills').GetSkill
            for skillTypeID in (const.typeConnections, const.typeDiplomacy, const.typeCriminalConnections):
                skillInfo = mySkills(skillTypeID)
                if skillInfo:
                    skills[skillTypeID] = skillInfo

        unused, facBonus = standingUtil.GetStandingBonus(fac, fromFactionID, skills)
        unused, cocBonus = standingUtil.GetStandingBonus(coc, fromFactionID, skills)
        unused, cacBonus = standingUtil.GetStandingBonus(cac, fromFactionID, skills)
        if facBonus > 0.0:
            fac = (1.0 - (1.0 - fac / 10.0) * (1.0 - facBonus / 10.0)) * 10.0
        if cocBonus > 0.0:
            coc = (1.0 - (1.0 - coc / 10.0) * (1.0 - cocBonus / 10.0)) * 10.0
        if cacBonus > 0.0:
            cac = (1.0 - (1.0 - cac / 10.0) * (1.0 - cacBonus / 10.0)) * 10.0
    if max(fac, coc, cac) >= m and min(fac, coc, cac) > -2.0:
        if agentTypeID == const.agentTypeResearchAgent and coc < m - 2.0:
            return 0
        return 1
    else:
        return 0


class EveDataConfig(sysCfg.DataConfig):
    __guid__ = 'svc.eveDataconfig'
    __replaceservice__ = 'dataconfig'

    def __init__(self):
        sysCfg.DataConfig.__init__(self)

    def _CreateConfig(self):
        return eveConfig


class EveConfig(sysCfg.Config):
    __guid__ = 'util.EveConfig'

    def __init__(self):
        sysCfg.Config.__init__(self)
        self.fmtMapping[const.UE_OWNERID] = lambda value, value2: cfg.eveowners.Get(value).ownerName
        self.fmtMapping[const.UE_OWNERIDNICK] = lambda value, value2: cfg.eveowners.Get(value).ownerName.split(' ')[0]
        self.fmtMapping[const.UE_LOCID] = lambda value, value2: cfg.evelocations.Get(value).locationName
        self.fmtMapping[const.UE_TYPEID] = lambda value, value2: evetypes.GetName(value)
        self.fmtMapping[const.UE_TYPEID2] = lambda value, value2: evetypes.GetDescription(value)
        self.fmtMapping[const.UE_TYPEIDL] = lambda value, value2: cfg.FormatConvert(const.UE_LIST, [ (const.UE_TYPEID, x) for x in value ], value2)
        self.fmtMapping[const.UE_BPTYPEID] = lambda value, value2: evetypes.GetName(cfg.blueprints.Get(value).blueprintTypeID)
        self.fmtMapping[const.UE_GROUPID] = lambda value, value2: evetypes.GetGroupNameByGroup(value)
        self.fmtMapping[const.UE_GROUPID2] = lambda value, value2: ''
        self.fmtMapping[const.UE_CATID] = lambda value, value2: evetypes.GetCategoryNameByCategory(value)
        self.fmtMapping[const.UE_CATID2] = lambda value, value2: ''
        self.fmtMapping[const.UE_AMT] = lambda value, value2: formatUtil.FmtAmt(value)
        self.fmtMapping[const.UE_AMT2] = lambda value, value2: evefmtutil.FmtISK(value)
        self.fmtMapping[const.UE_AMT3] = lambda value, value2: evefmtutil.FmtISK(value)
        self.fmtMapping[const.UE_ISK] = lambda value, value2: evefmtutil.FmtISK(value)
        self.fmtMapping[const.UE_AUR] = lambda value, value2: evefmtutil.FmtAUR(value)
        self.fmtMapping[const.UE_DIST] = lambda value, value2: formatUtil.FmtDist(value)
        self.fmtMapping[const.UE_TYPEIDANDQUANTITY] = self.__FormatTypeIDAndQuantity
        self.crystalgroups = []
        self.rawCelestialCache = {}
        self.stationLocalizationData = {}
        self._mapRegionCache = None
        self._mapConstellationCache = None
        self._mapSystemCache = None
        self._mapJumpCache = None
        self._mapSolarSystemContentCache = None
        self._map_stargate_id_mapping = None
        self.mapObjectsDb = None
        self.staticMapDb = None

    def Release(self):
        sysCfg.Config.Release(self)
        self.graphics = None
        self.graphicEffects = None
        self.eveowners = None
        self.evelocations = None
        self.rawCelestialCache = None
        self.corptickernames = None
        self.allianceshortnames = None
        self.crystalgroups = None
        self._ReleaseMapCache()
        self.planetResources = None
        self.planetBlacklist = None
        self.overviewDefaults = None
        self.overviewDefaultGroups = None
        self.positions = None
        self.messages = None
        self.mapObjectsDb = None

    def _ReleaseMapCache(self):
        self._mapRegionCache = None
        self._mapConstellationCache = None
        self._mapSystemCache = None
        self._mapJumpCache = None
        self._mapSolarSystemContentCache = None
        self._map_stargate_id_mapping = None

    def GetStartupData(self):
        sysCfg.Config.GetStartupData(self)
        if self.IsClient():
            self.messages = _LoadMessagesFromFSD()

    def IsClient(self):
        return boot.role == 'client'

    @telemetry.ZONE_METHOD
    def GetMessage(self, key, dict = None, onNotFound = 'return', onDictMissing = 'error', languageID = None):
        try:
            msg = self.messages[key]
        except KeyError:
            return self._GetContentForMissingMessage(key, dict, languageID=languageID)

        bodyID, titleID = msg.bodyID, msg.titleID
        title, text = self._GetTitleAndTextForMessage(dict, titleID, bodyID, languageID=languageID)
        return utillib.KeyVal(text=text, title=title, type=msg.dialogType, audio=msg.urlAudio, icon=msg.urlIcon, suppress=msg.suppressable, closable=msg.closable)

    @telemetry.ZONE_METHOD
    def GetMessageTypeAndText(self, key, paramDict, onNotFound = 'return', onDictMissing = 'error', languageID = None):
        try:
            msg = self.messages[key]
        except KeyError:
            return self._GetContentForMissingMessage(key, paramDict, languageID=languageID)

        for k, v in paramDict.iteritems():
            if type(v) != types.TupleType:
                continue
            value2 = None
            if len(v) >= 3:
                value2 = v[2]
            paramDict[k] = self.FormatConvert(v[0], v[1], value2)

        text = localization.GetByMessageID(msg.bodyID, languageID=languageID, **paramDict)
        return utillib.KeyVal(text=text, type=msg.dialogType)

    def _GetContentForMissingMessage(self, key, paramDict, languageID):
        if key != 'ErrMessageNotFound':
            return self.GetMessage('ErrMessageNotFound', {'msgid': key,
             'args': repr(paramDict)}, languageID=languageID)
        else:
            return utillib.KeyVal(text='Could not find message with key ' + key, title='Message not found', type='fatal', audio='', icon='', suppress=False)

    def _GetTitleAndTextForMessage(self, paramDict, titleID, bodyID, languageID):
        if paramDict is not None and paramDict != -1:
            paramDict = self.__prepdict(paramDict)
            title = localization.GetByMessageID(titleID, languageID=languageID, **paramDict) if titleID is not None else None
            text = localization.GetByMessageID(bodyID, languageID=languageID, **paramDict) if bodyID is not None else None
        else:
            title = localization.GetByMessageID(titleID, languageID=languageID) if titleID is not None else None
            text = localization.GetByMessageID(bodyID, languageID=languageID) if bodyID is not None else None
        return (title, text)

    def GetRawMessageTitle(self, key):
        msg = self.messages.get(key, None)
        if msg:
            if msg.titleID is not None:
                return localization._GetRawByMessageID(msg.titleID)

    @Memoize
    def GetSuppressValueForMessage(self, msgKey, msgParams):
        import carbonui.const as uiconst
        constMapping = {'ID_YES': uiconst.ID_YES,
         'ID_NO': uiconst.ID_NO,
         False: None,
         True: True}
        try:
            return constMapping[cfg.GetMessage(msgKey, msgParams).suppress]
        except StandardError:
            return

    def IsChargeCompatible(self, item):
        if not item[const.ixSingleton]:
            return 0
        else:
            return item[const.ixGroupID] in self.__chargecompatiblegroups__

    def IsContainer(self, item, doSpaceComponentCheck = True):
        if not item.singleton:
            return False
        elif IsTypeContainer(item.typeID):
            return True
        elif doSpaceComponentCheck:
            return idCheckers.IsSolarSystem(item.locationID) and HasCargoBayComponent(item.typeID)
        else:
            return False

    def IsCargoContainer(self, item):
        return item.singleton and item.groupID in CONTAINER_GROUPS

    def AppGetStartupData(self):
        self.LoadCfgData()

    def LoadSqliteDB(self, fileName):
        res = blue.ResFile()
        if boot.role == 'client' and blue.pyos.packaged:
            mapObjectsResPath = blue.paths.ResolvePath('bin:/staticdata/{fileName}.db'.format(fileName=fileName))
        else:
            mapObjectsResPath = blue.paths.ResolvePath('res:/staticdata/{fileName}.db'.format(fileName=fileName))
        if not res.Open(mapObjectsResPath):
            cfg.LogError('Could not find file %s.' % mapObjectsResPath)
        else:
            dbConnection = sqlite3.connect(mapObjectsResPath)
            dbConnection.row_factory = sqlite3.Row
        res.Close()
        return dbConnection

    def LoadCfgData(self):
        cfg.LogNotice('App LoadCfgData')
        remotefilecache.prefetch_folder('res:/staticdata')
        sysCfg.Config.LoadCfgData(self)
        self.fsdDustIcons = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/dustIcons.static')
        self.messages = _LoadMessagesFromFSD()
        cfg.LogNotice('Done Loading static data')
        if self.IsClient():
            self.mapObjectsDb = self.LoadSqliteDB('mapObjects')
            self.mapCelestialLocationCache = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/locationCache.static')
            self.mapFactionsOwningSolarSystems = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/factionsOwningSolarSystems.static', 'res:/staticdata/factionsOwningSolarSystems.schema', optimize=False)
            infoBubbleData = fsdlite.EveStorage(data='infoBubbleElements', cache='infoBubbles.static')
            self.infoBubbleElements = {int(k):v for k, v in infoBubbleData['infoBubbleElements'].items()}
            self.infoBubbleFactions = {int(k):v for k, v in infoBubbleData['infoBubbleFactions'].items()}
            self.infoBubbleGroups = {int(k):v for k, v in infoBubbleData['infoBubbleGroups'].items()}
            self.infoBubbleTypeElements = {int(k):v['elements'] for k, v in infoBubbleData['infoBubbleTypeElements'].items()}
            self.infoBubbleTypeBonuses = {int(k):v for k, v in infoBubbleData['infoBubbleTypeBonuses'].items()}
            self.certificates = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/certificates.static', optimize=False)
            self.LoadTypesUsedByBlueprints()
        else:
            self.securityForSystemsWithPlanetsInLocation = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/securityForSystemsWithPlanetsInLocation.static')
            self.staticMapDb = self.LoadSqliteDB('staticMap')
        self.LoadStationLocalizationData()
        cfg.LogNotice('Done loading sqlite data')
        self.LoadPlanetBlacklist()
        self.LoadCrpTickerNames()
        self.LoadEveOwners()
        self.LoadEveLocations()
        cfg.LogNotice('Done loading owner and location data')
        self.blueprints = industry.BlueprintStorage()
        allianceshortnameRowHeader = blue.DBRowDescriptor((('allianceID', const.DBTYPE_I4), ('shortName', const.DBTYPE_WSTR)))
        self.allianceshortnameRowset = CRowset(allianceshortnameRowHeader, [])
        self.allianceshortnames = sysCfg.Recordset(AllShortNames, 'allianceID', 'GetAllianceShortNamesEx', 'GetMultiAllianceShortNamesEx')
        self.ConvertData(self.allianceshortnameRowset, self.allianceshortnames)
        positionRowHeader = blue.DBRowDescriptor((('itemID', const.DBTYPE_I8),
         ('x', const.DBTYPE_R5),
         ('y', const.DBTYPE_R5),
         ('z', const.DBTYPE_R5),
         ('yaw', const.DBTYPE_R4),
         ('pitch', const.DBTYPE_R4),
         ('roll', const.DBTYPE_R4)))
        positionRowset = CRowset(positionRowHeader, [])
        self.positions = sysCfg.Recordset(Position, 'itemID', 'GetPositionEx', 'GetPositionsEx')
        self.ConvertData(positionRowset, self.positions)
        cfg.LogNotice('Done loading alliance and position data')
        if self.IsClient():
            self._averageMarketPrice = {}
            uthread.new(self.GetAveragePricesThread)
        else:
            self._averageMarketPrice = self.GetConfigSvc().GetAverageMarketPrices()
        cfg.LogNotice('Done loading market data')
        self.__chargecompatiblegroups__ = (const.groupFrequencyMiningLaser,
         const.groupEnergyWeapon,
         const.groupProjectileWeapon,
         const.groupMissileLauncher,
         const.groupCapacitorBooster,
         const.groupHybridWeapon,
         const.groupScanProbeLauncher,
         const.groupComputerInterfaceNode,
         const.groupMissileLauncherBomb,
         const.groupMissileLauncherCruise,
         const.groupMissileLauncherDefender,
         const.groupMissileLauncherAssault,
         const.groupMissileLauncherSiege,
         const.groupMissileLauncherHeavy,
         const.groupMissileLauncherHeavyAssault,
         const.groupMissileLauncherRocket,
         const.groupMissileLauncherStandard,
         const.groupMissileLauncherXLTorpedo,
         const.groupMissileLauncherXLCruise,
         const.groupMissileLauncherRapidTorpedo,
         const.groupMissileLauncherFestival,
         const.groupMissileLauncherDot,
         const.groupBubbleProbeLauncher,
         const.groupSensorBooster,
         const.groupStructureECM,
         const.groupRemoteSensorBooster,
         const.groupRemoteSensorDamper,
         const.groupTrackingComputer,
         const.groupTrackingDisruptor,
         const.groupTrackingLink,
         const.groupWarpDisruptFieldGenerator,
         const.groupFueledShieldBooster,
         const.groupFueledArmorRepairer,
         const.groupSurveyProbeLauncher,
         const.groupMissileLauncherRapidHeavy,
         const.groupDroneTrackingModules,
         const.groupMissileGuidanceComputer,
         const.groupStructureAreaMissileLauncher,
         const.groupStructureECMScript,
         const.groupStructureFlakMissileLauncher,
         const.groupStructureMissileLauncher,
         const.groupFlexArmorHardener,
         const.groupFlexShieldHardener,
         const.groupFueledRemoteShieldBooster,
         const.groupFueledRemoteArmorRepairer,
         const.groupCommandBurstModule,
         const.groupStructureWarpDisruptor,
         const.groupStructureFestivalLauncher,
         const.groupPrecursorTurret,
         const.groupStasisNullifier,
         const.groupChainLightningTurret,
         const.groupStructureDefenseBattery)

    def LoadTypesUsedByBlueprints(self):
        res = blue.ResFile()
        resPath = 'res:/staticdata/blueprintsByMaterialTypeIDs.pickle'
        if not res.open('%s' % resPath):
            self.LogError('Could not load Blueprints by material Cache data file: %s' % resPath)
        else:
            try:
                pickleData = res.Read()
                self.blueprintsByMaterialTypeIDs = cPickle.loads(pickleData)
            finally:
                res.Close()

    def LoadPlanetBlacklist(self):
        self.planetBlacklist = self.GetConfigSvc().GetBlackListedPlanets()

    def LoadCrpTickerNames(self):
        self.corptickernames = sysCfg.Recordset(CrpTickerNames, 'corporationID', 'GetCorpTickerNamesEx', 'GetMultiCorpTickerNamesEx')
        tickers = []
        for corporationID in iter_npc_corporation_ids():
            tickers.append(CorporationTicker(corporationID=corporationID, tickerName=get_corporation_ticker_name(corporationID), shape1=None, shape2=None, shape3=None, color1=None, color2=None, color3=None))

        self.corptickernames.PopulateDataset(CorporationTickerProps, tickers)

    @telemetry.ZONE_METHOD
    def __prepdict(self, dict):
        dict = copy.deepcopy(dict)
        if charsession:
            for k, v in {'session.char': (const.UE_OWNERID, charsession.charid),
             'session.nick': (const.UE_OWNERIDNICK, charsession.charid),
             'session.corp': (const.UE_OWNERID, charsession.corpid),
             'session.station': (const.UE_LOCID, charsession.stationid),
             'session.solarsystem': (const.UE_LOCID, charsession.solarsystemid2),
             'session.constellation': (const.UE_LOCID, charsession.constellationid),
             'session.region': (const.UE_LOCID, charsession.regionid),
             'session.location': (const.UE_LOCID, charsession.locationid)}.iteritems():
                if v[1] is not None:
                    dict[k] = v

        for k, v in dict.iteritems():
            if type(v) != types.TupleType:
                continue
            value2 = None
            if len(v) >= 3:
                value2 = v[2]
            dict[k] = self.FormatConvert(v[0], v[1], value2)

        return dict

    def __FormatTypeIDAndQuantity(self, typeID, quantity):
        return localization.GetByLabel('UI/Common/QuantityAndItem', quantity=quantity, item=typeID)

    def GetAveragePricesThread(self):
        blue.pyos.synchro.SleepWallclock(2000)
        self._averageMarketPrice = self.GetConfigSvc().GetAverageMarketPrices()

    def GetCrystalGroups(self):
        if not self.crystalgroups:
            crystalGroupIDs = [ groupID for groupID in evetypes.GetGroupIDsByCategory(const.categoryCharge) if localization.CleanImportantMarkup(evetypes.GetGroupNameByGroup(groupID, 'en')).endswith('Crystal') ]
            self.crystalgroups.extend(crystalGroupIDs)
            scriptGroupIDs = [ groupID for groupID in evetypes.GetGroupIDsByCategory(const.categoryCharge) if localization.CleanImportantMarkup(evetypes.GetGroupNameByGroup(groupID, 'en')).endswith('Script') ]
            self.crystalgroups.extend(scriptGroupIDs)
        return self.crystalgroups

    def GetLocationWormholeClass(self, solarSystemID):
        system = self.mapSystemCache[solarSystemID]
        return getattr(system, 'wormholeClassID', const.INVALID_WORMHOLE_CLASS_ID)

    def GetNebula(self, solarSystemID, constellationID, regionID, returnPath = True):
        if returnPath:
            return self.mapRegionCache.Get(regionID).nebulaPath
        else:
            return self.mapRegionCache.Get(regionID).nebulaID

    @telemetry.ZONE_METHOD
    def LoadEveOwners(self):
        rowDescriptor = self.GetOwnersRowDescriptor()
        self.eveowners = sysCfg.Recordset(EveOwners, 'ownerID', 'GetOwnersEx', 'GetMultiOwnersEx')
        self.eveowners.header = ['ownerID',
         'ownerName',
         'typeID',
         'gender',
         'ownerNameID']
        for factionID, faction in iter_factions():
            if self.IsClient():
                factionName = get_faction_name(factionID, faction, important=True)
            else:
                factionName = get_faction_name(factionID, faction)
            self.eveowners.data[factionID] = blue.DBRow(rowDescriptor, [factionID,
             factionName,
             const.typeFaction,
             None,
             faction.nameID])

        for corporationID, corporation in iter_npc_corporations():
            if self.IsClient():
                corporationName = get_npc_corporation_name(corporationID, corporation, important=True)
            else:
                corporationName = get_npc_corporation_name(corporationID, corporation)
            self.eveowners.data[corporationID] = blue.DBRow(rowDescriptor, [corporationID,
             corporationName,
             const.typeCorporation,
             None,
             corporation.nameID])

        for charID, character in iter_npc_characters():
            if self.IsClient():
                important = True
            else:
                important = False
            npcName = get_npc_character_name(charID, character, important=important)
            try:
                self.eveowners.data[charID] = blue.DBRow(rowDescriptor, [charID,
                 npcName,
                 const.typeCharacter,
                 character.gender,
                 character.nameID])
            except KeyError:
                self.LogError('ERROR: NPC missing from eveowner table - PLEASE FIX THIS!', charID, npcName)

        self.eveowners.data[1] = blue.DBRow(rowDescriptor, [1,
         localization.GetByLabel(OWNER_NAME_OVERRIDES[OWNER_SYSTEM_IDENTIFIER]),
         0,
         None,
         None])

    def UpdateEveOwnerName(self, ownerID, ownerName):
        owner = self.eveowners.Get(ownerID)
        self.eveowners.data[ownerID] = blue.DBRow(self.GetOwnersRowDescriptor(), [ownerID,
         ownerName,
         owner.typeID,
         owner.gender,
         owner.ownerNameID])

    def GetOwnersRowDescriptor(self):
        return blue.DBRowDescriptor((('ownerID', const.DBTYPE_I4),
         ('ownerName', const.DBTYPE_WSTR),
         ('typeID', const.DBTYPE_I4),
         ('gender', const.DBTYPE_I2),
         ('ownerNameID', const.DBTYPE_I4)))

    def GetLocationRowDescriptor(self):
        return blue.DBRowDescriptor((('locationID', const.DBTYPE_I8),
         ('locationName', const.DBTYPE_WSTR),
         ('solarSystemID', const.DBTYPE_I8),
         ('x', const.DBTYPE_R5),
         ('y', const.DBTYPE_R5),
         ('z', const.DBTYPE_R5),
         ('locationNameID', const.DBTYPE_I4)))

    @property
    def mapRegionCache(self):
        if not self._mapRegionCache:
            self._mapRegionCache = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/regions.static', 'res:/staticdata/regions.schema', optimize=False)
        return self._mapRegionCache

    @property
    def mapConstellationCache(self):
        if not self._mapConstellationCache:
            self._mapConstellationCache = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/constellations.static', 'res:/staticdata/constellations.schema', optimize=False)
        return self._mapConstellationCache

    @property
    def mapSystemCache(self):
        if not self._mapSystemCache:
            self._mapSystemCache = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/systems.static', 'res:/staticdata/systems.schema', optimize=False)
        return self._mapSystemCache

    @property
    def mapJumpCache(self):
        if not self._mapJumpCache:
            self._mapJumpCache = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/jumps.static', 'res:/staticdata/jumps.schema', optimize=False)
        return self._mapJumpCache

    @property
    def mapSolarSystemContentCache(self):
        if not self._mapSolarSystemContentCache:
            self._mapSolarSystemContentCache = fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/solarSystemContent.static')
        return self._mapSolarSystemContentCache

    @property
    def mapStargateIdMappingCache(self):
        if not self._map_stargate_id_mapping:
            self._map_stargate_id_mapping = {}
            for solarSystemID, solarSystem in self.mapSolarSystemContentCache.iteritems():
                for stargate_id, stargate in solarSystem.stargates.iteritems():
                    self._map_stargate_id_mapping[stargate_id] = stargate.destination
                    self._map_stargate_id_mapping[stargate.destination] = stargate_id

        return self._map_stargate_id_mapping

    @telemetry.ZONE_METHOD
    def LoadEveLocations(self):
        rowDescriptor = self.GetLocationRowDescriptor()
        self.evelocations = sysCfg.Recordset(EveLocations, 'locationID', 'GetLocationsEx', 'GetMultiLocationsEx', 'GetLocationsLocal')
        self.evelocations.header = ['locationID',
         'locationName',
         'solarSystemID',
         'x',
         'y',
         'z',
         'locationNameID']
        for regionID, region in self.mapRegionCache.iteritems():
            regionName = localization.GetImportantByMessageID(region.nameID)
            self.evelocations.data[regionID] = blue.DBRow(rowDescriptor, [regionID,
             regionName,
             None,
             region.center[0],
             region.center[1],
             region.center[2],
             region.nameID])

        for constellationID, constellation in self.mapConstellationCache.iteritems():
            constellationName = localization.GetImportantByMessageID(constellation.nameID)
            self.evelocations.data[constellationID] = blue.DBRow(rowDescriptor, [constellationID,
             constellationName,
             None,
             constellation.center.x,
             constellation.center.y,
             constellation.center.z,
             constellation.nameID])

        for solarSystemID, solarSystem in self.mapSystemCache.iteritems():
            solarSystemName = localization.GetImportantByMessageID(solarSystem.nameID)
            self.evelocations.data[solarSystemID] = blue.DBRow(rowDescriptor, [solarSystemID,
             solarSystemName,
             solarSystemID,
             solarSystem.center.x,
             solarSystem.center.y,
             solarSystem.center.z,
             solarSystem.nameID])

        self.LoadOldStationsInfo()
        self.LoadNPCStations()
        localStations = {}
        if self.IsClient():
            localStations = self.PrimeStationCelestials()
        for row in self.stations:
            if self.IsClient() and row.stationID in localStations:
                stationName = self.GetNPCStationNameFromLocalRow(localStations[row.stationID])
            else:
                stationName = row.stationName
            self.evelocations.data[row.stationID] = blue.DBRow(rowDescriptor, [row.stationID,
             stationName,
             row.solarSystemID,
             row.x,
             row.y,
             row.z,
             None])

        self.LoadStationLocalizationData()

    @telemetry.ZONE_METHOD
    def LoadStationLocalizationData(self):
        if self.IsClient():
            db = self.mapObjectsDb
            key = 'stationID'
            sql = 'SELECT stationID, celestialIndex, orbitIndex, useOperationName FROM npcStations'
        else:
            db = self.staticMapDb
            key = 'id'
            sql = 'SELECT id, celestialIndex, orbitIndex, useOperationName FROM NpcStations'
        cursor = db.execute(sql)
        self.stationLocalizationData = {row[key]:(row['celestialIndex'], row['orbitIndex'], row['useOperationName']) for row in cursor}

    def LoadNPCStations(self):
        npcStations = []
        for stationID, data in self.mapSolarSystemContentCache.npcStations.iteritems():
            position = data.position
            npcStations.append(NPCStation(stationID=stationID, stationName=data.stationName, x=position[0], y=position[1], z=position[2], stationTypeID=data.typeID, solarSystemID=data.solarSystemID, orbitID=data.orbitID, ownerID=data.ownerID))

        npcStations.append(DOOMHEIM_STATION)
        self.stations = sysCfg.Recordset(sysCfg.Row, 'stationID', (NPCStationProps, npcStations))

    def LoadOldStationsInfo(self):
        self.oldStations = sysCfg.Recordset(sysCfg.Row, 'stationID')
        if self.IsClient():
            uthread.new(self._LoadOldStationsInfo)
        else:
            self._LoadOldStationsInfo()

    def _LoadOldStationsInfo(self):
        oldStations = self.GetConfigSvc().GetOldStationData()
        if oldStations:
            self.oldStations = sysCfg.Recordset(sysCfg.Row, 'stationID', (oldStations.columns, oldStations.values()))

    @telemetry.ZONE_METHOD
    def PrimeStationCelestials(self):
        if boot.role != 'client':
            raise RuntimeError('PrimeStationCelestials::Non-client based call to PrimeStationCelestials!')
        sql = 'SELECT *\n                   FROM npcStations\n              '
        stations = self.mapObjectsDb.execute(sql)
        localStations = {}
        primeList = []
        for station in stations:
            if station['orbitID'] is not None:
                primeList.append(station['orbitID'])
            localStations[station['stationID']] = station

        cfg.evelocations.Prime(primeList)
        return localStations

    @telemetry.ZONE_METHOD
    def GetMarketGroup(self, marketGroupID):
        if boot.role != 'client':
            raise RuntimeError('GetMarketGroup::Non-clientbased call made!!')
        return MarketGroupObject(marketGroupID)

    @telemetry.ZONE_METHOD
    def GetLocationsLocalBySystem(self, solarSystemID, requireLocalizedTexts = True, doYields = False):
        if boot.role != 'client':
            raise RuntimeError('GetLocationsLocalBySystem::Non-clientbased call made!!')
        solarSystemObjectRowDescriptor = blue.DBRowDescriptor((('groupID', const.DBTYPE_I4),
         ('typeID', const.DBTYPE_I4),
         ('itemID', const.DBTYPE_I8),
         ('itemName', const.DBTYPE_WSTR),
         ('locationID', const.DBTYPE_I4),
         ('orbitID', const.DBTYPE_I4),
         ('connector', const.DBTYPE_BOOL),
         ('x', const.DBTYPE_R5),
         ('y', const.DBTYPE_R5),
         ('z', const.DBTYPE_R5),
         ('celestialIndex', const.DBTYPE_I4),
         ('orbitIndex', const.DBTYPE_I4)))
        sql = ' SELECT *\n                    FROM celestials\n                   WHERE solarSystemID = %d' % solarSystemID
        data = []
        rs = self.mapObjectsDb.execute(sql)
        for row in rs:
            try:
                celestialName = self.GetCelestialNameFromLocalRow(row, requireLocalizedTexts)
                data.append(blue.DBRow(solarSystemObjectRowDescriptor, [row['groupID'],
                 row['typeID'],
                 row['celestialID'],
                 celestialName,
                 solarSystemID,
                 row['orbitID'],
                 0,
                 row['x'],
                 row['y'],
                 row['z'],
                 row['celestialIndex'],
                 row['orbitIndex']]))
            except IndexError as e:
                rowContents = 'Row: '
                if row:
                    rowContents = ', '.join([ '%s=%s' % (key, row[key]) for key in row.keys() ])
                error = 'GetLocationsLocalBySystem: Failed getting local celestial data!\nRow is: %s\nError is: %s' % (rowContents, e)
                self.LogError(error)

            if doYields:
                blue.synchro.Yield()

        sql = '\n                SELECT *\n                  FROM npcStations\n                 WHERE solarSystemID = %d\n              ' % solarSystemID
        rs = self.mapObjectsDb.execute(sql)
        for row in rs:
            try:
                celestialName = self.GetNPCStationNameFromLocalRow(row, requireLocalizedTexts)
                data.append(blue.DBRow(solarSystemObjectRowDescriptor, [evetypes.GetGroupID(row['typeID']),
                 row['typeID'],
                 row['stationID'],
                 celestialName,
                 solarSystemID,
                 row['orbitID'],
                 0,
                 row['x'],
                 row['y'],
                 row['z'],
                 row['celestialIndex'],
                 row['orbitIndex']]))
            except IndexError as e:
                rowContents = 'Row: '
                if row:
                    rowContents = ', '.join([ '%s=%s' % (key, row[key]) for key in row.keys() ])
                error = 'GetLocationsLocalBySystem: Failed getting local station data!\nRow is: %s\nError is: %s' % (rowContents, e)
                self.LogError(error)

            if doYields:
                blue.synchro.Yield()

        data = CRowset(solarSystemObjectRowDescriptor, data)
        return data

    @telemetry.ZONE_METHOD
    def GetLocationsLocal(self, keys):
        if boot.role != 'client':
            raise RuntimeError('GetLocationsLocal::Non-clientbased call made!!')
        rowDescriptor = self.GetLocationRowDescriptor()
        data = []
        keyString = ','.join([ str(x) for x in keys ])
        sql = 'SELECT *\n                   FROM celestials\n                  WHERE celestialID IN (%s)' % keyString
        rs = self.mapObjectsDb.execute(sql)
        for row in rs:
            celestialNameData = self._GetCelestialNameDataFromLocalRow(row)
            self.rawCelestialCache[row['celestialID']] = celestialNameData
            celestialName = localization.GetImportantByLabel(celestialNameData[0], **celestialNameData[1])
            data.append(blue.DBRow(rowDescriptor, [row['celestialID'],
             celestialName,
             row['solarSystemID'],
             row['x'],
             row['y'],
             row['z'],
             None]))

        data = CRowset(rowDescriptor, data)
        return (data.columns, data)

    @telemetry.ZONE_METHOD
    def GetNPCStationNameFromLocalRow(self, row, requireLocalizedTexts = True):
        orbitID = row['orbitID']
        if row['celestialIndex'] is None:
            orbitID = row['solarSystemID']
        if not requireLocalizedTexts:
            return ''
        if row['useOperationName']:
            labelPath = 'UI/Locations/LocationNPCStationFormatter'
            operationName = get_station_operation_name(row['operationID'])
            operationNameEN = get_station_operation_name(row['operationID'], localization.const.LOCALE_SHORT_ENGLISH)
        else:
            labelPath = 'UI/Locations/LocationNPCStationFormatter_NoOpName'
            operationName = ''
            operationNameEN = ''
        locName = localization.GetByLabel(labelPath, orbitID=orbitID, corporationID=row['ownerID'], operationName=operationName)
        locNameEN = localization.GetByLabel(labelPath, localization.const.LOCALE_SHORT_ENGLISH, orbitID=orbitID, corporationID=row['ownerID'], operationName=operationNameEN)
        return localization.FormatImportantString(locName, locNameEN)

    def GetNpcStationName(self, stationID, solarSystemID, ownerID, operationID, languageID = None):
        celestialIndex, orbitIndex, useOperationName = self.stationLocalizationData[stationID]
        if celestialIndex is None:
            orbit_name = None
        elif orbitIndex is not None:
            orbit_name = localization.GetByLabel('UI/Locations/LocationMoonFormatter', solarSystemID=solarSystemID, romanCelestialIndex=formatUtil.IntToRoman(celestialIndex), orbitIndex=orbitIndex, languageID=languageID)
        else:
            orbit_name = localization.GetByLabel('UI/Locations/LocationPlanetFormatter', solarSystemID=solarSystemID, romanCelestialIndex=formatUtil.IntToRoman(celestialIndex), languageID=languageID)
        corp = self.eveowners.Get(ownerID)
        corp_name = corp.GetRawName(languageID=languageID)
        operation_name = get_station_operation_name(operationID, languageID)
        if useOperationName:
            return localization.GetByLabel(LOCATION_NPC_STATION_FORMATTER_RAW, orbitName=orbit_name, npcOrganizationName=corp_name, operationName=operation_name)
        return localization.GetByLabel(LOCATION_NPC_STATION_FORMATTER_NO_OP_NAME_RAW, orbitName=orbit_name, npcOrganizationName=corp_name)

    @telemetry.ZONE_METHOD
    def _GetCelestialNameDataFromLocalRow(self, row):
        celestialGroupID = row['groupID']
        celestialNameID = row['celestialNameID']
        celestialNameData = (None, None)
        if celestialNameID is not None and celestialGroupID != const.groupStargate:
            celestialNameData = ('UI/Util/GenericText', {'text': celestialNameID})
        elif celestialGroupID == const.groupAsteroidBelt:
            celestialNameData = ('UI/Locations/LocationAsteroidBeltFormatter', {'solarSystemID': row['solarSystemID'],
              'romanCelestialIndex': formatUtil.IntToRoman(row['celestialIndex']),
              'typeID': row['typeID'],
              'orbitIndex': row['orbitIndex']})
        elif celestialGroupID == const.groupMoon:
            celestialNameData = ('UI/Locations/LocationMoonFormatter', {'solarSystemID': row['solarSystemID'],
              'romanCelestialIndex': formatUtil.IntToRoman(row['celestialIndex']),
              'orbitIndex': row['orbitIndex']})
        elif celestialGroupID == const.groupPlanet:
            celestialNameData = ('UI/Locations/LocationPlanetFormatter', {'solarSystemID': row['solarSystemID'],
              'romanCelestialIndex': formatUtil.IntToRoman(row['celestialIndex'])})
        elif celestialGroupID == const.groupStargate:
            celestialNameData = ('UI/Locations/LocationStargateFormatter', {'destinationSystemID': row['celestialNameID']})
        elif celestialGroupID == const.groupSun:
            celestialNameData = ('UI/Locations/LocationStarFormatter', {'solarSystemID': row['solarSystemID']})
        return celestialNameData

    @telemetry.ZONE_METHOD
    def GetCelestialNameFromLocalRow(self, row, requireLocalizedTexts = True):
        if not requireLocalizedTexts:
            return ''
        lbl, kwargs = self._GetCelestialNameDataFromLocalRow(row)
        if lbl:
            return localization.GetByLabel(lbl, **kwargs)

    def ReloadLocalizedNames(self):
        self.LoadEveOwners()
        self.LoadEveLocations()

    def GetShipGroupByClassType(self):
        try:
            return self.shipGroupByClassType
        except AttributeError:
            self.shipGroupByClassType = {const.GROUP_CAPSULES: (const.groupCapsule,),
             const.GROUP_FRIGATES: (const.groupShuttle,
                                    const.groupRookieship,
                                    const.groupFrigate,
                                    const.groupAssaultFrigate,
                                    const.groupCovertOps,
                                    const.groupElectronicAttackShips,
                                    const.groupPrototypeExplorationShip,
                                    const.groupInterceptor,
                                    const.groupStealthBomber,
                                    const.groupExpeditionFrigate,
                                    const.groupLogisticsFrigate),
             const.GROUP_DESTROYERS: (const.groupDestroyer,
                                      const.groupInterdictor,
                                      const.groupTacticalDestroyer,
                                      const.groupCommandDestroyer),
             const.GROUP_CRUISERS: (const.groupCruiser,
                                    const.groupStrategicCruiser,
                                    const.groupCombatReconShip,
                                    const.groupForceReconShip,
                                    const.groupHeavyAssaultCruiser,
                                    const.groupHeavyInterdictors,
                                    const.groupLogistics,
                                    const.groupFlagCruiser),
             const.GROUP_BATTLECRUISERS: (const.groupBattlecruiser, const.groupAttackBattlecruiser, const.groupCommandShip),
             const.GROUP_BATTLESHIPS: (const.groupBattleship, const.groupBlackOps, const.groupMarauders),
             const.GROUP_CAPITALSHIPS: (const.groupCarrier,
                                        const.groupCapitalIndustrialShip,
                                        const.groupDreadnought,
                                        const.groupTitan,
                                        const.groupSupercarrier,
                                        const.groupForceAux,
                                        const.groupLancerDreadnought),
             const.GROUP_INDUSTRIALS: (const.groupBlockadeRunner,
                                       const.groupExhumer,
                                       const.groupFreighter,
                                       const.groupIndustrial,
                                       const.groupIndustrialCommandShip,
                                       const.groupJumpFreighter,
                                       const.groupMiningBarge,
                                       const.groupTransportShip),
             const.GROUP_POS: tuple((groupID for groupID in evetypes.GetGroupIDsByCategory(const.categoryStarbase))),
             const.GROUP_STRUCTURES: tuple((groupID for groupID in evetypes.GetGroupIDsByCategory(const.categoryStructure)))}

        return self.shipGroupByClassType

    def GetShipClassTypeByGroupID(self, groupID):
        for classTypeID, groupIDs in self.GetShipGroupByClassType().iteritems():
            if groupID in groupIDs:
                return classTypeID


eveConfig = EveConfig()

def GetStrippedEnglishMessage(messageID):
    msg = localization._GetRawByMessageID(messageID, 'en-us')
    if msg:
        regex = '</localized>|<localized>|<localized .*?>|<localized *=.*?>'
        return ''.join(re.split(regex, msg))
    else:
        return ''


def CfgFsdDustIcons():
    return cfg.fsdDustIcons


def CfgAverageMarketPrice():
    return cfg._averageMarketPrice


class Region(sysCfg.Row):
    __guid__ = 'eveCfg.Region'

    def __getattr__(self, name):
        if name == 'regionName':
            if self.regionID < const.mapWormholeRegionMin:
                return sysCfg.Row.__getattr__(self, 'regionName')
            else:
                return 'Unknown'
        return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'Region ID: %d, name: %s' % (self.regionID, self.regionName)


class Constellation(sysCfg.Row):
    __guid__ = 'eveCfg.Constellation'

    def __getattr__(self, name):
        if name == 'constellationName':
            if self.constellationID < const.mapWormholeConstellationMin:
                return sysCfg.Row.__getattr__(self, 'constellationName')
            else:
                return 'Unknown'
        return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'Constellation ID: %d, name: %s' % (self.constellationID, self.constellationName)


class SolarSystem(sysCfg.Row):
    __guid__ = 'eveCfg.SolarSystem'

    def __getattr__(self, name):
        if name == 'pseudoSecurity':
            value = sysCfg.Row.__getattr__(self, 'security')
            if value > 0.0 and value < 0.05:
                return 0.05
            else:
                return value
        return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'SolarSystem ID: %d, name: %s' % (self.solarSystemID, self.solarSystemName)


def StackSize(item):
    if item[const.ixQuantity] < 0:
        return 1
    return item[const.ixQuantity]


def Singleton(item):
    if item[const.ixQuantity] < 0:
        return -item[const.ixQuantity]
    if 30000000 <= item[const.ixLocationID] < 40000000:
        return 1
    return 0


def CheckShipHasFighterBay(shipID):
    item = sm.GetService('godma').GetItem(shipID)
    if not item:
        return False
    godmaSM = sm.GetService('godma').GetStateManager()
    return godmaSM.GetType(item.typeID).fighterCapacity > 0


def IsPreviewable(typeID):
    if not evetypes.Exists(typeID):
        return False
    if IsApparel(typeID):
        return True
    if IsShipSkin(typeID):
        return True
    if evetypes.GetGraphicID(typeID) is None:
        return False
    return evetypes.GetCategoryID(typeID) in const.previewCategories or evetypes.GetGroupID(typeID) in const.previewGroups


def IsShip(typeID):
    if not evetypes.Exists(typeID):
        return False
    return evetypes.GetCategoryID(typeID) == const.categoryShip


def IsShipSkin(typeID):
    if not evetypes.Exists(typeID):
        return False
    return evetypes.GetCategoryID(typeID) == const.categoryShipSkin


def IsApparel(typeID):
    if not evetypes.Exists(typeID):
        return False
    return evetypes.GetCategoryID(typeID) == const.categoryApparel


def IsBlueprint(typeID):
    if not evetypes.Exists(typeID):
        return False
    return evetypes.GetCategoryID(typeID) == const.categoryBlueprint


def IsPlaceable(typeID):
    if not evetypes.Exists(typeID):
        return False
    return evetypes.GetCategoryID(typeID) == const.categoryPlaceables


def GetCharacterType(characterID):
    if idCheckers.IsEveUser(characterID):
        return 'capsuleer'
    else:
        return 'unknown'


def IsOutlawStatus(securityStatus):
    if securityStatus is None:
        return False
    else:
        return round(securityStatus, 1) <= const.outlawSecurityStatus


OWNER_NAME_OVERRIDES = {OWNER_AURA_IDENTIFIER: 'UI/Agents/AuraAgentName',
 OWNER_SYSTEM_IDENTIFIER: 'UI/Chat/ChatEngine/EveSystem'}

class EveOwners(sysCfg.Row):
    __guid__ = 'cfg.EveOwners'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            name = 'ownerName'
        elif name == 'groupID':
            if self.typeID is None:
                return
            return evetypes.GetGroupID(self.typeID)
        if name == 'ownerName' and boot.role != 'client' and self.ownerNameID is not None:
            return localization.GetByMessageID(self.ownerNameID)
        return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'EveOwner ID: %d, "%s"' % (self.ownerID, self.ownerName)

    def GetRawName(self, languageID = None):
        if self.ownerNameID is not None:
            if self.ownerNameID in OWNER_NAME_OVERRIDES:
                return localization.GetByLabel(OWNER_NAME_OVERRIDES[self.ownerNameID], languageID)
            return localization.GetByMessageID(self.ownerNameID, languageID)
        return self.name

    def IsSystem(self):
        return self.ownerID <= 15

    def IsNPC(self):
        return idCheckers.IsNPC(self.ownerID)

    def IsCharacter(self):
        return self.groupID == const.groupCharacter

    def IsCorporation(self):
        return self.groupID == const.groupCorporation

    def IsAlliance(self):
        return self.typeID == const.typeAlliance

    def IsFaction(self):
        return self.groupID == const.groupFaction

    def Type(self):
        raise evetypes.TypeNotFoundException('Not supported anymore to get a whole type, please change the caller. Hint: you have self.typeID')

    def Group(self):
        raise evetypes.TypeNotFoundException('Not supported anymore to get a whole group, please change the caller. Hint: you have self.groupID')


class CrpTickerNames(sysCfg.Row):
    __guid__ = 'cfg.CrpTickerNames'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            return self.tickerName
        else:
            return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'CorpTicker ID: %d, "%s"' % (self.corporationID, self.tickerName)


class AllShortNames(sysCfg.Row):
    __guid__ = 'cfg.AllShortNames'

    def __getattr__(self, name):
        if name == 'name' or name == 'description':
            return self.shortName
        else:
            return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'AllianceShortName ID: %d, "%s"' % (self.allianceID, self.shortName)


class EveLocations(sysCfg.Row):
    __guid__ = 'dbrow.Location'

    def __setattr__(self, name, value):
        if name in ('id', 'header', 'line', 'locationName'):
            self.__dict__[name] = value
        else:
            raise RuntimeError('ReadOnly', name)

    def __getattr__(self, name):
        if name == 'name' or name == 'description' or name == 'locationName':
            locationName = sysCfg.Row.__getattr__(self, 'locationName')
            if boot.role == 'client' and idCheckers.IsAbyssalSpaceSystem(self.locationID):
                locationName = localization.GetByLabel('UI/Common/Unknown')
            elif (locationName is None or len(locationName) == 0) and self.locationNameID is not None:
                if isinstance(self.locationNameID, (int, long)):
                    locationName = localization.GetImportantByMessageID(self.locationNameID)
                elif isinstance(self.locationNameID, tuple):
                    locationName = localization.GetImportantByLabel(self.locationNameID[0], **self.locationNameID[1])
                if boot.role == 'client':
                    setattr(self, 'locationName', locationName)
            elif boot.role != 'client' and self.locationNameID is not None:
                locationName = localization.GetByMessageID(self.locationNameID)
            return locationName
        return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        return 'EveLocation ID: %d, "%s"' % (self.locationID, self.locationName)

    def GetRawName(self, languageID = None):
        if self.locationNameID is not None:
            return localization.GetByMessageID(self.locationNameID, languageID)
        if self.locationID in cfg.rawCelestialCache:
            lbl, kwargs = cfg.rawCelestialCache[self.locationID]
            return localization.GetByLabel(lbl, languageID, **kwargs)
        return self.name

    def Station(self):
        return cfg.GetSvc('stationSvc').GetStation(self.id)


class RamCompletedStatus(sysCfg.Row):
    __guid__ = 'cfg.RamCompletedStatus'

    def __getattr__(self, name):
        if name == 'name':
            name = 'completedStatusText'
        value = sysCfg.Row.__getattr__(self, name)
        if name == 'completedStatusText':
            value = localization.GetByMessageID(self.completedStatusTextID)
        elif name == 'description':
            return localization.GetByMessageID(self.descriptionID)
        return value

    def __str__(self):
        try:
            return 'RamCompletedStatus ID: %d, "%s"' % (self.completedStatus, self.completedStatusText)
        except:
            sys.exc_clear()
            return 'RamCompletedStatus containing crappy data'


class RamActivity(sysCfg.Row):
    __guid__ = 'cfg.RamActivity'

    def __getattr__(self, name):
        if name in ('activityName', 'name'):
            return localization.GetByMessageID(self.activityNameID)
        if name == 'description':
            return localization.GetByMessageID(self.descriptionID)
        return sysCfg.Row.__getattr__(self, name)

    def __str__(self):
        try:
            return 'RamActivity ID: %d, "%s"' % (self.activityID, self.activityName)
        except:
            sys.exc_clear()
            return 'RamActivity containing crappy data'


class OverviewDefault(sysCfg.Row):
    __guid__ = 'eveCfg.OverviewDefault'

    def __getattr__(self, name):
        if name == '_overviewName':
            return sysCfg.Row.__getattr__(self, 'overviewName')
        if name in ('name', 'overviewName'):
            return localization.GetByMessageID(self.overviewNameID)
        value = sysCfg.Row.__getattr__(self, name)
        return value

    def __str__(self):
        return 'DefaultOverview ID: %d, "%s"' % (self.overviewID, self.overviewName)


class Position(sysCfg.Row):
    __guid__ = 'cfg.Position'

    @property
    def latitude(self):
        return self.x

    @property
    def longitude(self):
        return self.y

    @property
    def radius(self):
        return self.z


def _LoadMessagesFromFSD():
    return fsdBinaryLoader.LoadFSDDataForCFG('res:/staticdata/dialogs.static', 'res:/staticdata/dialogs.schema', optimize=False)


def IsPolarisFrigate(typeID):
    return typeID in (const.typePolarisCenturion,
     const.typePolarisCenturionFrigate,
     const.typePolarisInspectorFrigate,
     const.typePolarisLegatusFrigate,
     const.typePolarisEnigmaFrigate)


def MakeConstantName(val, prefix):
    name = val.replace(' ', '')
    if name == '':
        name = 'invalidName_' + val
    name = prefix + name[0].upper() + name[1:]
    ret = ''
    okey = range(ord('a'), ord('z') + 1) + range(ord('A'), ord('Z') + 1) + range(ord('0'), ord('9') + 1)
    for ch in name:
        if ord(ch) in okey:
            ret += ch

    if ret == '':
        ret = 'invalidName_' + ret
    elif ord(ret[0]) in range(ord('0'), ord('9') + 1):
        ret = '_' + ret
    return ret


locationPathByFlagID = {const.flagCargo: 'UI/Ship/CargoHold',
 const.flagDroneBay: 'UI/Ship/DroneBay',
 const.flagShipHangar: 'UI/Ship/ShipMaintenanceBay',
 const.flagSpecializedFuelBay: 'UI/Ship/FuelBay',
 const.flagGeneralMiningHold: 'UI/Ship/GeneralMiningHold',
 const.flagSpecializedIceHold: 'UI/Ship/IceHold',
 const.flagSpecialAsteroidHold: 'UI/Ship/AsteroidHold',
 const.flagSpecializedGasHold: 'UI/Ship/GasHold',
 const.flagSpecializedMineralHold: 'UI/Ship/MineralHold',
 const.flagSpecializedSalvageHold: 'UI/Ship/SalvageHold',
 const.flagSpecializedShipHold: 'UI/Ship/ShipHold',
 const.flagSpecializedSmallShipHold: 'UI/Ship/SmallShipHold',
 const.flagSpecializedMediumShipHold: 'UI/Ship/MediumShipHold',
 const.flagSpecializedLargeShipHold: 'UI/Ship/LargeShipHold',
 const.flagSpecializedIndustrialShipHold: 'UI/Ship/IndustrialShipHold',
 const.flagSpecializedAmmoHold: 'UI/Ship/AmmoHold',
 const.flagSpecializedCommandCenterHold: 'UI/Ship/CommandCenterHold',
 const.flagSpecializedPlanetaryCommoditiesHold: 'UI/Ship/PlanetaryCommoditiesHold',
 const.flagSpecializedMaterialBay: 'UI/Ship/MaterialBay',
 const.flagFighterBay: 'UI/Ship/FighterBay',
 const.flagFrigateEscapeBay: 'UI/Ship/FrigateEscapeBay'}

def GetShipFlagLocationName(flagID):
    if flagID in const.hiSlotFlags:
        locationPath = 'UI/Ship/HighSlot'
    elif flagID in const.medSlotFlags:
        locationPath = 'UI/Ship/MediumSlot'
    elif flagID in const.loSlotFlags:
        locationPath = 'UI/Ship/LowSlot'
    elif flagID in const.rigSlotFlags:
        locationPath = 'UI/Ship/RigSlot'
    elif IsSubsystemFlagVisible(flagID):
        locationPath = 'UI/Ship/Subsystem'
    elif flagID in const.flagCorpSAGs:
        locationPath = 'UI/Corporations/Common/CorporateHangar'
    elif flagID in const.fighterTubeFlags:
        locationPath = 'UI/Ship/FighterLaunchTube'
    else:
        locationPath = locationPathByFlagID.get(flagID, '')
    if locationPath:
        return localization.GetByLabel(locationPath)
    else:
        return ''


def GetSunWarpInPoint(ballID, position, radius):
    offset = 100000
    x = position[0] + (radius + offset) * math.cos(radius)
    y = position[1] + radius / 5
    z = position[2] - (radius + offset) * math.sin(radius)
    return (x, y, z)


def GetPlanetWarpInPoint(ballID, position, radius):
    dx = float(position[0])
    dz = float(-position[2])
    f = float(dz) / float(math.sqrt(dx ** 2 + dz ** 2))
    if dz > 0 and dx > 0 or dz < 0 and dx > 0:
        f *= -1.0
    theta = math.asin(f)
    myRandom = random.Random(ballID)
    rr = (myRandom.random() - 1.0) / 3.0
    theta += rr
    offset = 1000000
    FACTOR = 20.0
    dd = math.pow((FACTOR - 5.0 * math.log10(radius / 1000000) - 0.5) / FACTOR, FACTOR) * FACTOR
    dd = min(10.0, max(0.0, dd))
    dd += 0.5
    offset += radius * dd
    d = radius + offset
    x = 1000000
    z = 0
    x = position[0] + math.sin(theta) * d
    y = position[1] + radius * math.sin(rr) * 0.5
    z = position[2] - math.cos(theta) * d
    return (x, y, z)


def GetWarpInPoint(ballID, position, radius):
    offset = 5000000
    p = const.jumpRadiusFactor / 100.0
    x = position[0] + (radius + offset) * math.cos(radius)
    y = position[1] + p * radius - 7500.0
    z = position[2] - (radius + offset) * math.sin(radius)
    return (x, y, z)


def GetActiveShip():
    return session.shipid


def InSpace():
    return bool(session.solarsystemid) and bool(session.shipid) and session.structureid in (session.shipid, None)


def InShip():
    return bool(session.shipid) and bool(session.shipid != session.structureid)


def InShipInSpace():
    return bool(session.solarsystemid) and bool(session.shipid) and not bool(session.structureid)


def IsDocked():
    return bool(session.stationid) or IsDockedInStructure()


def InStructure():
    return bool(session.structureid)


def IsDockedInStructure():
    return bool(session.structureid) and bool(session.structureid != session.shipid)


def IsControllingStructure():
    return bool(session.structureid) and bool(session.structureid == session.shipid)


def IsAtLocation(locationID):
    if locationID is None:
        return False
    elif InStructure():
        return locationID == session.structureid
    else:
        return locationID == session.locationid


def IsBookmarkModerator(corpRole):
    return corpRole & const.corpRoleChatManager == const.corpRoleChatManager
