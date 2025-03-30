#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\moonscan.py
from carbon.common.script.util.linkUtil import GetShowInfoLink
from eve.client.script.ui.control.entries.util import GetFromClass
from menu import MenuLabel
from carbonui.primitives.container import Container
from carbonui.util.various_unsorted import SortListOfTuples
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.eveScroll import Scroll
import evetypes
import localization
from eve.client.script.ui.control.gauge import Gauge
from eve.client.script.ui.control.infoIcon import InfoIcon
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.ui.shared.ledger.ledgerUtil import GetColorForBaseTypeID
from eveservices.menu import GetMenuService
import carbonui.const as uiconst
from carbonui.uicore import uicore
import mathext

class MoonScanView(Container):
    __update_on_reload__ = 1

    def Startup(self):
        self.sr.scroll = Scroll(parent=self)
        self.sr.scroll.sr.id = 'moonsurveyscroll'
        self.sr.scroll.sr.fixedColumns = MoonProductEntry.GetFixedColumns()
        self.sr.scroll.GetStrengir = self.GetScrollStrengir

    def ClearAll(self, *args):
        sm.GetService('moonScan').Clear()

    def Clear(self):
        self.sr.scroll.Clear()

    def SetEntries(self, entries, moonID = None):
        scrolllist = []
        entries = SortListOfTuples([ (celestialID, (celestialID, products)) for celestialID, products in entries.iteritems() ])
        for celestialID, products in entries:
            if celestialID == moonID:
                blink = True
            else:
                blink = False
            scrolllist.append(GetFromClass(MoonGroup, {'GetSubContent': self.GetSubContent,
             'MenuFunction': self.GetMenu,
             'label': cfg.evelocations.Get(celestialID).name,
             'groupItems': products,
             'id': ('moon', celestialID),
             'tabs': [],
             'state': 'locked',
             'showlen': 1,
             'blink': blink}))

        pos = self.sr.scroll.GetScrollProportion()
        headers = [localization.GetByLabel('UI/Inflight/Scanner/MoonProduct'), localization.GetByLabel('UI/Common/Quantity')]
        self.sr.scroll.Load(contentList=scrolllist, headers=headers, scrollTo=pos, noContentHint=localization.GetByLabel('UI/Inflight/Scanner/NoScanResult'))

    def GetSubContent(self, data, *args):
        scrolllist = []
        for typeID, quantity in data.groupItems.iteritems():
            name = evetypes.GetName(typeID)
            roundedQty = mathext.clamp(round(quantity, 2), 0, 1.0)
            scrolllist.append(GetFromClass(MoonProductEntry, {'label': '%s<t>%s' % (name, roundedQty),
             'typeName': name,
             'percentage': roundedQty,
             'typeID': typeID,
             'GetMenu': self.OnGetEntryMenu,
             'itemID': None,
             'getIcon': 1,
             'sublevel': 1,
             'gaugeColor': GetOreColor(typeID)[:3] + (0.6,)}))

        return scrolllist

    def GetMenu(self, entry, *args):
        celestialID = entry.id[1]
        noteList = []
        for typeID, quantity in entry.groupItems.iteritems():
            text = '%s [%s]' % (GetShowInfoLink(typeID, evetypes.GetName(typeID)), quantity)
            noteList.append(text)

        note = '<br>'.join(noteList)
        celestialMenu = GetMenuService().CelestialMenu(celestialID, hint=note)
        return celestialMenu + [None] + [(MenuLabel('UI/Common/Delete'), self.ClearEntry, (celestialID,))]

    def ClearEntry(self, celestialID, *args):
        if eve.Message('DeleteScanResult', {}, uiconst.YESNO, suppress=uiconst.ID_YES) == uiconst.ID_YES:
            sm.GetService('moonScan').ClearEntry(celestialID)

    def OnGetEntryMenu(self, entry, *args):
        return GetMenuService().GetMenuFromItemIDTypeID(None, entry.sr.node.typeID, includeMarketDetails=True)

    def GetScrollStrengir(self, node, fontsize, letterspace, shift, idx = None):
        t = node.typeName
        if node.panel and node.productNameLabel:
            label = node.productNameLabel
            fontsize = label.fontsize
            letterspace = label.letterspace
            shift = label.left
        elif node.decoClass == MoonProductEntry:
            shift = MoonProductEntry.GetShift(node)
        return (t,
         fontsize,
         letterspace,
         shift,
         0)


class MoonGroup(ListGroup):
    __guid__ = 'MoonGroup'

    def Startup(self, *etc):
        ListGroup.Startup(self, *etc)
        self.highlightFill = FillThemeColored(parent=self, padding=(1, 0, 1, 1), colorType=uiconst.COLORTYPE_UIHILIGHTGLOW, opacity=0.15)
        self.highlightFill.display = False

    def Load(self, node):
        ListGroup.Load(self, node)
        if node.blink:
            self.highlightFill.display = True
            uicore.animations.BlinkIn(self.highlightFill, startVal=0.0, endVal=0.15, duration=0.5, curveType=uiconst.ANIM_WAVE)
            node.blink = False


class MoonProductEntry(BaseListEntryCustomColumns):
    default_name = 'MoonProductEntry'
    default_height = 32

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.sr.infoicon = InfoIcon(left=2, parent=self, idx=0, align=uiconst.CENTERRIGHT)
        self.sr.infoicon.OnClick = self.ShowInfo
        qtyCol = self.AddColumnContainer()
        self.icon = ItemIcon(parent=qtyCol, pos=(1, 0, 32, 32), align=uiconst.TOPLEFT, idx=0)
        self.productNameLabel = Label(parent=qtyCol, text='', align=uiconst.CENTERLEFT, left=28)
        qtyCont = self.AddColumnContainer()
        self.gauge = Gauge(parent=qtyCont, name='productGauge', value=0.0, color=(1, 1, 1, 0), gaugeHeight=16, align=uiconst.TOALL, pos=(5, 5, 5, 0), state=uiconst.UI_DISABLED, gradientBrightnessFactor=1.5)
        self.tempQtyLabel = Label(parent=qtyCont, text='', align=uiconst.CENTERLEFT, left=6)

    def Load(self, node):
        self.sr.node = node
        self.typeID = node.typeID
        self.gauge.SetColor((1, 0, 0, 1))
        self.icon.SetTypeID(self.typeID)
        self.icon.left = node.sublevel * 16
        self.productNameLabel.text = node.typeName
        self.productNameLabel.left = self.icon.left + self.icon.width
        value = node.percentage
        isNew = True
        self.gauge.SetValue(value, animate=isNew)
        self.gauge.SetValueText(value)
        self.gauge.SetColor(node.gaugeColor)
        if value >= 1:
            self.gauge.display = False
            self.tempQtyLabel.text = value

    def ShowInfo(self):
        sm.GetService('info').ShowInfo(self.typeID)

    @staticmethod
    def GetFixedColumns():
        return {localization.GetByLabel('UI/Inflight/Scanner/Abundance'): 100}

    @staticmethod
    def GetShift(node):
        return node.sublevel * 16 + 33


def GetOreColor(typeID):
    return GetColorForBaseTypeID(typeID)
