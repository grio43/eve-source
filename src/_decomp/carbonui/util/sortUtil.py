#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\util\sortUtil.py


def SortListOfTuples(lst, reverse = 0):
    lst = sorted(lst, reverse=reverse, key=lambda data: data[0])
    return [ item[1] for item in lst ]
