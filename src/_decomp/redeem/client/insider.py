#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\redeem\client\insider.py
import collections
import datetime
import random
import datetimeutils
import inventorycommon.const as invconst
from carbon.common.script.sys.serviceManager import ServiceManager
from redeem.data import TYPE_THAT_GIVES_ISK

def get_insider_qa_menu():
    return ['Redeeming', [('Clear token cache', clear_token_cache), ('Create test tokens', create_test_tokens)]]


def clear_token_cache():
    ServiceManager.Instance().GetService('redeem').ResetCache()


def create_test_tokens():
    create_redeem_token(type_id=invconst.typeTritanium, quantity=100)
    create_redeem_token(type_id=TYPE_THAT_GIVES_ISK, quantity=1000000)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    create_redeem_token(type_id=3715, expires=expires)
    skill_point_type_ids = sm.GetService('redeem').redeemData._skill_points_by_type.keys()
    skill_point_type_id = random.choice(skill_point_type_ids)
    create_redeem_token(type_id=skill_point_type_id)
    create_redeem_token(type_id=41580, soulbound=True)
    create_redeem_token(type_id=3898)
    create_redeem_token(type_id=33087, soulbound=True)
    create_redeem_token(type_id=49806)


BlueprintData = collections.namedtuple('BlueprintData', ['runs', 'material_level', 'productivity_level'])

def create_redeem_token(type_id, quantity = 1, blueprint_data = None, available = None, expires = None, label = None, description = None, soulbound = False):
    if expires is not None:
        expires = datetimeutils.datetime_to_filetime(expires)
    if available is not None:
        available = datetimeutils.datetime_to_filetime(available)
    if label is None:
        label = ''
    if description is None:
        description = 'TEST TOKEN'
    ServiceManager.Instance().RemoteSvc('userSvc').CreateRedeemTokenQA(userID=session.userid, typeID=type_id, quantity=quantity, blueprintRuns=blueprint_data.runs if blueprint_data else 0, blueprintMaterialLevel=blueprint_data.material_level if blueprint_data else 0, blueprintProductivityLevel=blueprint_data.productivity_level if blueprint_data else 0, expiry=expires, label=label, description=description, addedByContext=1, addedByExtra=None, available=available, soulbound=soulbound)
