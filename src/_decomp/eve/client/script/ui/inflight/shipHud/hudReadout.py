#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\shipHud\hudReadout.py
import carbonui.const as uiconst
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.line import Line
from eve.client.script.ui.control.eveLabel import EveLabelSmall
import eve.client.script.ui.shared.pointerTool.pointerToolConst as pConst
from localization import GetByLabel
from uihider import UiHiderMixin

class HudReadout(UiHiderMixin, ContainerAutoSize):
    default_name = 'hudReadout'
    uniqueUiName = pConst.UNIQUE_NAME_HUD_READOUT

    def ApplyAttributes(self, attributes):
        self.controller = attributes.controller
        super(HudReadout, self).ApplyAttributes(attributes)
        self.shield = self._ConstructLabel('shield')
        self.armor = self._ConstructLabel('armor')
        self.structure = self._ConstructLabel('structure')

    def _ConstructLabel(self, refName):
        container = ContainerAutoSize(name=refName, parent=self, align=uiconst.TOTOP)
        label = EveLabelSmall(parent=container, left=2, state=uiconst.UI_DISABLED, align=uiconst.TOPRIGHT)
        Line(parent=container, top=6, width=-130, height=1, align=uiconst.TOPRIGHT)
        Line(parent=container, top=6, width=-130, height=1, align=uiconst.TOPRIGHT, color=(0.1, 0.1, 0.1, 0.5))
        return label

    def _UpdateLabelWithHpPercentage(self, labelName, hpPercentage):
        label = getattr(self, labelName, None)
        if label:
            label.text = GetByLabel('UI/Common/Formatting/Percentage', percentage=hpPercentage * 100)

    def _UpdateLabelWithHpAbsolute(self, labelName, hp, hpMax):
        label = getattr(self, labelName, None)
        if label:
            label.text = GetByLabel('UI/Inflight/GaugeAbsolute', left=hp, total=hpMax)

    def UpdateHpPercentages(self):
        shieldHpPercentage = self.controller.GetShieldHPPortion()
        armorHpPercentage = self.controller.GetArmorHPPortion()
        structureHpPercentage = self.controller.GetStructureHPPortion()
        self._UpdateLabelWithHpPercentage('shield', shieldHpPercentage)
        self._UpdateLabelWithHpPercentage('armor', armorHpPercentage)
        self._UpdateLabelWithHpPercentage('structure', structureHpPercentage)

    def UpdateHpAbsolutes(self):
        shieldHp = self.controller.GetShieldHP()
        armorHp = self.controller.GetArmorHP()
        structureHp = self.controller.GetStructureHP()
        shieldHpMax = self.controller.GetShieldHPMax()
        armorHpMax = self.controller.GetArmorHPMax()
        structureHpMax = self.controller.GetStructureHPMax()
        self._UpdateLabelWithHpAbsolute('shield', shieldHp, shieldHpMax)
        self._UpdateLabelWithHpAbsolute('armor', armorHp, armorHpMax)
        self._UpdateLabelWithHpAbsolute('structure', structureHp, structureHpMax)
