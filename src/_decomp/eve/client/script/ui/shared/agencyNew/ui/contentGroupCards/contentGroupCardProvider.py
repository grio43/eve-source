#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\agencyNew\ui\contentGroupCards\contentGroupCardProvider.py
from eve.client.script.ui.shared.agencyNew.ui.contentGroupCards.verticalContentGroupCard import VerticalContentGroupCard
_contentGroupCardClassByContentTypeID = {}

def GetContentGroupCardCls(contentType):
    return _contentGroupCardClassByContentTypeID.get(contentType, VerticalContentGroupCard)
