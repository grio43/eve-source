#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\util\bubble.py


def SlimItemFromCharID(charID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        for item in bp.slimItems.values():
            if item.charID == charID:
                return item


def InBubble(itemID):
    bp = sm.GetService('michelle').GetBallpark()
    if bp:
        return itemID in bp.balls
    else:
        return False
