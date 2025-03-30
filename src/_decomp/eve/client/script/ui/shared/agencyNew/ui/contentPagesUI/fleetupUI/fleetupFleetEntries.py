#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentPagesUI\fleetupUI\fleetupFleetEntries.py
import math
import blue
import evefleet
import evefleet.client
import gametime
from carbonui.primitives.fill import Fill
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui import eveColor
from eve.client.script.ui.control.baseListEntry import BaseListEntryCustomColumns
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveWindowUnderlay import ListEntryUnderlay
from eve.client.script.ui.util import uix
from carbon.common.script.sys.serviceConst import ROLE_GML
from carbon.common.script.util.format import FmtDate
from carbonui import uiconst
from eve.client.script.ui.shared.agencyNew.contentGroups import contentGroupConst
from eve.client.script.ui.shared.fleet.fleet import GetFleetActivityName
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIcon
from eve.client.script.ui.shared.agencyNew.ui.contentPagesUI.fleetupUI.joinFleetConfirmation import RequestToJoinFleet
from eveservices.menu import GetMenuService
from localization import GetByLabel
from menu import MenuLabel

class FleetUpListEntryUnderlay(ListEntryUnderlay):
    OPACITY_HOVER = 0.1
    OPACITY_MOUSEDOWN = 0.3
    OPACITY_SELECTED = 0.2
    default_color = eveColor.CRYO_BLUE
    default_padBottom = 0


class FleetUpListEntryBase(BaseListEntryCustomColumns):
    default_highlightClass = FleetUpListEntryUnderlay
    MOD_DIV = 2
    labelLeftDefault = 16

    def ApplyAttributes(self, attributes):
        self.currentBandingValue = None
        self._bandingFill = None
        self._selectionTriangle = None
        super(FleetUpListEntryBase, self).ApplyAttributes(attributes)

    def Load(self, node):
        super(FleetUpListEntryBase, self).Load(node)
        self.UpdateEntryWhenChangingSelection(node.selected)
        self.UpdateBandingColor()
        self.UpdateBandingFillVisibility()

    def AddColumnText(self, text = None, autoFadeValue = None):
        label = super(FleetUpListEntryBase, self).AddColumnText(text)
        if autoFadeValue is not None:
            label.autoFadeSides = autoFadeValue
        if self.sr.node.tabMargin:
            label.left = self.sr.node.tabMargin
        return label

    def GetTextColor(self, isSelected):
        if isSelected:
            textColor = eveColor.CRYO_BLUE
        else:
            textColor = self.sr.node.Get('fontColor', EveLabelMedium.default_color)
        return textColor

    def GetBandingColor(self):
        if self.currentBandingValue > 0:
            return (1.0, 1.0, 1.0, 0.05)
        else:
            return (0, 0, 0, 0.5)

    def UpdateBandingColor(self):
        idx = self.sr.node.idx
        self.currentBandingValue = idx % self.MOD_DIV
        if self._bandingFill:
            self._bandingFill.color = self.GetBandingColor()

    def ConstructBandingFill(self):
        if self._bandingFill is None or self._bandingFill.destroyed:
            self._bandingFill = Fill(name='bandingFill', bgParent=self, color=self.GetBandingColor())

    def UpdateBandingFillVisibility(self):
        isSelected = self.sr.node.selected
        isVisible = not isSelected and self.currentBandingValue > 0
        if isVisible:
            self.ConstructBandingFill()
            self._bandingFill.display = True
        elif self._bandingFill:
            self._bandingFill.display = False

    def ConstructTriangle(self):
        if self._selectionTriangle is None:
            self._selectionTriangle = Sprite(align=uiconst.CENTERLEFT, pos=(6, 0, 3, 5), parent=self, idx=0, name='_selectionTriangle', texturePath='res:/UI/Texture/classes/Agency/fleetup/scrollSelectedArrow.png', rotation=math.pi / 2)

    def UpdateEntryWhenChangingSelection(self, isSelected):
        pass

    def Select(self, animate = True):
        super(FleetUpListEntryBase, self).Select(animate)
        self.UpdateEntryWhenChangingSelection(True)
        self.UpdateBandingFillVisibility()
        self.ConstructTriangle()
        self._selectionTriangle.display = True

    def Deselect(self, animate = True):
        super(FleetUpListEntryBase, self).Deselect(animate)
        self.UpdateEntryWhenChangingSelection(False)
        self.UpdateBandingFillVisibility()
        if self._selectionTriangle:
            self._selectionTriangle.display = False


