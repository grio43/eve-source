#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\ecuContainer.py
import carbonui.const as uiconst
import evetypes
import blue
import localization
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from eve.client.script.ui.control.entries.generic import Generic
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet.pinContainers.BasePinContainer import BasePinContainer, CaptionAndSubtext
from eve.client.script.ui.shared.planet import planetCommon
from eve.client.script.ui.shared.planet.surveyUI import SurveyWindow
import eve.common.script.planet.entities.basePin as basePin
from eve.common.lib import appConst as const

class ECUContainer(BasePinContainer):
    default_name = 'ECUContainer'
    default_height = 185
    default_width = 300
    INFO_CONT_HEIGHT = 80
    panelIDs = [planetCommon.PANEL_SURVEYFORDEPOSITS, planetCommon.PANEL_PRODUCTS] + BasePinContainer.panelIDs

    def _GetInfoCont(self):
        self.currDepositTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/Extracting'), align=uiconst.TOTOP)
        self.timeToDeplTxt = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/TimeToDepletion'), align=uiconst.TOTOP)
        self.currCycleGauge = Gauge(parent=self.infoContRight, value=0.0, color=planetCommon.PLANET_COLOR_CYCLE, label=localization.GetByLabel('UI/PI/Common/CurrentCycle'), cyclic=True, align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.currCycleOutputTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/CurrentCycleOutput'), align=uiconst.TOTOP)

    def _UpdateInfoCont(self):
        currentTime = blue.os.GetWallclockTime()
        if self.pin.programType is not None and self.pin.qtyPerCycle > 0 and self.pin.expiryTime > currentTime:
            timeToDepletion = self.pin.GetTimeToExpiry()
            qtyRemaining = int(timeToDepletion / self.pin.GetCycleTime()) * self.pin.qtyPerCycle
            totalTimeLeft = timeToDepletion
            self.timeToDeplTxt.SetCaption(localization.GetByLabel('UI/PI/Common/TimeToDepletion'))
            if totalTimeLeft < const.DAY:
                totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=long(totalTimeLeft))
            else:
                totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeWritten', time=long(totalTimeLeft))
            deposName = evetypes.GetName(self.pin.programType)
            if self.pin.activityState < basePin.STATE_IDLE:
                currCycle = 0
                currCycleProportion = 0.0
                cycleTime = 0
                currCycleOutput = localization.GetByLabel('UI/PI/Common/NoneOutput')
            else:
                currCycle = currentTime - self.pin.lastRunTime
                currCycleProportion = currCycle / float(self.pin.GetCycleTime())
                cycleTime = self.pin.GetCycleTime()
                currCycleOutput = localization.GetByLabel('UI/PI/Common/UnitsAmount', amount=self.pin.GetProgramOutput(blue.os.GetWallclockTime()))
            if self.IsSomeProductUnrouted():
                deposName += '\n<color=red>%s</color>' % localization.GetByLabel('UI/PI/Common/NotRouted')
        else:
            currCycle = 0L
            totalTimeLeft = localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=0L)
            currCycleProportion = 0.0
            cycleTime = 0L
            deposName = '<color=red>%s</color>' % localization.GetByLabel('UI/PI/Common/ProgramNotActive')
            qtyRemaining = 0
            currCycleOutput = localization.GetByLabel('UI/PI/Common/NoneOutput')
        self.currDepositTxt.SetIcon(self.pin.programType)
        self.currDepositTxt.SetSubtext(deposName)
        if sm.GetService('planetUI').GetCurrentPlanet().IsInEditMode():
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
            self.timeToDeplTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/InactiveEditMode'))
        else:
            self.currCycleGauge.SetValueInstantly(currCycleProportion)
            self.timeToDeplTxt.SetSubtext(totalTimeLeft)
            self.currCycleGauge.SetSubText(localization.GetByLabel('UI/PI/Common/CycleTimeElapsed', currTime=currCycle, totalTime=cycleTime))
        self.currCycleOutputTxt.SetSubtext(currCycleOutput)

    def OpenSurveyWindow(self):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            sm.GetService('planetUI').myPinManager.EnterSurveyMode(self.pin.id)
            self.CloseByUser()
            return
        cont = ContainerAutoSize(parent=self.actionCont, align=uiconst.TOTOP, padding=4)
        EveLabelMedium(text=localization.GetByLabel('UI/PI/Common/CantSurveyInEditMode'), parent=cont, align=uiconst.TOTOP)
        return cont

    def GetStatsEntries(self):
        scrolllist = BasePinContainer.GetStatsEntries(self)
        if self.pin.programType is not None:
            label = '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/Extracting'), evetypes.GetName(self.pin.programType))
            scrolllist.append(GetFromClass(Generic, {'label': label}))
        else:
            label = '%s<t>%s' % (localization.GetByLabel('UI/PI/Common/Extracting'), localization.GetByLabel('UI/PI/Common/NothingExtracted'))
            scrolllist.append(GetFromClass(Generic, {'label': label}))
        return scrolllist

    def _DecommissionSelf(self, *args):
        if planetCommon.PinHasBeenBuilt(self.pin.id):
            surveyWnd = SurveyWindow.GetIfOpen()
            if surveyWnd and surveyWnd.ecuPinID == self.pin.id:
                sm.GetService('planetUI').ExitSurveyMode()
        BasePinContainer._DecommissionSelf(self)
