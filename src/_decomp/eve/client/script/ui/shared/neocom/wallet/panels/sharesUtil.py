#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\sharesUtil.py
from menu import MenuLabel
from eve.client.script.ui.shared.neocom.corporation.corpVotingWindow import CorpVotingWindow
from eve.client.script.ui.shared.neocom.wallet.giveSharesDialog import GiveSharesDialog
from eve.common.lib import appConst
import inventorycommon.const as invConst
from eve.common.script.sys.idCheckers import IsCorporation
from eveservices.menu import GetMenuService

def GetSharesMenu(entry):
    m = []
    ownerID = entry.sr.node.ownerID
    corpID = entry.sr.node.corporationID
    shares = entry.sr.node.shares
    if ownerID == session.charid or ownerID == session.corpid and sm.GetService('corp').UserIsActiveCEO():
        m.append((MenuLabel('UI/Wallet/WalletWindow/MenuVotes'), OpenVotes, (corpID,)))
        m.append(None)
    if ownerID == session.charid or ownerID == session.corpid and appConst.corpRoleDirector & session.corprole != 0:
        m.append((MenuLabel('UI/Wallet/WalletWindow/MenuGiveShares'), GiveShares, (ownerID, corpID, shares)))
        m.append(None)
    if IsCorporation(ownerID):
        m.append([MenuLabel('UI/Wallet/WalletWindow/MenuOwner'), GetMenuService().GetMenuFromItemIDTypeID(ownerID, typeID=invConst.typeCorporation)])
    else:
        m.append([MenuLabel('UI/Wallet/WalletWindow/MenuOwner'), GetMenuService().CharacterMenu(ownerID)])
    m.append([MenuLabel('UI/Wallet/WalletWindow/MenuCorporation'), GetMenuService().GetMenuFromItemIDTypeID(corpID, typeID=invConst.typeCorporation)])
    return m


def OpenVotes(corpID):
    CorpVotingWindow.Open(corpID=corpID)


def GiveShares(ownerID, corpID, shares):
    GiveSharesDialog.CloseIfOpen()
    dlg = GiveSharesDialog(corporationID=corpID, maxShares=shares, shareholderID=ownerID)
    dlg.ShowModal()
