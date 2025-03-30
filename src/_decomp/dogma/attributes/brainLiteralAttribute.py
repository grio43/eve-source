#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dogma\attributes\brainLiteralAttribute.py
from dogma.attributes import LiteralAttribute
from dogma.dogmaLogging import GetTypeNameFromID

class BrainLiteralAttribute(LiteralAttribute):
    __slots__ = ['skills', 'forceUnnurfed', 'noPropagation']

    def __init__(self, value):
        self.skills, value = value
        super(BrainLiteralAttribute, self).__init__(value)
        self.forceUnnurfed = True
        self.noPropagation = True

    def __str__(self):
        skills = [ GetTypeNameFromID(x) for x in self.skills ]
        return 'BrainLiteralAttribute value %s from skills %s' % (self.value, skills)
