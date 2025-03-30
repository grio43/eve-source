#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\charsheet\skinsPanel.py
from functools import partial
from collections import Counter
import eveicon
import localization
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.layoutGrid import LayoutGrid
from carbonui.control.buttonIcon import ButtonIcon
from eve.client.script.ui.control.entries.item import Item
from eve.client.script.ui.control.entries.util import GetFromClass
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveScroll import Scroll
from eve.client.script.ui.control.listgroup import ListGroup
from eve.client.script.ui.control.utilMenu import UtilMenu
from eve.client.script.ui.quickFilter import QuickFilterEdit
from eve.client.script.ui.services.menuSvcExtras import menuFunctions
from eve.client.script.ui.shared.skins.skinPanel import SkinDurationLabel
from cosmetics.client.cosmeticsSvc import FirstPartySkin
from inventorycommon.const import typeCapsuleGolden
from itertoolsext import bucket, count
from menucheckers import ItemChecker
from menucheckers.sessionChecker import SessionChecker
from shipskins.uiUtil import GroupAndFilterByShip, GetDataForSkinEntry, GetSkinsAndTexturePathsByByMaterialName
SETTING_SHOW_SKINS = 'charsheet_skins_showSkins'
SHOW_ALL_SKINS = 'all_skins'
SHOW_ACTIVE_SKINS = 'active_skins'
SHOW_INACTIVE_SKINS = 'inactive_skins'
SETTING_DEFAULTS = {SETTING_SHOW_SKINS: SHOW_ALL_SKINS}

