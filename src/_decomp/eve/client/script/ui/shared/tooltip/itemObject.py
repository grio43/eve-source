#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\itemObject.py
import evetypes
import menucheckers
import inventorycommon.const as invconst

class ItemObject(object):

    def __init__(self, itemTypeID, item = None):
        self.itemTypeID = itemTypeID
        self.item = item
        self.skillSvc = sm.GetService('skills')
        self.isMissingRarePrereq = None

    def NeedsOmegaUpgrade(self):
        cloneGradeService = sm.GetService('cloneGradeSvc')
        isOmegaRestricted = cloneGradeService.IsRequirementsRestricted(self.itemTypeID)
        isUnlockedWithExpertSystem = self.skillSvc.IsUnlockedWithExpertSystem(self.itemTypeID)
        if isOmegaRestricted and not isUnlockedWithExpertSystem:
            return True
        isSkill = evetypes.GetCategoryID(self.itemTypeID) == invconst.categorySkill
        if not isSkill:
            return False
        level = self.skillSvc.MySkillLevelIncludingQueued(self.itemTypeID)
        if cloneGradeService.IsSkillLevelRestricted(self.itemTypeID, level):
            return True
        if level < 5 and cloneGradeService.IsSkillLevelRestricted(self.itemTypeID, level + 1):
            return True
        return False

    def CanInjectSkill(self):
        if self.item is None:
            return False
        checker = menucheckers.ItemChecker(self.item)
        return checker.OfferInjectSkill()

    def CanActivateSkinLicense(self):
        if self.item is None:
            return False
        checker = menucheckers.ItemChecker(self.item)
        return checker.OfferActivateShipSkinLicense()

    def CanApplySkin(self):
        if self.item is None:
            return False
        checker = menucheckers.ItemChecker(self.item)
        return checker.IsSkinForCurrentShip()

    def CanConsumeSkinDesignComponent(self):
        if self.item is None:
            return False
        checker = menucheckers.ItemChecker(self.item)
        return checker.OfferConsumeShipSkinDesignComponent()

    def GetMissingSkillBooks(self):
        if self.skillSvc.IsSkillRequirementMet(self.itemTypeID):
            return []
        missingSkills = self.skillSvc.GetSkillsMissingToUseItemRecursive(self.itemTypeID)
        missing = [ typeID for typeID in missingSkills.iterkeys() if self.skillSvc.GetSkillIncludingLapsed(typeID) is None ]
        if evetypes.GetCategoryID(self.itemTypeID) == invconst.categorySkill:
            if self.skillSvc.GetSkillIncludingLapsed(self.itemTypeID) is None:
                missing.append(self.itemTypeID)
        return missing

    def CanTrainNow(self):
        if not evetypes.IsPublished(self.itemTypeID):
            return False
        isRequirementsMet = sm.GetService('skills').IsSkillRequirementMetIncludingSkillQueue(self.itemTypeID)
        if not isRequirementsMet:
            return True
        return self.IsSkill() and sm.GetService('skillqueue').CheckCanAppendSkill(self.itemTypeID, check=True)

    def IsRareSkill(self):
        if not self.IsSkill():
            return False
        return not evetypes.IsSkillAvailableForPurchase(self.itemTypeID)

    def IsMissingRarePrereqs(self):
        if self.isMissingRarePrereq is not None:
            return self.isMissingRarePrereq
        missingSkillbooks = self.GetMissingSkillBooks()
        self.isMissingRarePrereq = any((not evetypes.IsSkillAvailableForPurchase(typeID) for typeID in missingSkillbooks))
        return self.isMissingRarePrereq

    def IsSkill(self):
        return evetypes.GetCategoryID(self.itemTypeID) == invconst.categorySkill
