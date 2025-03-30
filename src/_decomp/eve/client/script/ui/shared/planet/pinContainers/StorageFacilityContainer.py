#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\pinContainers\StorageFacilityContainer.py
import carbonui.const as uiconst
import blue
import localization
from carbonui.primitives.container import Container
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.shared.planet.pinContainers.storageIcon import StorageIcon
from .BasePinContainer import BasePinContainer, CaptionAndSubtext
from eve.client.script.ui.shared.planet import planetCommon

class StorageFacilityContainer(BasePinContainer):
    default_name = 'StorageFacilityContainer'
    INFO_CONT_HEIGHT = 80
    panelIDs = [planetCommon.PANEL_STORAGE] + BasePinContainer.panelIDs

    def _GetInfoCont(self):
        self.storageGauge = Gauge(parent=self.infoContLeft, value=0.0, color=planetCommon.PLANET_COLOR_STORAGE, label=localization.GetByLabel('UI/PI/Common/Storage'), align=uiconst.TOTOP, padding=(0, 0, 10, 4))
        self.cooldownTimer = CaptionAndSubtext(parent=self.infoContLeft, caption=localization.GetByLabel('UI/PI/Common/NextTransferAvailable'), align=uiconst.TOTOP)
        self.itemsTxt = CaptionAndSubtext(parent=self.infoContRight, caption=localization.GetByLabel('UI/PI/Common/StoredItems'), state=uiconst.UI_DISABLED, align=uiconst.TOTOP)
        self.iconCont = Container(parent=self.infoContRight, height=60, align=uiconst.TOTOP, state=uiconst.UI_PICKCHILDREN)
        self._DrawStoredCommoditiesIcons()

    def _DrawStoredCommoditiesIcons(self):
        self.iconCont.Flush()
        i = 0
        maxNumIcons = 8
        if self.pin.contents:
            for typeID, amount in self.pin.contents.iteritems():
                iconLeft, iconTop = self._GetIconPos(i)
                icon = StorageIcon(parent=self.iconCont, pos=(iconLeft,
                 iconTop,
                 28,
                 28), hint=localization.GetByLabel('UI/PI/Common/ItemAmount', itemName=planetCommon.GetProductNameAndTier(typeID), amount=int(amount)), typeID=typeID, amount=amount, size=32, ignoreSize=True)
                i += 1
                if i >= maxNumIcons:
                    break

            self.itemsTxt.SetSubtext('')
        else:
            self.itemsTxt.SetSubtext(localization.GetByLabel('UI/PI/Common/NothingStored'))

    def _UpdateInfoCont(self):
        self.storageGauge.SetValue(float(self.pin.capacityUsed) / self.pin.GetCapacity())
        text = localization.GetByLabel('UI/PI/Common/StorageUsed', capacityUsed=self.pin.capacityUsed, capacityMax=self.pin.GetCapacity())
        if not self.pin.GetCapacityRemaining():
            text = '<color=red>%s</color>' % text
        self.storageGauge.SetSubText(text)
        if self.pin.lastRunTime is None or self.pin.lastRunTime <= blue.os.GetWallclockTime():
            self.cooldownTimer.SetSubtext(localization.GetByLabel('UI/Common/Now'))
        else:
            self.cooldownTimer.SetSubtext(localization.GetByLabel('UI/PI/Common/TimeHourMinSec', time=self.pin.lastRunTime - blue.os.GetWallclockTime()))

    def _GetIconPos(self, iconNum):
        iconsInRow = 4
        iconSpace = 30
        left = iconSpace * (iconNum % iconsInRow)
        top = iconSpace * (iconNum / iconsInRow)
        return (left, top)

    def OnRefreshPins(self, pinIDs):
        if not self or self.destroyed:
            return
        BasePinContainer.OnRefreshPins(self, pinIDs)
        self._DrawStoredCommoditiesIcons()
