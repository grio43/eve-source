#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\clonegrade\storage.py
import collections
import fsdlite
import immutable

class CloneGrade(object):
    __metaclass__ = immutable.Immutable

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls, *args, **kwargs)
        obj.internalDescription = None
        obj._skills = None
        obj.skillsByTypeID = None
        return obj

    def _get_skills(self):
        return self._skills

    def _set_skills(self, skills):
        self._skills = skills
        self.skillsByTypeID = {skill.typeID:skill for skill in skills}

    skills = property(_get_skills, _set_skills)


Skill = collections.namedtuple('Skill', ['typeID', 'level'])
MAPPING = [('$', CloneGrade), ('skills$', Skill)]

def CloneGradeStorage():
    try:
        return CloneGradeStorage._storage
    except AttributeError:
        CloneGradeStorage._storage = fsdlite.EveStorage(data='clonegrades', cache='clonegrades.static', mapping=MAPPING, coerce=int)
        return CloneGradeStorage._storage
