#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\sofselection\constraints.py


class Constraints(object):

    def __init__(self, view):
        self.view = view

    @property
    def faction(self):
        return self.view.factionConstraint.GetValue()

    @faction.setter
    def faction(self, value):
        self.view.factionConstraint.SetValue(value)

    @property
    def race(self):
        return self.view.raceConstraint.GetValue()

    @race.setter
    def race(self, value):
        self.view.raceConstraint.SetValue(value)

    @property
    def hull(self):
        return self.view.hullConstraint.GetValue()

    @hull.setter
    def hull(self, value):
        self.view.hullConstraint.SetValue(value)

    @property
    def pattern(self):
        return self.view.patternConstraint.GetValue()

    @pattern.setter
    def pattern(self, value):
        self.view.patternConstraint.SetValue(value)

    def SetAll(self, flag):
        self.faction = flag
        self.hull = flag
        self.race = flag
        self.pattern = flag

    def HasNoConstraints(self):
        return not self.faction and not self.hull and not self.race and not self.pattern
