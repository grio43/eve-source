#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\shipTree\shipTreeUnlockContainer.py
import eveicon
import trinity
from carbon.client.script.environment.AudioUtil import PlaySound
from carbonui import uiconst, Align, TextHeader
from carbonui.control.button import Button
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.line import Line
from carbonui.primitives.sprite import Sprite
from carbonui.services.setting import CharSettingBool
from carbonui.uianimations import animations
from characterdata.factions import get_faction_name
from eve.client.script.ui import eveThemeColor, eveColor
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from eve.client.script.ui.shared.shipTree.shipTreeConst import ICON_BY_FACTIONID
from localization import GetByMessageID
from shipprogression import shipUnlockSignals
from shipprogression.shipUnlockSvc import GetShipUnlockService
from eve.common.script.sys.eveCfg import eveConfig
import localization
UNLOCK_HEADER_PADDING = 24
UNLOCK_HEADER_HEIGHT = 30
REWARD_ENTRY_PADDING = 8
SCROLL_CONTAINER_PADDING = 24

class ShipTreeUnlockContainer(Container):
    default_state = uiconst.UI_NORMAL
    default_name = 'ShipTreeUnlockContainer'
    default_color = (0, 0, 0, 0.9)

    def ApplyAttributes(self, attributes):
        super(ShipTreeUnlockContainer, self).ApplyAttributes(attributes)
        self._callback = attributes.get('callback', None)
        self._shipUnlockSvc = GetShipUnlockService()
        self._expanded = False
        self._ignore_setting = CharSettingBool('ShipProgression_Ignore', False)
        self._ConstructHeader()
        self._ConstructMainContainer()
        self._ConstructFrame()
        self._ConstructInitialContent()
        self.RegisterListeners()

    def Close(self):
        super(ShipTreeUnlockContainer, self).Close()
        self.UnregisterListeners()

    def RegisterListeners(self):
        shipUnlockSignals.on_group_unlocked.connect(self._on_group_unlocked)
        shipUnlockSignals.on_group_unlock_viewed.connect(self._on_group_viewed)
        shipUnlockSignals.on_unlocks_dismissed.connect(self._on_unlocks_dismissed)

    def UnregisterListeners(self):
        shipUnlockSignals.on_group_unlocked.disconnect(self._on_group_unlocked)
        shipUnlockSignals.on_group_unlock_viewed.disconnect(self._on_group_viewed)
        shipUnlockSignals.on_unlocks_dismissed.disconnect(self._on_unlocks_dismissed)

    def _ConstructLine(self):
        Line(parent=self, align=uiconst.TOTOP, outputMode=trinity.Tr2SpriteTarget.COLOR_AND_GLOW, color=eveThemeColor.THEME_ACCENT)

    def _ConstructHeader(self):
        self._ConstructLine()
        self.headerContainer = Container(name='headerContainer', parent=self, align=uiconst.TOTOP, padding=(UNLOCK_HEADER_PADDING,
         UNLOCK_HEADER_PADDING,
         UNLOCK_HEADER_PADDING,
         UNLOCK_HEADER_PADDING), height=UNLOCK_HEADER_HEIGHT, contentSpacing=(8, 0))
        self.titleLabel = EveCaptionLarge(parent=ContainerAutoSize(parent=self.headerContainer, align=uiconst.TOLEFT), name='headerLabel', align=Align.TOLEFT, state=uiconst.UI_DISABLED, text=localization.GetByLabel('UI/ShipTree/NewUnlocks'))
        self.claimAllBtn = Button(parent=self.headerContainer, label=localization.GetByLabel('UI/ShipTree/DismissAllUnlocks'), align=Align.TORIGHT, func=self._dismiss_all)

    def _ConstructMainContainer(self):
        self.mainCont = Container(name='mainContainer', parent=self, align=uiconst.TOALL, padding=(SCROLL_CONTAINER_PADDING,
         0,
         10,
         SCROLL_CONTAINER_PADDING))
        self.rewardsScroll = ScrollContainer(name='unlockScroll', parent=self.mainCont, align=uiconst.TOALL, padding=(0, 0, 12, 0))

    def _ConstructInitialContent(self):
        unlocks = self._shipUnlockSvc.GetUnseenEntries()
        if len(unlocks) == 0:
            self.display = False
            return
        for entry in unlocks:
            self._add_unlock_entry(entry)

        self.FadeIn()

    def _add_unlock_entry(self, shipUnlockEntry):
        ShipTreeUnlockEntry(name='unlock_entry', align=Align.TOTOP, parent=self.rewardsScroll, opacity=0.8, height=58, unlockEntry=shipUnlockEntry, callback=self._callback)

    def _ConstructFrame(self):
        Frame(bgParent=self, texturePath='res:/UI/Texture/Shared/DarkStyle/panel1Corner_Solid.png', cornerSize=9, color=eveColor.BLACK, opacity=0.9)

    def _on_group_unlocked(self, shipUnlockEntry):
        if self._ignore_setting.is_enabled():
            return
        self.display = True
        self._add_unlock_entry(shipUnlockEntry)
        if self.opacity < 1:
            animations.StopAllAnimations(self)
            self.FadeIn()

    def _on_group_viewed(self, shipUnlockEntry):
        if len(self._shipUnlockSvc.GetUnseenEntries()) == 0:
            self.FadeOut()

    def _on_unlocks_dismissed(self):
        self.FadeOut(callback=self._on_dismiss_fade_complete)

    def _on_dismiss_fade_complete(self):
        for child in self.rewardsScroll.mainCont.children:
            child.display = False

        self.display = False

    def _dismiss_all(self, *args, **kwargs):
        self._shipUnlockSvc.DismissAll()

    def FadeOut(self, callback = None):
        if callback is None:
            callback = self._FadeOutComplete
        animations.FadeOut(self, duration=0.4, callback=callback)

    def _FadeOutComplete(self):
        self.display = False

    def FadeIn(self, callback = None):
        animations.FadeIn(self, duration=0.4, callback=callback)


