#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\extras\tourneyUISvc.py
from carbon.common.script.sys.service import Service
from carbonui import uiconst
from eve.client.script.ui.extras import tourneyBanUI
from eve.client.script.ui.extras import tourneyMatchStatusUI

class TourneyUISvc(Service):
    __guid__ = 'svc.tourneyUISvc'
    __notifyevents__ = ['OnTournamentPerformBan',
     'OnChangeFleetBoss',
     'OnEnterTournamentSystem',
     'OnTournamentMatchStateChange',
     'OnLeaveTournamentSystem']

    def Run(self, memStream = None):
        super(TourneyUISvc, self).Run(memStream)
        self.matchStatusWindow = None

    def OnTournamentPerformBan(self, banID, numBans, curBans, deadline, respondToNodeID, tourneyID):
        self.LogInfo('OnTourneyBan recv', banID, numBans, curBans, deadline, respondToNodeID)
        banWindow = tourneyBanUI.TourneyBanUI
        banWindow.CloseIfOpen()
        tourneyMgr = sm.RemoteSvc('tourneyMgr')
        tournamentShipDetails = tourneyMgr.QueryShipList(tourneyID)
        shipList = tournamentShipDetails['allowedShipList']
        banBox = banWindow.Open()
        banBox.Execute(banID, numBans, curBans, deadline, respondToNodeID, shipList)
        banBox.ShowModal()

    def OnChangeFleetBoss(self, charID, respondToNodeID):
        self.LogInfo('OnChangeFleetBoss received', charID, respondToNodeID)
        response = eve.Message('CustomQuestion', {'header': 'Team Captain Selection',
         'question': '{} has nominated you as a Team Member for a Tournament Match. Do you accept?             <br><br>Accepting means they will be able to see your fleet composition.'.format(cfg.eveowners.Get(charID).name)}, uiconst.YESNO)
        if response == uiconst.ID_YES:
            machoNet = sm.GetService('machoNet')
            remoteTourneyMgr = machoNet.ConnectToRemoteService('tourneyMgr', respondToNodeID)
            remoteTourneyMgr.ExecuteMemberChange()

    def OnEnterTournamentSystem(self):
        self.GetMatchStatusWindow()

    def OnTournamentMatchStateChange(self, redPoints, bluePoints, myTeam, matchStatus):
        self.LogInfo('OnTournamentMatchStateChange Received', redPoints, bluePoints, myTeam, matchStatus)
        self.GetMatchStatusWindow().OnTournamentMatchStateChange(redPoints, bluePoints, myTeam, matchStatus)

    def OnLeaveTournamentSystem(self):
        self.GetMatchStatusWindow().Close()
        self.matchStatusWindow = None

    def GetMatchStatusWindow(self):
        if not self.matchStatusWindow or self.matchStatusWindow.destroyed:
            statusWindow = tourneyMatchStatusUI.TourneyMatchStatusUI
            self.matchStatusWindow = statusWindow.Open(windowID='matchStatusWindow')
        return self.matchStatusWindow
