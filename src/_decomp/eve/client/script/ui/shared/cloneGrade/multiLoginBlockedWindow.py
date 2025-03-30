#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\multiLoginBlockedWindow.py
import carbonui.const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from clonegrade import COLOR_OMEGA_ORANGE
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.cloneGrade.cloneUpgradeWindow import CloneUpgradeWindow, STATE_UPGRADE, STATE_EXTEND
from localization import GetByLabel

class MultiLoginBlockedWindow(CloneUpgradeWindow):
    default_windowID = 'MultiLoginBlockedWindow'

    @property
    def analyticID(self):
        return 'omega_upgrade_multi_login'

    def ConstructBenefitEntries(self):
        self.bottomCont = Container(name='bottomCont', parent=self.mainCont, align=uiconst.CENTERBOTTOM, pos=(0, 30, 450, 220), bgColor=(0, 0, 0, 0.4))
        self.benefitCont = ContainerAutoSize(parent=self.bottomCont, align=uiconst.CENTER, width=400)
        Label(parent=self.benefitCont, align=uiconst.TOTOP, text=GetByLabel('UI/CloneState/MultiLoginBlockedHeader'), fontsize=18, bold=True, padBottom=8, color=COLOR_OMEGA_ORANGE)
        Label(parent=self.benefitCont, align=uiconst.TOTOP, text=GetByLabel('UI/CloneState/MultiLoginBlockedMain'), fontsize=14)

    def ConstructUpgradeButton(self):
        if self.windowState == STATE_EXTEND:
            Label(parent=self.mainCont, align=uiconst.CENTERTOP, state=uiconst.UI_DISABLED, text=GetByLabel('UI/CloneState/UpgradeSuccessful'), uppercase=True, bold=True, color=COLOR_OMEGA_ORANGE, top=296, width=self.width)
        elif self.windowState == STATE_UPGRADE:
            super(MultiLoginBlockedWindow, self).ConstructUpgradeButton()

    def ConstructPlexContainer(self):
        pass
