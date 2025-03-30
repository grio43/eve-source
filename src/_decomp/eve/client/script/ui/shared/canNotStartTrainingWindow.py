#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\canNotStartTrainingWindow.py
import eveformat
import localization
import uthread
from carbon.common.script.sys import serviceManager
from carbonui import uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.uicore import uicore
from eve.client.script.ui.control import eveLabel
from carbonui.control.button import Button
from eveprefs import boot
from inventorycommon import const as inventory_const
from regionalui import regionalutils

class CanNotStartTrainingClass(ContainerAutoSize):

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        charactersTrainingCount = attributes.messageData['charactersTrainingCount']
        if charactersTrainingCount == 1:
            mainText = localization.GetByLabel('UI/DualTraining/TrainingOnAnotherCharacter', characterName=attributes.messageData['charName1'], loggedInCharacterName=cfg.eveowners.Get(session.charid).ownerName)
        else:
            mainText = localization.GetByLabel('UI/DualTraining/TrainingOnThirdCharacter', characterName=attributes.messageData['charName1'], characterName2=attributes.messageData['charName2'], loggedInCharacterName=cfg.eveowners.Get(session.charid).ownerName)
        eveLabel.Label(parent=self, align=uiconst.TOTOP, text=mainText, padding=(16, 0, 16, 0))
        eveLabel.EveCaptionMedium(parent=self, align=uiconst.TOTOP, top=16, text=eveformat.center(localization.GetByLabel('UI/DualTraining/ToAcquirePLEX')), padding=(16, 0, 16, 0))
        Button(parent=ContainerAutoSize(parent=self, align=uiconst.TOTOP, top=16), align=uiconst.CENTER, label=localization.GetByLabel('UI/DualTraining/BuyOnEveMarket'), func=self.OpenMarketWindow, args=())
        Button(parent=ContainerAutoSize(parent=self, align=uiconst.TOTOP, top=16), align=uiconst.CENTER, label=self._buyOnlineButtonText(), func=self._buyOnlineClick, args=())

    def _buyOnlineButtonText(self):
        if regionalutils.in_china(boot.region):
            return localization.GetByLabel('UI/PlexVault/OpenNewEdenStore')
        else:
            return localization.GetByLabel('UI/DualTraining/BuyOnline')

    def _buyOnlineClick(self):
        if regionalutils.in_china(boot.region):
            vgs = serviceManager.ServiceManager.Instance().GetService('vgsService')
            vgs.OpenStore(typeIds=[inventory_const.typeServiceMultipleCharacterTraining])
        else:
            uicore.cmd.BuyMultipleCharacterTrainingOnline(origin='characterSheet')
        self.CloseMe()

    def CloseMe(self):
        uicore.registry.GetModalWindow().Close()

    def OpenMarketWindow(self, *args):
        sm = serviceManager.ServiceManager.Instance()
        uthread.new(sm.GetService('marketutils').ShowMarketDetails, inventory_const.typePlex, None)
        self.CloseMe()

    def GetContentHeight(self):
        _, h = self.GetAbsoluteSize()
        return h
