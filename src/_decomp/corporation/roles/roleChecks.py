#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\corporation\roles\roleChecks.py
import localization
from eve.common.script.sys import idCheckers

def CheckCanLaunchForCorp(corpID, corprole, whoseBehalfID, itemCategory):
    isOrbital = idCheckers.IsOrbital(itemCategory)
    if corpID != whoseBehalfID:
        raise UserError('CantLaunchNotInCorp', {'corp': (const.UE_OWNERID, whoseBehalfID)})
    if cfg.eveowners.Get(corpID).IsNPC():
        raise UserError('CantLaunchCorpDoesntAllow', {'corp': (const.UE_OWNERID, corpID)})
    if isOrbital:
        if const.corpRoleEquipmentConfig != const.corpRoleEquipmentConfig & corprole:
            raise UserError('CrpAccessDenied', {'reason': localization.GetByLabel('UI/Corporations/AccessRestrictions/NotEquipmentConfigManager')})
