#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\corp\corpSharesPanel.py
from eve.client.script.ui.shared.neocom.wallet.panels.sharesPanel import SharesPanel

class CorpSharesPanel(SharesPanel):

    def IsCorpWallet(self):
        return True

    def GetOwnerID(self):
        return session.corpid
