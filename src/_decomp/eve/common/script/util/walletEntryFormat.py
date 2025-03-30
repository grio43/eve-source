#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\script\util\walletEntryFormat.py
from corporation.common.goals.link import get_goal_link
from eveaccounting import get_entry_format_localization_id
import evetypes
import eve.common.lib.appConst as appConst
from eve.common.script.sys.idCheckers import IsCorporation
from eve.common.script.util.eveFormat import GetName, GetLocation
from eve.common.script.util.walletEntryConst import ENTRY_LABEL_BY_REFERENCE
from localization import GetByLabel, GetByMessageID
from localization.uiutil import PrepareLocalizationSafeString
from logging import getLogger
import re
import uuid
logger = getLogger(__name__)
MANUAL_WALLET_REFERENCES = [appConst.refProjectPayouts, appConst.refDailyGoalPayouts, appConst.refCareerProgramPayouts] + appConst.COSMETIC_MARKET_TRANSACTION_REFS

def FmtWalletEntry(entryTypeID, o1, o2, arg1, pretty = 1, amount = 0.0, reason = None):
    if entryTypeID not in MANUAL_WALLET_REFERENCES:
        messageID = get_entry_format_localization_id(entryTypeID)
        if messageID is not None:
            return _FmtWalletEntryNormalized(messageID, GetName(o1), GetName(o2), arg1)
    return _FmtWalletEntryManual(entryTypeID, o1, o2, arg1, pretty, amount, reason)


def _FmtWalletEntryNormalized(messageID, name1, name2, arg1):
    return GetByMessageID(messageID, name1=name1, name2=name2, arg1=arg1, name=name1, arg=arg1)


