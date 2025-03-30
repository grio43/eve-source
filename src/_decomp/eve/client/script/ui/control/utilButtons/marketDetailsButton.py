#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\utilButtons\marketDetailsButton.py
from eve.client.script.ui.control.glowSprite import GlowSprite
from localization import GetByLabel

class ShowMarketDetailsButton(GlowSprite):
    default_texturePath = 'res:/ui/Texture/Icons/show_in_market_20.png'
    default_width = 20
    default_height = 20

    def ApplyAttributes(self, attributes):
        GlowSprite.ApplyAttributes(self, attributes)
        self.typeID = attributes.typeID
        self.hint = GetByLabel('UI/Inventory/ItemActions/ViewTypesMarketDetails')

    def OnClick(self, *args):
        sm.StartService('marketutils').ShowMarketDetails(self.typeID, None)

    def SetTypeID(self, typeID):
        self.typeID = typeID
