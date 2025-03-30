#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\client\components\alignmentBasedToll.py
from carbonui import uiconst
from eve.common.script.util.eveFormat import FmtISK
from spacecomponents import Component
from spacecomponents.common.components.alignmentBasedToll import GetToll

class AlignmentBasedToll(Component):

    @property
    def alignmentRestrictionList(self):
        return self.attributes.alignmentRestrictionList

    @property
    def pricePerKilo(self):
        return self.attributes.pricePerKilo

    @property
    def exponent(self):
        return self.attributes.exponent

    @property
    def minCost(self):
        return self.attributes.minCost

    @property
    def fixedAddition(self):
        return self.attributes.fixedAddition

    @property
    def alignedDiscountMultiplier(self):
        return self.attributes.alignedDiscountMultiplier

    @property
    def shipMassFactor(self):
        return self.attributes.shipMassFactor

    def CalculateMyToll(self, ballpark):
        shipMass = ballpark.GetBall(session.shipid).mass
        return GetToll(shipMass, self.pricePerKilo, self.exponent, self.minCost, self.AmIAligned(), self.fixedAddition, self.alignedDiscountMultiplier)

    def AmIAligned(self):
        return session.warfactionid in self.alignmentRestrictionList

    def CheckWithPlayer(self, ballpark):
        toll = self.CalculateMyToll(ballpark)
        if toll <= 0:
            return True
        formattedTollAmount = FmtISK(toll, False)
        messageName = 'GateTollConfirmAligned'
        args = {'amount': formattedTollAmount}
        if not self.AmIAligned():
            messageName = 'GateTollConfirmUnAligned'
            factionNames = [ cfg.eveowners.Get(factionID).name for factionID in self.alignmentRestrictionList ]
            args = {'amount': formattedTollAmount,
             'factionNames': ', '.join(factionNames)}
        userPromptResult = eve.Message(messageName, args, buttons=uiconst.YESNO)
        return userPromptResult == uiconst.ID_YES
