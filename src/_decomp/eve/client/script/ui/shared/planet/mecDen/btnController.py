#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\mecDen\btnController.py
from appConst import maxCargoContainerTransferDistance
import eveicon
from eve.client.script.ui.control.statefulButtonLocationController import LocationButtonController
from localization import GetByLabel
STATE_ACCESS_MERC_DEN = -1

class MercDenButtonController(LocationButtonController, object):

    def _GetButtonStateForLocationInSpace(self):
        if self.IsInCurrentSolarSystem():
            slimItem = sm.GetService('michelle').GetItem(self.itemID)
            if slimItem:
                inRange = sm.GetService('autoPilot').InInteractionRange(self.itemID, maxCargoContainerTransferDistance)
                if inRange:
                    return STATE_ACCESS_MERC_DEN
        return super(MercDenButtonController, self)._GetButtonStateForLocationInSpace()

    def GetButtonLabel(self):
        if self.buttonState == STATE_ACCESS_MERC_DEN:
            return GetByLabel('UI/Sovereignty/MercenaryDen/ConfigurationWindow/ConfigureMercenaryDen')
        return super(MercDenButtonController, self).GetButtonLabel()

    def GetButtonTexturePath(self):
        if self.buttonState == STATE_ACCESS_MERC_DEN:
            return eveicon.mercenary_den
        return super(MercDenButtonController, self).GetButtonTexturePath()

    def _ExecutePrimaryFunction(self, buttonState):
        if self.buttonState == STATE_ACCESS_MERC_DEN:
            sm.GetService('menu').OpenMercenaryDen(self.itemID)
            return
        return super(MercDenButtonController, self)._ExecutePrimaryFunction(buttonState)
