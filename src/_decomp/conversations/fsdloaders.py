#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\conversations\fsdloaders.py
from fsdBuiltData.common.base import BuiltDataLoader
try:
    import conversationsLoader
except ImportError:
    conversationsLoader = None

try:
    import conversationAgentsLoader
except ImportError:
    conversationAgentsLoader = None

class ConversationsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/conversations.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/conversations.fsdbinary'
    __loader__ = conversationsLoader

    @classmethod
    def GetByID(cls, conversationID):
        return cls.GetData().get(conversationID, None)


class ConversationAgentsLoader(BuiltDataLoader):
    __resBuiltFile__ = 'res:/staticdata/conversationAgents.fsdbinary'
    __clientAutobuildBuiltFile__ = 'eve/autobuild/staticdata/client/conversationAgents.fsdbinary'
    __loader__ = conversationAgentsLoader

    @classmethod
    def GetByID(cls, agentID):
        return cls.GetData().get(agentID, None)
