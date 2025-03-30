#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\hacking\hackingUtilityElementData.py
import hackingcommon.hackingConstants as hackingConst

class UtilityElementData(object):

    def __init__(self, id = None, subtype = None, info = None, index = None):
        self.id = id
        self.subtype = subtype
        self.info = info
        self.index = index
        self.isSelected = False
        self.isInUse = False
        self.durationRemaining = None
        self.info = None
        self.totalDuration = None

    def __repr__(self):
        return '<UtilityElementData: id=%s, subtype=%s, isSelected=%s, isInUse=%s, info=%s, durationRemaining=%s>' % (self.id,
         self.subtype,
         self.isSelected,
         self.isInUse,
         self.info,
         self.durationRemaining)

    def Update(self, **kw):
        for key, value in kw.iteritems():
            setattr(self, key, value)

        if self.subtype == hackingConst.SUBTYPE_NONE:
            self.durationRemaining = None
        if self.totalDuration is None and self.durationRemaining:
            self.totalDuration = self.durationRemaining
