#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\common\contextualOfferDTO.py
import datetimeutils
from contextualOffers.common.contextualOfferDataHelpers import make_offer_info_object
from contextualOffers.common.contextualOfferDataHelpers import make_purchase_info_object

def make_purchase_info_from_protobuf(data):
    purchaseInfo = make_purchase_info_object(offerID=data.offer_identifier.identifier, confirmationTitle=data.confirmationTitle, confirmationBackground=data.confirmationBackground, confirmationButtonText=data.confirmationButtonTitle, confirmationDescription=data.confirmationDescription, notificationBody=data.notificationBody, notificationTitle=data.notificationTitle, notificationType=data.notificationType)
    return purchaseInfo


def make_from_protobuf(data):
    dateToEveTime = datetimeutils.unix_to_blue(data.validTo.ToSeconds())
    dateFromEveTime = datetimeutils.unix_to_blue(data.validFrom.ToSeconds())
    infoObject = make_offer_info_object(offerID=data.offer_identifier.identifier, startTime=dateFromEveTime, endTime=dateToEveTime, originalPrice=data.originalPrice, offerPrice=data.offerPrice, percentageOff=data.priceOffString, purchaseTitle=data.purchaseTitle, purchaseBody=data.purchaseBody, purchaseBackground=data.purchaseBackground, purchaseButtonTitle=data.purchaseButtonTitle, purchaseURL=data.purchaseURL, notificationBody=data.notificationBody, notificationTitle=data.notificationTitle, notificationType=data.notificationType, tooltipHeader=data.tooltipHeader, tooltipContent=data.tooltipContent)
    return infoObject
