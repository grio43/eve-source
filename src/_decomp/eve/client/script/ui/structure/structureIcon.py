#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\structure\structureIcon.py
from eve.client.script.ui.control.itemIcon import ItemIcon
from carbonui.control.buttonIcon import ButtonIcon
import carbonui.const as uiconst
from eve.client.script.ui.shared.info.infoConst import TAB_WARHQ
from localization import GetByLabel
IS_AT_WAR_HQ_TEXTURE_PATH = 'res:/UI/Texture/WindowIcons/wars.png'
MAX_DISPLAYED = 5

class StructureIcon(ItemIcon):

    def __init__(self, *args, **kwargs):
        self.warSprite = None
        self.wars = None
        super(StructureIcon, self).__init__(*args, **kwargs)

    def ApplyAttributes(self, attributes):
        ItemIcon.ApplyAttributes(self, attributes)
        structureTypeID = attributes.typeID
        structureID = attributes.structureID
        self.wars = attributes.get('wars')
        if self.wars:
            self.warButton = ButtonIcon(parent=self, name='warsOverlay', state=uiconst.UI_NORMAL, align=uiconst.TOPRIGHT, texturePath=IS_AT_WAR_HQ_TEXTURE_PATH, pos=(-4, -4, 24, 24), iconColor=(0.6, 0.145, 0.12, 1.0), iconEnabledOpacity=3.0, idx=0, func=self.OpenWars, args=(structureID, structureTypeID))
            self.warButton.icon.gradientStrength = 1.0
            self.warButton.LoadTooltipPanel = self._LoadWarHQTooltip

    def OpenWars(self, structureID, structureTypeID, *args):
        sm.GetService('info').ShowInfo(structureTypeID, structureID, selectTabType=TAB_WARHQ)

    def _LoadWarHQTooltip(self, tooltipPanel, *args):
        allWars = sm.RemoteSvc('warsInfoMgr').GetPublicWarInfo(self.wars)
        if not allWars:
            return
        tooltipPanel.LoadGeneric1ColumnTemplate()
        tooltipPanel.cellSpacing = (10, 4)
        ownersToPrime = set()
        for war in allWars:
            ownersToPrime.add(war.againstID)
            ownersToPrime.add(war.declaredByID)

        cfg.eveowners.Prime(ownersToPrime)
        tooltipPanel.AddLabelMedium(text=GetByLabel('UI/InfoWindow/WarHQHeader'), colSpan=tooltipPanel.columns, bold=True)
        for war in allWars[:MAX_DISPLAYED]:
            aggressor = cfg.eveowners.Get(war.declaredByID)
            defender = cfg.eveowners.Get(war.againstID)
            text = '%s  %s  %s' % (aggressor.ownerName, GetByLabel('UI/Corporations/Wars/Vs'), defender.ownerName)
            tooltipPanel.AddLabelMedium(text=text)

        more = len(allWars) - MAX_DISPLAYED
        if more > 0:
            t = GetByLabel('UI/Corporations/CorporationWindow/Wars/AndMoreWars', numMore=more)
            tooltipPanel.AddLabelMedium(text=t)
