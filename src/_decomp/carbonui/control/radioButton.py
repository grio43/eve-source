#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\radioButton.py
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.uianimations import animations
from carbonui.util.various_unsorted import GetWindowAbove
from eve.client.script.ui import eveThemeColor
from eve.client.script.ui.control.tooltips import TooltipPanel

class RadioButton(Checkbox):
    default_retval = None
    default_groupname = None

    def ApplyAttributes(self, attributes):
        self.returnValue = attributes.get('retval', self.default_retval)
        self._radioGroupName = attributes.get('groupname', self.default_groupname)
        super(RadioButton, self).ApplyAttributes(attributes)

    @property
    def groupName(self):
        return self._radioGroupName

    def GetGroup(self):
        if self._radioGroupName is not None:
            return self._radioGroupName
        return self.setting

    def SetGroup(self, groupName):
        force = groupName != self._radioGroupName
        self._radioGroupName = groupName
        if force:
            self.ConstructCheckboxCont()
        self.SetChecked(self._checked, 0)

    def GetReturnValue(self):
        return self.returnValue

    def SetReturnValue(self, returnValue):
        self.returnValue = returnValue

    def _ConstructCheckmark(self):
        self.checkMark = Sprite(name='self_ok', parent=self.checkboxCont, align=uiconst.CENTER, state=uiconst.UI_HIDDEN, pos=(0, 0, 16, 16), texturePath='res:/UI/Texture/classes/checkbox/radio_selected.png', color=eveThemeColor.THEME_FOCUS)
        self.underlay = RadioButtonUnderlay(parent=self.checkboxCont, enabled=self._enabled)

    def GetSelectedFromGroup(self):
        ancestor = GetWindowAbove(self) or self.parent
        for each in ancestor.FindByInstance(RadioButton):
            if each.GetValue() and each.GetGroup() == self.GetGroup():
                return each

    def GetGroupValue(self):
        btn = self.GetSelectedFromGroup()
        if btn:
            return btn.GetReturnValue()

    def ToggleState(self):
        otherCbInGroup = self.FindOtherCbInGroup()
        for eachCb in otherCbInGroup:
            eachCb.SetChecked(0, 0)

        if not self.destroyed:
            self.SetChecked(1)

    def FindOtherCbInGroup(self):
        otherCbInGroup = []
        par = GetWindowAbove(self)
        if par is None:
            tooltipParent = self.parent
            from carbonui.control.contextMenu.contextMenu import ContextMenu
            while tooltipParent:
                if isinstance(tooltipParent, (TooltipPanel, ContextMenu)):
                    par = tooltipParent
                    break
                tooltipParent = tooltipParent.parent

            if par is None:
                par = self.parent
        for each in par.FindByInstance(RadioButton):
            if each != self and each.GetGroup() == self.GetGroup():
                otherCbInGroup.append(each)

        return otherCbInGroup

    def UpdateSettings(self):
        if not self._checked:
            return
        if self.setting:
            self.setting.set(self.returnValue)
        elif self.settingsPath:
            self._ApplySettingOld(self.returnValue)

    def _GetSettingValue(self):
        return self.setting.get()

    def _GetIsCheckedSettingValue(self):
        return self.returnValue == self._GetSettingValue()

    def _on_setting_changed(self, value):
        if value == self.returnValue:
            self.SetChecked(True, report=False)


class RadioButtonUnderlay(Container):
    UNDERLAY_OPACITY_NORMAL = 1.0
    UNDERLAY_OPACITY_DISABLED = 0.5

    def __init__(self, parent = None, bgParent = None, align = uiconst.TOALL, padding = 0, enabled = True):
        self._hover = None
        self._highlight = None
        self._underlay = None
        super(RadioButtonUnderlay, self).__init__(parent=parent, bgParent=bgParent, align=align, padding=padding)
        self._hover = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, padding=-5, texturePath='res:/UI/Texture/classes/checkbox/radio_underlay_hover.png', color=eveThemeColor.THEME_FOCUS, opacity=0.0)
        self._highlight = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/checkbox/radio_highlight.png', opacity=0.0)
        self._underlay = Sprite(parent=self, align=uiconst.TOALL, state=uiconst.UI_DISABLED, texturePath='res:/UI/Texture/classes/checkbox/radio_underlay.png', opacity=self.UNDERLAY_OPACITY_NORMAL if enabled else self.UNDERLAY_OPACITY_DISABLED)

    def Enable(self):
        self._underlay.opacity = self.UNDERLAY_OPACITY_NORMAL

    def Disable(self):
        self._underlay.opacity = self.UNDERLAY_OPACITY_DISABLED

    def Select(self, animate = True):
        pass

    def Deselect(self, animate = True):
        pass

    def OnMouseEnter(self, *args):
        if self._hover is not None:
            animations.FadeIn(self._hover, duration=0.1)

    def OnMouseExit(self, *args):
        if self._hover is not None:
            animations.FadeOut(self._hover, duration=0.3)

    def OnMouseDown(self, *args):
        animations.FadeIn(self._highlight, duration=uiconst.TIME_ENTRY)

    def OnMouseUp(self, *args):
        animations.FadeOut(self._highlight, duration=uiconst.TIME_MOUSEUP)
