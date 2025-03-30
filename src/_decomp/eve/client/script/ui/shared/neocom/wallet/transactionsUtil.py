#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\transactionsUtil.py
import datetime
import sys
import types
import yaml
import evetypes
import log
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency, SafeGetName
from eve.common.lib import appConst
from eve.common.lib import appConst as const
from localization import GetByLabel, formatters
from utillib import KeyVal
descriptionByRefType = {appConst.refCorporationTaxNpcBounties: 'UI/Wallet/WalletWindow/HintNPCBountyTax',
 appConst.refCorporationTaxAgentRewards: 'UI/Wallet/WalletWindow/HintAgentRewardTax',
 appConst.refCorporationTaxAgentBonusRewards: 'UI/Wallet/WalletWindow/HintAgentBonusRewardTax',
 appConst.refCorporationTaxRewards: 'UI/Wallet/WalletWindow/HintCorporateRewardTax',
 appConst.refProjectDiscoveryTaxRewards: 'UI/Wallet/WalletWindow/HintProjectDiscoveryRewardTax'}
NO_TOOLTIP_TYPES = [appConst.refProjectPayouts, appConst.refDailyGoalPayouts, appConst.refCareerProgramPayouts] + appConst.COSMETIC_MARKET_TRANSACTION_REFS

def GetDerivedTransactions(transaction):
    derivedTransactions = []
    if not transaction.description:
        return derivedTransactions
    if transaction.description:
        try:
            descriptionDict = yaml.load(transaction.description, Loader=yaml.CSafeLoader)
            if type(descriptionDict) == types.DictType:
                for refTypeID in appConst.derivedTransactionParentMapping.keys():
                    if refTypeID in descriptionDict:
                        donorCorpID = transaction.ownerID1 if refTypeID == appConst.refCorporationTaxRewards else None
                        hintText = None
                        if refTypeID in descriptionByRefType:
                            hintText = descriptionByRefType[refTypeID]
                        taxTransaction = _GetDerivedCorporationTaxTransaction(transaction, descriptionDict, refTypeID, hintText, donorCorpID=donorCorpID)
                        derivedTransactions.insert(0, taxTransaction)

        except yaml.scanner.ScannerError as e:
            log.LogError('wallet::_GetDerivedTransactions: ScannerError: Could not parse wallet transaction description:', transaction.description)
            sys.exc_clear()

    return derivedTransactions


def _GetDerivedCorporationTaxTransaction(transaction, descriptionDict, entryTypeID, descriptionLabel, donorCorpID = None):
    corpID = descriptionDict[entryTypeID][0]
    taxAmount = descriptionDict[entryTypeID][1]
    taxTransaction = KeyVal(transaction)
    taxTransaction.amount = -taxAmount
    taxTransaction.sortValue = transaction.transactionID + 0.5
    taxTransaction.ownerID2 = corpID
    corporationName = cfg.eveowners.Get(corpID).name
    _, surcharge = descriptionDict.get(appConst.refBountySurcharge, (0, 0))
    taxPercentage = float(taxAmount) / (transaction.amount - surcharge + taxAmount) * 100
    taxTransaction.entryTypeID = entryTypeID
    transaction.amount += taxAmount
    transaction.balance += taxAmount
    if descriptionLabel is None:
        taxTransaction.description = ''
        return taxTransaction
    if donorCorpID is None:
        taxTransaction.description = GetByLabel(descriptionLabel, taxPercentage=taxPercentage, corporationName=corporationName, amountInIsk=FmtWalletCurrency(appConst.minCorporationTaxAmount, appConst.creditsISK))
    else:
        donorCorporationName = cfg.eveowners.Get(donorCorpID).name
        taxTransaction.description = GetByLabel(descriptionLabel, taxPercentage=taxPercentage, corporationName=corporationName, donorCorporationName=donorCorporationName, amountInIsk=FmtWalletCurrency(appConst.minCorporationTaxAmount, appConst.creditsISK))
    return taxTransaction


def ShouldTransactionTextBeClickable(entryTypeID):
    if entryTypeID == appConst.refProjectPayouts:
        return True
    return False


