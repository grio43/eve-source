#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\script\util\linkUtil.py


def GetTextForShowInfo(typeID, itemID = None):
    if itemID is not None:
        return 'showinfo:%s//%s' % (typeID, itemID)
    else:
        return 'showinfo:%s' % typeID


def GetShowInfoLink(typeID, text, itemID = None):
    showInfoText = GetTextForShowInfo(typeID, itemID)
    return '<a href="%s">%s</a>' % (showInfoText, text)
