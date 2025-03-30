#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\info\panels\panelShipAvailableSkinLicenses.py
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.util.sortUtil import SortListOfTuples
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
import evetypes
from carbonui import const as uiconst
from localization import GetByLabel

class PanelShipAvailableSkinLicenses(Container):

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.Layout()

    def Layout(self):
        self.scroll = Scroll(name='scroll', parent=self, padding=4)

    def Load(self):
        entries = []
        cosmeticsSvc = sm.GetService('cosmeticsSvc')
        skins = cosmeticsSvc.GetSkins(self.typeID)
        skinForType = {s.skinID:s.expires for s in cosmeticsSvc.GetLicensedSkinsForType(self.typeID)}
        for skin in skins:
            static = cosmeticsSvc.static
            licenses = static.GetLicensesForTypeWithMaterial(self.typeID, skin.materialID)
            for license in licenses:
                skinID = license.skinID
                haveSkinMaterial = skinID in skinForType
                ownSkinTypeInList = False
                if haveSkinMaterial:
                    expiryOfOwnedSkin = skinForType[skinID]
                    if license.duration == -1:
                        if expiryOfOwnedSkin is None:
                            ownSkinTypeInList = True
                    else:
                        ownSkinTypeInList = True
                skinName = evetypes.GetName(license.licenseTypeID)
                data = {'typeID': license.licenseTypeID,
                 'itemID': None,
                 'label': skinName,
                 'sublevel': 1,
                 'getIcon': True,
                 'ownSkin': ownSkinTypeInList}
                entry = GetFromClass(SkinItemEntry, data=data)
                sortKey = (-ownSkinTypeInList, skinName)
                entries.append((sortKey, entry))

        entries = SortListOfTuples(entries)
        self.scroll.Load(contentList=entries)


class SkinItemEntry(Item):

    def Startup(self, *args):
        Item.Startup(self, args)
        self.haveIcon = Sprite(parent=self, align=uiconst.CENTERLEFT, pos=(0, 0, 16, 16), texturePath='res:/ui/Texture/classes/Skills/SkillRequirementMet.png', hint=GetByLabel('UI/Skins/OwnSkinLicense'))

    def Load(self, node):
        Item.Load(self, node)
        ownSkin = node.ownSkin
        self.haveIcon.display = bool(ownSkin)
