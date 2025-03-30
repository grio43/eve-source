#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentGroups\dynamicContentGroup.py
from eve.client.script.ui.shared.agencyNew.contentGroups.externalContentGroup import ExternalContentGroup

class DynamicContentGroup(ExternalContentGroup):
    default_backgroundTexture = 'res:/UI/Texture/Classes/Agency/navigationCards/defaultDynamicTexture.png'

    def __init__(self, contentGroupID = None, itemID = None, parent = None, callback = None, groupName = None, groupDesc = None, texturePath = None, opensInAgency = False):
        self.callback = callback
        self.groupName = groupName
        self.groupDesc = groupDesc
        self.texturePath = texturePath or self.default_backgroundTexture
        self.opensInAgency = opensInAgency
        self.contentGroupID = contentGroupID
        super(DynamicContentGroup, self).__init__(itemID=itemID, parent=parent)

    def GetBackgroundTexture(self):
        return self.texturePath

    def GetName(self):
        return self.groupName

    def GetDescription(self):
        return self.groupDesc

    def CallExternalFunc(self):
        if self.callback:
            self.callback()

    def OpensWithinAgency(self):
        return self.opensInAgency
