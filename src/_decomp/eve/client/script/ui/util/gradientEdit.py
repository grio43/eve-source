#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\gradientEdit.py
import carbonui.const as uiconst
import trinity
import blue
from carbonui.control.combo import Combo
from carbonui.control.slider import Slider
from carbonui.primitives.container import Container
from carbonui.primitives.sprite import Sprite
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.window import Window

class GradientEditor(Window):
    __guid__ = 'form.GradientEditor'
    default_width = 300
    default_height = 300
    default_minSize = (480, 480)
    default_windowID = 'GradientEditor'
    default_state = uiconst.UI_NORMAL
    default_caption = 'Gradient Editor'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.buttonBar = Container(parent=self.sr.main, name='buttonBar', padLeft=10, padRight=10, padTop=8, padBottom=8, align=uiconst.TOBOTTOM, height=80)
        self.mainEditor = Container(parent=self.sr.main, name='mainEditor', align=uiconst.TOALL)
        rightArea = Container(parent=self.mainEditor, name='rightArea', padLeft=8, padRight=8, padTop=8, padBottom=8, align=uiconst.TORIGHT, width=200)
        leftArea = Container(parent=self.mainEditor, name='leftArea', align=uiconst.TOALL)
        self.rgbSelected = 0
        self.rgbPoints = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.rgbDivs = [0.0, 0.5, 1.0]
        self.alphaSelected = 0
        self.alphaPoints = [1.0, 1.0]
        self.alphaDivs = [0.0, 1.0]
        self.gradientData = {'textureSize': 128,
         'rgbPoints': self.rgbPoints,
         'rgbDivs': self.rgbDivs,
         'rgbInterp': 'linear',
         'alphaPoints': self.alphaPoints,
         'alphaDivs': self.alphaDivs,
         'alphaInterp': 'linear'}
        rgbCursorParentCont = Container(parent=leftArea, align=uiconst.TOTOP, height=32)
        rgbSliderCont = Container(parent=rgbCursorParentCont, align=uiconst.TOALL, padLeft=20, padRight=20)
        self.rgbSelectedSlider = Slider(parent=rgbSliderCont, align=uiconst.TOTOP, label='rgb pos', name='rgbSelectedSlider', height=32, minValue=0, maxValue=1.0, value=0.0, on_dragging=self.OnSliderDragging)
        self.rgbCursorCont = Container(parent=leftArea, padLeft=12, padRight=12, height=32, align=uiconst.TOTOP)
        alphaSliderCont = Container(parent=leftArea, padLeft=20, padRight=20, align=uiconst.TOBOTTOM, height=32)
        self.alphaCursorCont = Container(parent=leftArea, padLeft=12, padRight=12, align=uiconst.TOBOTTOM, height=32)
        self.alphaSelectedSlider = Slider(parent=alphaSliderCont, align=uiconst.TOTOP, label='alpha pos', name='alphaSelectedSlider', height=32, minValue=0, maxValue=1.0, value=0.0, on_dragging=self.OnAlphaSliderDragging)
        self.gradientPreview = Sprite(parent=leftArea, pos=(20, 20, 20, 20), state=uiconst.UI_NORMAL, align=uiconst.TOALL)
        self.UpdateGradientPreview()
        self.rgbMode = Combo(top=16, align=uiconst.TOTOP, parent=rightArea, label='RGB Mode', options=[('linear', 'linear'), ('cosine', 'cosine'), ('bezier', 'bezier')], name='rgbMode', select='linear', callback=lambda combo, key, index: self.UpdateGradientData({'rgbInterp': key}))
        self.rSlider = Slider(parent=rightArea, label='R', align=uiconst.TOTOP, minValue=0, maxValue=1, value=self.rgbPoints[self.rgbSelected][0], height=28, on_dragging=self.OnRSliderDragging)
        self.gSlider = (Slider(parent=rightArea, label='G', align=uiconst.TOTOP, minValue=0, maxValue=1, value=self.rgbPoints[self.rgbSelected][1], height=28, on_dragging=self.OnGSliderDragging),)
        self.bSlider = (Slider(parent=rightArea, label='B', align=uiconst.TOTOP, minValue=0, maxValue=1, value=self.rgbPoints[self.rgbSelected][2], height=28, on_dragging=self.OnBSliderDragging),)
        Button(parent=rightArea, align=uiconst.TOTOP, label='Delete RGB', func=lambda *args: self.DeleteRGBPoint(self.rgbSelected))
        Button(parent=rightArea, align=uiconst.TOTOP, label='Insert RGB', func=lambda *args: self.AddRGBPoint(self.rgbSelected))
        self.radialCheck = Checkbox(text='Radial', parent=rightArea, align=uiconst.TOTOP, checked=False, callback=lambda *args: self.UpdateGradientData({}))
        Button(parent=rightArea, align=uiconst.TOBOTTOM, label='Insert Alpha', func=lambda *args: self.AddAlphaPoint(self.alphaSelected))
        Button(parent=rightArea, align=uiconst.TOBOTTOM, label='Delete Alpha', func=lambda *args: self.DeleteAlphaPoint(self.alphaSelected))
        self.alphaSlider = Slider(parent=rightArea, label='A', align=uiconst.TOBOTTOM, minValue=0, maxValue=1, value=1, on_dragging=self.OnASliderDragging, height=28)
        self.alphaMode = Combo(align=uiconst.TOBOTTOM, parent=rightArea, label='Alpha Mode', options=[('linear', 'linear'), ('cosine', 'cosine'), ('bezier', 'bezier')], name='alphaMode', select='linear', callback=lambda combo, key, index: self.UpdateGradientData({'alphaInterp': key}))
        self.rgbCursors = []
        self.rgbCursorSelectedSprite = None
        self.CreateRGBCursors()
        Button(parent=self.buttonBar, align=uiconst.TOLEFT, label='Copy Data To Clipboard', func=self.CopyConstructorToClipboard)

    def OnASliderDragging(self, slider):
        self.AlphaCursor(self.alphaSelected, slider.value)

    def OnRSliderDragging(self, slider):
        self.RGBCursor(self.rgbSelected, 0, slider.value)

    def OnGSliderDragging(self, slider):
        self.RGBCursor(self.rgbSelected, 1, slider.value)

    def OnBSliderDragging(self, slider):
        self.RGBCursor(self.rgbSelected, 2, slider.value)

    def OnAlphaSliderDragging(self, slider):
        self.MoveAlphaCursor(self.alphaSelected, slider.value)

    def OnSliderDragging(self, slider):
        self.MoveRGBCursor(self.rgbSelected, slider.value)

    def SelectAlphaCursor(self, idx):
        self.alphaSelected = idx
        self.alphaSlider.SetValue(self.alphaPoints[idx])
        self.alphaSelectedSlider.SetValue(self.alphaDivs[idx])

    def MoveAlphaCursor(self, idx, position):
        self.alphaDivs[idx] = position
        if 'alphaCursorCont' not in self.__dict__:
            return
        if len(self.alphaCursorCont.children) <= idx:
            return
        self.alphaCursorCont.children[idx].left = self.alphaCursors[idx].left - 2
        self.UpdateGradientData({'alphaDivs': self.alphaDivs})

    def AlphaCursor(self, idx, value):
        self.alphaPoints[idx] = value
        self.UpdateGradientData({'alphaPoints': self.alphaPoints})

    def SelectRGBCursor(self, idx):
        self.rgbSelected = idx
        data = self.rgbPoints[idx]
        self.rSlider.SetValue(data[0])
        self.gSlider.SetValue(data[1])
        self.bSlider.SetValue(data[2])
        if self.rgbCursorSelectedSprite:
            self.rgbCursorSelectedSprite.left = self.rgbCursors[idx].left - 2
        self.rgbSelectedSlider.SetValue(self.rgbDivs[idx])

    def MoveRGBCursor(self, idx, position):
        self.rgbDivs[idx] = position
        if 'rgbCursorCont' not in self.__dict__:
            return
        self.rgbCursorCont.children[idx].left = int(self.rgbCursorCont.GetAbsoluteSize()[0] * position) - 4
        self.UpdateGradientData({'rgbDivs': self.rgbDivs})

    def RGBCursor(self, idx, colourComponent, value):
        if 'rgbCursorCont' not in self.__dict__:
            return
        self.rgbPoints[idx][colourComponent] = value
        self.UpdateGradientData({'rgbPoints': self.rgbPoints})

    def CreateAlphaCursors(self):
        while len(self.alphaCursorCont.children) > 0:
            self.alphaCursorCont.children.remove(self.alphaCursorCont.children[0])

        width = self.alphaCursorCont.GetAbsoluteSize()[0] - 8
        self.alphaCursors = map(lambda loc: Container(parent=self.alphaCursorCont, align=uiconst.BOTTOMLEFT, width=10, height=16, top=2, left=int(width * loc)), self.alphaDivs)
        for i, (s, val) in enumerate(zip(self.alphaCursors, self.alphaPoints)):
            middle = Sprite(parent=s, align=uiconst.BOTTOMLEFT, color=(val, val, val), width=6, height=12, top=2, left=2, spriteEffect=trinity.TR2_SFX_FILL)
            Sprite(parent=s, align=uiconst.BOTTOMLEFT, width=10, height=16, color=(0.5, 0.5, 0.5), spriteEffect=trinity.TR2_SFX_FILL)

            def fake(slf, idx):

                def inner(*args):
                    slf.SelectAlphaCursor(idx)

                return inner

            middle.OnMouseDown = fake(self, i)

        self.alphaCursorSelectedSprite = Sprite(parent=self.alphaCursorCont, align=uiconst.BOTTOMLEFT, color=(1.0, 1.0, 1.0), width=14, height=20, left=int(width * self.alphaDivs[self.alphaSelected]) - 2, spriteEffect=trinity.TR2_SFX_FILL)

    def CreateRGBCursors(self):
        while len(self.rgbCursorCont.children) > 0:
            self.rgbCursorCont.children.remove(self.rgbCursorCont.children[0])

        width = self.rgbCursorCont.GetAbsoluteSize()[0] - 8
        self.rgbCursors = map(lambda loc: Container(parent=self.rgbCursorCont, align=uiconst.BOTTOMLEFT, width=10, height=16, top=2, left=int(width * loc)), self.rgbDivs)
        for i, (s, val) in enumerate(zip(self.rgbCursors, self.rgbPoints)):
            middle = Sprite(parent=s, align=uiconst.BOTTOMLEFT, color=tuple(val), width=6, height=12, top=2, left=2, spriteEffect=trinity.TR2_SFX_FILL)
            Sprite(parent=s, align=uiconst.BOTTOMLEFT, width=10, height=16, color=(0.5, 0.5, 0.5), spriteEffect=trinity.TR2_SFX_FILL)

            def fake(slf, idx):

                def inner(*args):
                    slf.SelectRGBCursor(idx)

                return inner

            middle.OnMouseDown = fake(self, i)

        self.rgbCursorSelectedSprite = Sprite(parent=self.rgbCursorCont, align=uiconst.BOTTOMLEFT, color=(1.0, 1.0, 1.0), width=14, height=20, left=int(width * self.rgbDivs[self.rgbSelected]) - 2, spriteEffect=trinity.TR2_SFX_FILL)

    def AddRGBPoint(self, index):
        if index >= len(self.rgbPoints):
            self.rgbPoints.append(self.rgbPoints[-1])
            self.rgbDivs.append(1.0)
            self.SelectRGBCursor(len(self.rgbDivs) - 1)
        elif index < 0:
            self.rgbPoints.insert(0, self.rgbPoints[0])
            self.rgbDivs.insert(0, 0.0)
            self.rgbSelected = 0
            self.SelectRGBCursor(0)
        else:
            value = self.rgbPoints[index]
            location = self.rgbDivs[index]
            if index < len(self.rgbPoints) - 1:
                value = map(lambda (x, y): (x + y) * 0.5, zip(value, self.rgbPoints[index + 1]))
                location = 0.5 * (location + self.rgbDivs[index + 1])
                self.rgbDivs.insert(index + 1, location)
                self.rgbPoints.insert(index + 1, value)
                self.SelectRGBCursor(index + 1)
            elif index > 0:
                value = map(lambda (x, y): (x + y) * 0.5, zip(value, self.rgbPoints[index - 1]))
                location = 0.5 * (location + self.rgbDivs[index - 1])
                self.rgbDivs.insert(index, location)
                self.rgbPoints.insert(index, value)
                self.SelectRGBCursor(index)
            else:
                self.rgbDivs.insert(index, location)
                self.rgbPoints.insert(index, value)
                self.SelectRGBCursor(index)
        self.CreateRGBCursors()
        self.UpdateGradientData({'rgbPoints': self.rgbPoints,
         'rgbDivs': self.rgbDivs})

    def AddAlphaPoint(self, index):
        if index >= len(self.rgbPoints):
            self.alphaPoints.append(self.alphaPoints[-1])
            self.alphaDivs.append(1.0)
            self.SelectAlphaCursor(len(self.alphaDivs) - 1)
        elif index < 0:
            self.alphaPoints.insert(0, self.alphaPoints[0])
            self.alphaDivs.insert(0, 0.0)
            self.SelectAlphaCursor(0)
        else:
            value = self.alphaPoints[index]
            location = self.alphaDivs[index]
            if index < len(self.alphaPoints) - 1:
                value = 0.5 * (value + self.alphaPoints[index + 1])
                location = 0.5 * (location + self.alphaDivs[index + 1])
                self.alphaDivs.insert(index + 1, location)
                self.alphaPoints.insert(index + 1, value)
                self.SelectAlphaCursor(index + 1)
            elif index > 0:
                value = 0.5 * (value + self.alphaPoints[index - 1])
                location = 0.5 * (location + self.alphaDivs[index - 1])
                self.alphaDivs.insert(index, location)
                self.alphaPoints.insert(index, value)
                self.SelectAlphaCursor(index)
            else:
                self.alphaDivs.insert(index, location)
                self.alphaPoints.insert(index, location)
                self.SelectAlphaCursor(index + 1)
        self.CreateAlphaCursors()
        self.UpdateGradientData({'alphaPoints': self.alphaPoints,
         'alphaDivs': self.alphaDivs})

    def DeleteRGBPoint(self, index):
        if len(self.rgbPoints) <= 1:
            return
        if index < 0 or index >= len(self.rgbPoints):
            return
        self.rgbPoints = self.rgbPoints[:index] + self.rgbPoints[index + 1:]
        self.rgbDivs = self.rgbDivs[:index] + self.rgbDivs[index + 1:]
        self.CreateRGBCursors()
        self.UpdateGradientData({'rgbPoints': self.rgbPoints,
         'rgbDivs': self.rgbDivs})

    def DeleteAlphaPoint(self, index):
        if len(self.alphaPoints) <= 1:
            return
        if index < 0 or index >= len(self.alphaPoints):
            return
        self.alphaPoints = self.alphaPoints[:index] + self.alphaPoints[index + 1:]
        self.alphaDivs = self.alphaDivs[:index] + self.alphaDivs[index + 1:]
        self.CreateAlphaCursors()
        self.UpdateGradientData({'alphaPoints': self.alphaPoints,
         'alphaDivs': self.alphaDivs})

    def RemoveRGBPoint(self, location):
        if len(self.rgbPoints) <= 1:
            return
        if location >= 1.0:
            self.rgbPoints = self.rgbPoints[:-1]
            self.rgbDivs = self.rgbDivs[:-1]
        elif location <= 0.0:
            self.rgbPoints = self.rgbPoints[1:]
            self.rgbDivs = self.rgbDivs[1:]
        else:
            best = 10000
            loc = 0.0
            idx = 0
            for i, k in enumerate(self.rgbDivs):
                dist = abs(k - location)
                if dist < best:
                    best = dist
                    idx = i
                    loc = k

            self.rgbPoints.remove(self.rgbPoints[idx])
            self.rgbDivs.remove(loc)
        self.UpdateGradientData({'rgbPoints': self.rgbPoints,
         'rgbDivs': self.rgbDivs})

    def UpdateGradientData(self, data):
        self.gradientData.update(data)
        self.UpdateGradientPreview()

    def UpdateGradientPreview(self):
        radial = False
        if hasattr(self, 'radialCheck'):
            radial = self.radialCheck.checked
        self.CreateRGBCursors()
        self.CreateAlphaCursors()
        dataStr = str(self.gradientData)
        if radial:
            self.gradientPreview.SetTexturePath('dynamic:/gradient_radial/' + dataStr)
        else:
            self.gradientPreview.SetTexturePath('dynamic:/gradient/' + dataStr)

    def OnResize_(self, *args):
        Window.OnResize_(self, *args)
        if hasattr(self, 'rgbCursorCont'):
            self.CreateRGBCursors()
        if hasattr(self, 'alphaCursorCont'):
            self.CreateAlphaCursors()

    def SpriteConstructorText(self):
        interp = {'linear': 'GradientConst.INTERP_LINEAR',
         'cosine': 'GradientConst.INTERP_COSINE',
         'bezier': 'GradientConst.INTERP_BEZIER'}
        dataWithDefaults = {'rgbDivs': [0.0, 1.0],
         'rgbPoints': [(1.0, 0.0, 0.0), (0.0, 1.0, 1.0)],
         'alphaDivs': [0.0, 1.0],
         'alphaPoints': [1.0, 1.0],
         'alphaInterp': 'linear',
         'rgbInterp': 'linear'}
        dataWithDefaults.update(self.gradientData)
        text = 'GradientSprite(\n'
        text += '\tparent = uicore.desktop, \n'
        text += '\tpos = (0, 0, 256, 256), \n'
        text += '\trgbData = ' + str(zip(dataWithDefaults['rgbDivs'], map(tuple, dataWithDefaults['rgbPoints']))) + ', \n'
        text += '\talphaData = ' + str(zip(dataWithDefaults['alphaDivs'], dataWithDefaults['alphaPoints'])) + ', \n'
        text += '\talphaInterp = ' + interp[dataWithDefaults['alphaInterp']] + ', \n'
        text += '\tcolorInterp = ' + interp[dataWithDefaults['rgbInterp']]
        if self.radialCheck.checked:
            text += ', \n\tradial = True, \n'
            text += '\ttoCorners =' + str(dataWithDefaults.get('toCorners', False))
        text += '\n\t)'
        return text

    def CopyConstructorToClipboard(self, *args):
        blue.pyos.SetClipboardData(self.SpriteConstructorText())
