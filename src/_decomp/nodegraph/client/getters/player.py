#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\getters\player.py
from .base import GetterAtom
from eve.common.script.sys.idCheckers import IsCharacter

class GetCorporation(GetterAtom):
    atom_id = 544

    def __init__(self, character_id = None):
        self.character_id = character_id

    def get_values(self, **kwargs):
        if not self.character_id or not IsCharacter(self.character_id):
            return None
        if self.character_id == session.charid:
            return {'corporation_id': session.corpid}
        info = sm.RemoteSvc('charMgr').GetPublicInfo3(self.character_id)
        if info:
            corp_id = info[0].corporationID
            return {'corporation_id': corp_id}

    @classmethod
    def get_subtitle(cls, character_id = None, **kwargs):
        if character_id:
            return character_id
        return ''
