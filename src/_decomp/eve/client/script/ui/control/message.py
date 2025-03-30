#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\message.py
import math
import collections
import blue
import eveicon
import localization
import uthread
from carbon.common.script.util import timerstuff
from carbonui import uiconst
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveLabel import Label, EveLabelMedium, EveLabelLarge
from carbonui.decorative.menuUnderlay import MenuUnderlay
from eve.client.script.ui.control.themeColored import FillThemeColored
from eve.client.script.util.settings import IsShipHudTopAligned
from eve.common.lib import appConst as const

def ShowQuickMessage(text, layer = None, flashNewText = True):
    if layer is None:
        layer = uicore.layer.abovemain
    for each in layer.children[:]:
        if isinstance(each, QuickMessage):
            each.ShowMsg(text, flashNewText)
            return

    message = QuickMessage(parent=layer)
    message.ShowMsg(text)
    message.AnimEntry()


class MessageParentClass(Container):
    __guid__ = 'uicls.MessageParentClass'
    __notifyevents__ = ['OnEndChangeDevice', 'OnSessionChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.myLayer = uicore.layer.abovemain
        self.minTop = 0
        config = settings.char.ui.Get(self.configName, self.defaultConfig)
        if not isinstance(config, tuple) or len(config) != 4:
            config = self.defaultConfig
        self.SetAllAlignments(config)
        self.inDragMode = False
        sm.RegisterNotify(self)

    def SetAllAlignments(self, config, *args):
        align, textAlign, left, topOffset = config
        self.SetAlign(align)
        self.currentTextAlignment = textAlign
        self.left = left
        self.topOffset = topOffset

    def EnterDragMode(self, *args):
        self.dragFill = Sprite(parent=self, name='dragFill', texturePath='res:/UI/Texture/classes/Neocom/buttonDown.png', state=uiconst.UI_DISABLED, align=uiconst.TOALL, idx=2)
        func = sm.GetService('logger').MoveNotifications
        self.exitMoveModeBtn = ButtonIcon(name='close', parent=self, align=uiconst.TOPRIGHT, state=uiconst.UI_NORMAL, width=24, height=24, iconSize=16, texturePath=eveicon.close, func=lambda : func(False), hint=localization.GetByLabel('UI/Accessories/Log/ExitMessageMovingMode'), idx=0)
        self.state = uiconst.UI_NORMAL
        self.inDragMode = True
        uicore.animations.SpSwoopBlink(self.dragFill, rotation=math.pi - 0.5, duration=1.5, loops=10)

    def BeginDrag(self, *args):
        layerOffset = self.GetLayerOffset()
        mouseX = uicore.uilib.x - layerOffset
        self.lastx = mouseX
        fromTop = self.absoluteTop - uicore.uilib.y
        while not self.destroyed and getattr(self, 'dragging', 0):
            self.CalculateRepositioning(fromTop)
            blue.pyos.synchro.SleepWallclock(1)

    def GetLayerOffset(self):
        return uicore.layer.abovemain.absoluteLeft

    def CalculateRepositioning(self, fromTop, *args):
        mouseX = uicore.uilib.x - self.GetLayerOffset()
        xDiff = mouseX - self.lastx
        uicore.uilib.SetCursor(uiconst.UICURSOR_NONE)
        self.top = max(self.minTop, uicore.uilib.y + fromTop)
        self.topOffset = self.top + self.height
        self.DoAlignment(xDiff)
        self.lastx = mouseX

    def DoAlignment(self, xDiff = 0, *args):
        layerOffset = self.GetLayerOffset()
        if self.myLayer.display:
            fullWidth, fullHeight = self.myLayer.GetAbsoluteSize()
        else:
            fullWidth = uicore.desktop.width - layerOffset
        fromRightBorder = fullWidth - (self.absoluteRight - layerOffset)
        alignmentMode = settings.user.ui.Get(self.settingNameAlign, 'auto')
        autoAlign = alignmentMode == 'auto'
        if autoAlign and fromRightBorder < 200 or alignmentMode == 'right':
            if self.align != uiconst.TOPRIGHT:
                self.SetAlign(uiconst.TOPRIGHT)
                self.left = fromRightBorder
            else:
                self.left = max(0, self.left - xDiff)
            self.left = min(self.left, fullWidth - 100)
            self.left = max(self.left, 0)
            self.SetTextAlignmentIfNeeded('right')
        elif autoAlign and self.absoluteLeft - layerOffset < 200 or alignmentMode == 'left':
            if self.align != uiconst.TOPLEFT:
                left = self.absoluteLeft - layerOffset
                self.SetAlign(uiconst.TOPLEFT)
                self.left = left
            else:
                self.left = max(0, self.left + xDiff)
            self.left = min(self.left, fullWidth - 100)
            self.left = max(self.left, 0)
            self.SetTextAlignmentIfNeeded('left')
        else:
            if self.align != uiconst.CENTERTOP:
                self.left = self.absoluteLeft - layerOffset + self.width / 2 - fullWidth / 2
                self.SetAlign(uiconst.CENTERTOP)
            else:
                self.left = self.left + xDiff
            self.left = max(self.left, -(fullWidth - 100) / 2)
            self.left = min(self.left, (fullWidth - 100) / 2)
            self.SetTextAlignmentIfNeeded('center')
        self.SaveSettings()

    def OnMouseDown(self, *args):
        self.dragging = 1
        uthread.new(self.BeginDrag)

    def OnMouseUp(self, *args):
        self.dragging = 0

    def ExitDragMode(self, *args):
        self.dragging = 0
        dragFill = getattr(self, 'dragFill', None)
        if dragFill:
            dragFill.Close()
        fakeText = getattr(self, 'fakeText', None)
        if fakeText:
            fakeText.Close()
        exitMoveModeBtn = getattr(self, 'exitMoveModeBtn', None)
        if exitMoveModeBtn:
            exitMoveModeBtn.Close()
        self.SaveSettings()
        self.inDragMode = False

    def SetTextAlignmentIfNeeded(self, alignment, *args):
        pass

    def SaveSettings(self, *args):
        pass

    def OnEndChangeDevice(self, *args):
        self.defaultConfig = self.GetDefaultAlignmentValues()
        if settings.char.ui.Get(self.configName, None) is None:
            self.SetAllAlignments(self.defaultConfig)

    def OnSessionChanged(self, isRemote, sess, change):
        pass

    def ResetAlignment(self, *args):
        self.SetAllAlignments(self.defaultConfig)
        self.SetSizeAndPosition()

    def GetFakeText(self):
        if getattr(self, 'fakeText', None) and not self.fakeText.destroyed:
            return self.fakeText


class QuickMessage(MessageParentClass):
    default_width = 300

    def ApplyAttributes(self, attributes):
        self.configName = 'generalMessages_config'
        self.settingNameAlign = 'generalnotifictions_alignment'
        self.defaultConfig = self.GetDefaultAlignmentValues()
        MessageParentClass.ApplyAttributes(self, attributes)
        self.layerOffset = 0
        self.myLayer = uicore.layer.abovemain
        self.minTop = 0
        self.scope = uiconst.SCOPE_INGAME
        self.message = None
        self.allLabels = []
        self.pureText = ''
        self.Prepare_Text_()
        self.Prepare_Underlay_()

    def GetLayerOffset(self):
        return 0

    def GetDefaultAlignmentValues(self, *args):
        offset = sm.GetService('window').GetCameraLeftOffset(300, align=uiconst.CENTERTOP, left=0)
        if IsShipHudTopAligned():
            top = uicore.desktop.height * 0.75
        else:
            top = max(uicore.desktop.height * 0.2, 175)
        defaultConfig = (uiconst.CENTERTOP,
         'center',
         offset,
         top)
        return defaultConfig

    def Prepare_Text_(self):
        self.message = EveLabelLarge(text='', parent=self, pos=(8, 8, 284, 0), state=uiconst.UI_DISABLED)
        self.allLabels.append(self.message)

    def Prepare_Underlay_(self):
        self.flashBG = FillThemeColored(bgParent=self, colorType=uiconst.COLORTYPE_FLASH)
        MenuUnderlay(bgParent=self)

    def ShowMsg(self, text, flash = True):
        if getattr(self, 'fakeText', None) is not None:
            self.fakeText.Close()
        self.message.text = '<%s>%s' % (self.currentTextAlignment, text)
        self.pureText = text
        self.SetSizeAndPosition()
        if not self.inDragMode:
            self.state = uiconst.UI_DISABLED
        self.SetOrder(0)
        if flash:
            self.AnimFlash()
        if not self.inDragMode:
            self.timer = timerstuff.AutoTimer(5000, self.hide)

    def AnimEntry(self):
        animations.FadeTo(self, self.opacity, 1.0, duration=0.3)
        animations.MorphScalar(self, 'height', 0, self.height, duration=0.15)

    def AnimFlash(self):
        animations.FadeTo(self.flashBG, 2.0, 0.0, duration=0.3)

    def SetSizeAndPosition(self, *args):
        fakeText = self.GetFakeText()
        if self.message.textheight == 0 and fakeText is not None:
            self.height = fakeText.textheight
        else:
            self.height = self.message.textheight
        self.height += 16
        self.top = max(self.minTop, min(uicore.desktop.height - self.height, self.topOffset - self.height))

    def hide(self):
        self.Close()

    def kill_timer(self):
        self.timer = None

    def EnterDragMode(self, *args):
        self.isVisible = self.state != uiconst.UI_HIDDEN
        self.kill_timer()
        if not self.isVisible:
            if self.message is None:
                self.Prepare_Text_()
                self.Prepare_Underlay_()
            self.message.text = ''
            fakeText = self.GetFakeText()
            if fakeText is None:
                self.fakeText = EveLabelMedium(text='', parent=self, name='faketext', left=6, top=5, width=288, state=uiconst.UI_DISABLED, idx=0)
            self.fakeText.text = '<br><%s>%s' % (self.currentTextAlignment, localization.GetByLabel('UI/Accessories/Log/ExampleText'))
            self.height = self.fakeText.textheight + 10
        MessageParentClass.EnterDragMode(self, *args)

    def ExitDragMode(self, *args):
        MessageParentClass.ExitDragMode(self, *args)
        isVisible = getattr(self, 'isVisible', False)
        if isVisible:
            self.state = uiconst.UI_DISABLED
            self.timer = timerstuff.AutoTimer(5000, self.hide)
        else:
            self.hide()

    def SetTextAlignmentIfNeeded(self, alignment, *args):
        if self.currentTextAlignment != alignment:
            self.currentTextAlignment = alignment
            fakeText = self.GetFakeText()
            if fakeText:
                fakeText.text = '<br><%s>%s' % (alignment, localization.GetByLabel('UI/Accessories/Log/ExampleText'))
            else:
                self.message.text = '<br><%s>%s' % (alignment, self.pureText)

    def SaveSettings(self, *args):
        settings.char.ui.Set('generalMessages_config', (self.align,
         self.currentTextAlignment,
         self.left,
         self.topOffset))

    def _OnClose(self, *args):
        self.kill_timer()

    def ChangeFontSize(self, *args):
        if self.message:
            self.message.fontsize = settings.user.ui.Get('dmgnotifictions_fontsize', 12)


class CombatMessage(MessageParentClass):

    def ApplyAttributes(self, attributes):
        self.noDamageMsgTimer = 10 * const.SEC
        self.expiryTime = 5 * const.SEC
        numMessagePerSec = 6
        self.messageSleepTime = 1000 / numMessagePerSec
        self.messageSleepTimeInMs = self.messageSleepTime / 1000.0
        self.fadeOutTime = 5.0
        self.moveUpTime = 0.8
        self.messageList = []
        self.showingMessage = False
        self.configName = 'damageMessages_config'
        self.settingNameAlign = 'dmgnotifictions_alignment'
        self.defaultConfig = self.GetDefaultAlignmentValues()
        MessageParentClass.ApplyAttributes(self, attributes)
        self.myLayer = uicore.layer.target
        self.minTop = -40
        self.scope = uiconst.SCOPE_INGAME
        self.state = uiconst.UI_DISABLED
        self.allContainers = []
        self.allLabels = []
        self.noDamageDict = {}
        self.messageCounter = collections.deque([], maxlen=8 * numMessagePerSec)
        uthread.new(self.ShowMsg)

    def GetLayerOffset(self):
        return uicore.layer.target.absoluteLeft

    def GetDefaultAlignmentValues(self, *args):
        offset = sm.GetService('window').GetCameraLeftOffset(300, align=uiconst.CENTERTOP, left=0)
        if IsShipHudTopAligned():
            top = uicore.desktop.height * 0.7
        else:
            top = max(uicore.desktop.height * 0.32, 225)
        defaultConfig = (uiconst.CENTERTOP,
         uiconst.CENTERBOTTOM,
         offset,
         top)
        return defaultConfig

    def Prepare_Text_(self):
        uiAlignment = self.GetUIAlignment(self.currentTextAlignment)
        notificationFontSize = settings.user.ui.Get('dmgnotifictions_fontsize', 12)
        for i in xrange(6):
            container = ContainerAutoSize(parent=self, name='C%s' % i, left=6, top=5, align=uiAlignment, state=uiconst.UI_DISABLED)
            numberContainer = ContainerAutoSize(parent=container, width=0, height=0, align=uiconst.TOLEFT)
            container.numberLabel = Label(text='', name='N%s' % i, parent=numberContainer, align=uiAlignment, state=uiconst.UI_DISABLED, fontsize=notificationFontSize)
            iconContainer = Container(parent=container, width=0, height=0, align=uiconst.TOLEFT)
            container.iconContainer = iconContainer
            name = 'L%s' % i
            labelContainer = ContainerAutoSize(parent=container, width=0, height=0, align=uiconst.TOLEFT)
            message = Label(text='', name=name, parent=labelContainer, align=uiAlignment, state=uiconst.UI_DISABLED, fontsize=notificationFontSize)
            container.msgIndex = i
            container.label = message
            container.display = False
            setattr(self, 'message%s' % i, message)
            self.allLabels.append(message)
            self.allContainers.append(container)

    def ShowMsg(self, *args):
        if self.showingMessage:
            return
        while 1:
            if not self or self.destroyed:
                return
            try:
                if len(self.messageList) == 0:
                    self.messageCounter.append(0)
                    continue
                self.messageCounter.append(1)
                now = blue.os.GetWallclockTime()
                validTime = now - self.expiryTime
                text = ''
                numMessagesDiscarded = 0
                while len(self.messageList) > 0:
                    nextMessage = self.messageList.pop(0)
                    if len(nextMessage) == 4:
                        timeStamp, text, icons, damageHtml = nextMessage
                    else:
                        timeStamp, text, icons = nextMessage
                        damageHtml = None
                    if timeStamp < validTime:
                        numMessagesDiscarded += 1
                        continue
                    break

                if numMessagesDiscarded:
                    sm.GetService('logger').LogWarn('CombatMessage::ShowMsg - Discarded %s combat UI messages' % numMessagesDiscarded)
                if not text:
                    continue
                if len(self.allContainers) < 1:
                    self.Prepare_Text_()
                fakeText = self.GetFakeText()
                if fakeText:
                    fakeText.Close()
                container, otherVisibleContainers = self.FindFreeContainer()
                if icons:
                    container.label.text = ' ' + text
                else:
                    container.label.text = text
                container.iconContainer.Flush()
                container.iconContainer.width = container.label.height * len(icons)
                container.width = container.label.width + container.iconContainer.width
                container.height = container.label.height
                container.top = 0
                container.msgIndex = -1
                if damageHtml is not None:
                    container.numberLabel.text = damageHtml + ' '
                    container.numberLabel.Show()
                else:
                    container.numberLabel.Hide()
                container.display = True
                for iconResPath in icons:
                    Sprite(parent=container.iconContainer, width=container.label.height, height=container.label.height, texturePath=iconResPath, align=uiconst.TORIGHT)

                self.SetSizeAndPosition()
                otherVisibleContainers.sort(lambda x, y: cmp(x.top, y.top))
                if sum(self.messageCounter) > 8:
                    duration = 0.166
                    secondPoint = 0.05
                else:
                    secondPoint = 0.2
                    duration = 0.4
                for i, ovc in enumerate(otherVisibleContainers):
                    uicore.animations.MorphScalar(ovc, 'top', startVal=ovc.top, endVal=(i + 1) * 20, duration=duration)
                    ovc.msgIndex = i
                    if i == 4:
                        uicore.animations.FadeOut(ovc, duration=self.messageSleepTimeInMs)

                curvePoints = ([0, 0], [secondPoint, 1.0], [1, 0])
                uicore.animations.MorphScalar(container, 'opacity', duration=self.fadeOutTime, curveType=curvePoints)
                self.SetOrder(0)
            except Exception as e:
                sm.GetService('logger').LogWarn('failed at displaying message, e = ', e)
            finally:
                blue.pyos.synchro.SleepWallclock(self.messageSleepTime)

    def AddActionMessage(self, text, icons = None):
        now = blue.os.GetWallclockTime()
        if icons is None:
            icons = []
        self.messageList.append((now, text, icons))

    def AddMessage(self, text, hitQuality, attackerID, images, damageHtml, *args):
        now = blue.os.GetWallclockTime()
        if hitQuality == 0 and attackerID:
            if attackerID in self.noDamageDict:
                lastNoDmgMsgTime = self.noDamageDict[attackerID]
                if lastNoDmgMsgTime > now - self.noDamageMsgTimer:
                    return
            self.noDamageDict[attackerID] = now
            damageHtml = None
        else:
            self.noDamageDict.pop(attackerID, None)
        self.messageList.append((now,
         text,
         images,
         damageHtml))

    def FindFreeContainer(self, *args):
        myContainer = None
        self.allContainers.sort(lambda x, y: cmp(x.msgIndex, y.msgIndex), reverse=True)
        myContainer = self.allContainers[0]
        myContainer.StopAnimations()
        otherVisibleContainers = []
        for container in self.allContainers:
            if container == myContainer:
                continue
            if container.display and self.IsStillFadingOut(container):
                otherVisibleContainers.append(container)
            else:
                container.display = False
                container.msgIndex = len(self.allContainers)

        return (myContainer, otherVisibleContainers)

    def IsStillFadingOut(self, label):
        curveSet = uicore.animations.GetAnimationCurveSet(label, 'opacity')
        return bool(curveSet)

    def SetSizeAndPosition(self, *args):
        boxHeight = 0
        widths = []
        for container in self.allContainers:
            if container.display:
                boxHeight += container.label.textheight
                widths.append(container.label.textwidth)

        fakeText = self.GetFakeText()
        if not widths and fakeText:
            widths = [fakeText.textwidth]
        else:
            widths.append(100)
        self.width = max(widths) + 30
        if boxHeight == 0 and fakeText:
            self.height = fakeText.textheight
        else:
            self.height = boxHeight
        self.height += 10
        self.top = max(self.minTop, min(uicore.desktop.height - self.height, self.topOffset - self.height))

    def SaveSettings(self, *args):
        settings.char.ui.Set('damageMessages_config', (self.align,
         self.currentTextAlignment,
         self.left,
         self.topOffset))

    def SetTextAlignmentIfNeeded(self, alignment, *args):
        alignmentMode = settings.user.ui.Get(self.settingNameAlign, 'auto')
        if alignmentMode != 'auto' and alignmentMode in ('center', 'right', 'left'):
            alignment = alignmentMode
        if self.currentTextAlignment != alignment:
            uiAlignment = self.GetUIAlignment(alignment)
            for container in self.allContainers:
                container.SetAlign(uiAlignment)

            fakeText = self.GetFakeText()
            if fakeText:
                fakeText.text = '<%s>%s' % (alignment, self.fakeText.cleanText)
            self.currentTextAlignment = alignment

    def GetUIAlignment(self, alignment):
        if alignment == 'left':
            uiAlignment = uiconst.BOTTOMLEFT
        elif alignment == 'right':
            uiAlignment = uiconst.BOTTOMRIGHT
        else:
            uiAlignment = uiconst.CENTERBOTTOM
        return uiAlignment

    def ExitDragMode(self, *args):
        if getattr(self, 'border', None) is not None:
            self.border.Close()
        MessageParentClass.ExitDragMode(self, *args)
        self.state = uiconst.UI_DISABLED
        self.SetParent(uicore.layer.target)

    def EnterDragMode(self, *args):
        for container in self.allContainers:
            if container.display and container.opacity > 0.05:
                break
        else:
            uiAlignment = self.GetUIAlignment(self.currentTextAlignment)
            self.fakeText = Label(text='', name='faketext', parent=self, left=6, top=5, align=uiAlignment, state=uiconst.UI_DISABLED, fontsize=12, width=380)
            text = localization.GetByLabel('UI/Accessories/Log/ExampleText')
            self.fakeText.text = '<%s>%s' % (self.currentTextAlignment, text)
            self.fakeText.cleanText = text
            self.height = self.fakeText.textheight + 20
            self.width = 400

        self.border = Frame(parent=self, frameConst=uiconst.FRAME_BORDER1_CORNER5, state=uiconst.UI_DISABLED, color=(1.0, 1.0, 1.0, 0.25), top=-5)
        MessageParentClass.EnterDragMode(self, *args)
        self.dragFill.top = -5
        self.exitMoveModeBtn.top = -5
        self.SetParent(uicore.layer.abovemain)

    def ResetAlignment(self, *args):
        MessageParentClass.ResetAlignment(self, *args)
        self.ChangeAlignment()

    def ChangeFontSize(self, *args):
        fontsize = settings.user.ui.Get('dmgnotifictions_fontsize', 12)
        if len(self.allLabels) < 1:
            return
        for label in self.allLabels:
            label.fontsize = fontsize

    def ChangeAlignment(self, *args):
        self.DoAlignment()

    def OnSessionChanged(self, isRemote, sess, change):
        self.noDamageDict = {}
