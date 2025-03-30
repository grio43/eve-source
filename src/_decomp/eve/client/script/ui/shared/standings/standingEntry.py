#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\standings\standingEntry.py
import math
import localization
import evetypes
import inventorycommon.const as invconst
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import const as uiconst
from carbonui.control.scrollentries import SE_BaseClassCore
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from eve.client.script.ui.control import eveIcon, eveLabel
from eve.client.script.ui.shared.standings.standingsBonusTooltip import StandingBonusTooltip
POSITIVE_CHANGE_ICON = 'res:/UI/Texture/classes/Standings/positiveStandingChange.png'
NEGATIVE_CHANGE_ICON = 'res:/UI/Texture/classes/Standings/negativeStandingChange.png'

class StandingEntry(SE_BaseClassCore):
    __guid__ = 'listentry.StandingEntry'
    __notifyevents__ = ['OnStandingNotificationClicked', 'OnNPCStandingChange']

    def ApplyAttributes(self, attributes):
        SE_BaseClassCore.ApplyAttributes(self, attributes)
        self.standingSvc = sm.GetService('standing')
        self.isRead = True
        self.ConstructLayout()
        sm.RegisterNotify(self)

    def ConstructLayout(self):
        self.label = eveLabel.EveLabelMedium(name='ownerNameLabel', text='', parent=self, left=36, top=0, state=uiconst.UI_DISABLED, opacity=1.0, maxLines=1, align=uiconst.CENTERLEFT)
        iconCont = ContainerAutoSize(name='IconContainer', parent=self, align=uiconst.TORIGHT, left=5)
        unreadIconCont = ContainerAutoSize(name='unreadIconCont', parent=iconCont, align=uiconst.TORIGHT, left=5)
        self.unreadIcon = Sprite(name='unreadIcon', parent=unreadIconCont, align=uiconst.CENTER, width=8, height=8, rotation=math.pi, hint=localization.GetByLabel('UI/Standings/Common/UnreadStandingsHint'), state=uiconst.UI_DISABLED, opacity=0)
        self.unreadIcon.OnClick = self.OnClick
        self.ownerIconContainer = Container(name='iconParent', parent=self, left=1, top=0, width=32, height=32, align=uiconst.TOPLEFT, state=uiconst.UI_PICKCHILDREN)

    def Load(self, node):
        self.sr.node = node
        self.standingData = node.standingData
        self.tooltipPanelClassInfo = StandingBonusTooltip(self.standingData)
        self.MarkUnreadEntries()
        text = "%s <color='0x88ffffff'>%s</color>" % (self.standingData.GetStanding2To1Formatted(), self.standingData.GetOwner2Name())
        self.label.text = text
        self.UpdateIcon(node)
        if node.selected:
            self.Select()
        else:
            self.Deselect()

    def UpdateIcon(self, node):
        standingData = node.standingData
        typeID = standingData.GetOwner2TypeID()
        groupID = evetypes.GetGroupID(typeID)
        ownerID = standingData.GetOwnerID2()
        self.ownerIconContainer.Flush()
        iconParams = {'parent': self.ownerIconContainer,
         'align': uiconst.TOALL,
         'state': uiconst.UI_DISABLED,
         'idx': 0}
        if groupID in (invconst.groupCorporation, invconst.groupFaction, invconst.groupAlliance):
            eveIcon.GetLogoIcon(itemID=ownerID, **iconParams)
        elif groupID == invconst.groupCharacter:
            logo = eveIcon.Icon(icon=None, **iconParams)
            sm.GetService('photo').GetPortrait(ownerID, 64, logo)

    def OnDblClick(self, *args):
        self.ShowInfo()

    def OnClick(self, *args):
        SE_BaseClassCore.OnClick(self)
        PlaySound(uiconst.SOUND_ENTRY_SELECT)
        self.sr.node.scroll.SelectNode(self.sr.node)
        self.SetAsRead()
        if self.sr.node.Get('OnClick', None):
            self.sr.node.OnClick(self)

    def ShowInfo(self, node = None, *args):
        standingData = self.standingData
        typeID = standingData.GetOwner2TypeID()
        ownerID = standingData.GetOwnerID2()
        sm.GetService('info').ShowInfo(typeID, ownerID)

    def GetMenu(self):
        standingData = self.standingData
        return sm.GetService('menu').GetMenuForOwner(standingData.GetOwnerID2())

    def GetHeight(self, *args):
        node, width = args
        node.height = 32
        return node.height

    def SetAsUnread(self, isPositive):
        self.isRead = False
        iconPath = POSITIVE_CHANGE_ICON if isPositive else NEGATIVE_CHANGE_ICON
        self.unreadIcon.SetTexturePath(iconPath)
        self.ShowHilite(animate=True)
        animations.FadeTo(self.unreadIcon, startVal=0, duration=1.0, curveType=uiconst.ANIM_OVERSHOT3, callback=lambda : self.unreadIcon.SetState(uiconst.UI_NORMAL))

    def SetAsRead(self):
        self.isRead = True
        self.standingSvc.RemoveFromUnreadEntries(self.standingData.GetOwnerID2())
        self.unreadIcon.SetTexturePath(None)
        self.HideHilite(animate=True)
        animations.FadeOut(self.unreadIcon, callback=self.unreadIcon.SetState(uiconst.UI_DISABLED))

    def OnStandingNotificationClicked(self, entryToOpen):
        self.MarkUnreadEntries()

    def OnNPCStandingChange(self, fromID, newStanding, oldStanding):
        self.MarkUnreadEntries()

    def MarkUnreadEntries(self):
        unreadEntries = self.standingSvc.GetUnreadEntries()
        if self.standingData.GetOwnerID2() in unreadEntries:
            self.SetAsUnread(unreadEntries[self.standingData.GetOwnerID2()] > 0)

    def OnMouseExit(self, *args):
        if not self.unreadIcon.texturePath:
            super(StandingEntry, self).OnMouseExit(*args)
