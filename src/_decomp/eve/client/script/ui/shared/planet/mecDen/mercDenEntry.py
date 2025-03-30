#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\planet\mecDen\mercDenEntry.py
from collections import OrderedDict
import eveicon
import evetypes
from carbon.common.script.util.format import FmtAmt
from carbonui import TextColor, Align, Density, TextBody
from carbonui.control.button import Button
from carbonui.uiconst import LABELTABMARGIN, PickState
from carbonui.uicore import uicore
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from carbonui.primitives.fill import Fill
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.shared.planet.mecDen.mercDenUtil import DEN_COL_NAME, DEN_COL_SYSTEM, DEN_COL_PLANET, DEN_COL_STATE, DEN_COL_INFOM, DEN_COL_MTO
from localization import GetByLabel
LABEL_PATH_STATE_ACTIVE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/StateNameActive'
LABEL_PATH_STATE_INACTIVE = 'UI/Sovereignty/MercenaryDen/ConfigurationWindow/StateNameInactive'

class ColumnInfo(object):

    def __init__(self, labelPath, hintText = None):
        self._labelPath = labelPath
        self._hintText = hintText

    @property
    def columnText(self):
        if self._labelPath > 0:
            return GetByLabel(self._labelPath)

    @property
    def hintText(self):
        return self._hintText


class BaseMerDenEntry(BaseListEntryCustomColumns):
    default_height = 32
    headerInfo = d = OrderedDict()
    d[DEN_COL_NAME] = ColumnInfo('UI/Common/Name')
    d[DEN_COL_SYSTEM] = ColumnInfo('UI/Common/SolarSystem')
    d[DEN_COL_PLANET] = ColumnInfo('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/HeaderPlanet')
    d[DEN_COL_STATE] = ColumnInfo('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/HeaderState')
    d[DEN_COL_INFOM] = ColumnInfo('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/HeaderInfomorphs')
    d[DEN_COL_MTO] = ColumnInfo('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/HeaderMTOS', GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/HeaderMTOsTooltip'))

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.AddName()
        self.AddSystem()
        self.AddPlanet()
        self.AddState()
        self.AddInfomorphs()
        self.AddMTOs()

    def Load(self, node):
        labelsDict = self.node.labelsDict
        self.nameLabel.text = labelsDict.get(DEN_COL_NAME, '')
        self.systemLabel.text = labelsDict.get(DEN_COL_SYSTEM, '')
        self.planetLabel.text = labelsDict.get(DEN_COL_PLANET, '')
        self.stateLabel.text = labelsDict.get(DEN_COL_STATE, '')
        self.infomorphsLabel.text = labelsDict.get(DEN_COL_INFOM, '')
        self.mtoLabel.text = labelsDict.get(DEN_COL_MTO, '')

    def AddName(self):
        self.nameLabel = self.AddColumnBodyText()
        Fill(parent=self.nameLabel.parent, color=eveThemeColor.THEME_FOCUSDARK, opacity=0.15)

    def AddSystem(self):
        self.systemLabel = self.AddColumnBodyText()

    def AddPlanet(self):
        self.planetLabel = self.AddColumnBodyText()

    def AddState(self):
        self.stateLabel = self.AddColumnBodyText()

    def AddInfomorphs(self):
        self.infomorphsLabel = self.AddColumnBodyText()
        self.infomorphsLabel.SetAlign(Align.CENTERRIGHT)

    def AddMTOs(self):
        self.mtoLabel = self.AddColumnBodyText()
        self.mtoLabel.SetAlign(Align.CENTERRIGHT)
        self.mtoLabel.parent.pickState = PickState.ON
        if self.node.LoadMotTooltipPanelFunc:
            self.mtoLabel.parent.LoadTooltipPanel = lambda tooltipPanel, *args: self.node.LoadMotTooltipPanelFunc(tooltipPanel, self.node)

    @classmethod
    def GetHeaders(cls):
        return [ x.columnText for x in cls.headerInfo.itervalues() ]

    @staticmethod
    def GetColWidths(node, idx = None):
        LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)
        labelsDict = node.labelsDict

        def GetWidthFor(cIdx):
            if cIdx >= len(node.decoClass.headerInfo):
                return 50
            colName = node.decoClass.headerInfo.keys()[cIdx]
            text = labelsDict.get(colName, '')
            return uicore.font.MeasureTabstops([(text,) + LABEL_PARAMS])[0]

        if idx is None:
            colWidths = [ GetWidthFor(i) for i in xrange(len(MerDenEntry.headerInfo)) ]
            return colWidths
        return [GetWidthFor(idx)]

    @classmethod
    def GetHeadersHint(cls, i):
        key = cls.headerInfo.keys()[i]
        headerInfo = cls.headerInfo[key]
        return headerInfo.hintText


