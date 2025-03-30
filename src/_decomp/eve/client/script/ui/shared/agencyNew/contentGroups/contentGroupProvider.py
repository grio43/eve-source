#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\contentGroupProvider.py
import logging
from eve.client.script.ui.shared.agencyNew.contentGroups.homeContentGroup import HomeContentGroup
logger = logging.getLogger(__name__)
rootContentGroup = None

def GetRootContentGroup():
    global rootContentGroup
    if not rootContentGroup:
        rootContentGroup = HomeContentGroup()
    return rootContentGroup


def GetContentGroup(contentGroupID, itemID = None):
    contentGroup = GetRootContentGroup().GetContentGroup(contentGroupID, itemID)
    if not contentGroup:
        logger.warn('No Content Group found: contentGroupID=%s, itemID=%s - defaulting to home' % (contentGroupID, itemID))
        return GetRootContentGroup()
    return contentGroup


def IsContentGroupValid(contentGroupID, itemID = None):
    return bool(GetRootContentGroup().GetContentGroup(contentGroupID, itemID))


def ResetData():
    global rootContentGroup
    rootContentGroup = None
