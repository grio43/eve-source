#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evewar\util.py
import blue
from collections import namedtuple
from itertools import izip
_BaseWar = namedtuple('War', ['warID',
 'declaredByID',
 'againstID',
 'timeDeclared',
 'timeFinished',
 'retracted',
 'timeStarted',
 'retractedBy',
 'billID',
 'mutual',
 'allies',
 'createdFromWarID',
 'openForAllies',
 'canBeRetracted',
 'reasonEnded',
 'warHQ',
 'reasonStarted'])

class War(_BaseWar):
    __guid__ = 'warUtil.War'

    def __new__(cls, *args, **kwargs):
        row = args if len(args) > 1 else args[0]
        if hasattr(row, 'warID'):
            return _BaseWar.__new__(cls, *[ value for value in cls._WarCreatorIterator(row) ])
        return _BaseWar.__new__(cls, *row)

    @classmethod
    def _WarCreatorIterator(cls, row):
        for attributeName in cls.GetFields():
            try:
                yield getattr(row, attributeName)
            except AttributeError:
                if attributeName == 'allies':
                    yield {}
                else:
                    import log
                    log.LogException('_WarCreatorIterator expects attribute (%s) that was not in war row %s' % (attributeName, row))
                    yield

    def Copy(self, **kwargs):
        values = []
        for fieldName, value in izip(self._fields, self):
            if fieldName in kwargs:
                values.append(kwargs[fieldName])
            elif isinstance(value, dict):
                values.append(value.copy())
            else:
                values.append(value)

        return War(*values)

    @classmethod
    def GetFields(cls):
        return cls._fields

    @property
    def noOfAllies(self):
        return len([ allyRow for allyRow in self.allies.itervalues() if IsAllyActive(allyRow) ])


def GetWarEntity(corporationID, allianceID):
    if allianceID:
        return allianceID
    else:
        return corporationID


def HasActiveOrPendingWars(wars):
    for war in wars.itervalues():
        if war.timeFinished is None or DoesWarHaveFutureFinishTimeSet(war):
            return True

    return False


def IsWarInHostileState(row, currentTime):
    if row.timeFinished is None or DoesWarHaveFutureFinishTimeSet(row, currentTime):
        if currentTime > row.timeStarted:
            return 1
    return 0


def IsAtWar(wars, entities, currentTime):
    for war in wars:
        if war.declaredByID not in entities:
            continue
        if not IsWarInHostileState(war, currentTime):
            continue
        if war.againstID in entities:
            return war.warID
        for allyID, row in war.allies.iteritems():
            if allyID in entities:
                if row.timeStarted < currentTime < row.timeFinished:
                    return war.warID
                break

    return False


def DoesWarHaveFutureFinishTimeSet(war, currentTime = None):
    if war.timeFinished is None:
        return False
    if currentTime is None:
        currentTime = blue.os.GetWallclockTime()
    if currentTime < war.timeFinished:
        return True
    return False


def IsWarInCooldown(war, currentTime = None):
    if war.timeFinished is None:
        return False
    if currentTime is None:
        currentTime = blue.os.GetWallclockTime()
    if war.timeStarted < currentTime < war.timeFinished:
        return True
    return False


def IsWarFinished(war, currentTime = None):
    if war.timeFinished is None:
        return False
    if currentTime is None:
        currentTime = blue.os.GetWallclockTime()
    if war.timeFinished < currentTime:
        return True
    return False


def IsWarInSpoolup(war):
    now = blue.os.GetWallclockTime()
    if now < war.timeStarted:
        return True
    return False


def IsAllyActive(row, time = None):
    if time is None:
        time = blue.os.GetWallclockTime()
    return row.timeStarted < time < row.timeFinished


def IsAllyPendingOrActive(row, time = None):
    if time is None:
        time = blue.os.GetWallclockTime()
    return time < row.timeFinished


def IsWarActive(row):
    if row.timeFinished is None or blue.os.GetWallclockTime() < row.timeFinished:
        return 1
    return 0


def GetAllyCostToConcord(war, baseCostFunc):
    currentTime = blue.os.GetWallclockTime()
    activeAllies = len([ ally for ally in war.allies.itervalues() if currentTime < ally.timeFinished ])
    if activeAllies == 0:
        return 0
    else:
        return baseCostFunc() * 2 ** min(activeAllies - 1, 20)


def HandleWarChange(war, warsByWarID, warsByOwnerID, ownerIDs, change):
    warIDchange = change.get('warID')
    if warIDchange:
        oldWarID, newWarID = warIDchange
        if newWarID is None:
            try:
                del warsByWarID[oldWarID]
            except KeyError:
                pass

            return
    newWar = War(war)
    warsByWarID[newWar.warID] = newWar
    for ownerID in ownerIDs:
        try:
            warsByOwnerID[ownerID].add(newWar.warID)
        except KeyError:
            pass
