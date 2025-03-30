#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\factionwarfare\client\text.py
import localization

def GetLocalVictoryPointStateText(victoryPointState):
    if victoryPointState is None:
        return ''
    if victoryPointState.isVulnerable:
        return localization.GetByLabel('UI/Neocom/Vulnerable')
    if victoryPointState.isContested:
        return localization.GetByLabel('UI/Neocom/Contested')
    return ''


def GetVictoryPointStateText(victoryPointState):
    if victoryPointState is None:
        return
    if victoryPointState.isVulnerable:
        return localization.GetByLabel('UI/Neocom/Vulnerable')
    if victoryPointState.isContested:
        return localization.GetByLabel('UI/Neocom/Contested')
    return localization.GetByLabel('UI/Neocom/Uncontested')


def GetSystemCaptureStatusText(victoryPointState):
    if victoryPointState is None:
        return
    if victoryPointState.isVulnerable:
        return localization.GetByLabel('UI/FactionWarfare/StatusVulnerable')
    if victoryPointState.isContested:
        return localization.GetByLabel('UI/FactionWarfare/StatusContested', num=victoryPointState.contestedFraction * 100)
    return localization.GetByLabel('UI/FactionWarfare/StatusStable')


def GetSystemCaptureStatusHint(victoryPointState):
    if victoryPointState is None:
        return ''
    if victoryPointState.isVulnerable:
        return localization.GetByLabel('UI/FactionWarfare/StatusVulnerableHint')
    if victoryPointState.isContested:
        return localization.GetByLabel('UI/FactionWarfare/StatusContestedHint', percentage=victoryPointState.contestedFraction * 100)
    return ''
