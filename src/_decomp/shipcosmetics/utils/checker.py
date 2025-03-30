#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipcosmetics\utils\checker.py
__all__ = ['is_corp_logo', 'is_alliance_logo']
from shipcosmetics.common.const import CosmeticsType

def is_corp_logo(logo_module):
    return logo_module.getCosmeticType() == CosmeticsType.CORPORATION_LOGO


def is_alliance_logo(logo_module):
    return logo_module.getCosmeticType() == CosmeticsType.ALLIANCE_LOGO
