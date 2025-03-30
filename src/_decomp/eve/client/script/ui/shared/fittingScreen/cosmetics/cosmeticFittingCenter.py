#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\cosmetics\cosmeticFittingCenter.py
from collections import defaultdict
from carbonui.uianimations import animations
import uthread2
from cosmetics.common.ships.skins.static_data.skin_type import ShipSkinType
from shipcosmetics.common.const import CosmeticsType
from eve.client.script.ui.shared.fitting.slotAdder import SlotAdder
from shipcosmetics.client.fittingsgateway.fittingsSignals import on_ship_cosmetics_changed
from carbonui.primitives.container import Container
from eve.client.script.ui.shared.fitting.cosmeticFittingController import CosmeticFittingController
from eve.client.script.ui.shared.fitting.fittingUtil import GetScaleFactor
from eve.client.script.ui.shared.fittingScreen.cosmetics.cosmeticFittingLayout import CosmeticFittingLayout
from eve.client.script.ui.shared.fittingScreen.cosmetics.cosmeticsSlot import CosmeticAllianceLogoSlot, CosmeticCorporationLogoSlot, CosmeticSkinSlot, CosmeticBlankSlot
from eve.client.script.ui.shared.fittingScreen.fittingCenter import ShipSceneParent
from carbonui import uiconst
from eve.client.script.ui.shared.skins.skinUISignals import on_skin_selected
LOGO_SIZE = 64

