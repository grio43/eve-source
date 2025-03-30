#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warDeclareController.py
import signals
from localization import GetByLabel
MUTUAL_WAR = 1
AGGRESSIVE_WAR = 2
STEP_PICK_TYPE_CORP = 1
STEP_PICK_HQ = 2
STEP_COST = 3
STEP_SUMMARY = 4
PAGE_NAMES = {STEP_PICK_TYPE_CORP: 'UI/Corporations/Wars/DeclareWarPageTypeAndCorp',
 STEP_PICK_HQ: 'UI/Corporations/Wars/DeclareWarPagePickHQ',
 STEP_COST: 'UI/Corporations/Wars/DeclareWarPageCost',
 STEP_SUMMARY: 'UI/Corporations/Wars/DeclareWarPageSummary'}
MUTUAL_STEPS = [STEP_PICK_TYPE_CORP, STEP_SUMMARY]
AGGRESSIVE_STEPS = [STEP_PICK_TYPE_CORP,
 STEP_PICK_HQ,
 STEP_COST,
 STEP_SUMMARY]

class WarDeclareController(object):

    def __init__(self, defenderID, exactChecked = False):
        self.currentPage = STEP_PICK_TYPE_CORP
        self.warType = AGGRESSIVE_WAR
        self.warAttackerID = session.allianceid or session.corpid
        self.warDefenderID = defenderID
        self.exactChecked = exactChecked
        self.warHq = None
        self.on_war_info_changed = signals.Signal(signalName='on_war_info_changed')
        self.on_loading_changed = signals.Signal(signalName='on_loading_changed')
        self.on_war_type_changed = signals.Signal(signalName='on_war_type_changed')

    def SetWarHQ(self, itemID):
        self.warHq = itemID
        self.on_war_info_changed()

    def GetWarHQ(self):
        return self.warHq

    def SetWarType(self, warType):
        self.warType = warType
        if warType == MUTUAL_WAR:
            self.SetWarHQ(None)
        self.on_war_type_changed()
        self.on_war_info_changed()

    def GetWarType(self):
        return self.warType

    def SetDefenderID(self, ownerID):
        self.warDefenderID = ownerID
        self.on_war_info_changed()

    def GetDefenderID(self):
        return self.warDefenderID

    def SetAttackerID(self, ownerID):
        self.warAttackerID = ownerID
        self.on_war_info_changed()

    def GetAttackerID(self):
        return self.warAttackerID

    def GoToNextPage(self):
        allSteps = self.GetAllSteps()
        currIndex = allSteps.index(self.currentPage) if self.currentPage in allSteps else 0
        nextStepIdx = min(currIndex + 1, len(allSteps) - 1)
        nextStep = allSteps[nextStepIdx]
        self.currentPage = nextStep

    def GotToPreviousPage(self):
        allSteps = self.GetAllSteps()
        currIndex = allSteps.index(self.currentPage) if self.currentPage in allSteps else 0
        prevStep = allSteps[max(currIndex - 1, 0)]
        self.currentPage = prevStep

    def GetAllSteps(self):
        allSteps = MUTUAL_STEPS if self.warType == MUTUAL_WAR else AGGRESSIVE_STEPS
        return allSteps

    def GetCurrentPage(self):
        return self.currentPage

    def GetPageNameAndCount(self):
        allSteps = self.GetAllSteps()
        return (PAGE_NAMES[self.currentPage], allSteps.index(self.currentPage) + 1, len(allSteps))

    def IsMutualWar(self):
        return self.warType == MUTUAL_WAR

    def IsAggressiveWar(self):
        return self.warType == AGGRESSIVE_WAR

    def ChangeLoading(self, isLoading):
        self.on_loading_changed(isLoading)

    def GetExactCheckedValue(self):
        return self.exactChecked

    def SetExactCheckedValue(self, isChecked):
        self.exactChecked = isChecked


def GetWarTypeText(warType):
    if warType == MUTUAL_WAR:
        return 'Mutual War'
    if warType == AGGRESSIVE_WAR:
        return 'Aggressive war'
    return ''


def GetWarPartiesText(warType):
    if warType == MUTUAL_WAR:
        return (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryPartyA'), GetByLabel('UI/Corporations/Wars/WarDeclareSummaryPartyB'))
    return (GetByLabel('UI/Corporations/Wars/WarDeclareSummaryAttacker'), GetByLabel('UI/Corporations/Wars/WarDeclareSummaryDefender'))
