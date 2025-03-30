#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\development\notificationDevUI.py
from notifications.common.notification import SimpleNotification
from carbonui.control.window import Window
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from notifications.client.generator.notificationGenerator import NotificationGenerator
from notifications.client.controls.notificationSettingsWindow import NotificationSettingsWindow
from notifications.client.development.skillHistoryProvider import SkillHistoryProvider
import carbonui.const as uiconst

class NotificationDevWindow(Window):
    default_caption = 'Notification Debug window'
    default_windowID = 'NotificationDevWindow2'
    default_width = 300
    default_height = 300
    default_minSize = (250, 350)

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.mainContainer = NotificationDevMainContainer(name='mainContainer', align=uiconst.TOALL, parent=self.GetMainArea())


class NotificationDevMainContainer(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes=attributes)
        self.generateButton = Button(name='generationStartButton', align=uiconst.TOTOP, label='start Generating', func=self.OnGenerateButtonClicked, pos=(0, 20, 100, 20), parent=self)
        self.fillSkillHistoryBtn = Button(name='fillSkillHistory', align=uiconst.TOTOP, label='skillHistory()', func=self.OnSkillDevClick, pos=(0, 5, 100, 20), parent=self)
        self.makeAllNotificationsBtn = Button(name='MakeAllNotifications', align=uiconst.TOTOP, label='MakeAllNotifications()', func=self.OnMakeAllNotificationClick, pos=(0, 5, 100, 20), parent=self)
        self.displayNotificationSettingBtn = Button(name='NotificationSettingsWindowButton', align=uiconst.TOTOP, label='Notification Settings window', func=self.OnDisplayNotificationSettingClick, pos=(0, 5, 100, 20), parent=self)
        self.toggleEnabledFlagBtn = Button(name='NotificationSettingsWindowButton', align=uiconst.TOTOP, label='Toggle enabled', func=self.OnToggleEnabledClick, pos=(0, 5, 100, 20), parent=self)
        self.toggleEnabledDevModeFlagBtn = Button(name='DevToggleButton', align=uiconst.TOTOP, label='Toggle developermode', func=self.OnDevToggleButtonClick, pos=(0, 5, 100, 20), parent=self)
        self.testTransactionFun = Button(name='TransactioFun', align=uiconst.TOTOP, label='Generate random fake transaction', func=self.OnTransactionFun, pos=(0, 5, 100, 20), parent=self)
        self.isGenerating = False
        self.MakeNewGenerator()

    def OnTransactionFun(self, *args):
        import random
        aRandom = random.Random()
        startValue = 1000000
        transaction = aRandom.randint(-1000000, 1000000)
        sm.ScatterEvent('OnPersonalAccountChangedClient', startValue, transaction)

    def OnDevToggleButtonClick(self, *args):
        service = sm.GetService('notificationUIService')
        service.ToggleDeveloperMode()
        service.ToggleEnabledFlag()
        service.ToggleEnabledFlag()

    def OnToggleEnabledClick(self, *args):
        service = sm.GetService('notificationUIService')
        service.ToggleEnabledFlag()

    def OnDisplayNotificationSettingClick(self, *args):
        NotificationSettingsWindow.ToggleOpenClose()

    def OnMakeAllNotificationClick(self, *args):
        notificationMaker = FakeNotificationMaker()
        notificationMaker.MakeAndScatterAllClassicNotifications()

    def fakeNotification(self, typeID):
        newNotification = Notification(notificationID=1345)

    def OnSkillDevClick(self, *args):
        provider = SkillHistoryProvider()
        provider.provide()

    def OnMakeNewGeneratorClicked(self, *args):
        if self.notificationGenerator:
            self.notificationGenerator.Stop()
        self.MakeNewGenerator()

    def adjustLabel(self):
        if self.isGenerating:
            self.generateButton.SetLabel('Stop generating')
        else:
            self.generateButton.SetLabel('Start generating')

    def MakeNewGenerator(self):
        self.notificationGenerator = NotificationGenerator()

    def OnGenerateButtonClicked(self, *args):
        self.isGenerating = not self.isGenerating
        if self.isGenerating:
            sm.GetService('notificationUIService').SpawnFakeNotifications()
        else:
            sm.GetService('notificationUIService').notificationGenerator.Stop()
        self.adjustLabel()


import eve.common.script.util.notificationUtil as notificationUtil
import eve.common.script.util.notificationconst as notificationConst
import blue
import sys
from eve.client.script.ui.services.mail.notificationSvc import Notification

