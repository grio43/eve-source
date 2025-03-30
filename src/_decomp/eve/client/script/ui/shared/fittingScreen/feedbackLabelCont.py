#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fittingScreen\feedbackLabelCont.py
import uthread2
from carbonui import const as uiconst
from carbonui.primitives.container import Container
from eve.client.script.ui.control.eveLabel import EveCaptionMedium
import shipfitting.errorConst as errorConst
from localization import GetByLabel
from carbonui.uicore import uicore

class FeedbackLabelCont(Container):
    default_width = 100
    default_height = 30
    default_align = uiconst.CENTER
    __notifyevents__ = ['OnFeedbackTextChanged']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.timeoutThread = None
        self.currentErrorKey = None
        self.feedbackLabel = EveCaptionMedium(name='feedbackLabel', parent=self, text='', idx=0, align=uiconst.CENTER, width=300)
        self.feedbackLabel.SetRGB(220 / 255.0, 240 / 255.0, 255 / 255.0)
        self.CreateErrorDict()
        self.fallbackMsg = GetByLabel('UI/Fitting/FittingWindow/WarningModuleCouldntBeFitted')
        sm.RegisterNotify(self)

    def CreateErrorDict(self):
        self.errorDict = {errorConst.MODULE_NOT_APPROPRIATE_FOR_CATEGORY: GetByLabel('UI/Fitting/FittingWindow/WarningNotForThisHullCategory'),
         errorConst.CANT_FIT_MODULE_TO_SHIP: GetByLabel('UI/Fitting/FittingWindow/WarningHullCantFitThisModule'),
         errorConst.MODULE_TOO_BIG: GetByLabel('UI/Fitting/FittingWindow/WarningModuleTooBig'),
         errorConst.NOT_ENOUGH_LAUNCHER_SLOTS: GetByLabel('UI/Fitting/FittingWindow/WarningNotEnoughLauncherSlots'),
         errorConst.NOT_ENOUGH_TURRET_SLOTS: GetByLabel('UI/Fitting/FittingWindow/WarningNotEnoughTurretSlotsFree'),
         errorConst.NOT_ENOUGH_RIG_SLOTS: GetByLabel('UI/Fitting/FittingWindow/WarningNotEnoughRigSlots'),
         errorConst.RIG_WRONG_SIZE: GetByLabel('UI/Fitting/FittingWindow/WarningRigNotRightSize'),
         errorConst.SLOT_NOT_PRESENT: GetByLabel('UI/Fitting/FittingWindow/WarningNotEnoughFreeSlots'),
         errorConst.WRONG_SLOT: GetByLabel('UI/Fitting/FittingWindow/WarningIncorrectSlotForModule'),
         errorConst.SLOT_IN_USE: GetByLabel('UI/Fitting/FittingWindow/WarningModuleSlotInUse')}
        self.errorLabelPathDictWithVariables = {errorConst.CANT_FIT_TOO_MANY_BY_GROUP: 'UI/Fitting/FittingWindow/WarningMaxGroupFitted',
         errorConst.CANT_FIT_TOO_MANY_BY_TYPE: 'UI/Fitting/FittingWindow/WarningMaxTypeFitted'}

    def SetText(self, errorInfo):
        if self.timeoutThread:
            self.timeoutThread.kill()
            self.timeoutThread = None
        errorKey = errorInfo.errorKey if errorInfo else None
        textChanging = self.currentErrorKey in self.errorLabelPathDictWithVariables or self.currentErrorKey != errorKey
        if textChanging:
            if errorKey is None:
                text = ''
            elif errorKey in self.errorLabelPathDictWithVariables:
                labelPath = self.errorLabelPathDictWithVariables.get(errorKey)
                text = GetByLabel(labelPath, extraInfo=errorInfo.extraInfo)
            else:
                text = self.errorDict.get(errorKey, self.fallbackMsg)
            self.feedbackLabel.text = '<center>%s</center>' % text
        self.currentErrorKey = errorKey
        if textChanging:
            uicore.animations.MorphScalar(self.feedbackLabel, 'opacity', startVal=0, endVal=1.0, duration=0.2, loops=1, curveType=uiconst.ANIM_OVERSHOT)
        else:
            uicore.animations.MorphScalar(self.feedbackLabel, 'opacity', startVal=self.feedbackLabel.opacity, endVal=1.5, duration=0.2, loops=1, curveType=uiconst.ANIM_BOUNCE)

    def OnFeedbackTextChanged(self, errorInfo, timeout = False):
        self.SetText(errorInfo)
        if errorInfo and timeout:
            self.timeoutThread = uthread2.call_after_wallclocktime_delay(self.TimeOutLabel, 1.5)

    def TimeOutLabel(self):
        self.feedbackLabel.text = ''
