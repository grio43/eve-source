#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomTooltips.py
import localization
from eve.client.script.ui.shared.neocom.wallet import walletUtil
from eve.common.script.util.eveFormat import FmtISK

def LoadTooltipPanel(tooltipPanel, btnData):
    if btnData.id == 'wallet':
        LoadWalletTooltipPanel(tooltipPanel)


def LoadWalletTooltipPanel(tooltipPanel):
    showFractions = settings.char.ui.Get('walletShowCents', False)
    personalWealth = FmtISK(sm.GetService('wallet').GetWealth(), showFractions)
    tooltipPanel.AddLabelValue(label=localization.GetByLabel('Tooltips/Neocom/Balance'), value=personalWealth)
    canAccess = walletUtil.HaveReadAccessToCorpWalletDivision(session.corpAccountKey)
    if canAccess:
        corpWealth = FmtISK(sm.GetService('wallet').GetCorpWealthCached1Min(session.corpAccountKey), showFractions)
        tooltipPanel.AddLabelValue(label=localization.GetByLabel('Tooltips/Neocom/CorporationBalance'), value=corpWealth)
