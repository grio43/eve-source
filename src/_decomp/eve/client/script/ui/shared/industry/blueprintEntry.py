#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\industry\blueprintEntry.py
from evePathfinder.core import IsUnreachableJumpCount
from carbonui.const import TOALL, UI_DISABLED
from menu import MenuLabel
from carbonui.primitives.container import Container
from carbonui.primitives.gradientSprite import GradientSprite
from carbonui.util.color import Color
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import Label
from eve.client.script.ui.control.itemIcon import ItemIcon
from eve.client.script.ui.shared.industry import industryUIConst, GetTypeName, GetActivitySum
from eve.client.script.ui.shared.industry.views.containersMETE import ContainerTE, ContainerME
import industry
import localization
import carbonui.const as uiconst
from eve.client.script.ui.shared.industry.industryUIConst import ACTIVITY_ICONS_SMALL, ACTIVITY_NAMES, VIEWMODE_ICONLIST, VIEWMODE_LIST
from carbonui.primitives.sprite import Sprite
import eve.client.script.ui.util.uix as uix
from carbonui.control.buttonIcon import ButtonIcon
import telemetry
from carbonui.uicore import uicore
from eveservices.menu import GetMenuService

class BlueprintEntry(BaseListEntryCustomColumns):
    default_name = 'BlueprintEntry'

    def ApplyAttributes(self, attributes):
        BaseListEntryCustomColumns.ApplyAttributes(self, attributes)
        self.bpData = self.node.bpData
        self.item = self.node.item
        self.activityCallback = self.node.activityCallback
        self.activityButtons = []
        self.itemIcon = None
        self.viewMode = self.node.viewMode
        self.AddColumnBlueprintLabel()
        self.AddColumnMaterialEfficiency()
        self.AddColumnTimeEfficiency()
        self.AddColumnRunsRemaining()
        self.columnActivities = self.AddColumnActivities()
        if self.node.showFacility:
            self.AddColumnJumps()
            self.AddColumnText(self.bpData.GetFacilityName())
        if self.node.showLocation:
            self.AddColumnText(self.bpData.GetLocationName())
        self.AddColumnText(self.bpData.GetGroupName())
        self.AddColumnText(self.bpData.GetAvailabilityText())
        self.OnJobStateChanged()

    def OnJobStateChanged(self, status = None):
        if status:
            isInstalled = industry.STATUS_UNSUBMITTED < status < industry.STATUS_COMPLETED
            if status in (industry.STATUS_INSTALLED, industry.STATUS_DELIVERED):
                self.AnimFlash(Color.WHITE)
        else:
            isInstalled = self.bpData.IsInstalled()
        isImpounded = self.bpData.IsImpounded()
        disabled = isImpounded or isInstalled
        if isInstalled:
            opacity = 0.15
        elif isImpounded:
            opacity = 0.3
        else:
            opacity = 1.0
        for col in self.columns:
            col.opacity = opacity

        if disabled:
            self.columnActivities.Disable()
        else:
            self.columnActivities.Enable()

    def AnimFlash(self, color):
        width = 500
        flashCont = Container(parent=self, idx=0, align=uiconst.TOPLEFT, width=width, height=self.height)
        flashGradient = GradientSprite(bgParent=flashCont, rgbData=[(0, color[:3])], alphaData=[(0, 0.0), (0.9, 0.4), (1.0, 0.0)])
        arrows = Sprite(parent=flashCont, align=uiconst.CENTERLEFT, texturePath='res:/UI/Texture/Classes/Industry/CenterBar/arrows.png', pos=(0,
         0,
         375,
         self.height), color=color, opacity=0.15, tileX=True)
        duration = self.width / 600.0
        uicore.animations.MorphScalar(flashCont, 'left', -width, self.width + width, duration=duration, curveType=uiconst.ANIM_LINEAR)
        uicore.animations.FadeTo(flashCont, 0.0, 1.0, duration=duration, callback=flashCont.Close, curveType=uiconst.ANIM_WAVE)

    @staticmethod
    def GetDynamicHeight(node, width):
        if node.viewMode == VIEWMODE_ICONLIST:
            return 36
        else:
            return 22

    def AddColumnRunsRemaining(self):
        runsRemaining = self.bpData.runsRemaining
        if runsRemaining != -1:
            self.AddColumnText('%s' % runsRemaining)
        else:
            col = self.AddColumnContainer()
            Sprite(name='infinityIcon', parent=col, align=uiconst.CENTERLEFT, pos=(6, 0, 11, 6), texturePath='res:/UI/Texture/Classes/Industry/infinity.png', opacity=Label.default_color[3])

    def AddColumnJumps(self):
        jumps = self.node.jumps
        if not IsUnreachableJumpCount(jumps):
            self.AddColumnText(jumps)
        else:
            col = self.AddColumnContainer()
            Sprite(name='infinityIcon', parent=col, align=uiconst.CENTERLEFT, pos=(6, 0, 11, 6), texturePath='res:/UI/Texture/Classes/Industry/infinity.png', opacity=Label.default_color[3])

    def AddColumnBlueprintLabel(self):
        col = self.AddColumnContainer()
        if self.viewMode == VIEWMODE_LIST:
            texturePath, hint = uix.GetTechLevelIconPathAndHint(self.bpData.blueprintTypeID)
            if texturePath:
                techIconSize = 16 if self.viewMode == VIEWMODE_ICONLIST else 12
                Sprite(name='techIcon', parent=col, texturePath=texturePath, hint=hint, width=techIconSize, height=techIconSize)
        if self.viewMode == VIEWMODE_ICONLIST:
            iconSize = 32
            self.itemIcon = ItemIcon(parent=col, typeID=self.bpData.blueprintTypeID, align=uiconst.CENTERLEFT, state=uiconst.UI_DISABLED, width=iconSize, bpData=self.bpData, height=iconSize, left=2)
        else:
            iconSize = 0
        Label(parent=col, text=self.bpData.GetLabel(), align=uiconst.CENTERLEFT, left=iconSize + 4, idx=0)

    def _AddColumnMETE(self, cls, value):
        col = self.AddColumnContainer()
        opacity = 0.5 if not value else 1.0
        isCompact = self.viewMode != VIEWMODE_ICONLIST
        gauge = cls(parent=col, align=TOALL, state=UI_DISABLED, padding=(3, 2, 3, 6), opacity=opacity, showBG=False, isCompact=isCompact)
        gauge.SetValue(value)

    def AddColumnMaterialEfficiency(self):
        value = self.bpData.materialEfficiency
        cls = ContainerME
        self._AddColumnMETE(cls, value)

    def AddColumnTimeEfficiency(self):
        value = self.bpData.timeEfficiency
        cls = ContainerTE
        self._AddColumnMETE(cls, value)

    def AddColumnActivities(self):
        col = self.AddColumnContainer()
        ICONSIZE = 20 if self.viewMode == VIEWMODE_ICONLIST else 14
        for i, activityID in enumerate(industry.ACTIVITIES):
            isEnabled = activityID in self.bpData.activities.keys()
            hint = ACTIVITY_NAMES.get(activityID) if isEnabled else 'UI/Industry/ActivityNotAvailable'
            opacity = 1.0
            if isEnabled and not (self.bpData.facility and self.bpData.facility.CanDoActivity(activityID, self.bpData.productTypeID)):
                opacity = 0.4
            btn = ActivityButtonIcon(parent=col, align=uiconst.CENTERLEFT, pos=(6 + i * (ICONSIZE + 4),
             0,
             ICONSIZE + 4,
             ICONSIZE + 4), texturePath=ACTIVITY_ICONS_SMALL[activityID], iconSize=ICONSIZE, func=self.OnActivityBtn, args=(activityID, self.bpData), hint=localization.GetByLabel(hint), isHoverBGUsed=False, colorSelected=industryUIConst.GetActivityColor(activityID), iconEnabledOpacity=opacity)
            self.activityButtons.append(btn)
            if not isEnabled:
                btn.Disable(0.05)

        return col

    def OnActivityBtn(self, activityID, bpData):
        self.activityCallback(self.bpData, activityID)

    def GetMenu(self):
        m = GetMenuService().GetMenuFromItemIDTypeID(self.bpData.blueprintID, self.bpData.blueprintTypeID, includeMarketDetails=True, invItem=self.item)
        label = MenuLabel('UI/Industry/Facility')
        m.append((label, GetMenuService().CelestialMenu(itemID=self.bpData.facilityID)))
        return m

    @staticmethod
    def GetDefaultColumnWidth():
        return {localization.GetByLabel('UI/Industry/Blueprint'): 230,
         localization.GetByLabel('UI/Industry/MaterialEfficiency'): 80,
         localization.GetByLabel('UI/Industry/TimeEfficiency'): 80,
         localization.GetByLabel('UI/Industry/Facility'): 200}

    @staticmethod
    def GetFixedColumns(viewMode):
        if viewMode == VIEWMODE_ICONLIST:
            return {localization.GetByLabel('UI/Industry/Activities'): 157}
        else:
            return {localization.GetByLabel('UI/Industry/Activities'): 120}

    @staticmethod
    def GetHeaders(showFacility = True, showLocation = True, showImpounded = False):
        ret = [localization.GetByLabel('UI/Industry/Blueprint'),
         localization.GetByLabel('UI/Industry/MaterialEfficiency'),
         localization.GetByLabel('UI/Industry/TimeEfficiency'),
         localization.GetByLabel('UI/Industry/RunsRemaining'),
         localization.GetByLabel('UI/Industry/Activities')]
        if showFacility:
            ret.extend((localization.GetByLabel('UI/Common/Jumps'), localization.GetByLabel('UI/Industry/Facility')))
        if showLocation:
            ret.append(localization.GetByLabel('UI/Industry/InventoryLocation'))
        ret.append(localization.GetByLabel('UI/Common/Group'))
        if showImpounded:
            ret.append(localization.GetByLabel('UI/ScienceAndIndustry/ScienceAndIndustryWindow/Availability'))
        return ret

    @staticmethod
    @telemetry.ZONE_METHOD
    def GetColumnSortValues(bpData, jumps = None, showFacility = True, showLocation = True):
        activitySum = GetActivitySum(bpData.activities.keys())
        typeName = GetTypeName(bpData.blueprintTypeID)
        ret = [typeName.lower(),
         bpData.materialEfficiency,
         bpData.timeEfficiency,
         bpData.runsRemaining,
         activitySum]
        if showFacility:
            facilityName = bpData.GetFacilityName()
            if facilityName:
                facilityName = facilityName.lower()
            ret.extend((jumps, facilityName))
        if showLocation:
            ret.append(bpData.GetLocationName())
        ret.append(bpData.GetGroupName())
        ret.append(bpData.GetAvailabilityText())
        return ret

    @telemetry.ZONE_METHOD
    def OnActivitySelected(self, itemID, activityID):
        for btn in self.activityButtons:
            if self.bpData.blueprintID == itemID and btn.activityID == activityID:
                btn.SetSelected()
            else:
                btn.SetDeselected()

    def GetDragData(self):
        ret = []
        nodes = self.sr.node.scroll.GetSelectedNodes(self.sr.node)
        for node in nodes:
            ret.append(node.bpData.GetDragData())

        return ret

    def OnDblClick(self, *args):
        sm.ScatterEvent('OnBlueprintEntryDblClicked')

    def OnMouseEnter(self, *args):
        BaseListEntryCustomColumns.OnMouseEnter(self, *args)
        if self.itemIcon:
            self.itemIcon.OnMouseEnter()

    def OnMouseExit(self, *args):
        BaseListEntryCustomColumns.OnMouseExit(self, *args)
        if self.itemIcon:
            self.itemIcon.OnMouseExit()

    @classmethod
    def GetCopyData(cls, node):
        bpData = node.bpData
        labelList = [bpData.GetLabel(),
         unicode(bpData.materialEfficiency),
         unicode(bpData.timeEfficiency),
         unicode(bpData.runsRemaining)]
        if node.showFacility:
            labelList += [unicode(node.jumps), bpData.GetFacilityName()]
        if node.showLocation:
            labelList += [bpData.GetLocationName()]
        labelList += [bpData.GetGroupName()]
        return '\t'.join(labelList)


class ActivityButtonIcon(ButtonIcon):

    def ApplyAttributes(self, attributes):
        ButtonIcon.ApplyAttributes(self, attributes)
        if self.isActive:
            self.Enable()
        self.activityID, self.bpData = attributes.args

    def OnDblClick(self, *args):
        if uicore.uilib.Key(uiconst.VK_SHIFT):
            job = sm.GetService('industrySvc').CreateJob(self.bpData, self.activityID, self.bpData.facilityID)
            sm.GetService('industrySvc').InstallJob(job)
