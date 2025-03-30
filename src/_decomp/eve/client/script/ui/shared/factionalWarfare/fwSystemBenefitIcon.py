#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\fwSystemBenefitIcon.py
import math
import localization
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from eve.client.script.ui.control import eveLabel
from eve.common.lib import appConst as const
from eve.common.script.util import facwarCommon

class FWSystemBenefitIcon(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_width = 22

    def ApplyAttributes(self, attributes):
        ContainerAutoSize.ApplyAttributes(self, attributes)
        self.benefitType = attributes.benefitType
        self.benefitValue = attributes.benefitValue
        self.facwar = sm.GetService('facwar')
        Sprite(parent=self, state=uiconst.UI_DISABLED, align=uiconst.TOTOP, texturePath=self.GetTexturePath(), height=self.width, opacity=0.75)
        labelCont = Container(name='labelCont', parent=self, align=uiconst.TOTOP, height=12)
        eveLabel.EveLabelSmall(parent=labelCont, align=uiconst.CENTER, padTop=3, text=self.GetLabel(), color=Color.WHITE)

    def GetTexturePath(self):
        return {facwarCommon.BENEFIT_MARKETREDUCTION: 'res:/ui/texture/classes/FWInfrastructureHub/marketReduction.png',
         facwarCommon.BENEFIT_INDUSTRYCOST: 'res:/ui/texture/classes/FWInfrastructureHub/stationCopySlots.png'}.get(self.benefitType)

    def GetLabel(self):
        return {facwarCommon.BENEFIT_MARKETREDUCTION: '%s%%',
         facwarCommon.BENEFIT_INDUSTRYCOST: '%s%%'}.get(self.benefitType) % self.benefitValue

    def GetHint(self):
        if self.benefitType == facwarCommon.BENEFIT_MARKETREDUCTION:
            return localization.GetByLabel('UI/FactionWarfare/IHub/UpgradeHintMarketReduction', num=self.benefitValue)
        if self.benefitType == facwarCommon.BENEFIT_INDUSTRYCOST:
            return localization.GetByLabel('UI/FactionWarfare/IHub/UpgradeHintStationSlots', num=self.benefitValue)
