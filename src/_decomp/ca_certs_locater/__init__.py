#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\ca_certs_locater\__init__.py
from certifi import where

def get():
    return where()
