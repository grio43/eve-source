#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\personalSharesPanel.py
from eve.client.script.ui.shared.neocom.wallet.panels.sharesPanel import SharesPanel

class PersonalSharesPanel(SharesPanel):

    def IsCorpWallet(self):
        return False

    def GetOwnerID(self):
        return session.charid
