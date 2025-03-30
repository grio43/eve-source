#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\ExtractorContainer.py
import blue
import dogma.data
import evetypes
import localization
from carbon.common.script.util.format import FmtTime, FmtTimeInterval
from dogma.attributes.format import GetFormatAndValue
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import BasePinContainer, CaptionAndSubtext
from eve.client.script.ui.shared.planet.pinContainers.obsoletePinContainer import ObsoletePinContainer
from eve.client.script.ui.shared.planet import planetCommon as planetCommonUI
from eve.common.lib import appConst
from eve.common.script.planet.entities import basePin

class ExtractorContainer(ObsoletePinContainer):
    default_name = 'ExtractorContainer'
    INFO_CONT_HEIGHT = 95

    def ApplyAttributes(self, attributes):
        BasePinContainer.ApplyAttributes(self, attributes)

    def _GetInfoCont(self):
        self.currDepositTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/Extracting'), top=0)
        self.depositsLeftTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/TotalAmountLeft'), top=40)
        self.timeToDeplTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/TimeToDepletion'), top=70)
        self.currCycleGauge = Gauge(parent=self.infoContRight, value=0.0, color=planetCommonUI.PLANET_COLOR_CYCLE, label=localization.GetByLabel('UI/PI/Common/CurrentCycle'), cyclic=True)
        self.amountPerCycleTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/OutputPerCycle'), top=40)
        self.amountPerHourTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/OutputPerHour'), top=70)

    def _UpdateInfoCont(self):
        if self.pin.depositType is not None and self.pin.depositQtyPerCycle > 0:
            timeToDepletion = self.pin.GetTimeToDepletion()
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(localization.GetByLabel('UI/PI/Common/TimeToDepletion'))
            if totalTimeLeft < appConst.DAY:
                totalTimeLeft = FmtTime(float(totalTimeLeft))
            else:
                totalTimeLeft = FmtTimeInterval(long(totalTimeLeft), breakAt='hour')
            deposName = evetypes.GetName(self.pin.depositType)
            if self.pin.activityState < basePin.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                cycleTime = 0
            else:
                currCycle = blue.os.GetWallclockTime() - self.pin.lastRunTime
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
                cycleTime = self.pin.GetCycleTime()
        else:
            currCycle = 0
            totalTimeLeft = FmtTime(0)
            currCycleProportion = 0.0
            cycleTime = 0
            deposName = localization.GetByLabel('UI/PI/Common/NothingExtracted')
        self.currDepositTxt.SetIcon(self.pin.depositType)
        self.currDepositTxt.SetSubtext(deposName)
        self.depositsLeftTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.depositQtyRemaining))
        if self.pin.IsInEditMode():
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            self.timeToDeplTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=long(currCycle), totalTime=long(cycleTime)))
        self.amountPerCycleTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.depositQtyPerCycle))
        attr = dogma.data.get_attribute_with_default(appConst.attributeLogisticalCapacity)
        self.amountPerHourTxt.SetSubtext(GetFormatAndValue(attr, self.pin.GetOutputVolumePerHour()))
