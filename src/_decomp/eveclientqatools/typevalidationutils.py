#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\typevalidationutils.py
from eveexceptions import UserError
import evetypes
from carbon.common.script.util.linkUtil import GetShowInfoLink
import blue
RESULTMODE_FULL = 'full'
RESULTMODE_FAILURES = 'failures'

def RunTests(func, typeList, resultMode, **kwargs):
    resultList = []
    successCount = 0
    failCount = 0
    for typeID in typeList:
        try:
            success, result = func(typeID, **kwargs)
        except UserError as e:
            resultString = 'ERROR! TEST ABORTED - Reason: %s' % str(e.msg)
            resultList.append(resultString)
            failCount += 1
            break

        if success:
            successCount += 1
        else:
            failCount += 1
        if resultMode == RESULTMODE_FULL or not success:
            resultString = '%s - %s: %s  %s' % (typeID,
             CreateTypeLink(typeID),
             str(success),
             str(result))
            resultList.append(resultString)
        blue.pyos.BeNice()

    formattedResult = FormatResults(successCount, failCount, resultList)
    return formattedResult


def FormatResults(successCount, failCount, resultList):
    if successCount and failCount == 0:
        res = '<b>SUCCESS! All %s types passed the test!</b>' % successCount
    else:
        res = '<b>%s types passed and %s failed the test</b>' % (successCount, failCount)
    resultText = '<br>'.join(resultList)
    res = '%s<br>%s' % (res, resultText)
    return res


def CreateTypeLink(typeID):
    return GetShowInfoLink(typeID, evetypes.GetName(typeID))


def RepresentsType(s):
    try:
        t = int(s)
    except ValueError:
        return False

    if evetypes.Exists(t):
        return True
    return False


def SplitStringIntoList(typeListString):
    tempSet = {int(s) for s in typeListString.split(',') if RepresentsType(s)}
    return sorted(tempSet)


def FilterPublished(typeList, useOnlyPublished):
    if useOnlyPublished:
        return [ typeID for typeID in typeList if evetypes.IsPublished(typeID) ]
    else:
        return typeList
