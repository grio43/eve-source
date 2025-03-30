#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\contentPieces\controlBunkerContentPiece.py
import evetypes
from eve.client.script.ui.shared.agencyNew.contentPieces.baseContentPiece import BaseContentPiece

class ControlBunkerContentPiece(BaseContentPiece):

    def __init__(self, slimItem, ball, *args, **kwargs):
        super(ControlBunkerContentPiece, self).__init__(*args, **kwargs)
        self.slimItem = slimItem
        self.ball = ball

    def GetBracketIconTexturePath(self):
        texturePath = sm.GetService('bracket').GetBracketProps(self.slimItem, self.ball)[0]
        return texturePath

    def GetName(self):
        return evetypes.GetName(self.typeID)
