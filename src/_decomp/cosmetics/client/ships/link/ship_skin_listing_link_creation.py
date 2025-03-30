#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\cosmetics\client\ships\link\ship_skin_listing_link_creation.py
import evelink.client
from cosmetics.client.ships.link.scheme import LinkScheme
from localization import GetByLabel

def create_link(listing_id, name):
    return evelink.Link(url=u'{}:{}'.format(LinkScheme.SHIP_SKIN_LISTING, listing_id), text=GetByLabel('UI/Personalization/ShipSkins/SKINR/Store/SkinListingLink', name=name))