class FakeNotificationMaker:

    @staticmethod
    def MakeFakeData(senderID = 98000002):
        data = {'addCloneInfo': 1,
         'againstID': 98000002,
         'agentLocation': {3: 10000037,
                           4: 20000443,
                           5: 30003029,
                           15: 60011125},
         'aggressorCorpID': 98000002,
         'aggressorID': 98000001,
         'allianceID': 99000002,
         'allyID': 98000001,
         'amount': 6666,
         'armorValue': 0.2,
         'attackerID': 90000002,
         'billTypeID': 1,
         'body': 'This Is a body',
         'bounty': 666,
         'bountyPlacerID': 98000001,
         'celestialIndex': 1,
         'characterID': 90000001,
         'charID': 90000001,
         'charRefID': 90000001,
         'charsInCorpID': [90000001],
         'cloneStationID': 60012415,
         'corpID': senderID,
         'corporationID': senderID,
         'corpsPresent': '',
         'corpStationID': 60012415,
         'cost': 12456,
         'creditorID': 98000001,
         'debtorID': 90000003,
         'declaredByID': senderID,
         'defenderID': 98000001,
         'disqualificationType': 9,
         'districtIndex': 1,
         'enemyID': 90000001,
         'entityID': 90000001,
         'errorText': 'THIS IS AN ERROR TEXT',
         'event': 373,
         'factionID': 500001,
         'header': 'THIS IS A BULLSHIT HEADER',
         'hours': 667,
         'iskValue': 666,
         'itemRefID': 1,
         'level': 5,
         'locationID': 60012415,
         'locationOwnerID': 30005031,
         'lostList': None,
         'medalID': 132919,
         'mercID': 90000001,
         'messageIndex': 1,
         'myIsk': 668,
         'newOwnerID': 90000004,
         'newRank': 'Your New rank',
         'offeredID': 90000001,
         'offeringID': 90000001,
         'oldOwnerID': 90000001,
         'ownerID': 90000001,
         'ownerID1': 90000001,
         'parameter': 98000001,
         'password': 'thisIsPassword',
         'payout': 1231313,
         'planetID': 40318731,
         'planetTypeID': 1,
         'price': 45646456,
         'reason': 'This is a bullshit reason',
         'reinforceExitTime': blue.os.GetWallclockTime() + 100000,
         'security': 3,
         'shieldValue': 0.8,
         'skillPointsLost': 669,
         'solarSystemID': 30005031,
         'standingsChange': 0.2,
         'startDate': blue.os.GetWallclockTime(),
         'startTime': blue.os.GetWallclockTime(),
         'state': 1,
         'stationID': 60012415,
         'subject': 'This is a subject',
         'systemBids': (90000001, 1234),
         'teamNameInfo': (1000144, 17740, 3767636),
         'time': blue.os.GetWallclockTime(),
         'timeFinished': blue.os.GetWallclockTime(),
         'toEntityID': 90000001,
         'topTen': None,
         'totalIsk': 45646,
         'typeID': 17740,
         'typeIDs': None,
         'victimID': 90000001,
         'voteType': 1,
         'wants': None,
         'yourAmount': 6667,
         'hullValue': 0.9,
         'aggressorAllianceID': 99000002,
         'delayHours': 24,
         'hostileState': 1,
         'targetLocation': {3: 10000037,
                            4: 20000443,
                            5: 30003029,
                            15: 60011125},
         'requiredStanding': 0.5,
         'corpList': [98000001],
         'warHQ': 100000123,
         'currentStanding': 0.5,
         'warNegotiationID': 123}
        return data

    def ScatterSingleNotification(self, counter, notificationId, senderID, someAgentID, someCorp):
        data = self.MakeFakeData(someCorp)
        aNotification = Notification(notificationID=counter + 10000000, typeID=notificationId, senderID=senderID, receiverID=90000001, processed=False, created=blue.os.GetWallclockTime() - counter * 10000, data=data)
        fsubject, fbody = notificationUtil.Format(aNotification)
        try:
            characterID = None
            corporationId = None
            if notificationId in notificationConst.groupTypes[notificationConst.groupAgents]:
                senderID = someAgentID
            if notificationId in notificationConst.groupTypes[notificationConst.groupCorp]:
                senderID = someCorp
            newNotification = SimpleNotification(subject=fsubject, created=blue.os.GetWallclockTime() - counter * 10000, notificationID=counter + 1000000, notificationTypeID=notificationId, senderID=senderID, body=fbody)
            sm.ScatterEvent('OnNewNotificationReceived', newNotification)
        except:
            print 'exception'
            print sys.exc_info()[0]

    def MakeAndScatterAllClassicNotifications(self):
        counter = 0
        onlyOneGroup = False
        whitelistedGroups = [notificationConst.groupAgents, notificationConst.groupCorp]
        useWhiteLists = False
        for notificationId, dict in notificationUtil.formatters.iteritems():
            if useWhiteLists:
                foundSomething = False
                for group in whitelistedGroups:
                    if notificationId in notificationConst.groupTypes[group]:
                        foundSomething = True

                if not foundSomething:
                    continue
            agentStartID = 3008416
            someAgentID = agentStartID + counter
            senderID = 98000001
            corpStartID = 1000089
            someCorp = corpStartID + counter
            self.ScatterSingleNotification(counter, notificationId, senderID, someAgentID, someCorp)
            counter = counter + 1
            blue.synchro.Yield()
