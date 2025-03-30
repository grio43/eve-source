#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\fitting\utilBtns.py
from carbon.client.script.environment.AudioUtil import PlaySound
from eve.client.script.ui.control.eveIcon import Icon
from localization import GetByLabel
import carbonui.const as uiconst

class FittingUtilBtn(Icon):
    default_height = 16
    default_width = 16
    default_pickradius = -1
    default_idx = 0
    default_ignoreSize = True

    def ApplyAttributes(self, attributes):
        Icon.ApplyAttributes(self, attributes)
        self.controller = attributes.controller
        btnData = attributes.btnData
        self.isActive = btnData.isActive
        self.clickFunc = btnData.func
        self.mouseOverFunc = attributes.mouseOverFunc
        self.color.a = 0.0
        iconHint = btnData.hint
        if not self.isActive:
            if self.controller.GetModule() is None or self.controller.SlotExists():
                iconHint = GetByLabel('UI/Fitting/Disabled', moduleName=btnData.hint)
            else:
                iconHint = GetByLabel('UI/Fitting/CantOnlineIllegalSlot')
        self.hint = iconHint

    def OnClick(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_CLICK)
        if self.isActive and self.clickFunc:
            self.clickFunc(*args)

    def OnMouseEnter(self, *args):
        PlaySound(uiconst.SOUND_BUTTON_HOVER)
        self.mouseOverFunc(*args)

    def SetBtnColorBasedOnIsActive(self):
        if self.isActive:
            self.opacity = 1.0
        else:
            self.opacity = 0.25

    def Hide(self):
        self.opacity = 0.0

    def Close(self):
        self.controller = None
        Icon.Close(self)

    def GetHint(self):
        if self.opacity == 0.0:
            return
        return self.hint


class UtilBtnData(object):

    def __init__(self, hint, iconPath, func, isActive, onlineBtn):
        self.hint = hint
        self.iconPath = iconPath
        self.func = func
        self.isActive = isActive
        self.onlineBtn = onlineBtn
