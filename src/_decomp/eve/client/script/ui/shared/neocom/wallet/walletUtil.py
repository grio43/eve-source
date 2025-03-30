#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\walletUtil.py
import logging
import sys
import evetypes
from carbonui.util.color import Color
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.shared.neocom.wallet import walletConst
from eve.client.script.ui.shared.neocom.wallet.walletConst import corpWalletRoles, CURRENCY_DISPLAY_LABEL
from eve.client.script.ui.util.uix import ListWnd
from eve.common.lib import appConst
from eve.common.script.util.eveFormat import FmtCurrency
from localization import GetByLabel
logger = logging.getLogger(__name__)

def GetSettingValue(key):
    return settings.char.ui.Get(key, walletConst.SETTING_DEFAULTS[key])


def ToggleSetting(settingName):
    currVal = GetSettingValue(settingName)
    settings.char.ui.Set(settingName, not currVal)


def FmtWalletCurrency(amt, currency = appConst.creditsISK, showFractions = None):
    if showFractions is None:
        showFractions = GetSettingValue('walletShowCents')
        if not showFractions and 1 < abs(amt) and abs(amt) < sys.maxint:
            amt = int(amt)
    return FmtCurrency(amt, showFractionsAlways=showFractions, currency=currency)


def AmAccountantOrJuniorAccountant():
    return bool(session.corprole & (appConst.corpRoleJuniorAccountant | appConst.corpRoleAccountant))


def AmAccountantOrTrader():
    return bool(session.corprole & (appConst.corpRoleAccountant | appConst.corpRoleTrader))


def AmBrandManager():
    return bool(session.corprole & appConst.corpRoleBrandManager)


def AmDirector():
    return bool(session.corprole & appConst.corpRoleDirector)


def HaveAccessToCorpWallet():
    return bool(AmAccountantOrJuniorAccountant() or GetAccessibleCorpWalletDivisionIDs())


def HaveAccessToCorpWalletAndActiveDivision():
    return bool(HaveAccessToCorpWallet() and HaveAccessToCorpWalletDivision(session.corpAccountKey))


def HaveAccessToCorpEMWallet():
    return bool(AmBrandManager())


def HaveAccessToCorpLPWallet():
    return bool(AmDirector())


def HaveAccessToCorpWalletDivision(division):
    if division is None:
        return False
    return bool(session.corprole & corpWalletRoles[division])


def HaveReadAccessToCorpWalletDivision(division):
    if division is None:
        return False
    return bool(session.corprole & corpWalletRoles[division])


def GetAccessibleCorpWalletDivisionIDs():
    return filter(HaveAccessToCorpWalletDivision, corpWalletRoles)


def GetFirstAccesibleCorpWalletDivisionID():
    divisionIDs = GetAccessibleCorpWalletDivisionIDs()
    if divisionIDs:
        return divisionIDs[0]


def GetBalanceFormatted(amount, color = Color.WHITE, currency = appConst.creditsISK):
    text = FmtWalletCurrency(amount, currency)
    return GetByLabel(CURRENCY_DISPLAY_LABEL, color=color, currency=text)


def GetDivisionName(divisionID):
    if not divisionID:
        logger.warn('Tried to get division name with no divisionID', exc_info=True)
        return ''
    names = sm.GetService('corp').GetDivisionNames()
    return names.get(divisionID - 1000 + 8, '')


def SelectWalletDivision(*args):
    choices = SortListOfTuples([ (acctID, (sm.GetService('corp').GetCorpAccountName(acctID), acctID)) for acctID in GetAccessibleCorpWalletDivisionIDs() ])
    retval = ListWnd(choices, listtype='generic', caption=GetByLabel('UI/Wallet/WalletWindow/SelectDivision'))
    if retval:
        sm.GetService('corp').SetAccountKey(retval[1])


def CheckSetDefaultWalletDivision(*args):
    divisionIDs = GetAccessibleCorpWalletDivisionIDs()
    if session.corpAccountKey is None and divisionIDs:
        sm.GetService('corp').SetAccountKey(divisionIDs[0])


def SafeGetName(typeID):
    try:
        return evetypes.GetName(typeID)
    except evetypes.TypeNotFoundException:
        return GetByLabel('UI/Generic/Unknown')
