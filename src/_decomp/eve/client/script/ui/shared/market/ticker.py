#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\market\ticker.py
import eveui
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst
from carbonui.graphs import axis
from carbonui.graphs.graph import GraphArea
from carbonui.graphs.linegraph import LineGraph
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.services.setting import UserSettingBool
from carbonui.uianimations import animations
from carbonui.util.color import Color
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveHeaderLarge
from eve.client.script.ui.control.eveLoadingWheel import LoadingWheel
from eve.client.script.ui.control.glowSprite import GlowSprite
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.common.lib import appConst as const
import evetypes
import localization
import signals
import uthread
from menu import MenuLabel
from eveexceptions.exceptionEater import ExceptionEater
from marketutil.quickbarUtil import GetTypIDsInFolder, TICKER_SETTING_NAME
TICKER_ITEM_TYPES_ALWAYS_PRESENT = [const.typePlex,
 const.typeSkillInjector,
 const.typeSkillExtractor,
 const.typeSmallSkillInjector]
TICKER_ITEM_TYPES = (const.typePlex,
 const.typeSkillInjector,
 const.typeRaffleToken,
 const.typeMexallon,
 9848,
 28606,
 21815,
 const.typeNaniteRepairPaste,
 25624,
 17888,
 16681,
 const.typeTritanium,
 17918,
 const.typeZydrine,
 33681,
 28366,
 const.typeSkillExtractor,
 25591,
 const.typeNocxium,
 17887,
 25619,
 const.typeMegacyte,
 16274,
 const.typeStrontiumClathrates,
 16272,
 const.typeSistersCoreProbeLauncher,
 16273,
 const.typePyerite,
 17889,
 21096,
 33475,
 const.typeSmallSkillInjector)
TICKER_SCROLL_SPEED = 20.0

class TickerContainer(Container):
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        super(TickerContainer, self).ApplyAttributes(attributes)

    def _VerifyNewChild(self, child):
        if child.align != uiconst.TOLEFT:
            raise ValueError('TOLEFT is the only acceptable alignment')

    def PauseAnimation(self):
        if not self.children:
            return
        animations.StopAnimation(self.children[0], 'left')

    def ResumeAnimation(self):
        if not self.children:
            return
        child = self.children[0]
        while not child.destroyed and child.width == 0:
            eveui.wait_for_next_frame()

        animations.MorphScalar(child, 'left', startVal=child.left, endVal=-child.width, duration=(child.width + child.left) / float(TICKER_SCROLL_SPEED), curveType=uiconst.ANIM_LINEAR, callback=self._OnTickerEntryReachedEnd)

    def _OnTickerEntryReachedEnd(self):
        child = self.children[0]
        child.left = 0
        child.SetOrder(-1)
        child.opacity = 0.0
        animations.FadeTo(child)
        self.ResumeAnimation()


class TickerItem(object):

    def __init__(self, typeID):
        self.typeID = typeID
        self._loaded = False
        self._isAvailable = None
        self._averagePrice = None
        self._averagePriceDelta = None
        self._averagePriceHistory = None

    @property
    def isAvailable(self):
        self.LoadData()
        return self._isAvailable

    @property
    def averagePrice(self):
        self.LoadData()
        return self._averagePrice

    @property
    def averagePriceDelta(self):
        self.LoadData()
        return self._averagePriceDelta

    @property
    def name(self):
        return evetypes.GetName(self.typeID)

    def GetAveragePriceHistory(self):
        self.LoadData()
        return self._averagePriceHistory

    def LoadData(self):
        if self._loaded:
            return
        history = sm.GetService('marketQuote').GetPriceHistoryFromCache(self.typeID)
        if not history or len(history) < 7:
            self._isAvailable = False
            return
        self._averagePriceHistory = [ x.avgPrice for x in history[-7:] ]
        self._averagePrice = self._averagePriceHistory[-1]
        self._averagePriceDelta = self._averagePriceHistory[-1] / self._averagePriceHistory[-7] - 1.0
        if self._averagePrice <= 0 or all((x.volume == 0 for x in history)):
            self._isAvailable = False
        else:
            self._isAvailable = True
        self._loaded = True


