#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\cosmetics\ship\pages\store\skinListingDragData.py
from carbonui.control.dragdrop.dragdata import BaseDragData
from cosmetics.client.ships.link.ship_skin_listing_link_creation import create_link

class SkinListingDragData(BaseDragData):

    def __init__(self, listing, *args, **kwargs):
        self.listing = listing
        super(SkinListingDragData, self).__init__(*args, **kwargs)

    def GetIconTexturePath(self):
        return 'res:/UI/Texture/WindowIcons/paint_tool.png'

    def get_link(self):
        return create_link(listing_id=self.listing.identifier, name=self.listing.name)
