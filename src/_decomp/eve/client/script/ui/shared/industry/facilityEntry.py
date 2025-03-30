#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\facilityEntry.py
from evePathfinder.core import IsUnreachableJumpCount
from math import pi
import carbonui.const as uiconst
import eveformat.client
import industry
import localization
import structures
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.shared.industry import industryUIConst
from eve.client.script.ui.shared.industry.industryUIConst import VIEWMODE_ICONLIST
from eve.client.script.ui.shared.industry.installationActivityIcon import InstallationActivityIcon
from eveservices.menu import GetMenuService
from utillib import KeyVal

class FacilityEntry(BaseListEntryCustomColumns):
    default_name = 'FacilityEntry'

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.facilityData = self.node.facilityData
        self.item = self.node.item
        self.viewMode = self.node.viewMode
        self.showTax = self.node.activityID in industry.ACTIVITIES
        self.AddColumnJumps()
        self.AddColumnText(self.GetSecurityLabel())
        self.AddColumnText(self.facilityData.GetName())
        self.AddColumnsActivities()
        if self.showTax:
            self.AddColumnsTax()
        self.AddColumnText(self.facilityData.GetTypeName())
        self.AddColumnText(self.facilityData.GetOwnerName())

    def AddColumnJumps(self):
        jumps = self.node.jumps
        if not IsUnreachableJumpCount(jumps):
            self.AddColumnText(jumps)
        else:
            col = self.AddColumnContainer()
            Sprite(name='infinityIcon', parent=col, align=uiconst.CENTERLEFT, pos=(6, 0, 11, 6), texturePath='res:/UI/Texture/Classes/Industry/infinity.png', opacity=Label.default_color[3])

    def AddColumnsActivities(self):
        costIndexes = self.facilityData.GetCostIndexByActivityID()
        iconSize = 20 if self.viewMode == VIEWMODE_ICONLIST else 14
        for i, activityID in enumerate(industry.ACTIVITIES):
            col = self.AddColumnContainer()
            isEnabled = activityID in self.facilityData.activities
            isFilterTarget = isEnabled and (self.node.activityID not in self.facilityData.activities or self.node.activityID == activityID)
            btn = InstallationActivityIcon(parent=col, align=uiconst.CENTER, pos=(0,
             -1,
             iconSize,
             iconSize), iconSize=iconSize, activityID=activityID, isEnabled=isEnabled, isFilterTarget=isFilterTarget, facilityData=self.facilityData)
            systemCostIndex = costIndexes.get(activityID, None)
            if systemCostIndex:
                maxIndex = sm.GetService('facilitySvc').GetMaxActivityModifier(activityID)
                value = systemCostIndex / maxIndex
                self.ConstructSystemCostGradient(col, value)

    def AddColumnsTax(self):
        taxRates = self.facilityData.GetServiceTaxes()
        text = ''
        for serviceID, tax in taxRates.iteritems():
            if tax is None or structures.GetActivityID(serviceID) != self.node.activityID:
                continue
            text += '%.2f/' % tax

        self.AddColumnText(text[:-1])

    def ConstructSystemCostGradient(self, col, systemCostIndex):
        GradientSprite(name='systemCostGradient', align=uiconst.TOLEFT_PROP, state=uiconst.UI_DISABLED, parent=col, width=systemCostIndex, padding=0, rgbData=((0.0, industryUIConst.COLOR_SYSTEMCOSTINDEX[:3]),), rotation=pi / 2, alphaData=((0.0, 1.0),
         (0.075, 1.0),
         (0.075001, 0.2),
         (0.8, 0.0)))

    @staticmethod
    def GetDynamicHeight(node, width):
        if node.viewMode == VIEWMODE_ICONLIST:
            return 28
        else:
            return 20

    @staticmethod
    def GetDefaultColumnWidth():
        return {localization.GetByLabel('UI/Industry/Facility'): 230,
         localization.GetByLabel('UI/Common/Owner'): 230}

    @staticmethod
    def GetFixedColumns(viewMode):
        ret = {}
        if viewMode == VIEWMODE_ICONLIST:
            iconSize = 36
            ret[localization.GetByLabel('UI/Industry/Activities')] = 154
        else:
            iconSize = 22
            ret[localization.GetByLabel('UI/Industry/Activities')] = 130
        ret.update({localization.GetByLabel('UI/Industry/ActivityManufacturing'): iconSize,
         localization.GetByLabel('UI/Industry/ActivityCopying'): iconSize,
         localization.GetByLabel('UI/Industry/ActivityMaterialEfficiencyResearch'): iconSize,
         localization.GetByLabel('UI/Industry/ActivityTimeEfficiencyResearch'): iconSize,
         localization.GetByLabel('UI/Industry/ActivityInvention'): iconSize,
         localization.GetByLabel('UI/Industry/ActivityReaction'): iconSize})
        return ret

    def GetSecurityLabel(self):
        return eveformat.solar_system_security_status(self.facilityData.solarSystemID)

    @staticmethod
    def GetColumnSortValues(facilityData, jumps, activityID, showTax):
        if facilityData.facilityID == session.stationid:
            jumps = -1
        costIndexes = facilityData.GetCostIndexByActivityID()
        costIndexValues = tuple((costIndexes.get(activityID, None) for activityID in industry.ACTIVITIES))
        ret = (jumps, sm.GetService('map').GetSecurityStatus(facilityData.solarSystemID), facilityData.GetName()) + costIndexValues
        if showTax:
            taxes = []
            taxRates = facilityData.GetServiceTaxes()
            for serviceID, tax in taxRates.iteritems():
                if tax is None or structures.GetActivityID(serviceID) != activityID:
                    continue
                taxes.append(tax)

            if taxes:
                facilityTaxSortValue = float(sum(taxes)) / len(taxes)
            else:
                facilityTaxSortValue = facilityData.tax
            ret += (facilityTaxSortValue,)
        ret += (facilityData.GetTypeName(), facilityData.GetOwnerName().lower())
        return ret

    @staticmethod
    def GetHeaders(showTax = False):
        activityTexts = [ localization.GetByLabel(industryUIConst.ACTIVITY_NAMES[activityID]) for activityID in industry.ACTIVITIES ]
        ret = [localization.GetByLabel('UI/Common/Jumps'), localization.GetByLabel('UI/Common/Security'), localization.GetByLabel('UI/Industry/Facility')] + activityTexts
        if showTax:
            ret.append(localization.GetByLabel('UI/Industry/Tax'))
        ret.extend([localization.GetByLabel('UI/Industry/FacilityType'), localization.GetByLabel('UI/Common/Owner')])
        return tuple(ret)

    def GetMenu(self):
        return GetMenuService().GetMenuFromItemIDTypeID(itemID=self.facilityData.facilityID, typeID=self.facilityData.typeID)

    def GetDragData(self):
        ret = KeyVal(__guid__='xtriui.ListSurroundingsBtn', typeID=self.facilityData.typeID, itemID=self.facilityData.facilityID, label=self.facilityData.GetName())
        return (ret,)