ticker_enabled_setting = UserSettingBool(settings_key='market_ticker_enabled', default_value=True)

class TickerController(object):

    def __init__(self):
        self.items = self.GetItems()
        self._loaded = False

    def ResetController(self):
        self._loaded = False
        self.items = self.GetItems()

    def GetItems(self):
        itemTypes = self.GetItemsFromQuickbar()
        if itemTypes:
            itemTypes.update(TICKER_ITEM_TYPES_ALWAYS_PRESENT)
        else:
            itemTypes = TICKER_ITEM_TYPES
        return [ TickerItem(typeID) for typeID in itemTypes ]

    def GetItemsFromQuickbar(self):
        itemTypes = set()
        quickbar = settings.user.ui.Get('quickbar', {})
        marketTickerFolderID = settings.char.ui.Get(TICKER_SETTING_NAME, None)
        if marketTickerFolderID is not None:
            myTypeIDs = GetTypIDsInFolder(marketTickerFolderID, quickbar)
            for typeID in myTypeIDs:
                with ExceptionEater('TickerController:GetItems'):
                    if evetypes.GetMarketGroupID(typeID):
                        itemTypes.add(typeID)
                if len(itemTypes) >= 50:
                    return itemTypes

        return itemTypes

    @property
    def enabled(self):
        return ticker_enabled_setting.is_enabled()

    @enabled.setter
    def enabled(self, value):
        value = bool(value)
        ticker_enabled_setting.set(value)

    @property
    def on_enabled_changed(self):
        return ticker_enabled_setting.on_change

    def LoadData(self):
        if self._loaded:
            return
        for item in self.items:
            item.LoadData()

        self._loaded = True

    def ToggleEnabled(self):
        self.enabled = not self.enabled


class TickerToggleButton(GlowSprite):
    default_texturePath = 'res:/UI/Texture/Shared/triangleDown.png'
    default_width = 10
    default_height = 10
    default_hint = localization.GetByLabel('UI/Market/TickerToggleHint')

    def ApplyAttributes(self, attributes):
        super(TickerToggleButton, self).ApplyAttributes(attributes)
        self.controller = attributes.controller
        self.UpdateTexture()

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        self.controller.ToggleEnabled()
        self.UpdateTexture()

    def OnMouseEnter(self, *args):
        super(TickerToggleButton, self).OnMouseEnter(*args)
        PlaySound(uiconst.SOUND_BUTTON_HOVER)

    def UpdateTexture(self):
        if self.controller.enabled:
            self.SetTexturePath('res:/UI/Texture/Shared/triangleDown.png')
        else:
            self.SetTexturePath('res:/UI/Texture/Shared/triangleUp.png')


class MarketTicker(Container):
    default_state = uiconst.UI_NORMAL
    __notifyevents__ = ['OnMarketTickerSettingsUpdated']

    def ApplyAttributes(self, attributes):
        super(MarketTicker, self).ApplyAttributes(attributes)
        self.ticker = None
        self.controller = TickerController()
        ticker_enabled_setting.on_change.connect(self.OnEnabledChanged)
        self.BuildMarketTicker()
        sm.RegisterNotify(self)

    def BuildMarketTicker(self):
        self.Layout()
        uthread.new(self.Load)

    def Layout(self):
        self.display = self.controller.enabled
        self.ticker = TickerContainer(parent=self, align=uiconst.TOALL)

    def Load(self):
        loading_size = max(16, self.height - 8)
        loadingWheel = LoadingWheel(parent=self, align=uiconst.CENTER, width=loading_size, height=loading_size)
        typeIDsInTicker = {x.typeID for x in self.controller.items}
        sm.GetService('marketQuote').PopulatePriceHistoryCacheForManyTypeIDs(typeIDsInTicker)
        for item in self.controller.items:
            if not item.isAvailable:
                continue
            TickerEntry(parent=self.ticker, align=uiconst.TOLEFT, item=item, onMouseEnter=self.ticker.PauseAnimation, onMouseExit=self.ticker.ResumeAnimation, opacity=0.0)
            if len(self.ticker.children) > 15:
                break

        animations.FadeOut(loadingWheel, duration=0.5)
        if not self.ticker.children:
            self.DisplayNoItemsMessage()
        for i, child in enumerate(self.ticker.children):
            animations.FadeTo(child, duration=0.3, timeOffset=i * 0.1)

        if self.IsVisible():
            self.ticker.ResumeAnimation()

    def DisplayNoItemsMessage(self):
        EveHeaderLarge(parent=self, align=uiconst.CENTER, text=localization.GetByLabel('UI/Market/TickerNoItems'), opacity=0.6)

    def OnEnabledChanged(self, enabled):
        self.display = enabled

    def RefreshMarketTicker(self):
        self.Flush()
        self.BuildMarketTicker()

    def GetMenu(self):
        return GetTickerMenu()

    def OnMarketTickerSettingsUpdated(self, newTickerFolderID):
        self.controller.ResetController()
        self.RefreshMarketTicker()


