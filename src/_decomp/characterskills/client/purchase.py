#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\client\purchase.py
import sys
import carbonui.uiconst as uiconst
import characterskills.common
import evetypes
from UI.missingSkillbooksWnd import MissingSkillbooksWnd
from shipfitting.multiBuyUtil import BuyMultipleTypesWithQty

def dependency(name, injected = None):
    if injected is not None:
        return injected
    return sm.GetService(name)


def is_skill_purchase_enabled(macho_net_service = None):
    macho_net_service = dependency('machoNet', macho_net_service)
    return characterskills.common.is_skill_purchase_enabled(macho_net_service)


def purchase_skills(context, skill_type_ids, confirm = True):
    context.check_skill_purchase_enabled()
    if confirm:
        context.prevalidate_purchase(skill_type_ids)
        wnd = MissingSkillbooksWnd(context=context)
        ret = wnd.ShowModal()
        return context.skills_purchased or []
    else:
        context.validate_purchase(skill_type_ids)
        context.send_skill_purchase_request(skill_type_ids)
        return context.skills_purchased or []


class SkillPurchaseContext(object):

    def __init__(self, macho_net_service = None, skill_service = None, wallet_service = None, skill_plan_template = None):
        self.macho_net_service = dependency('machoNet', macho_net_service)
        self.skill_service = dependency('skills', skill_service)
        self.wallet_service = dependency('wallet', wallet_service)
        self.skills_purchased = []
        self.validator = SkillPurchaseValidator(skill_service=self.skill_service, wallet_service=self.wallet_service)
        self.available_for_purchase = []
        self.unavailable_for_purchase = []
        self.skill_plan_template = skill_plan_template

    def check_skill_purchase_enabled(self):
        characterskills.common.check_skill_purchase_enabled(self.macho_net_service)

    def prevalidate_purchase(self, skill_type_ids):
        self.available_for_purchase, self.unavailable_for_purchase = self.validator.prevalidate(skill_type_ids)

    def purchase_available_skills(self):
        if self.validate_purchase(self.available_for_purchase):
            self.send_skill_purchase_request(self.available_for_purchase)
            self.available_for_purchase = []
            return True
        else:
            return False

    def multibuy_all_skills(self):
        buyDict = {}
        for skill_type_id in self.available_for_purchase:
            buyDict[skill_type_id] = 1

        for skill_type_id in self.unavailable_for_purchase:
            buyDict[skill_type_id] = 1

        BuyMultipleTypesWithQty(buyDict)

    def multibuy_available_skills(self):
        buyDict = {}
        for skill_type_id in self.available_for_purchase:
            buyDict[skill_type_id] = 1

        BuyMultipleTypesWithQty(buyDict)

    def multibuy_unavailable_skills(self):
        buyDict = {}
        for skill_type_id in self.unavailable_for_purchase:
            buyDict[skill_type_id] = 1

        BuyMultipleTypesWithQty(buyDict)

    def validate_purchase(self, skill_type_ids):
        return self.validator.validate(skill_type_ids)

    def send_skill_purchase_request(self, skill_type_ids):
        skills_purchased = self.skill_service.GetSkillHandler().PurchaseSkills(skill_type_ids)
        self.skills_purchased.extend(skills_purchased)
        return True


def confirm_skill_purchase(skill_type_ids):
    if len(skill_type_ids) == 1:
        type_id = skill_type_ids[0]
        key = 'ConfirmSkillPurchase_v2'
        arguments = {'typeID': type_id,
         'cost': characterskills.common.get_direct_purchase_price(type_id)}
    else:
        key = 'ConfirmMultipleSkillPurchase'
        skill_names = [ '- %s' % evetypes.GetName(type_id) for type_id in skill_type_ids ]
        arguments = {'cost': sum(map(characterskills.common.get_direct_purchase_price, skill_type_ids)),
         'skills': '<br>'.join(skill_names)}
    return eve.Message(key, arguments, uiconst.YESNO) == uiconst.ID_YES


class SkillPurchaseValidator(characterskills.common.SkillPurchaseValidator):

    def __init__(self, skill_service = None, wallet_service = None):
        self.skill_service = dependency('skills', skill_service)
        self.wallet_service = dependency('wallet', wallet_service)

    def get_account_balance(self):
        return self.wallet_service.GetWealth()

    def is_skill_injected(self, skill_type_id):
        return self.skill_service.IsSkillInjected(skill_type_id)

    def validate(self, skill_type_ids):
        try:
            super(SkillPurchaseValidator, self).validate(skill_type_ids)
            return True
        except Exception as error:
            _, _, traceback = sys.exc_info()
            characterskills.common.handle_skill_purchase_error(error, traceback)
            return False

    def prevalidate(self, skill_type_ids):
        skill_type_ids = self._remove_duplicate_skills(skill_type_ids)
        skill_type_ids = self._remove_non_skill_type_ids(skill_type_ids)
        skill_type_ids = self._remove_skills_already_injected(skill_type_ids)
        return self._split_skills_available_for_purchase(skill_type_ids)

    def _remove_duplicate_skills(self, skill_type_ids):
        pruned_list = []
        for skill_type_id in skill_type_ids:
            if skill_type_id not in pruned_list:
                pruned_list.append(skill_type_id)

        return pruned_list

    def _remove_non_skill_type_ids(self, skill_type_ids):
        pruned_list = []
        for skill_type_id in skill_type_ids:
            if self.is_skill(skill_type_id):
                pruned_list.append(skill_type_id)

        return pruned_list

    def _remove_skills_already_injected(self, skill_type_ids):
        pruned_list = []
        for skill_type_id in skill_type_ids:
            if not self.is_skill_injected(skill_type_id):
                pruned_list.append(skill_type_id)

        return pruned_list

    def _split_skills_available_for_purchase(self, skill_type_ids):
        available_for_purchase = []
        unavailable_for_purchase = []
        for skill_type_id in skill_type_ids:
            if not self.is_skill_available_for_purchase(skill_type_id):
                unavailable_for_purchase.append(skill_type_id)
            else:
                available_for_purchase.append(skill_type_id)

        return (available_for_purchase, unavailable_for_purchase)
