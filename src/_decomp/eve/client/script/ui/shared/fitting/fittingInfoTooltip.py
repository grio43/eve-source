#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\fittingInfoTooltip.py
import evetypes
from carbonui import uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.entries.fitting import FittingModuleEntry
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium, EveLabelMediumBold
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.util.uix import GetTextWidth
from eve.common.lib import appConst as const
from localization import GetByLabel
from utillib import KeyVal

def LoadFittingInfoTooltip(tooltipPanel, fitting):
    tooltipPanel.LoadGeneric1ColumnTemplate()
    spacer = tooltipPanel.AddSpacer(width=280, height=2, colSpan=tooltipPanel.columns)
    tooltipPanel.AddLabelMedium(text='<b>%s</b>' % GetByLabel('UI/Market/MarketQuote/FitToApplyToCurrentShip'))
    shipInfoCont = Container(name='shipCont', parent=tooltipPanel, align=uiconst.TOTOP, height=64, padTop=6)
    shipIconCont = Container(name='shipIconCont', parent=shipInfoCont, align=uiconst.TOLEFT, width=64)
    shipIcon = ItemIcon(name='shipIcon', parent=shipIconCont, pos=(0, 0, 64, 64), left=const.defaultPadding, typeID=fitting.shipTypeID)
    shipTypeName = EveLabelMediumBold(text=evetypes.GetName(fitting.shipTypeID), parent=shipInfoCont, align=uiconst.TOTOP, padLeft=10)
    maxWidth = shipTypeName.textwidth + shipTypeName.padLeft
    if fitting.name:
        fittingName = EveLabelMedium(text=fitting.name, parent=shipInfoCont, align=uiconst.TOTOP, padTop=4, padLeft=10)
        maxWidth = max(maxWidth, fittingName.textwidth + fittingName.padLeft)
    scrollCont = Container(name='scrollCont', parent=tooltipPanel, align=uiconst.TOTOP, padTop=4)
    fittingInfoScroll = Scroll(name='fittingInfoScroll', parent=scrollCont)
    scrolllist, mW = GetFittingInfoScrollListAndMaxWidth(fitting)
    maxWidth = max(maxWidth, mW)
    spacer.width = min(300, maxWidth)
    fittingInfoScroll.Load(contentList=scrolllist)
    contentHeight = fittingInfoScroll.GetContentHeight() + 4
    if contentHeight > 200:
        tooltipPanel.SetState(uiconst.UI_NORMAL)
        contentHeight = 200
    scrollCont.height = contentHeight


def GetFittingInfoScrollListAndMaxWidth(fitting):
    scrollListData = sm.GetService('fittingSvc').GetFittingInfoForScrollList(fitting)
    scrollList = []
    maxWidth = 0
    for d in scrollListData:
        if isinstance(d, KeyVal):
            maxWidth = max(maxWidth, GetTextWidth(d.label) + 33 + 20)
            entry = GetFromClass(FittingModuleEntryFitted, d)
            scrollList.append(entry)
        else:
            scrollList.append(d)

    return (scrollList, maxWidth)


class FittingModuleEntryFitted(FittingModuleEntry):
    __guid__ = 'listentry.FittingModuleEntryFitted'

    def Load(self, node):
        FittingModuleEntry.Load(self, node)
        self.sr.haveIcon.display = False
        self.sr.infoicon.display = False
