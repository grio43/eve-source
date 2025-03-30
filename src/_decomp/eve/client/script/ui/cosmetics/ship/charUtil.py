#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\charUtil.py
from eve.common.lib import appConst
from localization import GetByLabel

def get_active_character_id():
    return session.charid


def get_portrait(character_id, sprite, size = 64):
    sm.GetService('photo').GetPortrait(character_id, size, sprite)


def get_name(character_id):
    return cfg.eveowners.Get(character_id).name


def get_name_link(character_id):
    return GetByLabel(labelNameAndPath='UI/Personalization/ShipSkins/SKINR/CharacterNameLink', showInfoName=get_name(character_id), info=('showinfo', appConst.typeCharacter, character_id))
