#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\common\lib\corporations.py
from ccp_exceptions import UserError
import appConst as const

def IsAccountantOrJuniorAccountantRole(role):
    return role & (const.corpRoleAccountant | const.corpRoleJuniorAccountant)


def ValidateAccountantRole(role):
    if not role & const.corpRoleAccountant:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotFullAccountant')})


def ValidateAccountantOrJuniorAccountantRole(role):
    if not IsAccountantOrJuniorAccountantRole(role):
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotAccountant')})


def ValidateAccountantOrTraderRole(role):
    if not role & (const.corpRoleAccountant | const.corpRoleJuniorAccountant):
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccountantOrTrader')})


_CORP_WALLET_DIVISION_ROLES = {1000: const.corpRoleAccountCanTake1,
 1001: const.corpRoleAccountCanTake2,
 1002: const.corpRoleAccountCanTake3,
 1003: const.corpRoleAccountCanTake4,
 1004: const.corpRoleAccountCanTake5,
 1005: const.corpRoleAccountCanTake6,
 1006: const.corpRoleAccountCanTake7,
 10000: const.corpRoleAccountant}

def ValidateCorpWalletDivisionAccess(role, key):
    if key is None:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})
    if _CORP_WALLET_DIVISION_ROLES[key] & role == 0:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})


def ValidateCorpWalletDivisionReadAccess(role, key):
    if IsAccountantOrJuniorAccountantRole(role):
        return
    if key is None:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})
    if _CORP_WALLET_DIVISION_ROLES[key] & role == 0:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NoAccessToWalletDivision')})


def ValidateDirectorRole(role):
    if not role & const.corpRoleDirector:
        raise UserError('CrpAccessDenied', {'reason': (const.UE_LOC, 'UI/Corporations/AccessRestrictions/NotDirector')})
