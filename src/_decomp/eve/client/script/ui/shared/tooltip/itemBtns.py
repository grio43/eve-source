#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\tooltip\itemBtns.py
import evetypes
from carbonui.control.button import Button
from eve.client.script.ui.shared.industry import submitButton
from eve.client.script.ui.shared.neocom import skillConst
from inventorycommon import const as invconst
from eve.client.script.ui.services.menuSvcExtras import menuFunctions
from localization import GetByLabel
from carbonui import uiconst

class TrainNowButton(submitButton.PrimaryButton):
    default_name = 'TrainNowButton'

    def ApplyAttributes(self, attributes):
        super(TrainNowButton, self).ApplyAttributes(attributes)
        self.typeID = attributes.typeID
        self.required = attributes.required
        self._isFinished = False
        self.UpdateState()

    def IsActive(self):
        return not self._isFinished

    def ClickFunc(self, *args):
        self.Disable()
        try:
            sm.GetService('skillqueue').AddSkillAndRequirementsToQueue(self.typeID)
            self._isFinished = True
        except Exception:
            self.Enable()

        self.UpdateState()

    def GetColor(self):
        if self._isFinished:
            return (1.0, 1.0, 1.0, 0.3)
        else:
            return skillConst.COLOR_SKILL_2

    def GetText(self):
        if self._isFinished:
            skills = GetMissingRequiredSkills(self.typeID)
            skillCount = len(skills)
            if evetypes.GetCategoryID(self.typeID) == invconst.categorySkill:
                skillCount += 1
            return GetByLabel('UI/SkillQueue/SkillsQueued', skillCount=skillCount)
        else:
            return GetByLabel('UI/SkillQueue/AddToQueue')


class InjectSkillButton(submitButton.PrimaryButton):
    default_name = 'InjectSkillButton'

    def ApplyAttributes(self, attributes):
        super(InjectSkillButton, self).ApplyAttributes(attributes)
        self._item = attributes.item
        self._injected = False
        self.UpdateState()

    def ClickFunc(self, *args):
        self.Disable()
        try:
            sm.GetService('skills').InjectSkillIntoBrain([self._item])
            self._injected = True
        except Exception:
            self.Enable()
            raise

        self.UpdateState()

    def IsActive(self):
        return not self._injected

    def GetColor(self):
        if self._injected:
            return (1.0, 1.0, 1.0, 0.3)
        else:
            return skillConst.COLOR_SKILL_2

    def GetText(self):
        if self._injected:
            return GetByLabel('UI/SkillQueue/SkillInjected')
        else:
            return GetByLabel('UI/SkillQueue/InjectSkill')


class ActivateSkinButton(submitButton.PrimaryButton):
    default_name = 'ActivateSkinButton'

    def ApplyAttributes(self, attributes):
        super(ActivateSkinButton, self).ApplyAttributes(attributes)
        self._item = attributes.item
        self._injected = False
        self.UpdateState()

    def ClickFunc(self, *args):
        self.Disable()
        try:
            menuFunctions.ActivateShipSkinLicense([[self._item.itemID, self._item.typeID]])
            self._injected = True
        except Exception:
            self.Enable()
            raise

        self.UpdateState()

    def IsActive(self):
        return not self._injected

    def GetColor(self):
        if self._injected:
            return (1.0, 1.0, 1.0, 0.3)
        else:
            return skillConst.COLOR_SKILL_2

    def GetText(self):
        return GetByLabel('UI/Commands/ActivateSkinLicense')


class ActivateAndApplySkinButton(submitButton.PrimaryButton):
    default_name = 'ActivateAndApplySkinButton'

    def ApplyAttributes(self, attributes):
        self._can_apply = attributes.can_apply
        attributes['enabled'] = self._can_apply
        super(ActivateAndApplySkinButton, self).ApplyAttributes(attributes)
        self._item = attributes.item
        self._injected = False
        self.UpdateState()

    def UpdateIsEnabledByState(self):
        if self._can_apply:
            self.Enable()
        else:
            self.Disable()

    def ClickFunc(self, *args):
        self.Disable()
        try:
            menuFunctions.ActivateShipSkinLicenseAndApply(self._item.itemID, self._item.typeID)
            self._injected = True
        except Exception:
            self.Enable()
            raise

        self.UpdateState()

    def IsActive(self):
        if not self._can_apply:
            return False
        return not self._injected

    def GetColor(self):
        if not self.enabled or self._injected:
            return (1.0, 1.0, 1.0, 0.3)
        else:
            return skillConst.COLOR_SKILL_2

    def GetText(self):
        if not self._can_apply:
            return GetByLabel('UI/Commands/ActivateAndApplySkinLicenseDisabled')
        return GetByLabel('UI/Commands/ActivateAndApplySkinLicense')


class ConsumeSkinDesignComponentButton(submitButton.PrimaryButton):
    default_name = 'ConsumeSkinDesignComponentButton'

    def ApplyAttributes(self, attributes):
        super(ConsumeSkinDesignComponentButton, self).ApplyAttributes(attributes)
        self._item = attributes.item
        self._isConsumed = False
        self.UpdateState()

    def ClickFunc(self, *args):
        self.Disable()
        try:
            menuFunctions.ConsumeSkinDesignComponent([(self._item.itemID, self._item.typeID, self._item.stacksize)])
            self._isConsumed = True
        except Exception:
            self.Enable()
            raise

        self.UpdateState()

    def IsActive(self):
        return not self._isConsumed

    def GetColor(self):
        if self._isConsumed:
            return (1.0, 1.0, 1.0, 0.3)
        else:
            return skillConst.COLOR_SKILL_2

    def GetText(self):
        return GetByLabel('UI/Inventory/ItemActions/ConsumeSkinDesignComponentItem')

    def GetHint(self):
        return GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/ActivateNowHint')


def GetMissingRequiredSkills(typeID):
    required = sm.GetService('skills').GetSkillsMissingToUseItemRecursive(typeID)
    inQueue = sm.GetService('skills').GetMaxSkillLevelsInQueue()
    missing = [ (s, l) for s, l in required.iteritems() if inQueue.get(s, 0) < l ]
    return missing
