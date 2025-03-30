#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\incursionJournal.py
import localization
from carbon.common.script.util.format import FmtAmt
from carbonui import uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from eve.client.script.ui.control import eveIcon, eveLabel
from carbonui.control.button import Button
from eve.client.script.ui.control.themeColored import LineThemeColored
from eve.client.script.ui.shared.mapView.mapViewUtil import OpenMap
from eve.client.script.ui.shared.infoPanels.infoPanelIncursions import IncursionFinalEncounterIcon, SystemInfluenceBar
from eve.client.script.ui.shared.maps.mapcommon import STARMODE_INCURSION, STARMODE_FRIENDS_CORP
from talecommon.influence import CalculateDecayedInfluence
MIDDLECONTAINER_WIDTH = 200
MARGIN = 8

class IncursionTab:
    GlobalReport, Encounters, LPLog = range(3)


class GlobalIncursionReportEntry(SE_BaseClassCore):
    __guid__ = 'listentry.GlobalIncursionReportEntry'
    MARGIN = 8
    TEXT_OFFSET = 84
    BUTTON_OFFSET = 295

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.iconsize = iconsize = 44
        LineThemeColored(parent=self, align=uiconst.TOBOTTOM)
        self.factionParent = Container(name='factionParent', parent=self, align=uiconst.TOLEFT, pos=(0, 0, 64, 64), padding=MARGIN)
        middleCont = Container(parent=self, name='middleContainer', width=MIDDLECONTAINER_WIDTH, align=uiconst.TOLEFT, padTop=MARGIN, clipChildren=True)
        self.constellationLabel = BigReportLabel(name='constellationName', parent=middleCont, fontsize=20, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.statusText = SmallReportLabel(parent=middleCont, align=uiconst.TOTOP, uppercase=True)
        SmallReportLabel(name='systemInfluence', parent=middleCont, align=uiconst.TOTOP, text=localization.GetByLabel('UI/Incursion/Common/HUDInfluenceTitle'))
        self.statusBar = SystemInfluenceBar(parent=middleCont, pos=(0, 0, 200, 10), align=uiconst.TOTOP, padding=(0, 4, 0, 4))
        self.stagingText = SmallReportLabel(parent=middleCont, align=uiconst.TOTOP, state=uiconst.UI_NORMAL)
        self.finalEncounterIcon = IncursionFinalEncounterIcon(parent=middleCont, left=3, top=3, align=uiconst.TOPRIGHT, idx=0)
        self.corpMapButton = Button(parent=self, texturePath='res:/ui/Texture/WindowIcons/corpmap.png', left=self.BUTTON_OFFSET, top=MARGIN, iconSize=iconsize, align=uiconst.BOTTOMLEFT, hint=localization.GetByLabel('UI/Incursion/Journal/ShowActiveCorpMembersInMap'))
        self.mapButton = Button(parent=self, texturePath='res:/ui/Texture/WindowIcons/map.png', left=self.BUTTON_OFFSET + 50, top=MARGIN, iconSize=iconsize, align=uiconst.BOTTOMLEFT, hint=localization.GetByLabel('UI/Incursion/Journal/ShowOnStarMap'))
        self.autopilotButton = Button(parent=self, texturePath='res:/ui/Texture/WindowIcons/ships.png', left=self.BUTTON_OFFSET + 100, top=MARGIN, iconSize=iconsize, align=uiconst.BOTTOMLEFT, hint=localization.GetByLabel('UI/Incursion/Journal/StagingAsAutopilotDestination'))
        self.lpButton = Button(parent=self, texturePath='res:/ui/Texture/WindowIcons/lpstore.png', left=self.BUTTON_OFFSET, top=MARGIN, iconSize=iconsize, align=uiconst.TOPLEFT, hint=localization.GetByLabel('UI/Incursion/Journal/ViewLoyaltyPointLog'))
        self.loyaltyPoints = ReportNumber(name='loyaltyPoints', parent=self, pos=(self.BUTTON_OFFSET + 50,
         MARGIN,
         105,
         iconsize), number=0, hint=localization.GetByLabel('UI/Incursion/Journal/LoyaltyPointsWin'), padding=(4, 4, 4, 4))

    def Load(self, data):
        iconsize = 48
        self.factionParent.Flush()
        if hasattr(data, 'aggressorFactionID') and data.aggressorFactionID:
            factionID = data.aggressorFactionID
            owner = cfg.eveowners.Get(factionID)
            eveIcon.GetLogoIcon(parent=self.factionParent, align=uiconst.RELATIVE, size=64, itemID=factionID, ignoreSize=True, hint=localization.GetByLabel('UI/Incursion/Journal/FactionStagingRuler', faction=owner.ownerName))
        rowHeader = localization.GetByLabel('UI/Incursion/Journal/ReportRowHeader', constellation=data.constellationID, constellationInfo=('showinfo', const.typeConstellation, data.constellationID))
        self.constellationLabel.SetText(rowHeader)
        incursionStateMessages = [localization.GetByLabel('UI/Incursion/Journal/Withdrawing'), localization.GetByLabel('UI/Incursion/Journal/Mobilizing'), localization.GetByLabel('UI/Incursion/Journal/Established')]
        self.statusText.SetText(incursionStateMessages[data.state])
        if data.jumps is not None:
            distanceAwayText = localization.GetByLabel('UI/Incursion/Journal/ReportRowNumJumps', jumps=data.jumps)
        else:
            distanceAwayText = localization.GetByLabel('UI/Incursion/Journal/ReportRowSystemUnreachable')
        bodyText = localization.GetByLabel('UI/Incursion/Journal/ReportRowBody', color='<color=' + sm.GetService('map').GetSystemColorString(data.stagingSolarSystemID) + '>', security=data.security, securityColor=sm.GetService('map').GetSystemColorString(data.stagingSolarSystemID), system=data.stagingSolarSystemID, systemInfo=('showinfo', const.typeSolarSystem, data.stagingSolarSystemID), distanceAway=distanceAwayText)
        self.stagingText.SetText(bodyText)
        self.statusBar.SetInfluence(CalculateDecayedInfluence(data.influenceData), None, animate=False)
        self.finalEncounterIcon.SetFinalEncounterSpawned(data.hasFinalEncounter)
        self.corpMapButton.func = lambda *args: OpenMap(interestID=data.constellationID, starColorMode=STARMODE_FRIENDS_CORP)
        self.mapButton.func = lambda *args: OpenMap(interestID=data.constellationID, starColorMode=STARMODE_INCURSION)
        self.autopilotButton.func = lambda *args: sm.GetService('starmap').SetWaypoint(data.stagingSolarSystemID, clearOtherWaypoints=True)
        self.lpButton.func = lambda *args: sm.GetService('journal').ShowIncursionTab(flag=IncursionTab.LPLog, taleID=data.taleID, constellationID=data.constellationID)
        self.loyaltyPoints.number.SetText(localization.GetByLabel('UI/Incursion/Journal/NumberLoyaltyPointsAcronym', points=FmtAmt(data.loyaltyPoints)))

    def GetDynamicHeight(node, width):
        rowHeader = localization.GetByLabel('UI/Incursion/Journal/ReportRowHeader', constellation=node.constellationID, constellationInfo=('showinfo', const.typeConstellation, node.constellationID))
        headerWidth, headerHeight = BigReportLabel.MeasureTextSize(rowHeader, fontsize=20, width=MIDDLECONTAINER_WIDTH)
        incursionStateMessages = [localization.GetByLabel('UI/Incursion/Journal/Withdrawing'), localization.GetByLabel('UI/Incursion/Journal/Mobilizing'), localization.GetByLabel('UI/Incursion/Journal/Established')]
        statusWidth, statusHeight = SmallReportLabel.MeasureTextSize(incursionStateMessages[node.state], width=MIDDLECONTAINER_WIDTH)
        influenceWidth, influenceHeight = SmallReportLabel.MeasureTextSize(localization.GetByLabel('UI/Incursion/Common/HUDInfluenceTitle'), width=MIDDLECONTAINER_WIDTH)
        statusBar = 18
        if node.jumps is not None:
            distanceAwayText = localization.GetByLabel('UI/Incursion/Journal/ReportRowNumJumps', jumps=node.jumps)
        else:
            distanceAwayText = localization.GetByLabel('UI/Incursion/Journal/ReportRowSystemUnreachable')
        bodyText = localization.GetByLabel('UI/Incursion/Journal/ReportRowBody', color='<color=' + sm.GetService('map').GetSystemColorString(node.stagingSolarSystemID) + '>', security=node.security, securityColor=sm.GetService('map').GetSystemColorString(node.stagingSolarSystemID), system=node.stagingSolarSystemID, systemInfo=('showinfo', const.typeSolarSystem, node.stagingSolarSystemID), distanceAway=distanceAwayText)
        bodyWidth, bodyHeight = SmallReportLabel.MeasureTextSize(bodyText, width=MIDDLECONTAINER_WIDTH)
        return max(114, headerHeight + statusHeight + influenceHeight + statusBar + bodyHeight + MARGIN * 2)


class ReportNumber(Container):
    default_align = uiconst.RELATIVE
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        number = attributes.Get('number', 0)
        self.number = BigReportLabel(name='bignumber', parent=self, align=uiconst.CENTERRIGHT, text=str(number), fontsize=18, hint=attributes.Get('hint', None))


class SmallReportLabel(eveLabel.Label):
    default_align = uiconst.RELATIVE
    default_fontsize = 13


class BigReportLabel(eveLabel.Label):
    default_fontsize = 20
    default_letterspace = 0
    default_align = uiconst.RELATIVE
    default_maxLines = None
