#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureBrowser\entries\structureEntry.py
import structures
from carbon.common.script.util.commonutils import StripTags
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.structure.structureIcon import StructureIcon
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.glowSprite import GlowSprite
from carbonui.fontconst import EVE_MEDIUM_FONTSIZE
from eve.client.script.ui.station import stationServiceConst
from eve.client.script.ui.structure.structureBrowser.browserUIConst import ALL_SERVICES
from eve.client.script.ui.structure.structureBrowser.extaColumnUtil import ExtraColumnProvider, GetHeaderForService, FormatColumnValue
from eve.client.script.ui.structure.structureBrowser.controllers.structureEntryController import StructureEntryController
from localization import GetByLabel
import carbonui.const as uiconst
from utillib import KeyVal
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService
HEIGHT = 48
ICONSIZE = 20
LABEL_PARAMS = (EVE_MEDIUM_FONTSIZE, 0, 0)

class StructureEntry(BaseListEntryCustomColumns):
    default_name = 'StructureEntry'

    def __init__(self, *args, **kwargs):
        self.controller = None
        super(StructureEntry, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.controller = self.node.controller
        self.AddColumnText(self.controller.GetNumJumps())
        self.AddColumnText(self.controller.GetSecurityWithColor())
        self.AddColumnText(self.controller.GetOwnerName())
        self.AddColumnName()
        self.AddColumnServices()
        self.AddExtraColumns()

    def AddColumnName(self):
        column = self.AddColumnContainer()
        name = self.controller.GetName()
        size = HEIGHT - 4
        StructureIcon(name='structureIcon_%s' % name.replace('<br>', '_'), parent=column, align=uiconst.CENTERLEFT, typeID=self.controller.GetTypeID(), structureID=self.controller.GetItemID(), pos=(0,
         0,
         size,
         size), state=uiconst.UI_PICKCHILDREN, wars=self.controller.GetWars())
        label = Label(parent=column, text=name, align=uiconst.CENTERLEFT, left=HEIGHT, state=uiconst.UI_NORMAL)
        label.GetMenu = None
        label.DelegateEventsNotImplemented(self)

    def AddColumnServices(self):
        column = self.AddColumnContainer()
        structureServices = self.controller.GetServices()
        structureServicesChecked = self.node.structureServicesChecked
        for i, data in enumerate(structureServices):
            left = i * ICONSIZE
            opacity = 1.0 if structureServicesChecked == ALL_SERVICES or data.name in structureServicesChecked else 0.2
            gs = StructureServiceIcon(name=data.name, parent=column, texturePath=data.iconID, pos=(left,
             0,
             ICONSIZE,
             ICONSIZE), hintHeader=data.label, opacity=opacity, serviceName=data.name, controller=self.controller, serviceID=data.serviceID)
            gs.DelegateEvents(self)

    def AddExtraColumns(self):
        structureServicesChecked = self.node.structureServicesChecked
        if structureServicesChecked == ALL_SERVICES:
            return
        extraColumnProvider = ExtraColumnProvider()
        checkedServicesWithUniqueColumns = extraColumnProvider.GetServicesForUniqueColumns(structureServicesChecked)
        for serviceName in checkedServicesWithUniqueColumns:
            columnText = extraColumnProvider.GetColumnText(self.controller, serviceName)
            if columnText is not None:
                self.AddColumnText(columnText)

    def GetDragData(self):
        nodesSelected = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        data = []
        for eachNode in nodesSelected:
            k = KeyVal(__guid__='xtriui.ListSurroundingsBtn', itemID=eachNode.controller.GetItemID(), typeID=eachNode.controller.GetTypeID(), label=StripTags(eachNode.controller.GetCleanName().replace('<br>', '-')), isMyCorpStructureEntry=True)
            data.append(k)

        return data

    @staticmethod
    def GetColumnSortValues(controller, structureServicesChecked):
        baseColumns = (controller.GetNumJumps(),
         controller.GetSecurity(),
         controller.GetOwnerName().lower(),
         '%s %s' % (controller.GetSystemName(), StripTags(controller.GetName()).lower()),
         len(controller.GetServices()))
        columnProvider = ExtraColumnProvider()
        extraColumnSortValues = []
        if structureServicesChecked != ALL_SERVICES:
            checkedServicesWithUniqueColumns = ExtraColumnProvider().GetServicesForUniqueColumns(structureServicesChecked)
            for eachServiceID in checkedServicesWithUniqueColumns:
                value = columnProvider.GetValueForColumn(controller, eachServiceID)
                if value == columnProvider.NOT_AVAILABLE:
                    continue
                extraColumnSortValues.append(value)

        baseColumns += tuple(extraColumnSortValues)
        return baseColumns

    @staticmethod
    def GetSortValue(node, by, sortDirection, idx):
        return (node.columnSortValues[idx],) + tuple(node.columnSortValues)

    @staticmethod
    def GetExtraHeaders(structureServicesChecked):
        extraHeaders = []
        if structureServicesChecked == ALL_SERVICES:
            return []
        for serviceName in structureServicesChecked:
            header = GetHeaderForService(serviceName)
            if header and header not in extraHeaders:
                extraHeaders += [header]

        return extraHeaders

    @staticmethod
    def GetHeaders(structureServicesChecked):
        extraHeaders = StructureEntry.GetExtraHeaders(structureServicesChecked)
        baseColumns = [GetByLabel('UI/Common/Jumps'),
         GetByLabel('UI/Common/Security'),
         GetByLabel('UI/Common/Owner'),
         GetByLabel('UI/Common/Name'),
         GetByLabel('UI/Structures/Browser/ServicesColumn')]
        return baseColumns + extraHeaders

    @staticmethod
    def GetDynamicHeight(node, width):
        return HEIGHT

    @staticmethod
    def GetDefaultColumnWidth():
        return {GetByLabel('UI/Industry/System'): 70,
         GetByLabel('UI/Common/Name'): 230}

    @staticmethod
    def GetFixedColumns():
        return {GetByLabel('UI/Structures/Browser/ServicesColumn'): ICONSIZE * len(stationServiceConst.serviceData) + 2}

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
            widths.append(uicore.font.MeasureTabstops([(controller.GetOwnerName(),) + LABEL_PARAMS])[0])
        if idx is None or idx == 3:
            nameToUse = max(StripTags(controller.GetName(), ignoredTags=('br',)).split('<br>'), key=len)
            widths.append(uicore.font.MeasureTabstops([(nameToUse,) + LABEL_PARAMS])[0] + HEIGHT - 4)
        return widths


class StructureServiceIcon(GlowSprite):
    default_align = uiconst.CENTERLEFT
    default_state = uiconst.UI_NORMAL

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        self.hintHeader = attributes.hintHeader
        self.serviceName = attributes.serviceName
        self.serviceID = attributes.serviceID
        self.isOffline = attributes.isOffline
        if self.isOffline:
            self.SetRGB(1.0, 1.0, 0.22)

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.margin = (4, 4, 4, 4)
        tooltipPanel.cellPadding = (4, 1, 4, 1)
        tooltipPanel.AddLabelMedium(text=self.hintHeader, colSpan=2)
        self.AddExtraInfo(tooltipPanel)

    def AddExtraInfo(self, tooltipPanel):
        if self.serviceID == structures.SERVICE_INDUSTRY:
            serviceIDs = structures.INDUSTRY_SERVICES
        else:
            serviceIDs = [self.serviceID]
        hintTextList = self.GetServiceNamesAndValues(serviceIDs)
        for name, value in hintTextList:
            if value is True:
                value = GetByLabel('UI/Common/True')
            tooltipPanel.AddLabelMedium(text=name, align=uiconst.CENTERLEFT)
            tooltipPanel.AddLabelMedium(text=value, align=uiconst.CENTERRIGHT)

    def GetServiceNamesAndValues(self, serviceIDs):
        namesAndValues = []
        for eachID in serviceIDs:
            settingIDForService = structures.SERVICES_ACCESS_SETTINGS.get(eachID, None)
            settingInfo = structures.SETTING_OBJECT_BY_SETTINGID.get(settingIDForService, None)
            if not settingInfo:
                continue
            value = self.controller.GetInfoForExtraColumns(eachID)
            if value is None:
                continue
            value = FormatColumnValue(value, settingInfo.valueType, settingIDForService)
            label = GetByLabel(settingInfo.labelPath)
            lineInfo = (label, value)
            if lineInfo not in namesAndValues:
                namesAndValues.append(lineInfo)

        return namesAndValues


class StructureServiceIconMyCorp(StructureServiceIcon):

    def AddExtraInfo(self, tooltipPanel):
        if self.isOffline:
            if self.serviceID == structures.SERVICE_INDUSTRY:
                labelPath = 'UI/Structures/Browser/IndustryServicesOffline'
            else:
                labelPath = 'UI/Structures/Browser/ServiceIsOffline'
            tooltipPanel.AddLabelMedium(text=GetByLabel(labelPath), align=uiconst.CENTERLEFT)
