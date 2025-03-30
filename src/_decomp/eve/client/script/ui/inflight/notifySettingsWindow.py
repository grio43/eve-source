#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\inflight\notifySettingsWindow.py
from carbonui import const as uiconst
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.window import Window
from eve.common.lib.appConst import soundNotifications
from eveaudio.shiphealthnotification import SoundNotification
import localization
from carbonui.uicore import uicore
lineHeight = 22

class NotifySettingsWindow(Window):
    default_windowID = 'NotifySettingsWindow'
    default_fixedWidth = 420

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.SetCaption(localization.GetByLabel('UI/Inflight/NotifySettingsWindow/DamageAlertSettings'))
        self.MakeUnResizeable()
        self.ConstructLayout()
        self.ApplyFixedHeight()

    def ApplyFixedHeight(self):
        _, height = self.mainContainer.GetAbsoluteSize()
        _, height = self.GetWindowSizeForContentSize(height=height)
        self.SetFixedHeight(height)

    def ConstructLayout(self):
        self.notifydata = []
        notificationList = ['shield',
         'armour',
         'hull',
         'capacitor',
         'cargoHold']
        for name in notificationList:
            notification = SoundNotification(name)
            data = {'checkboxLabel': localization.GetByLabel(notification.localizationLabel),
             'checkboxName': name + 'Notification',
             'checkboxSetting': notification.activeFlagSettingsName,
             'checkboxDefault': notification.defaultStatus,
             'sliderName': name,
             'sliderSetting': (name + 'Threshold', ('user', 'notifications'), notification.defaultThreshold)}
            self.notifydata.append(data)

        labelWidth = 180
        self.mainContainer = ContainerAutoSize(name='mainContainer', parent=self.sr.main, align=uiconst.TOTOP)
        for each in self.notifydata:
            name = each['sliderName']
            notifytop = Container(name='notifytop', parent=self.mainContainer, align=uiconst.TOTOP, pos=(uiconst.defaultPadding,
             uiconst.defaultPadding,
             0,
             lineHeight))
            Checkbox(text=each['checkboxLabel'], parent=notifytop, settingsKey=each['checkboxSetting'], settingsPath=('user', 'notifications'), checked=settings.user.notifications.Get(each['checkboxSetting'], each['checkboxDefault']), callback=self.CheckBoxChange, align=uiconst.TOPLEFT, pos=(uiconst.defaultPadding,
             0,
             labelWidth,
             0))
            _par = Container(name=name + '_slider', align=uiconst.TOPRIGHT, width=labelWidth, parent=notifytop, pos=(10,
             0,
             160,
             lineHeight))
            config = each['sliderSetting']
            slider = Slider(parent=_par, on_dragging=self.SliderChange, name=config[0], minValue=0.0, maxValue=1.0, config=config, getHintFunc=self.GetSliderHint, padTop=4)

    def GetSliderHint(self, slider):
        return localization.GetByLabel('UI/Common/Formatting/Percentage', percentage=slider.GetValue() * 100)

    def SliderChange(self, slider):
        if slider.name == 'shieldThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('shield')
        elif slider.name == 'armourThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('armour')
        elif slider.name == 'hullThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('hull')
        elif slider.name == 'capacitorThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('capacitor')
        elif slider.name == 'cargoHoldThreshold':
            uicore.layer.shipui.sr.shipAlertContainer.AlertThresholdChanged('cargoHold')

    def CheckBoxChange(self, checkbox, *args):
        notificationKey = checkbox.name[0:-len('NotificationEnabled')]
        if notificationKey in soundNotifications.keys():
            notification = SoundNotification(notificationKey)
            settings.user.notifications.Set(notification.activeFlagSettingsName, checkbox.checked)
            if checkbox.checked:
                sm.GetService('audio').SendUIEvent(notification.notificationEventName)
            uicore.layer.shipui.sr.shipAlertContainer.SetNotificationEnabled(notificationKey, checkbox.checked)
