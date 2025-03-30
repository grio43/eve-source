#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\dragdrop\dragdata\basedragdata.py


class BaseDragData(object):

    def GetIconTexturePath(self):
        return 'res:/UI/Texture/WindowIcons/items.png'

    def get_link(self):
        raise NotImplementedError
