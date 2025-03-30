#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\station\loyaltyPointStore\lpStoreWindow.py
from carbonui import uiconst
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.control.tabGroup import TabGroup
from carbonui.primitives.sprite import Sprite
from cosmetics.common.cosmeticsConst import IsEmblemProviderCorp
from eve.client.script.ui.station.loyaltyPointStore.lpStoreConst import FACTION_BACKGROUNDS
from eve.client.script.ui.station.loyaltyPointStore.lpStoreFiltersWindow import LPStoreFiltersWindow
from eve.client.script.ui.station.loyaltyPointStore.lpStorePanel import LPStorePanel
from eve.client.script.ui.station.loyaltyPointStore.paragonLpStorePanel import ParagonLPStorePanel
from eve.common.lib.appConst import corpHeraldry
from npcs.npccorporations import get_corporation_faction_id

class LPStoreWindow(Window):
    __guid__ = 'form.LPStore'
    default_windowID = 'lpstore'
    default_width = 837
    default_height = 580
    default_captionLabelPath = 'Tooltips/StationServices/LPStore'
    default_descriptionLabelPath = 'Tooltips/StationServices/LPStore_description'
    default_iconNum = 'res:/ui/Texture/WindowIcons/lpstore.png'

    def ApplyAttributes(self, attributes):
        super(LPStoreWindow, self).ApplyAttributes(attributes)
        self.corpIDs = attributes.corpIDs
        self.ConstructLayout()
        self.ConstructTabs()
        self.SetMinSize((self.default_width, 430))

    def SetFactionFlavour(self, factionID):
        if factionID in FACTION_BACKGROUNDS:
            self.factionFlavourSprite.SetTexturePath(FACTION_BACKGROUNDS[factionID])
            self.factionFlavourSprite.Show()
        else:
            self.factionFlavourSprite.Hide()

    def ConstructLayout(self):
        self.factionFlavourSprite = Sprite(parent=self.sr.underlay, align=uiconst.TOPLEFT, width=825, height=832, texturePath='')

    def ConstructTabs(self):
        self.panels = []
        if not self.corpIDs:
            return
        tabParent = Container(name='tabParent', parent=self.sr.main, align=uiconst.TOALL)
        self.tabGroups = TabGroup(name='tabparent', parent=tabParent, idx=0, groupID='lpStoreTab', callback=self._OnTabChanged)
        for corpID in self.corpIDs:
            if not IsEmblemProviderCorp(corpID):
                panel = LPStorePanel(corpID=corpID, parent=tabParent, lpStoreWindow=self)
            else:
                panel = ParagonLPStorePanel(corpID=corpID, parent=tabParent, lpStoreWindow=self, errorScreenPadding=self.sr.main.padding)
            self.panels.append(panel)
            corpName = cfg.eveowners.Get(corpID).ownerName
            self.tabGroups.AddTab(corpName, panel, tabParent)

        self.tabGroups.AutoSelect()

    def RefreshIfNotAlready(self):
        for t in self.panels:
            t.RefreshIfNotAlready()

    def RefreshOffers(self):
        for t in self.panels:
            t.RefreshOffers()

    def Refresh(self):
        for t in self.panels:
            t.Refresh()

    def _OnTabChanged(self, newTab, oldTab):
        panel = self.tabGroups.GetSelectedPanel()
        if panel and panel.corpID == corpHeraldry:
            self.factionFlavourSprite.Hide()
            LPStoreFiltersWindow.CloseIfOpen()
        else:
            self.SetFactionFlavour(get_corporation_faction_id(panel.corpID))
