#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\atWarTooltip.py
import gametime
import itertoolsext
from evewar.util import IsWarInHostileState
from localization import GetByLabel

def LoadAtWarTooltipPanelFindWars(tooltipPanel):
    ownerID = session.allianceid or session.corpid
    ownerWars = sm.GetService('war').GetWars(ownerID).values()
    if session.warfactionid:
        fwWars = sm.GetService('facwar').GetFactionWarsForWarFactionID(session.warfactionid).values()
        ownerWars += fwWars
    ongoingWars = []
    now = gametime.GetWallclockTime()
    for eachWar in ownerWars:
        if getattr(eachWar, 'timeStarted', None) and not IsWarInHostileState(eachWar, now):
            continue
        ongoingWars.append(eachWar)

    LoadAtWarTooltipPanel(tooltipPanel, ownerID, ongoingWars)


def LoadAtWarTooltipPanel(tooltipPanel, ownerID, ongoingWars):
    tooltipPanel.LoadGeneric2ColumnTemplate()
    ownerIDsToPrime = set()
    for eachWar in ongoingWars:
        ownerIDsToPrime.add(eachWar.againstID)
        ownerIDsToPrime.add(eachWar.declaredByID)

    cfg.eveowners.Prime(ownerIDsToPrime)
    aggressiveOpponents = []
    mutualOpponents = []
    for eachWar in ongoingWars:
        opponentID = itertoolsext.first_or_default([eachWar.declaredByID, eachWar.againstID], lambda x: x != ownerID, None)
        if not opponentID:
            continue
        listToUse = mutualOpponents if eachWar.mutual else aggressiveOpponents
        if opponentID == eachWar.declaredByID:
            allies = []
        else:
            allies = getattr(eachWar, 'allies', [])
        listToUse.append((cfg.eveowners.Get(opponentID).name, len(allies)))

    aggressiveOpponents.sort()
    mutualOpponents.sort()
    MAX_DISPLAYED = 5
    textAdded = False
    firstColumnWidth = 5
    for opponentType, opponentLabelPath in ((aggressiveOpponents, 'UI/Corporations/CorporationWindow/Wars/AggressiveWarsHeader'), (mutualOpponents, 'UI/Corporations/CorporationWindow/Wars/MutualWarsHeader')):
        if opponentType:
            if textAdded:
                tooltipPanel.AddSpacer(height=10, colSpan=tooltipPanel.columns)
            tooltipPanel.AddLabelMedium(text=GetByLabel(opponentLabelPath), colSpan=tooltipPanel.columns)
            textAdded = True
            for eachOpponent, numAllies in opponentType[:MAX_DISPLAYED]:
                tooltipPanel.AddSpacer(width=firstColumnWidth)
                if numAllies:
                    t = GetByLabel('UI/Corporations/CorporationWindow/Wars/WarOpponentLineWithAllies', warOpponent=eachOpponent, numAllies=numAllies)
                else:
                    t = GetByLabel('UI/Corporations/CorporationWindow/Wars/WarOpponentLineWithoutAllies', warOpponent=eachOpponent)
                tooltipPanel.AddLabelMedium(text=t)

            more = len(opponentType) - MAX_DISPLAYED
            if more > 0:
                tooltipPanel.AddSpacer(width=firstColumnWidth)
                t = GetByLabel('UI/Corporations/CorporationWindow/Wars/AndMoreWars', numMore=more)
                tooltipPanel.AddLabelMedium(text=t)
