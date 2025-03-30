#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\insurance\insuranceTooltip.py
from carbon.common.lib.const import DAY
from eve.client.script.ui.eveColor import WARNING_ORANGE_HEX
from eve.common.script.util.eveFormat import FmtISK
from localization import GetByLabel
import blue

def LoadInfoInsuranceTooltip(tooltipPanel, typeID, contract):
    tooltipPanel.LoadGeneric1ColumnTemplate()
    tooltipPanel.LoadStandardSpacingOld()
    if contract and contract.ownerID in (session.corpid, session.charid):
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Insurance/ShipInsured'))
        insuranceName = sm.GetService('info').GetInsuranceName(contract.fraction)
        tooltipPanel.AddLabelMedium(text=insuranceName)
        price = sm.GetService('insurance').GetInsurancePrice(typeID)
        payout = FmtISK(price * contract.fraction)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Insurance/EstimatedPayoutWithValue', estimatedPayout=payout))
        timeDiff = contract.endDate - blue.os.GetWallclockTime()
        days = timeDiff / DAY
        timeText = GetByLabel('UI/Insurance/TimeLeft', time=timeDiff)
        if days < 5:
            timeText = '<color=%s>%s</color>' % (WARNING_ORANGE_HEX, timeText)
        tooltipPanel.AddLabelMedium(text=timeText)
    else:
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Insurance/ShipUninsured'))
