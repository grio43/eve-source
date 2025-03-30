#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\cloneGrade\lapseNotifyWindow.py
from carbonui import fontconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from carbonui.util.color import Color
from clonegrade.const import COLOR_OMEGA_GOLD, COLOR_OMEGA_BG
from eve.client.script.ui.control.eveLabel import EveCaptionMedium, Label
from eve.client.script.ui.shared.cloneGrade import ORIGIN_LAPSENOTIFYWINDOW, REASON_DEFAULT
from eve.client.script.ui.shared.cloneGrade.upgradeButton import UpgradeButton
from eve.client.script.ui.shared.cloneGrade.baseClonesStateWindow import BaseCloneStateWindow
import carbonui.const as uiconst
from localization import GetByLabel
PADTOP = 10
ICONSIZE = 40

class LapseNotifyWindow(BaseCloneStateWindow):
    default_windowID = 'LapseNotifyWindow'
    default_width = 540
    default_fixedWidth = 540
    default_height = 680
    default_fixedHeight = 680
    default_analyticID = 'omega_lapsed_window_old'

    def ConstructLayout(self):
        self.outerCont = ContainerAutoSize(name='cont', parent=self.sr.main, align=uiconst.CENTER, pos=(0, 60, 450, 0))
        self.mainCont = ContainerAutoSize(name='bottomCont', parent=self.outerCont, padding=(PADTOP,
         0,
         PADTOP,
         PADTOP), align=uiconst.TOTOP)
        Fill(bgParent=self.mainCont, color=(0, 0, 0, 0.7), padding=(-15, -10, -15, -25))
        self.AddCaption(GetByLabel('UI/CloneState/LapseWindow/Caption'))
        self.AddLabel(GetByLabel('UI/CloneState/LapseWindow/SubCaption'), bold=True)
        self.AddIcon('res:/UI/Texture/classes/cloneGrade/benefits/allSkills.png', padTop=20)
        self.AddLabel(GetByLabel('UI/CloneState/LapseWindow/SkillLevelsRestriction'))
        self.AddIcon('res:/UI/Texture/classes/cloneGrade/benefits/allShipsAndModules.png')
        self.AddLabel(GetByLabel('UI/CloneState/LapseWindow/ActiveShipRestriction'))
        self.AddIcon('res:/UI/Texture/classes/cloneGrade/benefits/longerQueue.png')
        self.AddLabel(GetByLabel('UI/CloneState/LapseWindow/SkillQueueRestriction'))
        self.ConstructButtons()

    def ConstructButtons(self):
        buttonCont = Container(name='buttonCont', parent=self.outerCont, align=uiconst.TOTOP, height=50, padding=(0, 30, 0, 60))
        _buttonCont = ContainerAutoSize(parent=buttonCont, align=uiconst.CENTER, height=41)
        UpgradeButton(parent=_buttonCont, align=uiconst.TOLEFT, width=150, onClick=self.OnUpgradeButtonClick, text=GetByLabel('UI/CloneState/Upgrade'), analyticID='upgrade_omega_lapsed_secure_old')
        UpgradeButton(parent=_buttonCont, align=uiconst.TOLEFT, width=150, onClick=self.CloseByUser, text=GetByLabel('UI/Agents/Dialogue/Buttons/Continue'), padLeft=20, labelColor=Color.GRAY7)

    def OnUpgradeButtonClick(self, *args):
        self.CloseByUser()
        sm.GetService('cloneGradeSvc').UpgradeCloneAction(ORIGIN_LAPSENOTIFYWINDOW, REASON_DEFAULT)

    def ConstructBackground(self):
        BaseCloneStateWindow.ConstructBackground(self)
        self.bgSprite.effectOpacity = -0.7

    def AddLabel(self, text, bold = False):
        Label(parent=self.mainCont, align=uiconst.TOTOP, text='<center>' + text, fontsize=15, bold=bold, padTop=2, color=(1.0, 1.0, 1.0, 0.9))

    def AddCaption(self, text):
        EveCaptionMedium(parent=self.mainCont, align=uiconst.TOTOP, color=COLOR_OMEGA_GOLD, text='<center>' + text, padTop=PADTOP)

    def AddIcon(self, texturePath, padTop = PADTOP):
        cont = Container(parent=self.mainCont, align=uiconst.TOTOP, height=ICONSIZE, padTop=padTop)
        Sprite(parent=cont, align=uiconst.CENTER, texturePath=texturePath, pos=(0,
         0,
         ICONSIZE,
         ICONSIZE), color=COLOR_OMEGA_BG)
