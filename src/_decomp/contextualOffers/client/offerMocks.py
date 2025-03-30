#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\client\offerMocks.py
from contextualOffers.common.contextualOfferDataHelpers import make_offer_info_object
from eve.common.script.util import notificationconst as notificationConst
START_TIME = 132247779126847495L
END_TIME = 132347789126847495L

def MockOmegaOfferAvailable():
    return make_offer_info_object(offerID=1, startTime=START_TIME, endTime=END_TIME, originalPrice='$14.95', offerPrice='$9.99', percentageOff='-50%', purchaseTitle='GET 30 DAYS OF <color=0xfffbcc14>OMEGA</color>', purchaseBody='All ships, all skills, and faster training', purchaseBackground='res:/UI/Texture/classes/contextualOffers/omegaOffer/purchase_bg.png', purchaseButtonTitle='BUY', purchaseURL='https://secure.eveonline.com/Specials', notificationBody='Limited time Omega offer', notificationTitle='New offer available', notificationType=notificationConst.notificationTypeNewOfferAvailable, tooltipHeader='Omega Clone State', tooltipContent='\x95 Train skills 2x faster\n' + '\x95 Unlock unlimited skill queue\n' + '\x95 Gain access to all skills\n' + '\x95 Unlock all 350+ spaceships')


def MockDestroyerBundleOfferAvailable():
    return make_offer_info_object(offerID=3, startTime=START_TIME, endTime=END_TIME, originalPrice='$9.98', offerPrice='$4.99', percentageOff='-50%', purchaseTitle='DESTROYER BUNDLE - GET LIGHT YEARS AHEAD', purchaseBody='A fully fitted Destroyer with SKIN, PLEX and more', purchaseBackground='res:/UI/Texture/classes/contextualOffers/destroyerBundle/Catalyst-CombatCrate_770x415.png', purchaseButtonTitle='BUY', purchaseURL='https://secure.eveonline.com/Specials', notificationBody='Limited time Destroyer Bundle', notificationTitle='New offer available', notificationType=notificationConst.notificationTypeNewOfferAvailable, tooltipHeader='Destroyer Bundle', tooltipContent='\x95 Fully fitted destroyer\n' + '\x95 SKIN\n' + '\x95 Ship Insurance\n' + '\x95 PLEX and more')


def MockDestroyerBundleAndOmegaOfferAvailable():
    return make_offer_info_object(offerID=4, startTime=START_TIME, endTime=END_TIME, originalPrice='$24.94', offerPrice='$12.47', percentageOff='-50%', purchaseTitle='30 DAYS OF <color=0xfffbcc14>OMEGA</color> + <color=0xfffbcc14>DESTROYER</color> BUNDLE', purchaseBody='50% off Omega, fully fitted Destroyer, SKIN & more', purchaseBackground='res:/UI/Texture/classes/contextualOffers/destroyerBundleAndOmegaOffer/Catalyst-CombatCrate_770x415.png', purchaseButtonTitle='BUY', purchaseURL='https://secure.eveonline.com/Specials', notificationBody='Limited time Omega and Destroyer Bundle Offer', notificationTitle='New offer available', notificationType=notificationConst.notificationTypeNewOfferAvailable, tooltipHeader='Omega Clone State and Destroyer Bundle', tooltipContent='\x95 Train skills 2x faster\n' + '\x95 Unlock unlimited skill queue\n' + '\x95 Gain access to all skills\n' + '\x95 Unlock all 350+ spaceships\n' + '\x95 Fully fitted Destroyer\n' + '\x95 SKIN\n' + '\x95 Ship Insurance\n' + '\x95 PLEX and more')