class SkinsPanel(Container):
    __notifyevents__ = ['OnSkinLicenseActivated', 'OnSkinLicenseRemoved']
    default_name = 'SkinsPanel'

    def ApplyAttributes(self, attributes):
        super(SkinsPanel, self).ApplyAttributes(attributes)
        sm.RegisterNotify(self)
        self.isConstructed = False

    def ConstructLayout(self):
        if self.isConstructed:
            return
        self.isConstructed = True
        menuBar = ContainerAutoSize(parent=self, align=uiconst.TOTOP, padBottom=16, alignMode=uiconst.CENTERLEFT)
        UtilMenu(parent=menuBar, align=uiconst.CENTERLEFT, GetUtilMenu=self.GetSettingsMenu, texturePath=eveicon.settings, width=24, height=24, iconSize=16)
        self.filter = QuickFilterEdit(parent=menuBar, align=uiconst.CENTERRIGHT, left=2, width=150, hintText=localization.GetByLabel('UI/Inventory/Filter'))
        spacer = Container(parent=menuBar, align=uiconst.CENTERLEFT, pos=(0,
         0,
         1,
         self.filter.height))
        self.counterText = EveLabelMedium(parent=ContainerAutoSize(parent=menuBar, align=uiconst.TOLEFT, left=30), align=uiconst.CENTERLEFT, text='')
        self.filter.ReloadFunction = self.LoadPanel
        self.scroll = Scroll(parent=self, align=uiconst.TOALL)
        self.scroll.sr.content.OnDropData = self.OnDropData

    @property
    def filterText(self):
        return self.filter.GetValue().strip().lower()

    def LoadPanel(self, *args):
        self.ConstructLayout()
        self.scroll.Clear()
        skinsByMaterialID, numLicensedSkinsForShip = self._GetFilteredSkinsByMaterialID()
        skinsByByMaterialName, texturePathsByName = GetSkinsAndTexturePathsByByMaterialName(skinsByMaterialID, sm.GetService('cosmeticsSvc'))
        entries = []
        for eachName, skins in skinsByByMaterialName.iteritems():
            texturePaths = texturePathsByName.get(eachName, [])
            entry = self._CreateGroupEntryForMaterials(eachName, skins, texturePaths)
            if entry is not None:
                entries.append(entry)

        self.counterText.text = localization.GetByLabel('UI/Skins/YouHaveNumShipSkins', numSkins=numLicensedSkinsForShip)
        self.scroll.Load(contentList=sorted(entries, key=lambda e: e.label), noContentHint=localization.GetByLabel('UI/SkillQueue/NoResultsForFilters'))

    def _GetFilteredSkinsByMaterialID(self):
        cosmeticsSvc = sm.GetService('cosmeticsSvc')
        licensedSkinsByID = {s.skinID:s for s in cosmeticsSvc.GetLicensedSkins()}
        skins = []
        for staticSkin in cosmeticsSvc.static.GetAllShipSkins():
            licensedSkin = licensedSkinsByID.get(staticSkin.skinID, None)
            skins.append(self._CreateSkinObject(staticSkin, licensedSkin))

        allLicensedSkins = filter(lambda s: s.licensed, skins)
        show = GetSetting(SETTING_SHOW_SKINS)
        if show == SHOW_ACTIVE_SKINS:
            skins = allLicensedSkins
        elif show == SHOW_INACTIVE_SKINS:
            skins = filter(lambda s: not s.licensed, skins)
        numLicensedSkinsForShip = 0
        for skin in allLicensedSkins:
            numLicensedSkinsForShip += len(skin.types)

        return (bucket(skins, keyprojection=lambda s: s.materialID), numLicensedSkinsForShip)

    def _CreateSkinObject(self, staticSkin, licensedSkin = None):
        material = sm.GetService('cosmeticsSvc').static.GetMaterialByID(staticSkin.skinMaterialID)
        licensed = licensedSkin is not None
        expires = licensedSkin.expires if licensedSkin else None
        isSingleUse = licensedSkin.isSingleUse if licensedSkin else None
        return FirstPartySkin(material, skin=staticSkin, licensed=licensed, expires=expires, isSingleUse=isSingleUse)

    def _CreateGroupEntryForMaterials(self, materialName, skins, texturePaths):
        skinsByShipID = GroupAndFilterByShip(skins, self.filterText)
        if not skinsByShipID:
            return
        skinsByShipID.pop(typeCapsuleGolden, None)
        textureToUse = None
        if texturePaths:
            textureToUse, _ = Counter(texturePaths).most_common()[0]
        owned = count((ship for ship, skins in skinsByShipID.iteritems() if any((s.licensed for s in skins))))
        return GetFromClass(ListGroup, {'label': localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/SkinsGroupWithCount', groupName=materialName, skinsOwned=owned, skinsTotal=len(skinsByShipID)),
         'id': ('SkinMaterials', materialName),
         'showicon': textureToUse,
         'groupItems': skinsByShipID,
         'GetSubContent': self._GetSkinsSubContent,
         'showlen': False,
         'BlockOpenWindow': True,
         'state': 'locked',
         'DropData': self.OnDropData})

    def _GetSkinsSubContent(self, nodedata, *args):
        skinsByShipID = nodedata.groupItems
        nodes = []
        for shipTypeID, skins in skinsByShipID.iteritems():
            data = GetDataForSkinEntry(shipTypeID, skins)
            data['OnDropData'] = self.OnDropData
            entry = GetFromClass(ShipSkinEntry, data)
            nodes.append(entry)

        nodes = sorted(nodes, key=lambda x: x.label)
        return nodes

    def GetSettingsMenu(self, menuParent):
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/ShowAllSkins'), checked=GetSetting(SETTING_SHOW_SKINS) == SHOW_ALL_SKINS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_SKINS, SHOW_ALL_SKINS))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/ShowActiveSkins'), checked=GetSetting(SETTING_SHOW_SKINS) == SHOW_ACTIVE_SKINS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_SKINS, SHOW_ACTIVE_SKINS))
        menuParent.AddRadioButton(text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/ShowInactiveSkins'), checked=GetSetting(SETTING_SHOW_SKINS) == SHOW_INACTIVE_SKINS, callback=partial(self.SetSettingAndReload, SETTING_SHOW_SKINS, SHOW_INACTIVE_SKINS))

    def SetSettingAndReload(self, key, value):
        SetSetting(key, value)
        self.LoadPanel()

    def OnSkinLicenseActivated(self, skinID, licenseeID):
        if self.display:
            self.LoadPanel()

    def OnSkinLicenseRemoved(self, skinID, itemID, typeID):
        if self.display:
            self.LoadPanel()

    def OnDropData(self, dragObj, nodes):
        sessionChecker = SessionChecker(session, sm)
        itemAndTypeIDs = []
        for eachNode in nodes:
            if eachNode.__guid__ not in ('xtriui.InvItem', 'listentry.InvItem', 'listentry.InvAssetItem'):
                continue
            rec = eachNode.rec
            item = ItemChecker(rec, sessionChecker)
            if item.OfferActivateShipSkinLicense():
                itemAndTypeIDs.append((rec.itemID, rec.typeID))

        if itemAndTypeIDs:
            menuFunctions.ActivateShipSkinLicense(itemAndTypeIDs)


class ShipSkinEntry(Item):

    def Startup(self, *args):
        super(ShipSkinEntry, self).Startup(*args)
        self.previewIcon = ButtonIcon(name='previewIcon', parent=self, align=uiconst.CENTERRIGHT, texturePath='res:/UI/Texture/classes/skins/preview.png', func=self.PreviewSkin)

    def Load(self, node):
        super(ShipSkinEntry, self).Load(node)
        self.sr.infoicon.display = False
        if node.skin.licensed:
            self.sr.label.opacity = 1
        else:
            self.sr.label.opacity = 0.5
            self.sr.icon.opacity = 0.5
        if node.skin.licensed:
            grid = LayoutGrid(parent=self, align=uiconst.CENTERRIGHT, columns=2, left=26)
            EveLabelMedium(parent=grid, text=localization.GetByLabel('UI/CharacterSheet/CharacterSheetWindow/Skins/Active'))
            SkinDurationLabel(parent=grid, skin=node.skin)

    def PreviewSkin(self):
        node = self.sr.node
        materialID = node.skin.materialID
        licenses = sm.GetService('cosmeticsSvc').GetLicencesForTypeWithMaterial(node.typeID, materialID)
        if licenses:
            typeID = licenses[0]
            shipTypeID = node.typeID
            sm.GetService('preview').PreviewType(typeID, otherTypeID=shipTypeID)


def GetSetting(key):
    return settings.user.ui.Get(key, SETTING_DEFAULTS[key])


def SetSetting(key, value):
    settings.user.ui.Set(key, value)