def _FmtWalletEntryManual(entryTypeID, o1, o2, arg1, pretty, amount, reason):
    if entryTypeID == appConst.refBackwardCompatible:
        if pretty:
            return ''
        else:
            return GetByLabel('UI/Generic/FormatReference/backwardsCompatiable', type=entryTypeID, o1=o1, o2=o2, arg=arg1)
    if entryTypeID == appConst.refUndefined:
        if pretty:
            return ''
        else:
            return GetByLabel('UI/Generic/FormatReference/undefinedType', type=entryTypeID, o1=o1, o2=o2, arg=arg1)
    else:
        if entryTypeID == appConst.refCorporationPayment:
            name1 = GetName(o1)
            name2 = GetName(o2)
            if arg1 != -1:
                return GetByLabel('UI/Generic/FormatReference/corpPayment1', arg=GetName(arg1), name1=name1, name2=name2)
            return GetByLabel('UI/Generic/FormatReference/corpPayment2', name1=name1, name2=name2)
        if entryTypeID == appConst.refCSPA:
            name1 = GetName(o1)
            if arg1:
                return GetByLabel('UI/Generic/FormatReference/cspaServiceChargePaidBy', name1=name1, name2=GetName(arg1))
            else:
                return GetByLabel('UI/Generic/FormatReference/cspaServiceCharge', name=name1)
        elif entryTypeID == appConst.refCSPAOfflineRefund:
            name2 = GetName(o2)
            if arg1:
                return GetByLabel('UI/Generic/FormatReference/cspaServiceChargeRefundBy', name1=name2, name2=GetName(arg1))
            else:
                return GetByLabel('UI/Generic/FormatReference/cspaServiceChargeRefundByConcord', name1=name2)
        else:
            if entryTypeID == appConst.refBounty:
                return GetByLabel('UI/Generic/FormatReference/bountyPaidTo', name1=GetName(o1), name2=GetName(arg1))
            if entryTypeID == appConst.refBountyPrize:
                if arg1 == -1:
                    return GetByLabel('UI/Generic/FormatReference/bountyKilledMultipleEntities', name1=GetName(o2))
                else:
                    return GetByLabel('UI/Generic/FormatReference/bountyKilledHim', name1=GetName(o2), name2=GetName(arg1))
            else:
                if entryTypeID == appConst.refBountyPrizes:
                    locationName = GetLocation(arg1) or cfg.evelocations.Get(arg1).name
                    return GetByLabel('UI/Generic/FormatReference/bountyPrizes', location=locationName, name1=GetName(o2))
                if entryTypeID == appConst.refKillRightBuy:
                    name1 = GetName(o1)
                    name2 = GetName(o2)
                    return GetByLabel('UI/Generic/FormatReference/killRightFee', buyer=name1, seller=name2, name=GetName(arg1))
                if entryTypeID == appConst.refInsurance:
                    name1 = GetName(o1)
                    name2 = GetName(o2)
                    if arg1 > 0:
                        return GetByLabel('UI/Generic/FormatReference/insurancePaidByCoveringLoss', itemname=evetypes.GetName(arg1), name1=name1, name2=name2)
                    elif arg1 and arg1 < 0:
                        return GetByLabel('UI/Generic/FormatReference/insurancePaidForShip', location=GetLocation(-arg1), name1=name1, name2=name2, refID=-arg1)
                    else:
                        return GetByLabel('UI/Generic/FormatReference/insurancePaidTo', name1=name1, name2=name2)
                else:
                    if entryTypeID == appConst.refCorporationAccountWithdrawal:
                        name1 = GetName(o1)
                        name2 = GetName(o2)
                        return GetByLabel('UI/Generic/FormatReference/corpWithdrawl', name1=GetName(arg1), name2=name1, name3=name2)
                    if entryTypeID == appConst.refCorporationDividendPayment:
                        if o2 == appConst.ownerBank:
                            return GetByLabel('UI/Generic/FormatReference/corpDividendsPayed', name=GetName(o1))
                        else:
                            return GetByLabel('UI/Generic/FormatReference/corpDividendsPayedFrom', name1=GetName(o2), name2=GetName(arg1))
                    else:
                        if entryTypeID == appConst.refCorporationLogoChangeCost:
                            return GetByLabel('UI/Generic/FormatReference/corpLogoChangeFee', name1=GetName(o1), name2=GetName(arg1))
                        if entryTypeID == appConst.refReleaseOfImpoundedProperty:
                            return GetByLabel('UI/Generic/FormatReference/releaseImpoundFee', location=GetLocation(arg1), name1=GetName(o1), name2=GetName(o2))
                        if entryTypeID == appConst.refBrokerfee:
                            owner = cfg.eveowners.GetIfExists(o1)
                            if owner is not None:
                                return GetByLabel('UI/Generic/FormatReference/marketBrokersFeeBy', name1=owner.ownerName)
                            return GetByLabel('UI/Generic/FormatReference/marketBrokersFee')
                        if entryTypeID == appConst.refMarketProviderTax:
                            return GetByLabel('UI/Generic/FormatReference/marketProviderTaxAtStructure', structureID=arg1)
                        if entryTypeID == appConst.refMarketEscrow:
                            owner = cfg.eveowners.GetIfExists(o1 if arg1 == -1 else o2)
                            if owner is not None:
                                if amount < 0.0:
                                    return GetByLabel('UI/Generic/FormatReference/marketEscrowAuthorizedBy', name=owner.ownerName)
                            if amount < 0.0:
                                return GetByLabel('UI/Generic/FormatReference/marketEscrow')
                            else:
                                return GetByLabel('UI/Generic/FormatReference/marketEscrowRelease')
                        else:
                            if entryTypeID == appConst.refWarFee:
                                return GetByLabel('UI/Generic/FormatReference/warFee', name=GetName(arg1))
                            if entryTypeID == appConst.refAllianceMaintainanceFee:
                                return GetByLabel('UI/Generic/FormatReference/allianceMaintenceFee', name=GetName(arg1))
                            if entryTypeID == appConst.refSovereignityRegistrarFee:
                                return GetByLabel('UI/Generic/FormatReference/sovereigntyRegistrarFee', name=GetLocation(arg1))
                            if entryTypeID == appConst.refInfrastructureHubBill:
                                return GetByLabel('UI/Generic/FormatReference/infrastructureHubBillRef', name=GetLocation(arg1))
                            if entryTypeID == appConst.refSovereignityUpkeepAdjustment:
                                return GetByLabel('UI/Generic/FormatReference/sovereigntyAdjustmentFee', name=GetLocation(arg1))
                            if entryTypeID == appConst.refPlanetaryImportTax:
                                if arg1 is not None and arg1 != -1:
                                    planetName = cfg.evelocations.Get(arg1).name
                                else:
                                    planetName = GetByLabel('UI/Generic/Unknown')
                                return GetByLabel('UI/Generic/FormatReference/planetImportTax', name=GetName(o1), planet=planetName)
                            if entryTypeID == appConst.refPlanetaryExportTax:
                                if arg1 is not None and arg1 != -1:
                                    planetName = cfg.evelocations.Get(arg1).name
                                else:
                                    planetName = GetByLabel('UI/Generic/Unknown')
                                return GetByLabel('UI/Generic/FormatReference/planetExportTax', name=GetName(o1), planet=planetName)
                            if entryTypeID == appConst.refPlanetaryConstruction:
                                if arg1 is not None and arg1 != -1:
                                    planetName = cfg.evelocations.Get(arg1).name
                                else:
                                    planetName = GetByLabel('UI/Generic/Unknown')
                                return GetByLabel('UI/Generic/FormatReference/planetConstruction', name=GetName(o1), planet=planetName)
                            if entryTypeID == appConst.refWarSurrenderFee:
                                return GetByLabel('UI/Generic/FormatReference/WarFeeSurrender', loser=GetName(o1), winner=GetName(o2))
                            if entryTypeID == appConst.refWarAllyContract:
                                return GetByLabel('UI/Generic/FormatReference/WarAllyContract', defender=GetName(o1), ally=GetName(o2))
                            if entryTypeID == appConst.refReprocessingTax:
                                return GetByLabel('UI/Wallet/WalletWindow/ReprocessingWalletEntryDescription', characterName=GetName(o1), receiverName=GetName(o2))
                            if entryTypeID == appConst.refProjectPayouts:
                                if reason:
                                    corporation_id = arg1
                                    goal_id, goal_name = _GetProjectPayoutsData(reason)
                                    try:
                                        goal_id = uuid.UUID(goal_id).int
                                    except (AttributeError, TypeError, ValueError):
                                        return GetByLabel('UI/Generic/Unknown')

                                    if goal_id and goal_name:
                                        return _FormatProjectPayoutsEntry(corporation_id, goal_id, goal_name)
                                    return GetByLabel('UI/Generic/Unknown')
                            elif entryTypeID == appConst.refDailyGoalPayouts:
                                if reason:
                                    goal_name = _GetDailyPayoutsData(reason)
                                    return GetByLabel('UI/Generic/FormatReference/DailyGoalPayout', goal_name=goal_name, character_name=GetName(o2))
                            else:
                                if entryTypeID == appConst.refCareerProgramPayouts:
                                    return GetByLabel('UI/Generic/FormatReference/AirCareerProgramGoalPayout')
                                if entryTypeID in appConst.COSMETIC_MARKET_TRANSACTION_REFS:
                                    try:
                                        if entryTypeID == appConst.refCosmeticMarketSkinTransaction:
                                            if amount >= 0:
                                                return GetByLabel('UI/Generic/FormatReference/CosmeticMarketSkinSale')
                                            else:
                                                return GetByLabel('UI/Generic/FormatReference/CosmeticMarketSkinPurchase')
                                        reason = GetByLabel(ENTRY_LABEL_BY_REFERENCE[entryTypeID])
                                        if amount > 0 and entryTypeID != appConst.refCosmeticMarketSkinSale or amount < 0 and entryTypeID == appConst.refCosmeticMarketSkinSale:
                                            return GetByLabel('UI/Generic/FormatReference/Refund', reason=reason)
                                        return reason
                                    except KeyError as exc:
                                        logger.warning('Failed to format Wallet Entry for entry type %s: %s', entryTypeID, exc)

    if pretty:
        return PrepareLocalizationSafeString('-')
    else:
        return GetByLabel(labelNameAndPath='UI/Generic/FormatReference/unknowenJournalReference', ID=entryTypeID, arg=arg1, o1=o1, o2=o2)


