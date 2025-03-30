#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warReportController.py


class WarReportController(object):

    def __init__(self, warID):
        self.warID = warID
        self.war = None
        self.allies = None
        self.warNegotiationID = None

    def GetAttackerID(self):
        return self.war.declaredByID

    def GetDefenderID(self):
        return self.war.againstID

    def GetWarID(self):
        return self.warID

    def SetWar(self, war):
        self.war = war

    def GetWar(self):
        return self.war

    def IsWarMutual(self):
        return self.war.mutual

    def GetAllies(self):
        return self.allies

    def SetAllies(self, allies):
        self.allies = allies

    def IsWarOpenForAllies(self):
        return self.war.openForAllies

    def GetWarNegotiationID(self):
        return self.warNegotiationID

    def SetWarNegotiationID(self, warNegotiationID):
        self.warNegotiationID = warNegotiationID

    def GetWarHq(self):
        return getattr(self.war, 'warHQ', None)
