#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\factionalWarfare\enlistmentFlow\factionBanner.py
import uthread2
from carbonui import TextBody, TextAlign, TextCustom, TextHeadline, TextDetail
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
import carbonui.const as uiconst
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistCont import EnlistCont
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentConst import BANNER_TEXTURE_BY_FACTION_ID
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.enlistmentUtil import GetFactionColor, GetFactionIcon, GetFactionIconSmall
from eve.client.script.ui.shared.factionalWarfare.enlistmentFlow.warzoneGaugeCont import WarzoneGaugeCont
from eve.common.script.util.facwarCommon import GetCombatEnemyFactions, IsOccupierFWFaction
from fwwarzone.client.dashboard.gauges.warzoneStatusGauge import WarzoneStatusGauge
from localization import GetByLabel
import eve.common.lib.appConst as appConst
BANNER_WARZONE_GAUGE_SIZE = 51

class FactionBanner(Container):
    default_width = 370

    def ApplyAttributes(self, attributes):
        super(FactionBanner, self).ApplyAttributes(attributes)
        self.factionID = None
        self.ContructUI()

    def ContructUI(self):
        self.ConstructIcon()
        self.ConstructWarZone()
        self.ConstructFactionName()
        self.ConstructCTA()
        self.ConstructFrameSprite()

    def ConstructFrameSprite(self):
        self.frameSprite = Sprite(name='frameSprite', parent=self, pos=(0, 0, 370, 720), align=uiconst.CENTERTOP)

    def ConstructIcon(self):
        iconCont = Container(name='iconCont', parent=self, align=uiconst.TOTOP, height=152, top=90)
        self.factionIcon = Sprite(name='factionIcon', parent=iconCont, align=uiconst.CENTER, pos=(0, 0, 80, 80))

    def ConstructWarZone(self):
        self.warzoneCont = Container(name='warzoneCont', parent=self, align=uiconst.TOTOP, height=120, top=32)
        radius = BANNER_WARZONE_GAUGE_SIZE
        self.warzoneGaugeCont = WarzoneGaugeCont(parent=self.warzoneCont, pos=(0,
         0,
         2 * radius,
         2 * radius), gaugeRadius=radius, idx=0, iconSize=48)

    def ConstructFactionName(self):
        factionNameCont = ContainerAutoSize(parent=self, align=uiconst.TOTOP, alignMode=uiconst.TOTOP)
        self.factionNameLabel = TextHeadline(parent=factionNameCont, align=uiconst.TOTOP, text='', textAlign=TextAlign.CENTER, padTop=24)
        cont = Container(name='cont', parent=factionNameCont, align=uiconst.TOTOP, height=30, padTop=10)
        textWithIconsCont = ContainerAutoSize(name='textWithIconsCont', height=30, parent=cont, align=uiconst.CENTER, alignMode=uiconst.TOLEFT)
        TextDetail(parent=textWithIconsCont, align=uiconst.TOLEFT, text=GetByLabel('UI/FactionWarfare/frontlinesDashboard/atWarWith'))
        self.enemySpriteCont = ContainerAutoSize(name='enemySpriteCont', parent=textWithIconsCont, align=uiconst.TOLEFT, left=5)

    def LoadFactionID(self, factionID):
        if not factionID:
            return
        self.enemySpriteCont.Flush()
        self.factionID = factionID
        factionColor = GetFactionColor(factionID)
        self.frameSprite.texturePath = BANNER_TEXTURE_BY_FACTION_ID.get(factionID, '')
        texturePath = GetFactionIcon(factionID)
        self.factionIcon.texturePath = texturePath
        self.factionNameLabel.text = cfg.eveowners.Get(factionID).name
        self.factionNameLabel.SetRGBA(*factionColor)
        self.warzoneGaugeCont.ShowFaction(None)
        enemyFactionIDs = GetCombatEnemyFactions(factionID)
        for enemyFactionID in enemyFactionIDs:
            texturePath = GetFactionIconSmall(enemyFactionID)
            self.enemySprite = Sprite(parent=Container(parent=self.enemySpriteCont, align=uiconst.TOLEFT, width=24, height=24), pos=(0, -5, 24, 24), state=uiconst.UI_NORMAL, texturePath=texturePath, hint=cfg.eveowners.Get(enemyFactionID).name)
            self.enemySprite.GetMenu = lambda ef = enemyFactionID: sm.GetService('menu').GetMenuForOwner(ef)
            self.enemySprite.OnClick = lambda ef = enemyFactionID: sm.GetService('info').ShowInfo(appConst.typeFaction, ef)

        uthread2.StartTasklet(self.LoadGaugeAndBtns_thread, factionID)

    def LoadGaugeAndBtns_thread(self, factionID):
        self.warzoneGaugeCont.ShowFaction(factionID)
        self.LoadEnlist(factionID)

    def ConstructCTA(self):
        self.ctaCont = Container(name='ctaCont', parent=self)
        self.enlistCont = EnlistCont(parent=self.ctaCont)

    def LoadEnlist(self, factionID):
        self.enlistCont.LoadEnlist(factionID)
