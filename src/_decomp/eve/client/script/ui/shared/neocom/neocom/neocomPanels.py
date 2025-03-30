#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\neocomPanels.py
import blue
import carbonui.const as uiconst
import localization
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.util.mouseTargetObject import MouseTargetObject
from carbonui.decorative.blurredSceneUnderlay import BlurredSceneUnderlay
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom import neocomPanelEntries
from eve.client.script.ui.shared.neocom.neocom.neocomSettings import neocom_light_background_setting

class PanelBase(Container):
    default_state = uiconst.UI_NORMAL
    default_align = uiconst.TOPLEFT
    _blurred_underlay = None

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.btnData = attributes.btnData
        self.ConstructMainCont()
        self.ConstructUnderlay()
        neocom_light_background_setting.on_change.connect(self._on_light_background_changed)

    def ConstructMainCont(self):
        self.main = Container(parent=self, align=uiconst.TOALL)

    def ConstructUnderlay(self):
        self._blurred_underlay = BlurredSceneUnderlay(bgParent=self, isLightBackground=neocom_light_background_setting.get())

    def _on_light_background_changed(self, value):
        if self._blurred_underlay:
            if value:
                self._blurred_underlay.EnableLightBackground()
            else:
                self._blurred_underlay.DisableLightBackground()

    def EntryAnimation(self):
        uicore.animations.FadeIn(self, duration=0.3)
        for c in self.main.children:
            c.opacity = 0.0

        sleepTime = 100.0 / len(self.main.children)
        for c in self.main.children:
            uicore.animations.FadeTo(c, 0.0, 1.0, duration=0.3)
            blue.synchro.SleepWallclock(sleepTime)


class PanelGroup(PanelBase):
    default_name = 'PanelGroup'

    def ApplyAttributes(self, attributes):
        PanelBase.ApplyAttributes(self, attributes)
        btnDataList = self.GetButtonDataList()
        self.ConstructButtons(btnDataList)
        self.SetPanelHeight(btnDataList)
        self.SetPanelWidth()
        MouseTargetObject(self)

    def ConstructButtons(self, btnDataList):
        if btnDataList:
            for btnData in btnDataList:
                if btnData.btnType in neocomConst.COMMAND_BTNTYPES + (neocomConst.BTNTYPE_INVENTORY, neocomConst.BTNTYPE_NOTIFICATION, neocomConst.BTNTYPE_CAREER_PROGRAM):
                    cmdName = btnData.cmdName
                    cmd = uicore.cmd.GetCommandToExecute(cmdName)
                    if cmd:
                        neocomPanelEntries.PanelEntryCmd(parent=self.main, func=cmd, btnData=btnData)
                elif btnData.btnType in (neocomConst.BTNTYPE_GROUP, neocomConst.BTNTYPE_CHAT):
                    neocomPanelEntries.PanelEntryGroup(parent=self.main, btnData=btnData)
                elif btnData.btnType == neocomConst.BTNTYPE_CHATCHANNEL:
                    neocomPanelEntries.PanelChatChannel(parent=self.main, btnData=btnData)
                elif btnData.btnType == neocomConst.BTNTYPE_WINDOW:
                    neocomPanelEntries.PanelEntryWindow(parent=self.main, btnData=btnData)
                elif btnData.btnType == neocomConst.BTNTYPE_BOOKMARKS:
                    neocomPanelEntries.PanelEntryBookmarks(parent=self.main, btnData=btnData)
                elif btnData.btnType == neocomConst.BTNTYPE_BOOKMARK:
                    neocomPanelEntries.PanelEntryBookmark(parent=self.main, btnData=btnData)
                elif btnData.btnType == neocomConst.BTNTYPE_SPACER:
                    Container(parent=self.main, align=uiconst.TOTOP, height=30)

        else:
            neocomPanelEntries.PanelEntryText(parent=self.main, label=localization.GetByLabel('UI/Neocom/GroupEmpty'))

    def SetPanelHeight(self, btnDataList):
        height = 0
        for child in self.main.children:
            height += child.height

        self.height = max(height, neocomPanelEntries.PanelEntryBase.default_height)

    def SetPanelWidth(self):
        maxWidth = 220
        for panel in self.main.children:
            if hasattr(panel, 'GetRequiredWidth'):
                maxWidth = max(panel.GetRequiredWidth(), maxWidth)

        self.width = maxWidth

    def GetButtonDataList(self):
        return [ btnData for btnData in self.btnData.children if btnData.IsButtonInScope() ]


class PanelOverflow(PanelGroup):
    default_name = 'PanelOverflow'

    def ApplyAttributes(self, attributes):
        self.overflowButtons = attributes.overflowButtons
        PanelGroup.ApplyAttributes(self, attributes)

    def GetButtonDataList(self):
        return sm.GetService('neocom').GetNeocomContainer().overflowButtons


class PanelEveMenu(PanelGroup):
    default_name = 'PanelEveMenu'
    default_clipChildren = True

    def ApplyAttributes(self, attributes):
        PanelGroup.ApplyAttributes(self, attributes)
        sm.ScatterEvent('OnEveMenuOpened')
        self.btnData.SetHasNewActivityOff()

    def ConstructLayout(self):
        self.ConstructMainCont()
        self.ConstructUnderlay()

    def ConstructMainCont(self):
        self.main = Container(name='main', parent=self, padding=(8, 4, 0, 0))

    def SetPanelHeight(self, btnDataList):
        self.height = uicore.desktop.height

    def Close(self, *args):
        sm.ScatterEvent('OnEveMenuClosed')
        PanelGroup.Close(self, *args)
