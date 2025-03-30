#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\stackingNurfedAttribute.py
from math import exp
from dogma.attributes import Attribute
from dogma.const import dgmUnnerfedCategories, dgmOperators, dgmNurfableOperations
from dogma.const import dgmOperatorIDtoIndex, dgmOperatorPrecedence
from dogma.dogmaLogging import LogWarn, LogTraceback
MAX_NURF_SEQUENCE_LENGTH = 8
NurfDenominators = [ exp((i / 2.67) ** 2.0) for i in xrange(MAX_NURF_SEQUENCE_LENGTH) ]
import itertools
import operator
import bisect

def StackingOperator(valueDenomTuple):
    return (valueDenomTuple[0] - 1.0) * (1.0 / valueDenomTuple[1]) + 1.0


class StackingNurfedAttribute(Attribute):
    __slots__ = ['unNurfedMods', 'nurfedMods', 'nurfedModsFactor']

    def __init__(self, attribID, baseValue, dogmaItem, dogmaLM, staticAttr):
        self.unNurfedMods = None
        self.nurfedMods = None
        self.nurfedModsFactor = 0
        super(StackingNurfedAttribute, self).__init__(attribID, baseValue, dogmaItem, dogmaLM, staticAttr)

    def _initIncomingUnNurfedModifiers(self):
        self.unNurfedMods = self._makeEmptyIncomingModifiers()

    def _initIncomingNurfedModifiers(self):
        self.nurfedMods = self._makeEmptyIncomingModifiers()

    def AddIncomingModifier(self, op, attribute):
        if self._ShouldNotNurf(op, attribute):
            if self.unNurfedMods is None:
                self._initIncomingUnNurfedModifiers()
            self.unNurfedMods[dgmOperatorIDtoIndex[op]].add(attribute)
        else:
            if self.nurfedMods is None:
                self._initIncomingNurfedModifiers()
            self.nurfedMods[dgmOperatorIDtoIndex[op]].add(attribute)
        super(StackingNurfedAttribute, self).AddIncomingModifier(op, attribute)

    def RemoveIncomingModifier(self, op, attribute):
        try:
            doNotNurf = self._ShouldNotNurf(op, attribute)
            if doNotNurf:
                self.unNurfedMods[dgmOperatorIDtoIndex[op]].remove(attribute)
                if not any(self.unNurfedMods):
                    self.unNurfedMods = None
            else:
                self.nurfedMods[dgmOperatorIDtoIndex[op]].remove(attribute)
                if not any(self.nurfedMods):
                    self.nurfedMods = None
        except:
            pass

        super(StackingNurfedAttribute, self).RemoveIncomingModifier(op, attribute)

    def _ShouldNotNurf(self, op, attribute):
        if op not in dgmNurfableOperations:
            return True
        try:
            if attribute.item is not None:
                if attribute.item.invItem.categoryID in dgmUnnerfedCategories:
                    return True
        except ReferenceError:
            LogWarn("_ShouldNotNurf: 'Orphan' Attribute detected (its dogmaItem has gone!):", attribute)
            LogWarn('TraceReferrers is BEING SUPPRESSED in case it overloads the node! (Sorry)')
            LogTraceback('Orphan Attribute! (via _ShouldNotNurf)')

        if hasattr(attribute, 'forceUnnurfed') and attribute.forceUnnurfed:
            return True
        return False

    def _ApplyModifierOperationsToVal(self, val):
        unnurfedMods = self.unNurfedMods if self.unNurfedMods else self._makeEmptyIncomingModifiers()
        nurfedMods = self.nurfedMods if self.nurfedMods else self._makeEmptyIncomingModifiers()
        for idx, (unnurfedMods, nurfedMods) in enumerate(zip(unnurfedMods, nurfedMods)):
            dogmaOperator = dgmOperators[dgmOperatorPrecedence[idx]]
            for modAttrib in unnurfedMods:
                val = dogmaOperator(val, modAttrib.GetValue())

            if len(nurfedMods) <= 0:
                for modAttrib in nurfedMods:
                    val = dogmaOperator(val, modAttrib.GetValue())

            else:
                factors = sorted([ dogmaOperator(1, modAttrib.GetValue()) for modAttrib in nurfedMods ])
                splitPoint = bisect.bisect(factors, 1.0)
                self.nurfedModsFactor = reduce(operator.mul, itertools.imap(StackingOperator, itertools.chain(itertools.izip(factors[:splitPoint], NurfDenominators), itertools.izip(reversed(factors[splitPoint:]), NurfDenominators))))
                val *= self.nurfedModsFactor

        return val

    def GetNurfedModsFactor(self):
        self.Update()
        return self.nurfedModsFactor
