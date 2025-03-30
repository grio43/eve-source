#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\homestation\client\insider.py
from homestation.client.service import Service

def get_insider_qa_menu():
    return ('Home Station', [('Reset remote change timer', Service.instance().reset_remote_change_time), ('Clear cache', Service.instance().clear_cache)])
