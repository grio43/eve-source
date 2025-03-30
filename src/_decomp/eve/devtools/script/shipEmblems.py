#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\shipEmblems.py
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.control.button import Button
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from shipcosmetics.common.cosmeticlicenses.storage import ShipCosmeticLicensesStaticData

class ShipEmblemsTool(Window):
    default_windowID = 'ShipEmblemsToolWnd'
    default_caption = 'Ship Emblems'
    default_fixedWidth = 700
    default_fixedHeight = 300

    def ApplyAttributes(self, attributes):
        super(ShipEmblemsTool, self).ApplyAttributes(attributes)
        self.licenseStorage = ShipCosmeticLicensesStaticData()
        self.cosmeticsLicenseSvc = sm.GetService('cosmeticsLicenseSvc')
        self.Layout()

    def Layout(self):
        self.mainCont = Container(name='mainCont', parent=self.sr.main, padding=10)
        self.licensesCont = ContainerAutoSize(name='licensesCont', parent=self.mainCont, align=uiconst.TOTOP, height=32)
        licensesOptions = []
        for license in self.licenseStorage.data.itervalues():
            licensesOptions.append((license.name, license.licenseID))

        self.licenseCombo = Combo(parent=self.licensesCont, align=uiconst.TOLEFT, options=licensesOptions)
        self.grantLicenseButton = Button(parent=self.licensesCont, align=uiconst.TOLEFT, label='Grant License', func=self.GrantLicense)
        self.revokeLicenseButton = Button(parent=self.licensesCont, align=uiconst.TOLEFT, label='Revoke License', func=self.RevokeLicense, padLeft=10)

    def GrantLicense(self, *args):
        self.cosmeticsLicenseSvc.debug_grant_ship_cosmetics_license(self.licenseCombo.GetValue())

    def RevokeLicense(self, *args):
        self.cosmeticsLicenseSvc.debug_revoke_ship_cosmetics_license(self.licenseCombo.GetValue())