class TickerEntry(ContainerAutoSize):
    default_state = uiconst.UI_NORMAL
    default_name = 'tickerEntry'

    def ApplyAttributes(self, attributes):
        super(TickerEntry, self).ApplyAttributes(attributes)
        self.item = attributes.item
        self.onMouseEnter = signals.Signal(signalName='onMouseEnter')
        if callable(attributes.onMouseEnter):
            self.onMouseEnter.connect(attributes.onMouseEnter)
        self.onMouseExit = signals.Signal(signalName='onMouseExit')
        if callable(attributes.onMouseExit):
            self.onMouseExit.connect(attributes.onMouseExit)
        self.Layout()

    def Layout(self):
        self._hover = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_UIHILIGHT, opacity=0.0)
        iconCont = Container(parent=self, align=uiconst.TOLEFT, left=8, width=24)
        Icon(parent=iconCont, align=uiconst.CENTER, state=uiconst.UI_DISABLED, width=24, height=24, typeID=self.item.typeID, isCopy=False)
        if self.item.averagePriceDelta >= 0.0:
            changeColor = Color(eveColor.SUCCESS_GREEN)
        else:
            changeColor = Color(eveColor.DANGER_RED)
        EveHeaderLarge(parent=ContainerAutoSize(parent=self, align=uiconst.TOLEFT, padding=(4, 0, 4, 0)), align=uiconst.CENTERLEFT, text=localization.GetByLabel('UI/Market/TickerItemLabel', typeID=self.item.typeID, averagePrice=self.item.averagePrice, averagePriceDelta=self.item.averagePriceDelta, color=changeColor.GetHex()))
        values = self.item.GetAveragePriceHistory()
        vAxis = axis.BaseAxis((min(values), max(values)))
        hAxis = axis.CategoryAxis(range(len(values)))
        graph = GraphArea(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_DISABLED, padding=(0, 8, 8, 8), width=36, verticalAxis=[(vAxis, 1.0, 0.0)], horizontalAxis=[(hAxis, 0.0, 1.0)])
        LineGraph(parent=graph, categoryAxis=hAxis, valueAxis=vAxis, values=values, lineWidth=0.8)

    def OnClick(self, *args):
        sm.StartService('marketutils').ShowMarketDetails(self.item.typeID)

    def OnMouseEnter(self, *args):
        animations.FadeTo(self._hover, endVal=0.2, duration=0.15)
        self.onMouseEnter()

    def OnMouseExit(self, *args):
        animations.FadeOut(self._hover, duration=0.2)
        self.onMouseExit()

    def GetMenu(self):
        return GetTickerMenu()


def GetTickerMenu():
    return [(MenuLabel('UI/Market/TickerReset'), ResetMarketTicker, ())]


def ResetMarketTicker():
    settings.char.ui.Set(TICKER_SETTING_NAME, None)
    sm.ScatterEvent('OnMarketTickerSettingsUpdated', None)
