#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\buyButton.py
from eve.client.script.ui.shared.skins.event import LogBuySkinAur, LogBuySkinIsk
from eve.client.script.ui.shared.vgs.button import BuyButtonAurSmall, BuyButtonIskSmall

class SkinLicenseBuyButtonAur(BuyButtonAurSmall):

    def ApplyAttributes(self, attributes):
        self.logContext = attributes.logContext
        super(SkinLicenseBuyButtonAur, self).ApplyAttributes(attributes)

    def OpenOfferWindow(self):
        super(SkinLicenseBuyButtonAur, self).OpenOfferWindow()
        LogBuySkinAur(None, None, self.logContext)


class SkinLicenseBuyButtonIsk(BuyButtonIskSmall):
    default_name = 'SkinMaterialBuyButtonIsk'

    def ApplyAttributes(self, attributes):
        super(SkinLicenseBuyButtonIsk, self).ApplyAttributes(attributes)
        self.logContext = attributes.logContext

    def OpenMarketWindow(self):
        super(SkinLicenseBuyButtonIsk, self).OpenMarketWindow()
        LogBuySkinIsk(None, None, self.logContext)


class SkinMaterialBuyButtonAur(BuyButtonAurSmall):
    default_name = 'SkinMaterialBuyButtonAur'
    COLOR_DISABLED = (0.2, 0.2, 0.2, 0.8)
    COLOR_DISABLED_TEXT = (0.6, 0.6, 0.6, 1.0)
    COLOR_DISABLED_ICON = (0.6, 0.6, 0.6, 1.0)

    def ApplyAttributes(self, attributes):
        self.typeID = attributes.typeID
        self.materialID = attributes.materialID
        self.logContext = attributes.logContext
        attributes.types = self.GetLicenseTypesForMaterial()
        if attributes.disabled:
            attributes.color = self.COLOR_DISABLED
            attributes.iconColor = self.COLOR_DISABLED_ICON
            attributes.labelColor = self.COLOR_DISABLED_TEXT
        super(SkinMaterialBuyButtonAur, self).ApplyAttributes(attributes)

    def GetLicenseTypesForMaterial(self):
        cosmeticsSvc = sm.GetService('cosmeticsSvc')
        licenses = cosmeticsSvc.static.GetLicensesForTypeWithMaterial(self.typeID, self.materialID)
        return [ l.licenseTypeID for l in licenses ]

    def OpenOfferWindow(self):
        super(SkinMaterialBuyButtonAur, self).OpenOfferWindow()
        LogBuySkinAur(self.typeID, self.materialID, self.logContext)


class SkinMaterialBuyButtonIsk(BuyButtonIskSmall):
    default_name = 'SkinMaterialBuyButtonIsk'
    COLOR_DISABLED = (0.2, 0.2, 0.2, 0.8)
    COLOR_DISABLED_TEXT = (0.6, 0.6, 0.6, 1.0)
    COLOR_DISABLED_ICON = (0.6, 0.6, 0.6, 1.0)

    def ApplyAttributes(self, attributes):
        if attributes.disabled:
            attributes.color = self.COLOR_DISABLED
            attributes.iconColor = self.COLOR_DISABLED_ICON
            attributes.labelColor = self.COLOR_DISABLED_TEXT
        super(SkinMaterialBuyButtonIsk, self).ApplyAttributes(attributes)
        self.materialID = attributes.materialID
        self.logContext = attributes.logContext

    def OpenMarketWindow(self):
        sm.GetService('cosmeticsSvc').OpenMarketForTypeWithMaterial(self.typeID, self.materialID)
        LogBuySkinIsk(self.typeID, self.materialID, self.logContext)
