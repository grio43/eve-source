#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\contextualOffers\common\contextualOfferDataHelpers.py


def flatten_omega_prepared_message(offerInfo):
    return {'offerID': offerInfo['offerID'],
     'offerType': 'FirstTimeOmega',
     'purchaseTitle': offerInfo['purchaseStep']['Title'],
     'purchaseDescription': offerInfo['purchaseStep']['Body'],
     'purchaseBackground': offerInfo['purchaseStep']['Background'],
     'purchaseButtonLabel': offerInfo['purchaseStep']['ButtonTitle'],
     'purchaseURL': offerInfo['purchaseStep']['PurchaseURL'],
     'notificationTitle': offerInfo['notification']['Title'],
     'notificationBody': offerInfo['notification']['Body'],
     'notificationType': offerInfo['notification']['Type'],
     'tooltipHeader': offerInfo['tooltip']['header'],
     'tooltipDescription': offerInfo['tooltip']['content'],
     'originalPrice': offerInfo['price']['original'],
     'offerPrice': offerInfo['price']['offer'],
     'discount': offerInfo['price']['percentageOff'],
     'startTimestamp': offerInfo['validFrom'],
     'endTimestamp': offerInfo['validTo']}


def make_purchase_info_object(offerID, confirmationTitle, confirmationDescription, confirmationBackground, confirmationButtonText, notificationTitle, notificationBody, notificationType):
    return {'offerID': offerID,
     'confirmationTitle': confirmationTitle,
     'confirmationDescription': confirmationDescription,
     'confirmationBackground': confirmationBackground,
     'confirmationButtonLabel': confirmationButtonText,
     'notificationTitle': notificationTitle,
     'notificationBody': notificationBody,
     'notificationType': notificationType}


def make_offer_info_object(offerID, startTime, endTime, originalPrice, offerPrice, percentageOff, purchaseTitle, purchaseBody, purchaseBackground, purchaseButtonTitle, purchaseURL, notificationBody, notificationTitle, notificationType, tooltipHeader, tooltipContent):
    offerInfo = {'offerID': offerID,
     'validTo': endTime,
     'validFrom': startTime,
     'price': {'original': originalPrice,
               'offer': offerPrice,
               'percentageOff': percentageOff},
     'purchaseStep': {'Title': purchaseTitle,
                      'Body': purchaseBody,
                      'Background': purchaseBackground,
                      'PurchaseURL': purchaseURL,
                      'ButtonTitle': purchaseButtonTitle},
     'notification': {'Body': notificationBody,
                      'Title': notificationTitle,
                      'Type': notificationType},
     'tooltip': {'header': tooltipHeader,
                 'content': tooltipContent}}
    return offerInfo
