#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dynamicresources\common\ess\formulas.py


def GetPayout(currentPulse, totalPulses, windowAccessFactor, reserveBankMaxPayout, exponentLead, exponentTail, payoutPaddingValue):
    windowSize = totalPulses / windowAccessFactor
    if currentPulse <= totalPulses:
        if currentPulse < windowSize:
            return reserveBankMaxPayout * (currentPulse / windowSize) ** exponentLead + payoutPaddingValue
        else:
            return reserveBankMaxPayout * (windowSize / currentPulse) ** exponentTail + payoutPaddingValue
    else:
        raise RuntimeError('Bank Closed')
