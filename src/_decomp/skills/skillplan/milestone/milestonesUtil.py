#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\skills\skillplan\milestone\milestonesUtil.py
import evetypes
from eve.common.lib import appConst
from skills.skillplan.milestone.const import MilestoneSubType

def GetMilestoneSubType(typeID):
    if evetypes.GetCategoryID(typeID) == appConst.categoryShip:
        return MilestoneSubType.SHIP_MILESTONE
    elif evetypes.GetCategoryID(typeID) == appConst.categoryModule:
        return MilestoneSubType.MODULE_MILESTONE
    elif evetypes.GetCategoryID(typeID) == appConst.categorySkill:
        return MilestoneSubType.SKILL_MILESTONE
    else:
        return MilestoneSubType.OTHER_MILESTONE


def GetMilestonesToAddAndDeletedIDs(milestonesToAdd, milestoneIDsToDelete, oldMilestonesToDelete):
    milestonesToAddCopy = milestonesToAdd.copy()
    milestoneIDsToDeleteCopy = milestoneIDsToDelete.copy()
    deleteMilestoneIDsByData = {x.GetData():x.GetID() for x in oldMilestonesToDelete}
    for addController in milestonesToAdd:
        addData = addController.GetData()
        deleteMilestoneID = deleteMilestoneIDsByData.pop(addData, None)
        if deleteMilestoneID:
            milestoneIDsToDeleteCopy.discard(deleteMilestoneID)
            milestonesToAddCopy.discard(addController)

    return (milestonesToAddCopy, milestoneIDsToDeleteCopy)
