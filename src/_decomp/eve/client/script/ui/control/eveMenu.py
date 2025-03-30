#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\eveMenu.py
import dogma.data as dogma_data
from brennivin.itertoolsext import Bundle
from caching.memoize import Memoize
from carbonui.primitives.sprite import Sprite
import carbonui.const as uiconst
from eve.client.script.ui.crimewatch import crimewatchConst
from carbonui.control.contextMenu.menuEntryView import MenuEntryView
from eve.common.lib import appConst
from fsdBuiltData.common.iconIDs import GetIconFile

class SuspectMenuEntryView(MenuEntryView):
    default_warningColor = crimewatchConst.Colors.Suspect.GetRGBA()

    def ConstructIcon(self):
        super(SuspectMenuEntryView, self).ConstructIcon()
        self.icon.SetRGBA(*self.default_warningColor)

    def ConstructLabel(self, *args):
        super(SuspectMenuEntryView, self).ConstructLabel(*args)
        self.label.SetRGBA(*self.default_warningColor)


class CriminalMenuEntryView(SuspectMenuEntryView):
    default_warningColor = crimewatchConst.Colors.Criminal.GetRGBA()


class AmmoMenuEntryView(MenuEntryView):
    __guid__ = 'AmmoMenuEntryView'

    def ApplyAttributes(self, attributes):
        MenuEntryView.ApplyAttributes(self, attributes)
        self.ConstructLayout()
        typeID = self.menuEntryData.typeID
        if typeID:
            topAmmoDmgTypeInfo = GetAmmoTopDamageTypes(typeID)
            self.LoadIcons(topAmmoDmgTypeInfo)
            menuIconSize = self.iconSize

    def ConstructLayout(self):
        super(AmmoMenuEntryView, self).ConstructLayout()
        self.primaryDmgSprite = Sprite(parent=self, pos=(4, 0, 20, 20), align=uiconst.CENTERLEFT, idx=0, state=uiconst.UI_DISABLED)

    def _GetLabelLeft(self):
        return 24

    def LoadIcons(self, topAmmoDmgTypeInfo):
        if len(topAmmoDmgTypeInfo) > 0:
            self.primaryDmgSprite.texturePath = topAmmoDmgTypeInfo[0].iconFile


class AmmoMenuEntryView2(AmmoMenuEntryView):

    def ConstructLayout(self):
        super(AmmoMenuEntryView2, self).ConstructLayout()
        self.secondaryDmgSprite = Sprite(parent=self, pos=(24, 0, 20, 20), align=uiconst.CENTERLEFT, idx=0, state=uiconst.UI_DISABLED)

    def _GetLabelLeft(self):
        return 44

    def LoadIcons(self, topAmmoDmgTypeInfo):
        AmmoMenuEntryView.LoadIcons(self, topAmmoDmgTypeInfo)
        if len(topAmmoDmgTypeInfo) > 1:
            self.secondaryDmgSprite.texturePath = topAmmoDmgTypeInfo[1].iconFile


@Memoize
def GetAmmoTopDamageTypes(typeID):
    damageValueWithAttribute = []
    dogmaStaticMgr = sm.GetService('clientDogmaStaticSvc')
    for eachDamageType in appConst.damageTypeAttributes:
        value = dogmaStaticMgr.GetTypeAttribute(typeID, eachDamageType)
        if value:
            damageValueWithAttribute.append((eachDamageType, value))

    damageValueWithAttribute.sort(key=lambda x: x[1], reverse=True)
    totalDamage = sum((x[1] for x in damageValueWithAttribute))
    iconAndPercentage = []
    for eachAttributeID, eachDmg in damageValueWithAttribute[:2]:
        iconID = dogma_data.get_attribute_icon_id(eachAttributeID)
        iconFile = GetIconFile(iconID)
        iconAndPercentage.append(Bundle(iconFile=iconFile, percentage=eachDmg / totalDamage))

    return iconAndPercentage
