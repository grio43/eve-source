#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\industry\modifiers.py
import industry

class Modifier(industry.Base):

    def __init__(self, amount, reference = None, activity = None, output = False, blueprints = None, categoryID = None, groupID = None, invTypeID = None):
        self.amount = amount
        self.reference = reference
        self.activity = activity
        self.output = output
        self.blueprints = set(blueprints or [])
        self.categoryID = categoryID
        self.groupID = groupID
        self.invTypeID = invTypeID


class MaterialModifier(Modifier):
    pass


class TimeModifier(Modifier):
    pass


class CostModifier(Modifier):

    def __init__(self, *args, **kwargs):
        self.additive = kwargs.pop('additive', False)
        super(CostModifier, self).__init__(*args, **kwargs)


class ProbabilityModifier(Modifier):
    pass


class MaxRunsModifier(Modifier):
    pass


class SlotModifier(Modifier):
    pass


MODIFIER_CLASSES = {industry.MODIFIER_TYPE_TIME: TimeModifier,
 industry.MODIFIER_TYPE_MATERIAL: MaterialModifier,
 industry.MODIFIER_TYPE_COST: CostModifier,
 industry.MODIFIER_TYPE_PROBABILITY: ProbabilityModifier,
 industry.MODIFIER_TYPE_MAX_RUNS: ProbabilityModifier,
 industry.MODIFIER_TYPE_SLOTS: SlotModifier}