def GetTransactionHint(transaction):
    if not transaction.description:
        return None
    try:
        description = yaml.load(transaction.description, Loader=yaml.CSafeLoader)
    except yaml.scanner.ScannerError as e:
        log.LogError('wallet::_ParseDescription: ScannerError: Could not parse wallet transaction description:', transaction.description)
        sys.exc_clear()
        return None

    if type(description) != types.DictType:
        return None
    hintLines = []
    if transaction.entryTypeID == const.refBountyReimbursement:
        ownerIDs = description[const.recDescOwners].split(',')
        if description.get(const.recDescOwnersTrunc, 0):
            return GetByLabel('UI/Wallet/WalletWindow/HintBountyReimbursedTruncated', ownerList=formatters.FormatGenericList((cfg.eveowners.Get(ownerID).ownerName for ownerID in ownerIDs)), others=description.get(const.recDescOwnersTrunc, 0))
        else:
            return GetByLabel('UI/Wallet/WalletWindow/HintBountyReimbursed', ownerList=formatters.FormatGenericList((cfg.eveowners.Get(ownerID).ownerName for ownerID in ownerIDs), useConjunction=True))
    elif transaction.entryTypeID == const.refBountyPrize:
        try:
            ownerIDs = description[const.recDescOwners].split(',')
        except KeyError:
            pass
        else:
            if description.get(const.recDescOwnersTrunc, 0):
                return GetByLabel('UI/Wallet/WalletWindow/HintBountyPaidTruncated', ownerList=formatters.FormatGenericList((cfg.eveowners.Get(ownerID).ownerName for ownerID in ownerIDs)), others=description.get(const.recDescOwnersTrunc, 0))
            return GetByLabel('UI/Wallet/WalletWindow/HintBountyPaid', ownerList=formatters.FormatGenericList((cfg.eveowners.Get(ownerID).ownerName for ownerID in ownerIDs), useConjunction=True))

    elif transaction.entryTypeID in NO_TOOLTIP_TYPES:
        return None
    if const.recDescription in description:
        hintLines.append(description[const.recDescription])
    if const.recDescNpcBountyList in description:
        for typeID, numVictims in description.get(const.recDescNpcBountyList, {}).iteritems():
            hintLines.append(u'{} x {}'.format(SafeGetName(typeID), str(numVictims)))

        if const.recDescNpcBountyListTruncated in description:
            hintLines.append(GetByLabel('UI/Wallet/WalletWindow/HintBountyTruncated'))
    if const.recStoreItems in description:
        hintLines.append(GetByLabel('UI/Wallet/WalletWindow/HintVGpurchase'))
        for typeID, qty in description.get(const.recStoreItems, []):
            try:
                typeName = evetypes.GetName(typeID)
            except evetypes.TypeNotFoundException as e:
                log.LogError('wallet::_ParseDescription: TypeNotFoundException', e)
                sys.exc_clear()
                continue

            hintLines.append(GetByLabel('UI/Wallet/WalletWindow/HintItemNameQty', itemName=typeName, qty=int(qty)))

    if transaction.entryTypeID == const.refPlanetaryConstruction and not hintLines:
        ccUpgradeReason = ''
        if 'oldLevel' in description:
            ccUpgradeReason = GetByLabel('UI/PI/Planet/CommandCenterUpgradeReason', oldLevel=description['oldLevel'], newLevel=description['newLevel'])
        constructionReason = ''
        destructionReason = ''
        if 'constructions' in description:
            constructionParts = []
            for typeID, qty in description['constructions'].iteritems():
                constructionParts.append(GetByLabel('UI/Inventory/QuantityAndName', quantity=qty, name=evetypes.GetName(typeID)))

            constructionReason = GetByLabel('UI/PI/Planet/ConstructionReason', planet=transaction.referenceID, constructions='\r\n'.join(constructionParts))
        if 'destructions' in description:
            destructionParts = []
            for groupID, qty in description['destructions'].iteritems():
                destructionParts.append(GetByLabel('UI/Inventory/QuantityAndName', quantity=qty, name=evetypes.GetGroupNameByGroup(groupID)))

            destructionReason = GetByLabel('UI/PI/Planet/DestructionReason', destructions='\r\n'.join(destructionParts))
        hintLines.append(GetByLabel('UI/PI/Planet/NetworkUpdateTransactionReason', ccUpgrade=ccUpgradeReason, constructions=constructionReason, destructions=destructionReason))
    hintText = '<br>'.join(hintLines)
    return hintText or None


def GetLastNYearMonthTuples(numMonths):
    today = datetime.date.today()
    year = today.year
    month = today.month
    ret = []
    for i in xrange(numMonths):
        month -= 1
        if month == -1:
            month = 11
            year -= 1
        ret.append((year, month))

    return ret
