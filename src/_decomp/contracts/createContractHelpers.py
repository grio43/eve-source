#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contracts\createContractHelpers.py
import eve.common.lib.appConst as appConst
from eve.common.script.sys.idCheckers import IsCorporation, IsCharacter, IsNPC, IsStation
import eve.common.script.util.contractscommon as cc
import inventorycommon.const as invConst
from eveexceptions import UserError
from localization import GetByLabel
from utillib import KeyVal

def GetMaxNumContracts(forCorp, characterSkillInfo):
    if forCorp:
        skillLvl = characterSkillInfo[invConst.typeCorporationContracting]
        maxNumContracts = cc.NUM_CONTRACTS_BY_SKILL_CORP[skillLvl]
    else:
        skillLvl = characterSkillInfo[invConst.typeContracting]
        advSkillLvl = characterSkillInfo[invConst.typeAdvancedContracting]
        maxNumContracts = cc.NUM_CONTRACTS_BY_SKILL[skillLvl] + cc.NUM_CONTRACTS_BY_SKILL[advSkillLvl]
    return maxNumContracts


def IsInnerCorpContract(myCorpID, assignedToID, getCorporationIDForCharacterFunc):
    if assignedToID <= 0:
        return False
    if IsCorporation(assignedToID):
        if assignedToID == myCorpID:
            return True
    elif IsCharacter(assignedToID):
        assigneeCorpID = getCorporationIDForCharacterFunc(assignedToID)
        if assigneeCorpID == myCorpID and not IsNPC(myCorpID):
            return True
    return False


def VerifyCanCreateMoreContracts(forCorp, innerCorp, maxNumContractsForCharacter, numOutstandingContracts):
    if forCorp and numOutstandingContracts.myCorpTotal >= cc.MAX_NUM_CONTRACTS:
        raise UserError('ConTooManyContractsMax', {'max': cc.MAX_NUM_CONTRACTS})
    if not forCorp and numOutstandingContracts.myCharTotal >= cc.MAX_NUM_CONTRACTS:
        raise UserError('ConTooManyContractsMax', {'max': cc.MAX_NUM_CONTRACTS})
    if innerCorp:
        maxNumContracts = cc.MAX_NUM_CONTRACTS
    else:
        maxNumContracts = maxNumContractsForCharacter
    if forCorp:
        if innerCorp:
            n = numOutstandingContracts.myCorpTotal
        else:
            n = numOutstandingContracts.nonCorpForMyCorp
    elif innerCorp:
        n = numOutstandingContracts.myCharTotal
    else:
        n = numOutstandingContracts.nonCorpForMyChar
    if n + 1 > maxNumContracts >= 0:
        raise UserError('ConTooManyContractsMax', {'max': maxNumContracts})


def SanityCheckContract(contractInfo):
    if contractInfo.contractType == appConst.conTypeAuction:
        if contractInfo.price > contractInfo.collateral > 0:
            raise UserError('ConAuctionBuyoutTooSmall')
        if contractInfo.price < cc.const_conBidMinimum and contractInfo.assignedToID == 0:
            reason = GetByLabel('UI/Contracts/ContractsWindow/ErrorMinimumBidTooLow', minimumBid=cc.const_conBidMinimum)
            raise UserError('CustomInfo', {'info': reason})


def GetBrokersFeeAndDeposit(solarSystemID, warFactionID, characterSkillInfo, contractInfo):
    if contractInfo.isPrivate > 0:
        brokersFee = cc.const_conBrokersFeeMinimum
        deposit = 0.0
    else:
        skillLevels = KeyVal()
        skillLevels.brokerRelations = characterSkillInfo[invConst.typeBrokerRelations]
        skillLevels.accounting = characterSkillInfo[invConst.typeAccounting]
        fees = cc.CalcContractFees(contractInfo.price, contractInfo.reward, contractInfo.contractType, contractInfo.isPrivate, contractInfo.minutesExpire, skillLevels, solarSystemID, warFactionID)
        brokersFee = fees.brokersFeeAmt
        deposit = fees.depositAmt
    return (brokersFee, deposit)


def GetCrateLabel(contractInfo):
    label = GetByLabel('UI/Contracts/CrateLabel')
    if contractInfo.contractType == appConst.conTypeCourier:
        if IsStation(contractInfo.destinationID):
            label = cfg.evelocations.Get(contractInfo.destinationID).name
        else:
            structureInfo = sm.GetService('structureDirectory').GetStructureInfo(contractInfo.destinationID)
            label = '%s (%s)' % (structureInfo.itemName, cfg.eveowners.Get(structureInfo.ownerID).name)
    return label


def GetStartLocationIDs(_solarsystemid2, contractInfo):
    startStationID = contractInfo.startStationID
    startSolarSystemID = _solarsystemid2
    startRegionID = 0
    if contractInfo.startStationID > 0:
        startSolarSystemID = cfg.evelocations.Get(contractInfo.startStationID).solarSystemID
        startRegionID = cfg.mapSystemCache.Get(startSolarSystemID).regionID
    return (startRegionID, startSolarSystemID, startStationID)


def GetEndDestinationIDs(contractInfo):
    endStationID = contractInfo.startStationID
    endSolarSystemID = 0
    endRegionID = 0
    if contractInfo.destinationID > 0:
        endSolarSystemID = cfg.evelocations.Get(contractInfo.destinationID).solarSystemID
        endRegionID = cfg.mapSystemCache.Get(endSolarSystemID).regionID
        endStationID = contractInfo.destinationID
    return (endRegionID, endSolarSystemID, endStationID)
