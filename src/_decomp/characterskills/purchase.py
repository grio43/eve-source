#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\characterskills\purchase.py
import abc

def purchase_skills(context, skill_type_ids):
    skill_type_ids = list(skill_type_ids)
    context.validate(skill_type_ids)
    skills_to_inject = []
    try:
        for skill_type_id in skill_type_ids:
            context.pay_for_skill(skill_type_id)
            skills_to_inject.append(skill_type_id)

    finally:
        if skills_to_inject:
            context.inject_skills(skills_to_inject)

    return skills_to_inject


class SkillPurchaseContext(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_validator(self):
        pass

    @abc.abstractmethod
    def inject_skills(self, skill_type_ids):
        pass

    @abc.abstractmethod
    def pay_for_skill(self, skill_type_id):
        pass

    def validate(self, skill_type_ids):
        validator = self.get_validator()
        validator.validate(skill_type_ids)


class SkillPurchaseValidator(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_account_balance(self):
        pass

    @abc.abstractmethod
    def get_skill_price(self, skill_type_id):
        pass

    @abc.abstractmethod
    def is_skill(self, type_id):
        pass

    @abc.abstractmethod
    def is_skill_available_for_purchase(self, skill_type_id):
        pass

    @abc.abstractmethod
    def is_skill_injected(self, skill_type_id):
        pass

    def validate(self, skill_type_ids):
        self._check_no_duplicate_skills(skill_type_ids)
        self._check_all_type_ids_are_skills(skill_type_ids)
        self._check_all_skills_available_for_purchase(skill_type_ids)
        self._check_no_skills_already_injected(skill_type_ids)
        self._check_balance_can_cover_purchase_cost(skill_type_ids)

    def _check_no_duplicate_skills(self, skill_type_ids):
        duplicates = find_duplicates(skill_type_ids)
        if duplicates:
            raise DuplicateSkillValueError(duplicates)

    def _check_all_type_ids_are_skills(self, type_ids):
        for type_id in type_ids:
            if not self.is_skill(type_id):
                raise TypeIsNotSkillError(type_id)

    def _check_no_skills_already_injected(self, skill_type_ids):
        for skill_type_id in skill_type_ids:
            if self.is_skill_injected(skill_type_id):
                raise SkillAlreadyInjectedError(skill_type_id)

    def _check_all_skills_available_for_purchase(self, skill_type_ids):
        for skill_type_id in skill_type_ids:
            if not self.is_skill_available_for_purchase(skill_type_id):
                raise SkillUnavailableForPurchaseError(skill_type_id)

    def _check_balance_can_cover_purchase_cost(self, skill_type_ids):
        total_cost = sum(map(self.get_skill_price, skill_type_ids))
        balance = self.get_account_balance()
        if total_cost > balance:
            raise NotEnoughMoneyError(total_cost, balance)


def find_duplicates(seq):
    seen = set()
    duplicates = set()
    for item in seq:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return duplicates


class SkillPurchaseError(Exception):
    pass


class SkillAlreadyInjectedError(SkillPurchaseError):
    MESSAGE_TEMPLATE = 'The skill (type ID {}) is already injected'

    def __init__(self, type_id):
        message = self.MESSAGE_TEMPLATE.format(type_id)
        super(SkillAlreadyInjectedError, self).__init__(message)
        self.type_id = type_id


class SkillUnavailableForPurchaseError(SkillPurchaseError):
    MESSAGE_TEMPLATE = 'The skill (type ID {}) is not available for purchase'

    def __init__(self, type_id):
        message = self.MESSAGE_TEMPLATE.format(type_id)
        super(SkillUnavailableForPurchaseError, self).__init__(message)
        self.type_id = type_id


class TypeIsNotSkillError(SkillPurchaseError):
    MESSAGE_TEMPLATE = 'Type ID {} is not a skill'

    def __init__(self, type_id):
        message = self.MESSAGE_TEMPLATE.format(type_id)
        super(TypeIsNotSkillError, self).__init__(message)
        self.type_id = type_id


class NotEnoughMoneyError(SkillPurchaseError):
    MESSAGE_TEMPLATE = 'You need {} to complete this purchase but only have {}'

    def __init__(self, required_amount, current_balance):
        message = self.MESSAGE_TEMPLATE.format(required_amount, current_balance)
        super(NotEnoughMoneyError, self).__init__(message)
        self.required_amount = required_amount
        self.current_balance = current_balance


class DuplicateSkillValueError(SkillPurchaseError):
    MESSAGE_TEMPLATE = 'The following skill type IDs occurr more than once in the input: {}'

    def __init__(self, type_ids):
        message = self.MESSAGE_TEMPLATE.format(', '.join(map(str, type_ids)))
        super(DuplicateSkillValueError, self).__init__(message)
        self.type_ids = type_ids
