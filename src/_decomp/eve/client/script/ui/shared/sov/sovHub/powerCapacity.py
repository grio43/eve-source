#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\sovHub\powerCapacity.py
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
import carbonui
from eve.client.script.ui import eveColor
from sovereignty.client.sovHub.hubUtil import GetColorForUpgrade

class PowerCapacityCont(Container):

    def ApplyAttributes(self, attributes):
        super(PowerCapacityCont, self).ApplyAttributes(attributes)
        self.upgradeCont = Container(name='upgradeCont', parent=self, align=carbonui.Align.VERTICALLY_CENTERED, height=3, bgColor=eveColor.MATTE_BLACK[:3] + (0.5,), clipChildren=True)

    def LoadUpgrades(self, maxPower, installedUpgrades):
        self.upgradeCont.Flush()
        if not maxPower:
            return
        for upgrade in installedUpgrades:
            prop = float(upgrade.staticData.power) / maxPower
            color = GetColorForUpgrade(upgrade)
            f = Fill(parent=self.upgradeCont, color=color, align=carbonui.Align.TOLEFT_PROP, width=prop, padRight=3, pickState=carbonui.PickState.ON)
            f.hint = '%s<br>%s' % (upgrade.name, upgrade.upgradeStateText)
