#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\wallet\panels\personal\plexPanel.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.inventory.plexVault import PlexVaultController, PlexVaultActions
from eve.client.script.ui.shared.neocom.wallet import walletConst
from fastcheckout.const import FROM_WALLET_BUY_PLEX
ACTIONS_PAD_TOP = 20

class PlexPanel(Container):
    default_name = 'PlexPanel'
    panelID = walletConst.PANEL_PLEX

    def ApplyAttributes(self, attributes):
        super(PlexPanel, self).ApplyAttributes(attributes)
        self.controller = PlexVaultController()
        self.ConstructPlexVaultActions()

    def ConstructPlexVaultActions(self):
        self.actions = PlexVaultActions(parent=self, align=uiconst.TOTOP, controller=self.controller, logContext=FROM_WALLET_BUY_PLEX, top=ACTIONS_PAD_TOP)
