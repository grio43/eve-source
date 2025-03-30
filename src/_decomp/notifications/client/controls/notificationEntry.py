#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\notifications\client\controls\notificationEntry.py
import math
import blue
import carbon.common.script.util.format as formatUtil
import carbonui.const as uiconst
import eve.client.script.ui.util.uix as uiUtils
import eve.common.script.util.notificationconst as notificationConst
import eveicon
import localization
from carbon.client.script.environment.AudioUtil import PlaySound
from carbon.common.script.sys.serviceConst import ROLE_PROGRAMMER
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.primitives.frame import Frame
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveIcon import GetLogoIcon
from eve.client.script.ui.control.eveIcon import Icon
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from eve.client.script.ui.control.eveLabel import EveLabelSmall
from eve.client.script.ui.shared.stateFlag import AddAndSetFlagIconFromData
from eve.common.script.sys.idCheckers import IsCorporation, IsCharacter
from eveservices.menu import GetMenuService
from notifications.client.controls.notificationSettingChange import GetSettingsForNotification, ChangePopupSettingForNotification, ChangeShowAtAllSettingForNotification
from notifications.client.controls.notificationTextures import NOTIFICATION_TYPE_TO_TEXTURE
from notifications.client.notificationUIConst import NOTIFICATION_BACKGROUND_UP, NOTIFICATION_BACKGROUND_OVER, NOTIFICATION_BACKGROUND_CORNER_SIZE, NOTIFICATION_BACKGROUND_OFFSET
from notifications.common.formatters.killMailBase import KillMailBaseFormatter
from notifications.common.formatters.killMailFinalBlow import KillMailFinalBlowFormatter
from notifications.common.notification import Notification
from signals import Signal
from utillib import KeyVal
MAINAREA_WIDTH = 224
LEFT_PANEL_WIDTH = 40
MINENTRYHEIGHT = 50
PADDING_TOP = 5
PADDING_BOTTOM = 5
PADDING_ENTRY_TO_TIME = 5
LEFT_PANEL_PADDING = (5, 5, 10, 5)
TIMETEXT_PLACEHOLDER = '123'
TIMETEXT_COLOR = (0.5, 0.5, 0.5)
CHAR_PORTRAIT_SIZE = 128
SHIP_TYPE_ICON_SIZE = 40
SHIP_TECH_ICON_SIZE = 16
FLAG_ICON_PADDING = 10
CORP_LOGO_SIZE = 40
NOTIFICATION_SPRITE_SIZE = 40
DEFAULT_NOTIFICATION_TEXTURE_PATH = 'res:/ui/Texture/WindowIcons/bountyoffice.png'
NOTIFICATION_ICONS_TEXTURE_PATH = 'res:/UI/Texture/Icons/notifications/notificationIcon_%s.png'
BLINK_SPRITE_TEXTURE_PATH = 'res:/UI/Texture/classes/Neocom/buttonBlink.png'
BLINK_SPRITE_ROTATION = math.pi * 0.75
BLINK_SPRITE_DURATION = 0.8
BLINK_SPRITE_LOOPS = 1
TIME_AGO_LABEL = 'Notifications/NotificationWidget/NotificationTimeAgo'

