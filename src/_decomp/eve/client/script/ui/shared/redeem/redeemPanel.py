#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\redeem\redeemPanel.py
from eve.client.script.ui.shared.redeem.newRedeemPanel import RedeemPanelNew
from eve.client.script.ui.shared.redeem.oldRedeemPanel import RedeemPanel

def GetRedeemPanel():
    return RedeemPanelNew


def GetOldRedeemPanel():
    return RedeemPanel
