#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\entries\skyhookEntry.py
from carbon.common.script.util.commonutils import StripTags
from carbon.common.script.util.timerstuff import AutoTimer
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.control.eveLabel import Label
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from localization import GetByLabel
import carbonui.const as uiconst
from utillib import KeyVal
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
HEIGHT = 48
ICONSIZE = 20
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)
VULNERABILITY_LABEL_UPDATE_DELAY = 1000

class SkyhookEntry(BaseListEntryCustomColumns):
    default_name = 'SkyhookEntry'

    def __init__(self, *args, **kwargs):
        self.controller = None
        super(SkyhookEntry, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.controller = self.node.controller
        self.AddColumnText(self.controller.GetNumJumps())
        self.AddColumnText(self.controller.GetSecurityWithColor())
        self.AddColumnText(self.controller.GetSolarSystemName())
        self.AddColumnName()
        self.AddColumnText(self.controller.GetStateText())
        self.AddColumnText(self.controller.GetHarvestText())
        self._theftVulnerabilityLabel = self.AddColumnText(self.controller.GetTheftVulnerabilityText())
        self._updateThread = AutoTimer(VULNERABILITY_LABEL_UPDATE_DELAY, self.UpdateTheftVulnerabilityText)

    def UpdateTheftVulnerabilityText(self):
        if self.destroyed:
            if self._updateThread:
                self._updateThread.KillTimer()
            self._updateThread = None
            return
        self._theftVulnerabilityLabel.text = self.controller.GetTheftVulnerabilityText()

    def AddColumnName(self):
        column = self.AddColumnContainer()
        name = self.controller.GetName()
        size = HEIGHT - 4
        ItemIcon(name='skyhookIcon_%s' % name.replace('<br>', '_'), parent=column, align=uiconst.CENTERLEFT, typeID=self.controller.GetTypeID(), pos=(0,
         0,
         size,
         size), state=uiconst.UI_PICKCHILDREN)
        label = Label(parent=column, text=name, align=uiconst.CENTERLEFT, left=HEIGHT, state=uiconst.UI_NORMAL)
        label.GetMenu = None
        label.DelegateEventsNotImplemented(self)

    def GetDragData(self):
        nodesSelected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        data = []
        for eachNode in nodesSelected:
            k = KeyVal(__guid__='xtriui.ListSurroundingsBtn', itemID=eachNode.controller.GetItemID(), typeID=eachNode.controller.GetTypeID(), label=StripTags(eachNode.controller.GetCleanName().replace('<br>', '-')))
            data.append(k)

        return data

    @staticmethod
    def GetColumnSortValues(controller):
        baseColumns = (controller.GetNumJumps(),
         controller.GetSecurity(),
         controller.GetSystemName(),
         '%s %s' % (controller.GetSystemName(), StripTags(controller.GetName()).lower()),
         controller.GetStateText(),
         controller.GetHarvestText(),
         controller.GetTheftVulnerabilitySortValue())
        return baseColumns

    @staticmethod
    def GetSortValue(node, by, sortDirection, idx):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)

    @staticmethod
    def GetHeaders():
        baseColumns = [GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Common/Security'),
         GetByLabel('UI/Common/SolarSystem'),
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/StructureBrowser/SkyhookState'),
         GetByLabel('UI/StructureBrowser/SkyhookHarvest'),
         GetByLabel('UI/StructureBrowser/SkyhookTheftVulnerability')]
        return baseColumns

    @staticmethod
    def GetDynamicHeight(node, width):
        return HEIGHT

    @staticmethod
    def GetDefaultColumnWidth():
        return {GetByLabel('UI/Industry/SolarSystem'): 70,
         GetByLabel('UI/Common/Name'): 230}

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=self.controller.GetItemID(), typeID=self.controller.GetTypeID())

    @staticmethod
    def GetColWidths(node, idx = None):
        controller = node.controller
        widths = []
        if idx is None or idx == 0:
            jumpText = unicode(controller.GetNumJumps())
            widths.append(uicore.font.MeasureTabstops([(jumpText,) + LABEL_PARAMS])[0])
        if idx is None or idx == 1:
            securityText = unicode(controller.GetSecurity())
            widths.append(uicore.font.MeasureTabstops([(securityText,) + LABEL_PARAMS])[0])
        if idx is None or idx == 2:
            widths.append(uicore.font.MeasureTabstops([(controller.GetSolarSystemID(),) + LABEL_PARAMS])[0])
        if idx is None or idx == 3:
            nameToUse = max(StripTags(controller.GetName(), ignoredTags=('br',)).split('<br>'), key=len)
            widths.append(uicore.font.MeasureTabstops([(nameToUse,) + LABEL_PARAMS])[0] + HEIGHT - 4)
        if idx is None or idx == 4:
            widths.append(uicore.font.MeasureTabstops([(controller.GetStateText(),) + LABEL_PARAMS])[0])
        if idx is None or idx == 5:
            widths.append(uicore.font.MeasureTabstops([(controller.GetHarvestText(),) + LABEL_PARAMS])[0])
        if idx is None or idx == 6:
            widths.append(uicore.font.MeasureTabstops([(controller.GetTheftVulnerabilityText(),) + LABEL_PARAMS])[0])
        return widths