class MerDenEntry(BaseMerDenEntry):
    default_name = 'mercDenEntry'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        super(MerDenEntry, self).ApplyAttributes(attributes)
        self.AddReloadBtn()

    def Load(self, node):
        super(MerDenEntry, self).Load(node)
        if node.mercDenEntryInfo.has_complete_info:
            self.reloadBtn.Hide()
        else:
            self.reloadBtn.Show()

    def AddReloadBtn(self):
        self.reloadBtn = Button(parent=self, align=Align.CENTERRIGHT, label=GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/ReloadData'), func=self.ReloadEntry, density=Density.COMPACT, texturePath=eveicon.refresh)
        self.reloadBtn.Hide()

    def ReloadEntry(self, *args):
        node = self.sr.node
        reloadFunc = node.reloadFunc
        if reloadFunc:
            reloadFunc(self)

    @staticmethod
    def GetColumnSortValues(sortDict):
        return [ sortDict.get(h, '') for h in MerDenEntry.headerInfo ]


class MerDenEmptySlotEntry(BaseMerDenEntry):

    def ApplyAttributes(self, attributes):
        super(MerDenEmptySlotEntry, self).ApplyAttributes(attributes)
        systemParent = self.systemLabel.parent
        systemParent.clipChildren = False
        text = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/EmptySlotDesc')
        TextBody(parent=systemParent, text=text, align=Align.CENTERLEFT, left=LABELTABMARGIN, color=TextColor.SECONDARY)
        self.nameLabel.SetTextColor(TextColor.SECONDARY)

    @staticmethod
    def GetSortValue(node, by, direction, idx):
        if direction:
            return -9999999999999999999999L
        else:
            return 'zzzzzzzzzzzzzzzzzzzzz'


def GetMercDenEntry(wnd, mercDenEntryInfo, isSelected):
    data = GetMercDenEntryData(wnd, mercDenEntryInfo, isSelected)
    entry = GetFromClass(MerDenEntry, data)
    return entry


def GetMercDenEntryData(wnd, mercDenEntryInfo, isSelected):
    data = {}
    sortDict = {}
    if not mercDenEntryInfo.has_complete_info:
        labelsDict = {k:'' for k in MerDenEntry.headerInfo.keys()[1:]}
        labelsDict[DEN_COL_NAME] = GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/DenWithoutInfo')
        data['reloadFunc'] = wnd.ReloadEntry
    else:
        solarSystemName = cfg.evelocations.Get(mercDenEntryInfo.solar_system_id).name
        infomorphs_info = mercDenEntryInfo.infomorphs_info
        infomorphs_available = infomorphs_info.count
        denTypeID = mercDenEntryInfo.type_id
        denName = '%s %s' % (solarSystemName, evetypes.GetName(denTypeID))
        numMtos = FmtAmt(len(mercDenEntryInfo.activities))
        labelsDict = {DEN_COL_NAME: denName,
         DEN_COL_SYSTEM: solarSystemName,
         DEN_COL_PLANET: cfg.evelocations.Get(mercDenEntryInfo.planet_id).name if mercDenEntryInfo.planet_id else '-',
         DEN_COL_STATE: GetByLabel(LABEL_PATH_STATE_ACTIVE) if mercDenEntryInfo.is_enabled else GetByLabel(LABEL_PATH_STATE_INACTIVE),
         DEN_COL_INFOM: FmtAmt(infomorphs_available),
         DEN_COL_MTO: numMtos}
        sortDict = {k:v.lower() for k, v in labelsDict.iteritems()}
        sortDict[DEN_COL_INFOM] = infomorphs_available
        sortDict[DEN_COL_MTO] = len(mercDenEntryInfo.activities)
        data['LoadMotTooltipPanelFunc'] = wnd.LoadMotTooltipPanel
    sortValues = MerDenEntry.GetColumnSortValues(sortDict)
    data.update({'labelsDict': labelsDict,
     'itemID': mercDenEntryInfo.item_id,
     'OnClick': wnd.OnMercDenClicked,
     'mercDenEntryInfo': mercDenEntryInfo,
     'isSelected': isSelected,
     'GetMenu': wnd.GetMercDenMenu,
     'sortValues': sortValues})
    return data


def GetEmptySlotEntry():
    labelsDict = {DEN_COL_NAME: GetByLabel('UI/Sovereignty/MercenaryDen/MyMercenaryDensWindow/EmptySlot')}
    data = {'labelsDict': labelsDict,
     'selectable': False,
     'GetSortValue': MerDenEmptySlotEntry.GetSortValue}
    return GetFromClass(MerDenEmptySlotEntry, data)
