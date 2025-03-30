#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\seasons\client\commentator.py
LOOK_AT_CONVERSATIONS_BY_TYPE_ID = {49118: 512,
 49120: 514,
 49122: 513,
 49124: 511,
 49786: 518,
 49785: 519,
 49784: 520}

class Commentator(object):
    __notifyevents__ = ['OnCameraLookAt']

    def __init__(self, sm, conversationService, michelle):
        self.conversationService = conversationService
        self.michelle = michelle
        sm.RegisterNotify(self)

    def OnCameraLookAt(self, isEgo, itemID):
        item = self.michelle.GetItem(itemID)
        if item is not None:
            typeID = item.typeID
            if typeID is not None:
                conversation = LOOK_AT_CONVERSATIONS_BY_TYPE_ID.get(typeID, None)
                if conversation is not None:
                    self.conversationService.show_conversation(conversation, show_warning_on_first_close_setting=False)