class FleetUpFleetEntry(FleetUpListEntryBase):
    default_name = 'FleetUpFleetEntry'
    isDragObject = True

    def ApplyAttributes(self, attributes):
        self.allLabels = []
        super(FleetUpFleetEntry, self).ApplyAttributes(attributes)
        node = self.node
        self.allLabels.append(self.AddColumnText(node.fleetActivityName, 10))
        self.allLabels.append(self.AddFleetLeader())
        self.allLabels.append(self.AddColumnText(node.fleetName, 10))
        self.allLabels.append(self.AddColumnText(node.dateText, 10))
        self.allLabels.append(self.AddColumnText(node.numMembersText, 10))
        self.allLabels.append(self.AddColumnText(node.jumpsText, 10))

    @classmethod
    def GetDynamicHeight(cls, node, width = None):
        node.height = uix.GetTextHeight(node.label, maxLines=1) + 11
        return node.height

    def Load(self, node):
        super(FleetUpFleetEntry, self).Load(node)
        if node.isMyFleet:
            for eachLabel in self.allLabels:
                eachLabel.bold = True
                eachLabel.Update()

    def UpdateEntryWhenChangingSelection(self, isSelected):
        textColor = self.GetTextColor(isSelected)
        for eachLabel in self.allLabels:
            eachLabel.SetTextColor(textColor)

    def GetTextColor(self, isSelected):
        return super(FleetUpFleetEntry, self).GetTextColor(isSelected or self.node.isMyFleet)

    def AddFleetLeader(self):
        fleetLeaderName = self.node.fleetLeaderName
        label = self.AddColumnText(fleetLeaderName)
        flag = self.node.leaderFlag
        AddAndSetFlagIcon(parentCont=label.parent, flag=flag, align=uiconst.CENTERLEFT, left=self.node.tabMargin)
        label.left += 16
        label.autoFadeSides = 10
        return label

    def GetMenu(self):
        node = self.node
        fleetID = node.fleetID
        fleetAd = node.fleetAd
        leader = fleetAd.leader
        fleetbossMenu = GetMenuService().CharacterMenu(leader.charID)
        fleetSvc = sm.GetService('fleet')
        m = [(MenuLabel('UI/Agency/Fleetup/FleetLeaderSubmenu'), fleetbossMenu)]
        if session.fleetid != fleetID:
            m += [(MenuLabel('UI/Agency/Fleetup/RequestToJoin'), RequestToJoinFleet, (fleetID, fleetAd))]
        elif fleetSvc.IsBoss():
            m += [(MenuLabel('UI/Fleet/FleetWindow/EditAdvert'), self.EditAdvert)]
            if sm.GetService('fleet').GetCurrentAdvertForMyFleet() is not None:
                m += [(MenuLabel('UI/Fleet/FleetWindow/RemoveAdvert'), self.UnregisterFleet)]
        if session.role & ROLE_GML > 0:
            m.append(('GM - fleetID: %s' % fleetID, blue.pyos.SetClipboardData, (str(fleetID),)))
        return m

    def UnregisterFleet(self, *args):
        sm.GetService('fleet').UnregisterFleet()
        sm.ScatterEvent('OnOwnAdvertUpdated')

    def EditAdvert(self, *args):
        sm.GetService('agencyNew').OpenWindow(contentGroupConst.contentGroupFleetUpRegister)

    def GetDragData(self, *args):
        data = evefleet.client.FleetDragData(fleet_id=self.sr.node.fleetID, name=self.sr.node.fleetName)
        return [data]

    def LoadTooltipPanel(self, tooltipPanel, *args):
        tooltipPanel.LoadGeneric2ColumnTemplate()
        tooltipPanel.cellSpacing = (6, 0)
        fleetAd = self.sr.node.fleetAd
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/HintFleetName'))
        tooltipPanel.AddLabelMedium(text=fleetAd.fleetName)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/HintFleetBoss'))
        tooltipPanel.AddLabelMedium(text=cfg.eveowners.Get(fleetAd.leader.charID).name)
        fleetAge = FmtDate(gametime.GetWallclockTime() - fleetAd.dateCreated, 'ns')
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/HintFleetAge'))
        tooltipPanel.AddLabelMedium(text=fleetAge)
        if fleetAd.numMembers:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/HintFleetMemberCount'))
            tooltipPanel.AddLabelMedium(text=fleetAd.numMembers)
            if fleetAd.advertJoinLimit and fleetAd.numMembers >= fleetAd.advertJoinLimit:
                joinLimitText = GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintFleetMemberCountMoreThanLimit', advertJoinLimit=fleetAd.advertJoinLimit)
                joinLimitText = '<color=0xffdd0000>%s</color>' % joinLimitText
                tooltipPanel.AddLabelMedium(text=joinLimitText, colSpan=tooltipPanel.columns, wrapWidth=250)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/HintScope'))
        groupScopeEntryAdded = False
        for isOpen, labelPath in ((evefleet.IsOpenToCorp(fleetAd), 'UI/Common/Corporation'), (evefleet.IsOpenToAlliance(fleetAd), 'UI/Common/Alliance'), (evefleet.IsOpenToMilitia(fleetAd), 'UI/Common/Militia')):
            if not isOpen:
                continue
            if groupScopeEntryAdded:
                tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel(labelPath))
            tooltipPanel.FillRow()
            groupScopeEntryAdded = True

        if fleetAd.membergroups_minStanding is not None:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumStanding', standing=fleetAd.membergroups_minStanding))
        if fleetAd.membergroups_minSecurity is not None:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumSecurity', security=fleetAd.membergroups_minSecurity))
        if evefleet.IsOpenToPublic(fleetAd) or evefleet.IsOpenToAllPublic(fleetAd):
            if groupScopeEntryAdded:
                tooltipPanel.AddSpacer(height=10, colSpan=tooltipPanel.columns)
                tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/Public Access'))
        if fleetAd.public_minStanding is not None:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumStanding', standing=fleetAd.public_minStanding))
        if fleetAd.public_minSecurity is not None:
            tooltipPanel.AddCell()
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Fleet/FleetRegistry/AdvertDetails/HintMinimumSecurity', security=fleetAd.public_minSecurity))
        tooltipPanel.FillRow()
        if fleetAd.joinNeedsApproval:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/ApplicationRequiresApprovalSummary'), colSpan=tooltipPanel.columns)
        if fleetAd.newPlayerFriendly:
            tooltipPanel.AddLabelMedium(text=GetByLabel('UI/Agency/Fleetup/NewPlayerFriendlySummary'), colSpan=tooltipPanel.columns)

    @staticmethod
    def GetCharIndexValuesAndLabel(fleetAd, jumps):
        charIndexValues = [GetFleetActivityName(fleetAd.activityValue),
         cfg.eveowners.Get(fleetAd.leader.charID).name,
         fleetAd.fleetName,
         FmtDate(gametime.GetWallclockTime() - fleetAd.dateCreated, 'ns'),
         None if fleetAd.hideInfo else fleetAd.numMembers,
         jumps]
        label = '%s<t>%s<t>   %s<t>%s<t>%s<t>%s' % tuple(charIndexValues)
        return (charIndexValues, label)
