#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\contractutils.py
import blue
from eve.client.script.ui.util import uix
from eve.common.script.util.contractscommon import *
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
from localization.util import IsSessionLanguageConcise
import evetypes
from utillib import KeyVal
COL_PAY = '0xffcc2222'
COL_GET = '0xff00bb00'

def FmtISKWithDescription(isk, justDesc = False):
    iskFmt = FmtISK(isk, showFractionsAlways=0)
    isk = float(isk)
    if abs(isk) >= 1000000000000L:
        isk = long(isk / 10000000000L)
        if justDesc:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInTrillions', amount=isk / 100.0)
        else:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInTrillionsDetailed', iskAmount=iskFmt, amount=isk / 100.0)
    elif abs(isk) >= 1000000000:
        isk = long(isk / 10000000L)
        if justDesc:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInBillions', amount=isk / 100.0)
        else:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInBillionsDetailed', iskAmount=iskFmt, amount=isk / 100.0)
    elif abs(isk) >= 1000000:
        isk = long(isk / 10000L)
        if justDesc:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInMillions', amount=isk / 100.0)
        else:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInMillionDetailed', iskAmount=iskFmt, amount=isk / 100.0)
    elif abs(isk) >= 10000:
        isk = long(isk / 10L)
        if justDesc:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInThousands', amount=isk / 100.0)
        else:
            iskFmt = GetByLabel('UI/Contracts/Util/AmountInThousandsDetailed', iskAmount=iskFmt, amount=isk / 100.0)
    return iskFmt


def GetMarketTypes():
    data = []
    for typeID in evetypes.Iterate():
        blue.pyos.BeNice()
        if evetypes.IsPublished(typeID) and evetypes.IsGroupPublished(typeID) and evetypes.IsCategoryPublished(typeID):
            data.append(KeyVal(typeID=typeID, marketGroupID=evetypes.GetMarketGroupID(typeID), typeName=evetypes.GetName(typeID)))

    return data


def GetContractIcon(type):
    icons = {const.conTypeNothing: 'res:/ui/Texture/WindowIcons/contracts.png',
     const.conTypeItemExchange: 'res:/ui/Texture/WindowIcons/contractItemExchange.png',
     const.conTypeAuction: 'res:/ui/Texture/WindowIcons/contractAuction.png',
     const.conTypeCourier: 'res:/ui/Texture/WindowIcons/contractCourier.png',
     const.conTypeLoan: '64_15'}
    return icons.get(type, 'res:/ui/Texture/WindowIcons/contracts.png')


def GetColoredContractStatusText(status):
    cols = {0: 'ffffff',
     1: 'ffffff',
     2: 'ffffff',
     3: 'ffffff',
     4: 'ffffff',
     5: 'ffffff',
     6: 'ffffff',
     7: 'aa0000',
     8: 'ffffff'}
    col = cols[status]
    st = GetContractStatusText(status)
    return '<color=0xff%s>%s</color>' % (col, st)


def ConFmtDate(time, isText = False):
    if time < 0:
        return GetByLabel('UI/Contracts/Util/ContractExpiredEmphasized')
    res = ''
    d = time / const.DAY
    h = (time - d * const.DAY) / const.HOUR
    if isText:
        if d >= 1:
            res = GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=d)
        elif d < 0:
            res = GetByLabel('UI/Contracts/Util/ContractExpiredEmphasized')
        elif h >= 1:
            res = GetByLabel('UI/Contracts/Util/LessThanADay')
        else:
            res = GetByLabel('UI/Contracts/Util/LessThanAnHour')
    else:
        if d >= 1:
            if h > 0:
                res = GetByLabel('UI/Contracts/Util/DayToHour', days=d, hours=h)
            else:
                res = GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Day', days=d)
        elif h >= 1 and d == 0:
            res = GetByLabel('/Carbon/UI/Common/WrittenDateTimeQuantity/Hour', hours=h)
        if time / const.HOUR == 0:
            res = GetByLabel('UI/Contracts/Util/LessThanAnHour')
    return res


def GetContractTimeLeftText(c):
    if c.status == const.conStatusOutstanding:
        if c.dateExpired < blue.os.GetWallclockTime():
            return GetByLabel('UI/Contracts/Util/ContractExpired')
        else:
            return ConFmtDate(c.dateExpired - blue.os.GetWallclockTime(), c.type == const.conTypeAuction)
    else:
        return ''


def CutAt(txt, l):
    if len(txt) > l:
        return txt[:l - 3] + '...'
    else:
        return txt


def SelectItemTypeDlg(itemTypes):
    tmplst = []
    for typeID in itemTypes:
        itemTypeRow = GetByLabel('UI/Contracts/Util/ItemTypeLine', item=typeID, categoryName=evetypes.GetCategoryName(typeID))
        tmplst.append((itemTypeRow, typeID))

    if not tmplst:
        eve.Message('ConNoItemsFound')
        return
    elif len(tmplst) == 1:
        return tmplst[0][1]
    else:
        ret = uix.ListWnd(tmplst, 'generic', GetByLabel('UI/Contracts/Util/SelectItemType'), None, 1, windowName='contractSelectItemTypeDlg')
        return ret and ret[1]


def MatchInvTypeName(s, typeID):
    localized = evetypes.GetName(typeID)
    english = evetypes.GetEnglishName(typeID)
    return CaseInsensitiveSubMatch(s, localized) or CaseInsensitiveSubMatch(s, english)


def CaseInsensitiveSubMatch(matchStr, inStr):
    return matchStr.lower() in inStr.lower()


def TypeName(typeID):
    return evetypes.GetName(typeID)


def GroupName(groupID):
    return evetypes.GetCategoryNameByGroup(groupID)


def CategoryName(categoryID):
    return evetypes.GetCategoryNameByCategory(categoryID)


def IsSearchStringLongEnough(txt):
    error = None
    isLanguageConcise = IsSessionLanguageConcise()
    if isLanguageConcise and not txt:
        error = 'ConNeedAtLeastOneLetter'
    if not isLanguageConcise and (not txt or len(txt) < 3):
        error = 'ConNeedAtLeastThreeLetters'
    if error:
        eve.Message(error)
    return not error


def DoParseItemType(wnd, prevVal = None, marketOnly = False):
    itemTypes = []
    txt = wnd.GetValue()
    if len(txt) == 0 or not IsSearchStringLongEnough(txt):
        return
    if txt == prevVal:
        return
    for t in GetMarketTypes():
        if t.marketGroupID is None and marketOnly:
            continue
        if MatchInvTypeName(txt, t.typeID):
            itemTypes.append(t.typeID)

    typeID = SelectItemTypeDlg(itemTypes)
    if typeID:
        wnd.SetValue(TypeName(typeID))
    return typeID


def GetContractLabel(contract, contractItems, additionalColumns = ''):
    if contract.forCorp:
        issuerID = contract.issuerCorpID
    else:
        issuerID = contract.issuerID
    fromName = cfg.eveowners.Get(issuerID).ownerName
    if contract.acceptorID:
        toID = contract.acceptorID
    else:
        toID = contract.assigneeID
    if toID == 0:
        toName = GetByLabel('UI/Contracts/ContractEntry/NoneParen')
    else:
        toName = cfg.eveowners.Get(toID).ownerName
    name = GetContractTitle(contract, contractItems)
    label = '%s<t>%s<t>%s<t>%s%s' % (name,
     GetContractTypeText(contract.type),
     fromName,
     toName,
     additionalColumns)
    return label


def GetCorpseName(itemID):
    try:
        return cfg.evelocations.Get(itemID).name
    except StandardError:
        pass