class NotificationEntry(Container):
    default_height = MINENTRYHEIGHT
    default_state = uiconst.UI_NORMAL
    notification = None
    contentLoaded = False
    blinkSprite = None
    titleLabel = None
    subtextLabel = None
    timeLabel = None

    def GetFormattedTimeString(self, timestamp):
        delta = blue.os.GetWallclockTime() - timestamp
        return formatUtil.FmtTimeIntervalMaxParts(delta, breakAt='second', maxParts=2)

    def UpdateNotificationEntryHeight(self):
        height = PADDING_TOP
        size = EveLabelMedium.MeasureTextSize(self.title, width=MAINAREA_WIDTH, bold=True)
        height += size[1]
        if self.subtext:
            size = EveLabelMedium.MeasureTextSize(self.subtext, width=MAINAREA_WIDTH)
            height += size[1]
        if self.created:
            height += PADDING_ENTRY_TO_TIME
            size = EveLabelSmall.MeasureTextSize(TIMETEXT_PLACEHOLDER, width=MAINAREA_WIDTH)
            height += size[1]
        height += PADDING_BOTTOM
        return max(MINENTRYHEIGHT, height)

    def ApplyAttributes(self, attributes):
        self.notification = attributes.notification
        self.developerMode = attributes.developerMode
        self.created = attributes.created
        self.title = self.notification.subject
        self.subtext = self.notification.subtext
        attributes.height = self.UpdateNotificationEntryHeight()
        Container.ApplyAttributes(self, attributes)

    def LoadContent(self):
        if self.contentLoaded:
            return
        self.contentLoaded = True
        self._CreateMainBackground()
        self._CreatePanels()
        self._CreateNotificationText()
        self._CreateNotificationImage()
        self.on_closed_by_user_signal = Signal('on_close_button')
        self.closeButton = ButtonIcon(name='closeButton', parent=self, align=uiconst.TOPRIGHT, pos=(2, 2, 16, 16), texturePath=eveicon.close.resolve(16), func=self.OnCloseButton, opacity=0.0)
        if self.created:
            timeinterval = max(blue.os.GetWallclockTime() - self.created, 0)
            createdText = localization.GetByLabel(TIME_AGO_LABEL, time=timeinterval)
            self.timeLabel = EveLabelSmall(name='timeLabel', parent=self.rightContainer, align=uiconst.TOTOP, color=TIMETEXT_COLOR, padTop=PADDING_ENTRY_TO_TIME)
            self.timeLabel.text = createdText
        notification = self.notification
        if notification.typeID in [notificationConst.notificationTypeKillReportFinalBlow, notificationConst.notificationTypeKillReportVictim]:
            shipTypeID = KillMailFinalBlowFormatter.GetVictimShipTypeID(notification.data)
            if shipTypeID is not None:
                parentContainer = self.leftContainer
                Icon(name='shipTypeIcon', parent=parentContainer, align=uiconst.TOPRIGHT, size=SHIP_TYPE_ICON_SIZE, typeID=shipTypeID)
                shipTechIcon = Sprite(name='shipTechIcon', parent=parentContainer, width=SHIP_TECH_ICON_SIZE, height=SHIP_TECH_ICON_SIZE, idx=0)
                uiUtils.GetTechLevelIcon(shipTechIcon, 0, shipTypeID)
                self.imageSprite.GetDragData = lambda *args: self.MakeKillDragObject(notification)
                self.imageSprite.state = uiconst.UI_NORMAL
        if self.ShouldDisplayPortrait(notification):
            senderIsProperOwner = IsCorporation(notification.senderID) or IsCharacter(notification.senderID)
            if not senderIsProperOwner:
                self.characterSprite.texturePath = 'res:/UI/Texture/silhouette_64.png'
                self.characterSprite.state = uiconst.UI_DISABLED
            else:
                item = cfg.eveowners.Get(notification.senderID)
                if item.IsCharacter():
                    sm.GetService('photo').GetPortrait(notification.senderID, CHAR_PORTRAIT_SIZE, self.characterSprite)
                    if notification.typeID in notificationConst.notificationShowStanding:
                        charinfo = item
                        self.characterSprite.GetMenu = lambda : GetMenuService().GetMenuFromItemIDTypeID(notification.senderID, charinfo.typeID)
                        self.characterSprite.GetDragData = lambda *args: self.MakeCharacterDragObject(notification.senderID)
                        charData = KeyVal()
                        charData.charID = notification.senderID
                        charData.charinfo = charinfo
                        AddAndSetFlagIconFromData(charData, parentCont=self.leftContainer, top=self.characterSprite.height - FLAG_ICON_PADDING)
                else:
                    self.corpLogo = GetLogoIcon(itemID=notification.senderID, parent=self.leftContainer, align=uiconst.TOPLEFT, size=CORP_LOGO_SIZE, state=uiconst.UI_DISABLED, ignoreSize=True)
                self.characterSprite.state = uiconst.UI_NORMAL

    def OnCloseButton(self):
        self.on_closed_by_user_signal(self)

    def _CreateMainBackground(self):
        self.filler = Frame(name='mainBackgroundFrame', bgParent=self, texturePath=NOTIFICATION_BACKGROUND_UP, cornerSize=NOTIFICATION_BACKGROUND_CORNER_SIZE, offset=NOTIFICATION_BACKGROUND_OFFSET)

    def _CreatePanels(self):
        self.leftContainer = Container(name='leftContainer-notificationGraphic', width=LEFT_PANEL_WIDTH, padding=LEFT_PANEL_PADDING, parent=self, align=uiconst.TOLEFT)
        self.rightContainer = ContainerAutoSize(name='rightContainer-notificationInfo', width=MAINAREA_WIDTH, parent=self, align=uiconst.TOLEFT, padBottom=PADDING_BOTTOM)

    def _CreateNotificationText(self):
        self.titleLabel = EveLabelMedium(name='notificationSubjectLabel', parent=self.rightContainer, align=uiconst.TOTOP, text=self.title, padTop=PADDING_TOP, bold=True)
        if self.subtext:
            self.subtextLabel = EveLabelMedium(name='notificationSubtextLabel', parent=self.rightContainer, align=uiconst.TOTOP, text=self.subtext)

    def _CreateNotificationImage(self):
        if self.notification:
            texture = self.GetTexturePathForNotification(self.notification.typeID)
        else:
            texture = DEFAULT_NOTIFICATION_TEXTURE_PATH
        self.imageSprite = Sprite(name='notificationSprite', parent=self.leftContainer, texturePath=texture, align=uiconst.TOPLEFT, width=NOTIFICATION_SPRITE_SIZE, height=NOTIFICATION_SPRITE_SIZE, state=uiconst.UI_DISABLED)
        self.characterSprite = Sprite(name='notificationCharacterSprite', parent=self.leftContainer, texturePath=texture, align=uiconst.TOPLEFT, width=NOTIFICATION_SPRITE_SIZE, height=NOTIFICATION_SPRITE_SIZE, state=uiconst.UI_HIDDEN)

    def BlinkFinished(self, *args):
        if self.blinkSprite and not self.blinkSprite.destroyed:
            self.blinkSprite.Close()
            self.blinkSprite = None

    def Blink(self):
        if self.blinkSprite is None:
            self.blinkSprite = Sprite(bgParent=self, name='blinkSprite', texturePath=BLINK_SPRITE_TEXTURE_PATH, idx=0)
        self.blinkSprite.Show()
        uicore.animations.SpSwoopBlink(self.blinkSprite, rotation=BLINK_SPRITE_ROTATION, duration=BLINK_SPRITE_DURATION, loops=BLINK_SPRITE_LOOPS, callback=self.BlinkFinished)

    def GetTexturePathForNotification(self, notificationTypeID):
        texture = NOTIFICATION_TYPE_TO_TEXTURE.get(notificationTypeID, '')
        if not texture or not blue.paths.exists(texture):
            texture = None
        return texture

    def ShouldDisplayPortrait(self, notification):
        if notification and notification.typeID in notificationConst.notificationDisplaySender:
            return True
        else:
            return False

    def GetHint(self):
        if self.notification and self.developerMode:
            return '%s %s %s %s' % (str(self.notification.typeID),
             str(self.notification.subject),
             str(self.notification.senderID),
             self.notification.body)
        else:
            return ''

    def MakeCharacterDragObject(self, charid):
        typeID = cfg.eveowners.Get(charid).typeID
        fakeNode = KeyVal()
        fakeNode.charID = charid
        fakeNode.info = cfg.eveowners.Get(charid)
        fakeNode.itemID = charid
        fakeNode.__guid__ = 'listentry.User'
        return [fakeNode]

    def MakeKillDragObject(self, notification):
        fakeNode = KeyVal()
        kmID, kmHash = KillMailBaseFormatter.GetKillMailIDandHash(notification.data)
        theRealKm = sm.RemoteSvc('warStatisticMgr').GetKillMail(kmID, kmHash)
        fakeNode.mail = theRealKm
        fakeNode.__guid__ = 'listentry.KillMail'
        return [fakeNode]

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_ENTRY_HOVER)
        self.filler.texturePath = NOTIFICATION_BACKGROUND_OVER
        animations.FadeIn(self.closeButton)

    def OnMouseExit(self, *args):
        self.filler.texturePath = NOTIFICATION_BACKGROUND_UP
        animations.FadeOut(self.closeButton)

    def GetMenu(self):
        notificationTypeID = self.notification.typeID
        try:
            showAtAll, showPopup = GetSettingsForNotification(notificationTypeID)
        except KeyError:
            return []

        labelPath = notificationConst.notificationToSettingDescription.get(notificationTypeID, None)
        if not labelPath:
            return []
        labelText = localization.GetByLabel(labelPath)
        m = []
        if session.role & ROLE_PROGRAMMER:
            m.append(('GM - notificationID: %s' % self.notification.notificationID, blue.pyos.SetClipboardData, (str(self.notification.notificationID),)))
        text = localization.GetByLabel('UI/Mail/Notifications/MarkAsRead')
        if self.OfferMarkMailRead():
            m += [(text, self.MarkMailAsRead, ())]
        elif self.OfferMarkNotificationRead():
            m += [(text, self.MarkNotificationAsRead, ())]
        if showAtAll:
            text = localization.GetByLabel('Notifications/NotificationWidget/TurnHistoryVisibilityOff', settingName=labelText)
            m += [(text, ChangeShowAtAllSettingForNotification, (notificationTypeID, 0))]
        else:
            text = localization.GetByLabel('Notifications/NotificationWidget/TurnHistoryVisibilityOn', settingName=labelText)
            m += [(text, ChangeShowAtAllSettingForNotification, (notificationTypeID, 1))]
        if showPopup:
            text = localization.GetByLabel('Notifications/NotificationWidget/TurnPopupOff', settingName=labelText)
            m += [(text, ChangePopupSettingForNotification, (notificationTypeID, 0))]
        else:
            text = localization.GetByLabel('Notifications/NotificationWidget/TurnPopupOn', settingName=labelText)
            m += [(text, ChangePopupSettingForNotification, (notificationTypeID, 1))]
        return m

    def OfferMarkNotificationRead(self):
        processed = getattr(self.notification, 'processed', None)
        if processed is None or processed:
            return False
        if self.notification.metaType != Notification.NORMAL_NOTIFICATION:
            return
        if self.notification.notificationID is None:
            return
        if self.notification.typeID > 1000:
            return False
        return True

    def OfferMarkMailRead(self):
        if self.notification.typeID != notificationConst.notificationTypeNewMailFrom:
            return False
        if self.notification.data['msg'].read:
            return False
        return True

    def MarkNotificationAsRead(self, *args):
        notificationID = self.notification.notificationID
        sm.GetService('notificationSvc').MarkAsRead([notificationID])
        sm.ScatterEvent('OnNotificationReadOutside', notificationID)

    def MarkMailAsRead(self, *args):
        msgID = self.notification.data['msg'].messageID
        sm.GetService('mailSvc').MarkMessagesAsRead([msgID])
        self.notification.processed = True
