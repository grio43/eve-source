#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpBillsUtil.py
import evetypes
from eve.client.script.ui.shared.neocom.wallet.walletUtil import FmtWalletCurrency
from eve.common.lib import appConst
from billtypes.data import get_bill_type_name, get_bill_type_name_id
from localization import GetByLabel, GetByMessageID

def DoCfgPrimingForBills(bills):
    if not bills or len(bills) == 0:
        return
    owners = []
    locs = []
    relevantBillTypes = (appConst.billTypeMarketFine, appConst.billTypeRentalBill, appConst.billTypeBrokerBill)
    for bill in bills:
        for ownerID in (bill.creditorID, bill.debtorID):
            if ownerID not in owners:
                owners.append(ownerID)

        if bill.billTypeID in relevantBillTypes:
            if bill.externalID != -1 and bill.externalID2 != -1:
                if bill.externalID2 not in locs:
                    locs.append(bill.externalID2)

    if len(owners):
        cfg.eveowners.Prime(owners)
    if len(locs):
        cfg.evelocations.Prime(locs)


def GetTextForBill(bill, data):
    billTypeName = GetByMessageID(get_bill_type_name_id(bill.billTypeID))
    textList = [billTypeName,
     '<t>',
     FmtWalletCurrency(bill.amount, appConst.creditsISK),
     '<t>',
     GetByLabel('UI/Wallet/WalletWindow/FmtWalletDate', dt=bill.dueDateTime),
     '<t>',
     cfg.eveowners.Get(bill.debtorID).name,
     '<t>',
     cfg.eveowners.Get(bill.creditorID).name,
     '<t>',
     GetByLabel('UI/Wallet/WalletWindow/FmtInterest', interest=bill.interest)]
    data.Set('sort_%s' % GetByLabel('UI/Common/Date'), (bill.dueDateTime, bill.billID))
    data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderAmount'), bill.amount)
    data.Set('sort_%s' % GetByLabel('UI/Wallet/WalletWindow/ColHeaderInterest'), bill.interest)
    if bill.billTypeID == appConst.billTypeMarketFine:
        if bill.externalID != -1 and bill.externalID2 != -1:
            textList.append('<t>')
            textList.append(evetypes.GetName(bill.externalID))
            textList.append('<t>')
            textList.append(cfg.evelocations.Get(bill.externalID2).name)
        else:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/Something'))
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/SomeMarket'))
    elif bill.billTypeID == appConst.billTypeRentalBill:
        if bill.externalID != -1 and bill.externalID2 != -1:
            typeID = bill.externalID
            locationID = bill.externalID2
            if typeID == appConst.typeOfficeRental:
                whatOffice = GetByLabel('UI/Wallet/WalletWindow/Office')
            else:
                whatOffice = evetypes.GetName(typeID)
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/RentalOffice', whatOffice=whatOffice, location=cfg.evelocations.Get(locationID).name))
        else:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/BillFactoryOrOffice'))
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/SomeStation'))
    elif bill.billTypeID == appConst.billTypeBrokerBill:
        if bill.externalID != -1 and bill.externalID2 != -1:
            textList.append('<t>')
            textList.append(bill.externalID)
            textList.append('<t>')
            textList.append(cfg.evelocations.Get(bill.externalID2).name)
        else:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Generic/Unknown'))
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/Somewhere'))
    elif bill.billTypeID == appConst.billTypeWarBill:
        if bill.externalID != -1:
            textList.append('<t>')
            textList.append(cfg.eveowners.Get(bill.externalID).ownerName)
        else:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/Someone'))
    elif bill.billTypeID == appConst.billTypeAllianceMaintainanceBill:
        if bill.externalID != -1:
            textList.append('<t>')
            textList.append(cfg.eveowners.Get(bill.externalID).ownerName)
        else:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/SomeAlliance'))
    elif bill.billTypeID == appConst.billTypeInfrastructureHub:
        if bill.externalID2 != -1:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/SolarSystem', name=cfg.evelocations.Get(bill.externalID2).name))
        else:
            textList.append('<t>')
            textList.append(GetByLabel('UI/Wallet/WalletWindow/SolarSystem', name=GetByLabel('UI/Wallet/WalletWindow/Somewhere')))
    return ''.join(textList)
