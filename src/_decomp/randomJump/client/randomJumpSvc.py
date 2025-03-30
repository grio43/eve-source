#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\randomJump\client\randomJumpSvc.py
from carbon.common.script.sys.service import CoreService
from randomJump.client.randomJumpActivationWindow import RandomJumpActivationWindow

class RandomJumpService(CoreService):
    __guid__ = 'svc.randomJumpSvc'
    __displayname__ = 'Random Jump Client Service'

    def __init__(self):
        CoreService.__init__(self)

    def ActivateRandomJumpFilament(self, itemID):
        sm.RemoteSvc('randomJumpMgr').ActivateRandomJumpFilament(itemID)

    def open_random_jump_key_activation_window(self, key_item):
        RandomJumpActivationWindow.Open(item=key_item)
