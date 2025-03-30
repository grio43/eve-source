#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\missingItemsPopup.py
import evetypes
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbonui.primitives.container import Container
from carbonui.util.sortUtil import SortListOfTuples
from carbonui.button.group import ButtonGroup
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveCaptionLarge, EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
import carbonui.const as uiconst
from eve.client.script.ui.control.themeColored import SpriteThemeColored
from eve.common.lib.appConst import defaultPadding
from localization import GetByLabel
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty
import dynamicitemattributes

class BuyAllMessageBox(Window):
    __guid__ = 'BuyAllMessageBox'
    default_width = 340
    default_height = 210
    default_windowID = 'buyAllMessageBox'
    default_iconNum = 'res:/ui/Texture/WindowIcons/info.png'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.sr.main.clipChildren = True
        self.MakeUnMinimizable()
        self.HideHeader()
        descText = attributes.missingText
        self.faildToLoadInfo = attributes.faildToLoadInfo
        self.fitting = attributes.fitting
        self.topParent = Container(name='topParent', parent=self.GetMainArea(), align=uiconst.TOTOP, height=52, clipChildren=True)
        SpriteThemeColored(name='mainicon', parent=self.topParent, state=uiconst.UI_DISABLED, pos=(0, -3, 64, 64), texturePath=self.iconNum, colorType=uiconst.COLORTYPE_UIHILIGHTGLOW)
        title = GetByLabel('UI/Common/Information')
        caption = EveCaptionLarge(text=title, align=uiconst.CENTERLEFT, parent=self.topParent, left=64, width=270)
        self.topParent.height = max(56, caption.textheight + 16)
        descLabel = EveLabelMedium(parent=self.sr.main, text=descText, align=uiconst.TOTOP, padding=(11,
         11,
         defaultPadding,
         defaultPadding))
        buttonGroup = ButtonGroup(parent=self.sr.main, idx=0)
        buyAllBtn = buttonGroup.AddButton(GetByLabel('UI/Market/MarketQuote/BuyAll'), self.BuyAll)
        closeBtn = buttonGroup.AddButton(GetByLabel('/Carbon/UI/Common/Close'), self.Close)
        if session.role & ROLE_GML == ROLE_GML:
            buttonGroup.AddButton('GM: Give all', self.GiveAllGM)
        self.typeScroll = Scroll(name='typeScroll', parent=self.sr.main, padding=(defaultPadding,
         0,
         defaultPadding,
         0))
        self.LoadTypes(self.faildToLoadInfo)

    def LoadTypes(self, typeIDsAndQty):
        scrolllist = []
        for eachTypeID, qty in typeIDsAndQty.iteritems():
            typeName = evetypes.GetName(eachTypeID)
            scrolllist.append((typeName, GetFromClass(Item, {'label': '%sx %s' % (qty, typeName),
              'typeID': eachTypeID,
              'itemID': None,
              'getIcon': 1})))

        scrolllist = SortListOfTuples(scrolllist)
        self.typeScroll.Load(contentList=scrolllist)
        self.height = self.GetNewHeight()

    def BuyAll(self, *args):
        BuyMultipleTypesWithQty(self.faildToLoadInfo, self.fitting)
        self.Close()

    def GetNewHeight(self):
        contentHeight = self.typeScroll.GetContentHeight()
        newHeight = 150 + contentHeight
        return min(400, newHeight)

    def GiveAllGM(self, *args):
        GiveAllGM(self.faildToLoadInfo)
        self.Close()


def GiveAllGM(missingDict):
    return GiveOrLoadAllGM(missingDict, 'create')


def LoadAllGM(missingDict):
    return GiveOrLoadAllGM(missingDict, 'load me')


def GiveOrLoadAllGM(missingDict, slashCmd):
    numToCountTo = len(missingDict) + 1
    header = 'GM Item Gift (%s)' % slashCmd
    sm.GetService('loading').ProgressWnd(header, '', 1, numToCountTo)
    counter = 1
    itemsRemoved = False
    for typeID, qty in missingDict.iteritems():
        if dynamicitemattributes.IsDynamicType(typeID):
            itemsRemoved = True
            continue
        counter += 1
        sm.GetService('loading').ProgressWnd(header, '', counter, numToCountTo)
        sm.RemoteSvc('slash').SlashCmd('/%s %s %s' % (slashCmd, typeID, qty))

    sm.GetService('loading').ProgressWnd('Done', '', numToCountTo, numToCountTo)
    if itemsRemoved:
        eve.Message('CustomNotify', {'notify': 'Not all items were created'})


def OpenBuyAllBox(faildToLoadInfoCounters, fitting):
    faildToLoadInfo = dict(faildToLoadInfoCounters)
    BuyAllMessageBox.Open(missingText=GetByLabel('UI/Fitting/MissingItemsHeader'), faildToLoadInfo=faildToLoadInfo, fitting=fitting)
