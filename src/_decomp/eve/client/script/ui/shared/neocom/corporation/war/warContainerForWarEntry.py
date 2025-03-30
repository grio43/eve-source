#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\corporation\war\warContainerForWarEntry.py
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.common.lib import appConst as const
from eve.common.script.sys import idCheckers
from evewar.warText import GetWarText
from localization import GetByLabel

class WarContainer(Container):
    __notifyevents__ = []
    default_height = 36
    default_align = uiconst.TOTOP

    def __init__(self, **kwargs):
        self.textCont = None
        self.corpLabels = None
        self.dateLabel = None
        self.attackerID = None
        self.attackerLogo = self.attackerlogoCont = None
        self.defenderLogo = self.defenderlogoCont = None
        super(WarContainer, self).__init__(**kwargs)

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.ConstructLayout()
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.attackerlogoCont = Container(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=32, padding=2)
        swordCont = Container(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=24, padding=2)
        swordLogo = Sprite(name='warIcon', parent=swordCont, align=uiconst.CENTER, pos=(0, 0, 32, 32), state=uiconst.UI_NORMAL, opacity=0.3, texturePath='res:/UI/Texture/WindowIcons/wars.png', hint=GetByLabel('UI/Corporations/Wars/Vs'))
        self.defenderlogoCont = Container(parent=self, align=uiconst.TOLEFT, state=uiconst.UI_PICKCHILDREN, width=32, padding=2)
        self.textCont = Container(parent=self, align=uiconst.TOALL, state=uiconst.UI_PICKCHILDREN)
        self.corpLabels = EveLabelMedium(text='', parent=self.textCont, left=5, top=2, state=uiconst.UI_NORMAL, maxLines=1)
        self.dateLabel = EveLabelMedium(text='', parent=self.textCont, left=5, top=17, state=uiconst.UI_DISABLED, maxLines=1, autoFadeSides=35)

    def LoadWarInfo(self, war):
        if self.attackerLogo:
            self.attackerLogo.Close()
        if self.defenderLogo:
            self.defenderLogo.Close()
        if self.corpLabels:
            self.corpLabels.text = ''
        if self.dateLabel:
            self.dateLabel.text = ''
        attackerID = war.declaredByID
        self.attackerID = attackerID
        attackerName = cfg.eveowners.Get(war.declaredByID).name
        if idCheckers.IsCorporation(attackerID):
            attackerLinkType = const.typeCorporation
        elif idCheckers.IsAlliance(attackerID):
            attackerLinkType = const.typeAlliance
        else:
            attackerLinkType = const.typeFaction
        defenderID = war.againstID
        defenderName = cfg.eveowners.Get(war.againstID).name
        if idCheckers.IsCorporation(defenderID):
            defenderLinkType = const.typeCorporation
        elif idCheckers.IsAlliance(defenderID):
            defenderLinkType = const.typeAlliance
        else:
            defenderLinkType = const.typeFaction
        timeText = GetWarText(war)
        warMutual = war.mutual
        if warMutual:
            locText = 'UI/Corporations/Wars/WarMutual'
        else:
            locText = 'UI/Corporations/Wars/WarNotMutual'
        self.corpLabels.text = GetByLabel(locText, attackerName=attackerName, attackerInfo=('showinfo', attackerLinkType, attackerID), defenderName=defenderName, defenderInfo=('showinfo', defenderLinkType, defenderID))
        self.dateLabel.text = timeText
        self.attackerLogo = GetLogoIcon(itemID=attackerID, parent=self.attackerlogoCont, acceptNone=False, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.attackerLogo.SetSize(32, 32)
        self.attackerLogo.OnClick = (self.ShowInfo, attackerID, attackerLinkType)
        self.attackerLogo.hint = '%s<br>%s' % (cfg.eveowners.Get(attackerID).name, GetByLabel('UI/Corporations/Wars/Offender'))
        self.defenderLogo = GetLogoIcon(itemID=defenderID, parent=self.defenderlogoCont, acceptNone=False, align=uiconst.TOLEFT, state=uiconst.UI_NORMAL)
        self.defenderLogo.SetSize(32, 32)
        self.defenderLogo.OnClick = (self.ShowInfo, defenderID, defenderLinkType)
        self.defenderLogo.hint = '%s<br>%s' % (cfg.eveowners.Get(defenderID).name, GetByLabel('UI/Corporations/Wars/Defender'))

    @staticmethod
    def ShowInfo(itemID, typeID):
        sm.GetService('info').ShowInfo(typeID, itemID)
