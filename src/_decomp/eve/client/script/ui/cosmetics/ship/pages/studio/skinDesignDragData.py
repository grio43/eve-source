#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\studio\skinDesignDragData.py
from carbonui.control.dragdrop.dragdata.basedragdata import BaseDragData
from cosmetics.client.ships.link.ship_skin_design_link_creation import create_link

class SkinDesignDragData(BaseDragData):

    def __init__(self, design_data, saved_design_id, *args, **kwargs):
        self.design_data = design_data
        self.saved_design_id = saved_design_id
        super(SkinDesignDragData, self).__init__(*args, **kwargs)

    def GetIconTexturePath(self):
        return 'res:/UI/Texture/WindowIcons/paint_tool.png'

    def get_link(self):
        return create_link(character_id=self.design_data.creator_character_id, design_id=self.saved_design_id, name=self.design_data.name)
