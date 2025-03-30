#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\newFeatures\debugwindow.py
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveLabelMedium
from carbonui.control.window import Window
import localization
import newFeatures
from newFeatures.feature import ReleasedFeature
from newFeatures.newFeatureNotify import OpenNewFeaturesWindow

class NewFeatureNotifyDebugWindow(Window):
    __guid__ = 'newFeatures.NewFeatureNotifyDebugWindow'
    default_windowID = 'NewFeatureNotifyDebugWindow'
    default_width = 450
    default_height = 175
    default_minSize = (default_width, default_height)
    default_caption = 'New Feature Notification Debugger'

    def GetFeatureNotificationComboPairs(self):
        pairList = []
        fsdData = newFeatures.newFeatureNotify.GetFSDData()
        orderedKeys = reversed(sorted(fsdData.keys()))
        for k in orderedKeys:
            featureNotification = fsdData[k]
            comboEntryDisplayName = unicode(k) + ': ' + localization.GetByLabel(featureNotification.nameID)
            pairList.append((comboEntryDisplayName, featureNotification))

        return pairList

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        mainCont = Container(parent=self.sr.main, align=uiconst.TOALL)
        options = self.GetFeatureNotificationComboPairs()
        self.combo = Combo(parent=mainCont, label='Select Notification', options=options, name='', select=1, callback=self.OnComboChanged, pos=(0, 15, 0, 0), width=300, align=uiconst.TOTOP)
        buttonCont = Container(parent=mainCont, align=uiconst.TOTOP, height=32)
        self.button = Button(parent=buttonCont, label='Show Notification', align=uiconst.TOLEFT, func=self.OnButtonClicked, width=100)
        self.startDateLabel = EveLabelMedium(parent=mainCont, text='', align=uiconst.TOTOP)
        self.endDateLabel = EveLabelMedium(parent=mainCont, text='', align=uiconst.TOTOP)
        self.UpdateDates()

    def UpdateDates(self):
        feature = self.combo.GetValue()
        startDateLabelText = u'Starts at: {startDate}'.format(startDate=feature.startDate)
        endDateLabelText = u'Ends at: {startDate}'.format(startDate=feature.endDate)
        self.startDateLabel.SetText(startDateLabelText)
        self.endDateLabel.SetText(endDateLabelText)

    def OnComboChanged(self, combo, key, value):
        self.UpdateDates()

    def OnButtonClicked(self, button):
        featureID = int(self.combo.GetKey().split(':')[0])
        feature = self.combo.GetValue()
        releasedFeature = ReleasedFeature(featureID, feature)
        releasedFeature.MarkAsForceShow()
        OpenNewFeaturesWindow([releasedFeature])
