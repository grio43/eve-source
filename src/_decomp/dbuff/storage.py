#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\dbuff\storage.py
import collections
import fsdlite
import dogma.const
OPERATION_IDS_BY_NAME = {'PreAssignment': dogma.const.dgmAssPreAssignment,
 'PreMul': dogma.const.dgmAssPreMul,
 'PreDiv': dogma.const.dgmAssPreDiv,
 'ModAdd': dogma.const.dgmAssModAdd,
 'ModSub': dogma.const.dgmAssModSub,
 'PostMul': dogma.const.dgmAssPostMul,
 'PostDiv': dogma.const.dgmAssPostDiv,
 'PostPercent': dogma.const.dgmAssPostPercent,
 'PostAssignment': dogma.const.dgmAssPostAssignment}
ItemModifiersAttributes = collections.namedtuple('itemModifiersAttributes', ['dogmaAttributeID'])
LocationModifiersAttributes = collections.namedtuple('locationModifiersAttributes', ['dogmaAttributeID'])
LocationGroupModifiersAttributes = collections.namedtuple('locationGroupModifiersAttributes', ['dogmaAttributeID', 'groupID'])
LocationRequiredSkillModifiersAttributes = collections.namedtuple('locationRequiredSkillModifiersAttributes', ['dogmaAttributeID', 'skillID'])

class DbuffCollection(object):
    operation = property(lambda self: OPERATION_IDS_BY_NAME[self.operationName])


def GetDbuffCollection(dbuffCollectionID):
    return DbuffCollectionStorage()[dbuffCollectionID]


def GetDisplayNameID(dbuffCollectionID):
    dbuffCollection = GetDbuffCollection(dbuffCollectionID)
    try:
        return dbuffCollection.displayNameID
    except AttributeError:
        return None


def DbuffCollectionStorage():
    try:
        return DbuffCollectionStorage._storage
    except AttributeError:
        mapping = [('itemModifiers$', ItemModifiersAttributes),
         ('locationModifiers$', LocationModifiersAttributes),
         ('locationGroupModifiers$', LocationGroupModifiersAttributes),
         ('locationRequiredSkillModifiers$', LocationRequiredSkillModifiersAttributes),
         ('$', DbuffCollection)]
        DbuffCollectionStorage._storage = fsdlite.EveStorage(data='dbuff/collections', cache='dbuffCollections.static', mapping=mapping, coerce=int)
        return DbuffCollectionStorage._storage


def CloseStorage():
    DbuffCollectionStorage().cache.close()
