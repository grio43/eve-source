#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evewar\warText.py
import blue

def GetByLabel(*args, **kwargs):
    import localization
    return localization.GetByLabel(*args, **kwargs)


def FmtDate(*args, **kwargs):
    from carbon.common.script.util.format import FmtDate
    return FmtDate(*args, **kwargs)


def GetTimeParts(*args, **kwargs):
    from carbon.common.script.util.format import GetTimeParts
    return GetTimeParts(*args, **kwargs)


def GetWarText(war):
    textList = GetWarTextList(war)
    textListFull = []
    for each in textList:
        textListFull.append(GetByLabel(each[0], **each[1]))

    return ''.join(textListFull)


def GetCurrentTime():
    currentTime = blue.os.GetWallclockTime()
    return currentTime


def GetWarTextList(war):
    timeFinished = getattr(war, 'timeFinished', None)
    timeRetracted = getattr(war, 'retracted', None)
    timeStarted = getattr(war, 'timeStarted', 0)
    declareDate = FmtDate(war.timeDeclared, 'sn') if war.timeDeclared else GetByLabel('UI/Common/Unknown')
    fightDate = FmtDate(timeStarted, 'sn') if timeStarted else GetByLabel('UI/Common/Unknown')
    currentTime = GetCurrentTime()
    timeTextList = []
    if currentTime <= timeStarted and (timeFinished is None or currentTime < timeFinished):
        startedToday = GetTimeParts(war.timeStarted)[:4] == GetTimeParts(currentTime)[:4]
        if startedToday:
            fightDate = FmtDate(timeStarted, 'ns')
        else:
            fightDate = FmtDate(timeStarted, 'ss')
        timeTextList.append(('UI/Corporations/Wars/WarStartedCanFight', {'date': declareDate,
          'time': fightDate}))
        if timeFinished:
            finishDate = FmtDate(timeFinished, 'ss')
            timeTextList.append(('UI/Corporations/Wars/WarEndsAt', {'timeFinished': finishDate}))
    elif timeFinished:
        if currentTime < timeFinished:
            endsToday = GetTimeParts(timeFinished)[:4] == GetTimeParts(currentTime)[:4]
            if endsToday:
                endTime = FmtDate(timeFinished, 'ns')
            else:
                endTime = FmtDate(timeFinished, 'ss')
            timeTextList.append(('UI/Corporations/Wars/WarStartedEndsAt', {'date': fightDate,
              'time': endTime}))
        elif timeFinished > timeStarted:
            timeTextList.append(('UI/Corporations/Wars/WarStartedAndFinished', {'startDate': fightDate,
              'finishDate': FmtDate(timeFinished, 'sn')}))
        else:
            timeTextList.append(('UI/Corporations/Wars/WarStartedAndRetracted', {'startDate': declareDate,
              'retractDate': FmtDate(timeFinished, 'sn')}))
    elif timeRetracted is not None:
        timeTextList.append(('UI/Corporations/Wars/WarStartedAndRetracted', {'startDate': fightDate,
          'retractDate': FmtDate(timeRetracted, 'sn')}))
    elif timeStarted:
        timeTextList.append(('UI/Corporations/Wars/WarStarted', {'date': fightDate}))
    return timeTextList
