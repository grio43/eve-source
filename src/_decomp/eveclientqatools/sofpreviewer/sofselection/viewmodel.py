#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\sofselection\viewmodel.py


class SofSelectionViewModel(object):

    def __init__(self, model):
        dna = model.GetDnaFromPlayerShip()
        self.currentFaction = dna.split(':')[1]
        self.currentRace = dna.split(':')[2]
        self.currentHulls = self.GetCurrentHulls(dna, model)
        self.currentPattern = 'None'
        self.maxMultiHulls = model.const.MAX_MULTI_HULLS
        self.sofRaces = model.sofRaces
        self.sofHulls = model.sofHulls
        self.sofFactions = model.sofFactions
        self.sofPatterns = model.sofPatterns

    def GetCurrentHulls(self, dna, model):
        multiHulls = dna.split(':')[0].split(';')
        currentHulls = [ (None if i >= len(multiHulls) else multiHulls[i]) for i in xrange(0, model.const.MAX_MULTI_HULLS) ]
        return currentHulls