def GetProjectPayoutsReason(goal_id, goal_name):
    if not goal_name:
        goal_name = ''
    elif len(goal_name) > 97:
        goal_name = goal_name[:97] + '...'
    reason = 'goal_id={goal_id}:goal_name={goal_name}'.format(goal_id=goal_id or '', goal_name=goal_name.encode('unicode-escape'))
    return reason


def _GetMessageId(reference_name):
    message_id = str(int(reference_name))
    return message_id


def GetDailyGoalPayoutsReason(goal_name):
    try:
        return _GetMessageId(goal_name)
    except ValueError as exc:
        logger.warning('Failed to encode wallet transaction reason for daily goal %s. Error: %s', goal_name, exc)
        return None


def GetCosmeticMarketPurchaseReason(reference_name):
    try:
        return _GetMessageId(reference_name)
    except ValueError as exc:
        logger.warning('Failed to encode wallet transaction reason for cosmetic market purchase %s. Error: %s', reference_name, exc)
        return None


def _GetProjectPayoutsData(reason):
    goal_id = None
    goal_name = None
    try:
        if reason.startswith('DESC: '):
            reason = reason[6:]
        matcher = re.search(pattern='goal_id=(.*):goal_name=', string=reason)
        if matcher:
            goal_id = matcher.group(1)
        goal_name = reason.replace('goal_id={goal_id}:goal_name='.format(goal_id=goal_id), '')
        goal_name = _RemoveSpacing(goal_name)
        goal_name = goal_name.decode('unicode-escape')
    except Exception as exc:
        logger.warning(u'Failed to get project payouts data for Wallet Entry from reason %s: %s', reason, exc)

    return (goal_id, goal_name)


def _GetMessageData(reason):
    matcher = re.search(pattern="DESC: '(\\d+)'", string=reason)
    if matcher:
        message_id = int(matcher.group(1))
        text = GetByMessageID(message_id)
        text = _RemoveSpacing(text)
        text = text.strip(' ')
        return text


def _GetDailyPayoutsData(reason):
    try:
        text = _GetMessageData(reason)
        if text:
            return text
        logger.warning("No goal name found for daily goal, using 'Unknown'. Reason: %s.", reason)
    except Exception as exc:
        logger.warning("Could not parse name for daily goal, using 'Unknown'. Reason: %s. Error: %s.", reason, exc)

    return GetByLabel('UI/Common/Unknown')


def _FormatProjectPayoutsEntry(corporation_id, goal_id, goal_name):
    if IsCorporation(corporation_id):
        return GetByLabel('UI/Generic/FormatReference/ProjectPayout', corp_name=GetName(corporation_id), project_name=get_goal_link(goal_id, goal_name))
    else:
        return GetByLabel('UI/Generic/FormatReference/ProjectPayoutGeneric', project_name=get_goal_link(goal_id, goal_name))


def _RemoveSpacing(text):
    new_text = ''
    for text_line in text.splitlines():
        new_text = new_text + text_line.strip() + ' '

    return new_text
