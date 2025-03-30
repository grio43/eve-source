#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\login\charcreation_new\charCreationUtils.py
import carbonui.const as uiconst
import charactercreator.const as ccConst
from carbon.common.script.util import timerstuff
from carbonui.primitives.container import Container
from carbonui.uicore import uicore
from carbonui.primitives.gradientSprite import GradientConst, GradientSprite
from eve.client.script.ui.control import eveLabel

class CCLabel(eveLabel.Label):
    default_bold = 1
    default_color = ccConst.COLOR
    default_letterspace = 1
    default_state = uiconst.UI_DISABLED


class BitSlider(Container):
    default_name = 'BitSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitGap = attributes.get('bitGap', self.default_bitGap)
        bitAmount = attributes.bitAmount
        self.bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = self.bitHeight + 4
        if bitAmount:
            self.bitWidth = int(targetWidth / float(bitAmount))
        else:
            self.bitWidth = attributes.bitWidth or self.default_bitWidth
        self._value = 0.0
        self.bitParent = Container(parent=self, pos=(0,
         0,
         targetWidth,
         self.height), align=uiconst.TOPLEFT)
        self.handle = Container(parent=self.bitParent, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         0,
         3,
         self.height), bgColor=ccConst.COLOR + (1.0,))
        i = 0
        while True:
            if bitAmount is None and i >= 3 and i * (self.bitWidth + bitGap) + self.bitWidth > targetWidth:
                break
            bit = Container(parent=self.bitParent, pos=(i * (self.bitWidth + bitGap),
             2,
             self.bitWidth,
             self.bitHeight), align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, bgColor=ccConst.COLOR + (1.0,))
            bit.isBit = True
            i += 1
            if bitAmount is not None and i == bitAmount:
                break

        self._numBits = i
        if targetWidth != bit.left + bit.width:
            diff = targetWidth - (bit.left + bit.width)
            bit.width += diff
        self.bitParent.width = targetWidth
        self.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue

    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.softSlideTimer = None
        self.slideTimer = timerstuff.AutoTimer(33, self.UpdateSliderPortion)

    def OnMouseEnter(self, *args):
        self.softSlideTimer = timerstuff.AutoTimer(33, self.UpdateSoftSliderPortion)

    def OnMouseExit(self, *args):
        pass

    def OnMouseWheel(self, *args):
        if uicore.uilib.dz > 0:
            self.SetValue(self.GetValue() + 1.0 / self._numBits)
        else:
            self.SetValue(self.GetValue() - 1.0 / self._numBits)

    def UpdateSoftSliderPortion(self, *args):
        if uicore.uilib.mouseOver is self or uicore.uilib.mouseOver.IsUnder(self):
            l, t, w, h = self.bitParent.GetAbsolute()
            portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
            self.ShowSoftLit(portion)
        else:
            self.softSlideTimer = None
            self.ShowSoftLit(0.0)

    def UpdateSliderPortion(self, *args):
        l, t, w, h = self.bitParent.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int((w - self.bitWidth) * portion)
        self.ShowLit(portion)

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.slideTimer = None
        l, t, w, h = self.bitParent.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int((w - self.handle.width) * portion)
        self.SetValue(portion)

    def ShowLit(self, portion):
        l, t, w, h = self.bitParent.GetAbsolute()
        if not w:
            return
        self.handle.left = int((w - self.handle.width) * portion)
        for each in self.bitParent.children:
            if not hasattr(each, 'isBit'):
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(1.0)
            else:
                each.SetOpacity(0.333)

    def ShowSoftLit(self, portion):
        l, t, w, h = self.bitParent.GetAbsolute()
        for each in self.bitParent.children:
            if not hasattr(each, 'isBit'):
                continue
            if each.opacity == 1.0:
                continue
            mportion = max(0.0, min(1.0, (each.left + each.width / 2) / float(w)))
            if portion > mportion:
                each.SetOpacity(0.5)
            else:
                each.SetOpacity(0.333)

    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.ShowLit(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)

    def GetValue(self):
        return self._value


class GradientSlider(Container):
    default_name = 'GradientSlider'
    default_align = uiconst.RELATIVE
    default_bitWidth = 3
    default_bitHeight = 8
    default_bitGap = 1
    default_state = uiconst.UI_NORMAL
    default_left = 0
    default_top = 0
    default_width = 128
    default_height = 12
    cursor = uiconst.UICURSOR_SELECT

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        self.onSetValueCallback = None
        targetWidth = attributes.get('sliderWidth', 100)
        bitHeight = attributes.bitHeight or self.default_bitHeight
        self.height = bitHeight + 4
        self._value = 0.0
        self.handle = Container(parent=self, align=uiconst.RELATIVE, state=uiconst.UI_DISABLED, pos=(0,
         -2,
         3,
         self.height + 4), bgColor=ccConst.COLOR + (1.0,))
        if attributes.get('alphaValues'):
            alphaValues = attributes.get('alphaValues')
            rgbValues = [(0, (0, 0, 0))]
        else:
            alphaValues = (1, 1)
            rgbValues = [(0, (0, 0, 0)), (1.0, (1, 1, 1))]
        self.gradientSprite = GradientSprite(parent=self, pos=(0,
         0,
         targetWidth,
         self.height), rgbData=rgbValues, alphaData=[alphaValues, (1.0, 1.0)], alphaInterp=GradientConst.INTERP_LINEAR, colorInterp=GradientConst.INTERP_LINEAR, state=uiconst.UI_DISABLED)
        self.gradientSprite.width = targetWidth
        if attributes.setvalue is not None:
            self.SetValue(attributes.setvalue)
        self.onSetValueCallback = attributes.OnSetValue
        self.ChangeGradientColor(secondColor=(1.0, (1, 1, 0)))

    def OnMouseDown(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.slideTimer = timerstuff.AutoTimer(33, self.UpdateSliderPortion)

    def UpdateSliderPortion(self, *args):
        l, t, w, h = self.gradientSprite.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int(w * portion)

    def OnMouseUp(self, mouseBtn, *args):
        if mouseBtn != uiconst.MOUSELEFT:
            return
        self.slideTimer = None
        l, t, w, h = self.gradientSprite.GetAbsolute()
        portion = max(0.0, min(1.0, (uicore.uilib.x - l) / float(w)))
        self.handle.left = int(w * portion)
        self.SetValue(portion)

    def SetValue(self, value, doCallback = True):
        callback = value != self._value
        self._value = max(0.0, min(1.0, value))
        self.SetHandle(self._value)
        if callback and doCallback and self.onSetValueCallback:
            self.onSetValueCallback(self)

    def SetHandle(self, portion):
        l, t, w, h = self.gradientSprite.GetAbsolute()
        if not w:
            return
        self.handle.left = int((w - self.handle.width) * portion)

    def GetValue(self):
        return self._value

    def ChangeGradientColor(self, firstColor = None, secondColor = None):
        colorData = self.gradientSprite.colorData
        if len(colorData) < 2:
            firstColor = secondColor
        if firstColor is not None:
            colorData[0] = firstColor
        if secondColor is not None and len(colorData) > 1:
            colorData[1] = secondColor
        self.gradientSprite.SetGradient()
