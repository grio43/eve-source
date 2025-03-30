#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\components\alignmentBasedToll.py


def GetToll(shipMass, iskPerMass, exponent, minimumCost, playerIsAligned, fixedAmount, alignedDiscountMultiplier):
    toll = max(minimumCost, pow(shipMass * iskPerMass, exponent) + fixedAmount)
    if playerIsAligned:
        return toll * alignedDiscountMultiplier
    return toll