class ShipTreeUnlockEntry(Container):
    default_state = uiconst.UI_NORMAL
    FRAME_COLOR_DISABLED = tuple(eveColor.FOCUS_BLUE[:3]) + (0.2,)
    FRAME_GLOW_DISABLED = tuple(eveColor.FOCUS_BLUE[:3]) + (0.0,)
    FRAME_COLOR_ENABLED = tuple(eveColor.FOCUS_BLUE[:3]) + (0.5,)
    PIP_COLOR_DISABLED = tuple(eveColor.FOCUS_BLUE[:3]) + (0.0,)
    PIP_COLOR_ENABLED = eveColor.FOCUS_BLUE

    def ApplyAttributes(self, attributes):
        super(ShipTreeUnlockEntry, self).ApplyAttributes(attributes)
        self.unlockEntry = attributes.unlockEntry
        self.original_bgColor = attributes.bgColor
        self.callback = attributes.callback
        self.ConstructLayout()
        shipUnlockSignals.on_group_unlock_viewed.connect(self._on_unlock_viewed)

    def Close(self):
        shipUnlockSignals.on_group_unlock_viewed.disconnect(self._on_unlock_viewed)

    def _on_unlock_viewed(self, unlockEntry):
        if self.unlockEntry.shipGroupID == unlockEntry.shipGroupID:
            self._fade_out()

    def ConstructLayout(self):
        self.padCnt = Container(parent=self, align=Align.TOALL, padBottom=10)
        Button(parent=self.padCnt, align=Align.CENTERRIGHT, label=localization.GetByLabel('UI/Common/View'), padRight=8, func=self.OnClick)
        self.content = ContainerAutoSize(parent=self.padCnt, align=Align.CENTERLEFT, padLeft=15, height=20)
        self.factionIconCnt = Container(parent=self.content, align=Align.TOLEFT, width=24)
        self.factionIcon = Sprite(parent=self.factionIconCnt, align=Align.CENTERLEFT, height=24, width=24, texturePath=ICON_BY_FACTIONID.get(self.unlockEntry.FactionID), hint=get_faction_name(self.unlockEntry.FactionID))
        self.groupIconCnt = Container(parent=self.content, align=Align.TOLEFT, width=24, padLeft=8)
        self.groupIcon = Sprite(parent=self.groupIconCnt, align=Align.CENTERLEFT, height=24, width=24, texturePath=eveConfig.infoBubbleGroups[self.unlockEntry.GroupID]['icon'])
        self.groupName = TextHeader(parent=self.content, align=Align.TOLEFT, text=GetByMessageID(eveConfig.infoBubbleGroups[self.unlockEntry.GroupID]['nameID']), padLeft=5)
        frame_texture = 'res:/UI/Texture/classes/ShipProgression/Border.png'
        pip_texture = 'res:/UI/Texture/classes/ShipProgression/Detail.png'
        fill_texture = 'res:/UI/Texture/classes/ShipProgression/Fill.png'
        self._frame_glow = Frame(parent=self.padCnt, align=uiconst.TOALL, texturePath=frame_texture, cornerSize=9, color=self.FRAME_GLOW_DISABLED, outputMode=trinity.Tr2SpriteTarget.GLOW)
        self._pip_glow = Frame(parent=self.padCnt, align=uiconst.TOALL, texturePath=pip_texture, cornerSize=9, color=self.PIP_COLOR_DISABLED, outputMode=trinity.Tr2SpriteTarget.GLOW)
        self._frame = Frame(parent=self.padCnt, align=uiconst.TOALL, texturePath=frame_texture, cornerSize=9, color=self.FRAME_COLOR_DISABLED)
        self._pip = Frame(parent=self.padCnt, align=uiconst.TOALL, texturePath=pip_texture, cornerSize=9, color=self.PIP_COLOR_DISABLED)
        self._background = Frame(parent=self.padCnt, align=uiconst.TOALL, texturePath=fill_texture, cornerSize=9, color=(0.1, 0.1, 0.2, 0.6), outputMode=trinity.Tr2SpriteTarget.COLOR_AND_GLOW, glowBrightness=0.3)

    def OnClick(self, *args, **kwds):
        GetShipUnlockService().MarkAsSeen(self.unlockEntry)
        sm.GetService('shipTreeUI').ShowUnlockFanfare(self.unlockEntry.FactionID, self.unlockEntry.GroupID)
        PlaySound('ship_goals_reveal_button_ship_play')

    def OnMouseEnter(self, *args):
        super(ShipTreeUnlockEntry, self).OnMouseEnter(*args)
        duration = 0.1
        animations.StopAllAnimations(self._pip_glow)
        animations.StopAllAnimations(self._frame_glow)
        animations.StopAllAnimations(self._pip)
        animations.StopAllAnimations(self._frame)
        animations.SpColorMorphTo(self._pip_glow, endColor=self.PIP_COLOR_ENABLED, duration=duration)
        animations.SpColorMorphTo(self._frame_glow, endColor=self.FRAME_COLOR_ENABLED, duration=duration)
        animations.SpColorMorphTo(self._pip, endColor=self.PIP_COLOR_ENABLED, duration=duration)
        animations.SpColorMorphTo(self._frame, endColor=self.FRAME_COLOR_ENABLED, duration=duration)

    def OnMouseExit(self, *args):
        super(ShipTreeUnlockEntry, self).OnMouseExit(*args)
        duration = 0.1
        animations.StopAllAnimations(self._pip_glow)
        animations.StopAllAnimations(self._frame_glow)
        animations.StopAllAnimations(self._pip)
        animations.StopAllAnimations(self._frame)
        animations.SpColorMorphTo(self._pip_glow, endColor=self.PIP_COLOR_DISABLED, duration=duration)
        animations.SpColorMorphTo(self._frame_glow, endColor=self.FRAME_GLOW_DISABLED, duration=duration)
        animations.SpColorMorphTo(self._pip, endColor=self.PIP_COLOR_DISABLED, duration=duration)
        animations.SpColorMorphTo(self._frame, endColor=self.FRAME_COLOR_DISABLED, duration=duration)

    def _fade_out(self):
        animations.FadeOut(self, duration=0.3, callback=self._collapse)

    def _collapse(self):
        animations.MorphScalar(self, 'height', endVal=0, callback=self._disable, duration=1.5)

    def _disable(self):
        self.display = False