class CosmeticFittingCenter(CosmeticFittingLayout):
    __notifyevents__ = ['OnDogmaItemChange',
     'ProcessActiveShipChanged',
     'OnSessionChanged',
     'OnCorporationChanged',
     'OnCorpLogoReady',
     'OnAllianceLogoReady']
    default_name = 'CosmeticFittingCenter'
    default_align = uiconst.CENTER
    default_state = uiconst.UI_NORMAL
    default_top = -20
    cosmeticsFittingController = None

    def ApplyAttributes(self, attributes):
        super(CosmeticFittingCenter, self).ApplyAttributes(attributes)
        self.cosmeticsFittingController = attributes.controller
        self.slots = defaultdict(list)
        self.ConstructSlots()
        sm.RegisterNotify(self)
        on_skin_selected.connect(self.OnSkinEntrySelected)
        on_ship_cosmetics_changed.connect(self.OnShipCosmeticsChanged)
        self.ConstructSceneContainer()
        self._entryAnimThread = uthread2.start_tasklet(self.EntryAnimation)
        self._setupSkinSlotThread = uthread2.start_tasklet(self.SetupSkinSlot)

    def Close(self):
        sm.UnregisterNotify(self)
        on_skin_selected.disconnect(self.OnSkinEntrySelected)
        on_ship_cosmetics_changed.disconnect(self.OnShipCosmeticsChanged)
        if hasattr(self, '_entryAnimThread') and self._entryAnimThread:
            self._entryAnimThread.Kill()
        if hasattr(self, '_setupSkinSlotThread') and self._setupSkinSlotThread:
            self._setupSkinSlotThread.Kill()
        super(CosmeticFittingCenter, self).Close()

    def ConstructSlots(self):
        slotCont = Container(parent=self, name='slotCont', align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN, idx=0)
        slotAdder = SlotAdder(self.cosmeticsFittingController, CosmeticBlankSlot)
        slotAdder.rad = int(245 * GetScaleFactor())
        slotAdder.center = self.width / 2
        for groupID, cosmeticTypes in self.cosmeticsFittingController.SLOT_GROUPS.iteritems():
            arcStart, arcLength = self.cosmeticsFittingController.SLOT_GROUP_LAYOUT_ARCS[groupID]
            slotAdder.StartGroup(arcStart, arcLength, len(cosmeticTypes))
            slotClass = CosmeticBlankSlot
            for cosmeticType in cosmeticTypes:
                if cosmeticType == CosmeticsType.ALLIANCE_LOGO:
                    slotClass = CosmeticAllianceLogoSlot
                elif cosmeticType == CosmeticsType.CORPORATION_LOGO:
                    slotClass = CosmeticCorporationLogoSlot
                elif cosmeticType == CosmeticsType.SKIN:
                    slotClass = CosmeticSkinSlot
                slot = slotAdder.AddSlot(slotCont, cosmeticType, slotClass)
                self.slots[cosmeticType].append(slot)

        self.UpdateLogoSlots()

    def ConstructSceneContainer(self):
        size = self.width * GetScaleFactor()
        self.shipSceneContainer = ShipSceneParent(parent=self, align=uiconst.CENTER, width=size, height=size, controller=self.cosmeticsFittingController, stencilMask='res:/UI/Texture/classes/Fitting/fittingCircleStencil.png')

    def EntryAnimation(self):
        for i, slots in self.slots.iteritems():
            for slot in slots:
                if slot.state == uiconst.UI_DISABLED:
                    endOpacity = 0.05
                else:
                    endOpacity = 1.0
                animations.FadeTo(slot, 0.0, endOpacity, duration=0.3, timeOffset=0.2 * i / 1.7)

    def OnSkinEntrySelected(self, skin):
        texturePath = skin.iconTexturePath if skin else None
        self.slots[CosmeticsType.SKIN][0].SetupSlot(texturePath)

    def SetupSkinSlot(self):
        self.slots[CosmeticsType.SKIN][0].SetupSlot(self.cosmeticsFittingController.texturePath)

    def OnShipCosmeticsChanged(self, _ship_id, _cosmetics_types):
        self.UpdateLogoSlots()

    def ProcessActiveShipChanged(self, _shipID, _oldShipID):
        self.UpdateAllSlots()

    def OnSessionChanged(self, _isremote, _session, change):
        if 'corpid' or 'allianceid' in change:
            self.UpdateAllSlots()

    def OnCorporationChanged(self, _corpID, _change):
        self.UpdateAllSlots()

    def OnCorpLogoReady(self, corpID, size):
        if corpID == session.corpid and size == LOGO_SIZE:
            selectedCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
            if CosmeticsType.CORPORATION_LOGO in selectedCosmetics:
                texturePath = sm.GetService('photo').GetCorporationLogo(session.corpid, size=LOGO_SIZE)
                self.slots[CosmeticsType.CORPORATION_LOGO][0].SetupSlot(texturePath)

    def OnAllianceLogoReady(self, allianceID, size):
        if allianceID == session.allianceid and size == LOGO_SIZE:
            selectedCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
            if CosmeticsType.ALLIANCE_LOGO in selectedCosmetics:
                texturePath = sm.GetService('photo').GetAllianceLogo(session.allianceid, size=LOGO_SIZE)
                self.slots[CosmeticsType.ALLIANCE_LOGO][0].SetupSlot(texturePath)

    def UpdateAllSlots(self):
        self.UpdateLogoSlots()
        self.SetupSkinSlot()

    def UpdateLogoSlots(self):
        selectedCosmetics = sm.GetService('cosmeticsSvc').get_enabled_ship_cosmetics(session.shipid)
        if CosmeticsType.ALLIANCE_LOGO in selectedCosmetics:
            texturePath = sm.GetService('photo').GetAllianceLogo(session.allianceid, size=LOGO_SIZE, callback=True)
            self.slots[CosmeticsType.ALLIANCE_LOGO][0].SetupSlot(texturePath)
        else:
            self.slots[CosmeticsType.ALLIANCE_LOGO][0].SetupSlot(None)
        if CosmeticsType.CORPORATION_LOGO in selectedCosmetics:
            texturePath = sm.GetService('photo').GetCorporationLogo(session.corpid, size=LOGO_SIZE, callback=True)
            self.slots[CosmeticsType.CORPORATION_LOGO][0].SetupSlot(texturePath)
        else:
            self.slots[CosmeticsType.CORPORATION_LOGO][0].SetupSlot(None)
