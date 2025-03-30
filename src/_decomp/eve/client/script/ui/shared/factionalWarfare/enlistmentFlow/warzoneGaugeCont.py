#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\warzoneGaugeCont.py
import uthread2
from carbonui import const as uiconst, TextCustom
from carbonui.primitives.container import Container
from carbonui.text.const import FontSizePreset
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentUtil import GetFactionColor
from eve.common.script.util.facwarCommon import IsOccupierFWFaction
from fwwarzone.client.dashboard.gauges.warzoneStatusGauge import WarzoneStatusGaugeFaintOpponent

class WarzoneGaugeCont(Container):
    default_align = uiconst.CENTER
    default_fontsize = FontSizePreset.BODY
    default_showScore = True
    default_iconSize = 65

    def ApplyAttributes(self, attributes):
        super(WarzoneGaugeCont, self).ApplyAttributes(attributes)
        self.gaugeRadius = attributes.gaugeRadius or self.width / 2
        fontsize = attributes.get('fontsize', self.default_fontsize)
        showScore = attributes.get('showScore', self.default_showScore)
        self.iconSize = attributes.get('iconSize', self.default_iconSize)
        self.innerCont = Container(name='innerCont', parent=self, align=uiconst.CENTER, pos=(0,
         0,
         2 * self.gaugeRadius,
         2 * self.gaugeRadius))
        labelLeft = self.gaugeRadius + 20
        self.factionScoreLabel = TextCustom(name='factionScoreLabel', parent=Container(parent=self, align=uiconst.CENTER, pos=(labelLeft,
         0,
         20,
         20)), align=uiconst.CENTERLEFT, text='', fontsize=fontsize)
        labelLeft = -self.gaugeRadius - 20
        self.enemyScoreLAbel = TextCustom(name='enemyScoreLAbel', parent=Container(parent=self, align=uiconst.CENTER, pos=(labelLeft,
         0,
         20,
         20)), align=uiconst.CENTERRIGHT, text='', fontsize=fontsize)
        if not showScore:
            self.factionScoreLabel.Hide()
            self.enemyScoreLAbel.Hide()

    def ShowFaction(self, factionID):
        self.innerCont.Flush()
        if IsOccupierFWFaction(factionID):
            self.Show()
            uthread2.StartTasklet(self.LoadGauge_thread, factionID)
        else:
            self.Hide()
            self.factionScoreLabel.text = ''
            self.enemyScoreLAbel.text = ''

    def LoadGauge_thread(self, factionID):
        self.innerCont.Flush()
        warzoneID = sm.GetService('fwWarzoneSvc').GetWarzoneIdForFaction(factionID)
        warzoneStatusGauge = WarzoneStatusGaugeFaintOpponent(parent=self.innerCont, radius=self.gaugeRadius, lineWidth=6, align=uiconst.CENTER, warzoneId=warzoneID, animateIn=False, viewingFactionId=factionID, iconSize=self.iconSize)
        self.factionScoreLabel.text = warzoneStatusGauge.friendlySystemCount
        self.enemyScoreLAbel.text = warzoneStatusGauge.opposingSystemCount
        factionRGB = GetFactionColor(factionID) or (1, 1, 1, 1)
        self.factionScoreLabel.SetRGBA(*factionRGB)
