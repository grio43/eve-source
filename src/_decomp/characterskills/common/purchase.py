#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\common\purchase.py
import characterskills
import eveexceptions
import evetypes
import globalConfig
import logging
DIRECT_PURCHASE_TAX_RATE = 0.3

def is_skill_purchase_enabled(macho_net_service):
    return globalConfig.IsSkillPurchaseEnabled(macho_net_service)


def check_skill_purchase_enabled(macho_net_service):
    if not is_skill_purchase_enabled(macho_net_service):
        raise eveexceptions.UserError('SkillPurchaseDisabled')


def get_direct_purchase_price(skill_type_id):
    if not evetypes.IsSkill(skill_type_id):
        raise characterskills.TypeIsNotSkillError(skill_type_id)
    if not is_available_for_purchase(skill_type_id):
        raise characterskills.SkillUnavailableForPurchaseError(skill_type_id)
    base_price = evetypes.GetBasePrice(skill_type_id)
    return base_price * (1.0 + DIRECT_PURCHASE_TAX_RATE)


def is_available_for_purchase(skill_type_id):
    return evetypes.IsSkillAvailableForPurchase(skill_type_id)


def handle_skill_purchase_error(error, traceback):
    if isinstance(error, eveexceptions.UserError):
        raise error, None, traceback
    if isinstance(error, characterskills.TypeIsNotSkillError):
        key = 'ItemNotASkill'
        args = {'skillName': error.type_id}
    elif isinstance(error, characterskills.NotEnoughMoneyError):
        key = 'NotEnoughMoney'
        args = {'balance': error.current_balance,
         'amount': error.required_amount}
    elif isinstance(error, characterskills.SkillAlreadyInjectedError):
        key = 'CharacterAlreadyKnowsSkill'
        args = {'skillName': error.type_id}
    elif isinstance(error, characterskills.SkillUnavailableForPurchaseError):
        key = 'SkillUnavailableForPurchase'
        args = {'type': error.type_id}
    else:
        key = 'SkillPurchaseUnknownError'
        args = None
        logging.exception('Unknown exception caught while attempting to purchase skills')
    raise eveexceptions.UserError(key, args), None, traceback


class SkillPurchaseValidator(characterskills.SkillPurchaseValidator):

    def get_skill_price(self, skill_type_id):
        return get_direct_purchase_price(skill_type_id)

    def is_skill(self, type_id):
        return evetypes.IsSkill(type_id)

    def is_skill_available_for_purchase(self, skill_type_id):
        return is_available_for_purchase(skill_type_id)
