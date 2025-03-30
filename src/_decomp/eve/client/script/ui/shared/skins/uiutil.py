#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\skins\uiutil.py
import evelink.client
from inventorycommon.const import typeSkinMaterial
from utillib import KeyVal
OPEN_SKINR_BUTTON_ANALYTIC_ID = 'ShipSKINR_OpenFromSkinPanel'
OPEN_SKINR_BUTTON_INFO_WINDOW_ANALYTIC_ID = 'ShipSKINR_OpenFromInfoWindow'
OPEN_SKINR_BUTTON_NES_BANNER_ANALYTIC_ID = 'ShipSKINR_OpenFromNESBanner'

def GetMaterialDragData(material):
    data = KeyVal(typeID=typeSkinMaterial, materialID=material.materialID, label=material.name, texturePath=material.iconTexturePath, get_link=lambda : evelink.type_link(typeSkinMaterial, material.materialID, material.name))
    return [data]
