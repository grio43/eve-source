#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\control\hackingProgressBar.py
import math
import random
import blue
import uthread
from carbonui import uiconst
from carbonui.primitives.container import Container
from carbonui.primitives.fill import Fill
from carbonui.primitives.frame import Frame
from carbonui.util.color import Color
from carbonui.util.effect import UIEffects
from eve.client.script.ui.control.eveLabel import EveHeaderMedium, Label
from eve.client.script.ui.util import uix

class HackingProgressBar(Container):
    default_name = 'hackingProgressBar'
    HEXDIGITS = ['0',
     '1',
     '2',
     '3',
     '4',
     '5',
     '6',
     '7',
     '8',
     '9',
     'A',
     'B',
     'C',
     'D',
     'E',
     'F']

    def ApplyAttributes(self, attributes):
        Container.ApplyAttributes(self, attributes)
        color = attributes.Get('color', Color.WHITE)
        backgroundColor = attributes.Get('backgroundColor', None)
        self.value = attributes.Get('value', 0.0)
        self.uiEffects = UIEffects()
        self.busy = False
        self.queuedSetValue = None
        self.gaugeCont = Container(parent=self, name='gaugeCont', pos=(0,
         0,
         self.width,
         self.height), align=uiconst.TOPLEFT)
        Frame(parent=self.gaugeCont, color=(1.0, 1.0, 1.0, 0.2))
        self.gauge = Fill(parent=self.gaugeCont, name='gauge', align=uiconst.TOLEFT, width=0, color=color)
        if backgroundColor is None:
            backgroundColor = Color(*color).SetAlpha(0.2).GetRGBA()
        Fill(parent=self.gaugeCont, name='background', color=backgroundColor)
        testString = ''.join(self.HEXDIGITS)
        fontSize = 1
        textHeight = uix.GetTextHeight(testString, fontsize=fontSize)
        while textHeight < self.height:
            fontSize += 1
            textHeight = uix.GetTextHeight(testString, fontsize=fontSize)
        else:
            fontSize -= 1
            textHeight = uix.GetTextHeight(testString, fontsize=fontSize)

        self.textCont = Container(parent=self, name='textCont', pos=(0,
         0,
         self.width,
         textHeight), align=uiconst.CENTER, clipChildren=True, idx=0)
        self.text = Label(parent=self.textCont, name='hackText', align=uiconst.TOALL, fontsize=fontSize, text='')
        hackText = random.choice(self.HEXDIGITS)
        while uix.GetTextWidth(hackText[1:], fontsize=fontSize) < self.width:
            hackText += random.choice(self.HEXDIGITS)

        self.text.text = hackText
        self.SetValueInstantly(self.value)
        self.hackStrings = ['Hacking Gibson...',
         'Cracking Codes...',
         'Inserting Rootkit...',
         'Defeating ICE...',
         'Circumventing Firewall...',
         'Polymorphing Virii...',
         'Erasing Logs...',
         'Reticulating Splines...',
         'Twisting Mersenne...',
         'Curving Ellipses...',
         'Analyzing Ciphers...',
         'Factoring Primes...']
        self.hackText = EveHeaderMedium(text='', parent=self, align=uiconst.CENTERBOTTOM, height=20, state=uiconst.UI_HIDDEN, top=-24)
        self.active = True
        uthread.new(self._CycleText)

    def SetValue(self, value, frequency = 10.0):
        if self.value == value:
            return
        if self.busy:
            self.queuedSetValue = (self.gauge, value, frequency)
            return
        uthread.new(self._SetValue, self.gauge, value, frequency)

    def SetValueInstantly(self, value):
        self.value = value
        self.gauge.width = int(self.width * value)

    def _SetValue(self, gauge, value, frequency):
        if not self or self.destroyed:
            return
        self.busy = True
        self.value = value
        self.uiEffects.MorphUIMassSpringDamper(gauge, 'width', int(self.width * value), newthread=0, float=0, dampRatio=0.6, frequency=frequency, minVal=0, maxVal=self.width, maxTime=2.0)
        if not self or self.destroyed:
            return
        self.busy = False
        if self.queuedSetValue:
            nextSetValue = self.queuedSetValue
            self.queuedSetValue = None
            self._SetValue(*nextSetValue)

    def _CycleText(self):
        t = 0.0
        lastTextChange = blue.os.GetWallclockTime()
        self.hackText.text = random.choice(self.hackStrings)
        self.hackText.state = uiconst.UI_DISABLED
        while self and not self.destroyed and self.active:
            t += 1.0 / max(1.0, blue.os.fps)
            self.hackText.opacity = math.cos(t * math.pi / 0.5) * 0.4 + 0.6
            if lastTextChange + 5 * const.SEC < blue.os.GetWallclockTime():
                self.hackText.text = random.choice(self.hackStrings)
                lastTextChange = blue.os.GetWallclockTime()
            while uix.GetTextWidth(self.text.text[1:], fontsize=self.text.fontsize) - (60 + abs(self.text.left)) < self.width:
                self.text.text += random.choice(self.HEXDIGITS)

            self.text.left -= 2
            firstLetterWidth = uix.GetTextWidth(self.text.text[0], fontsize=self.text.fontsize)
            while abs(self.text.left) > firstLetterWidth:
                self.text.text = self.text.text[1:]
                self.text.left += firstLetterWidth
                firstLetterWidth = uix.GetTextWidth(self.text.text[0], fontsize=self.text.fontsize)

            blue.pyos.synchro.SleepWallclock(20)

        while self and not self.destroyed and self.text.opacity > 0.0:
            self.text.opacity -= 0.03
            self.text.opacity = max(self.text.opacity, 0.0)
            blue.pyos.synchro.SleepWallclock(70)

    def Finalize(self, complete = False):
        uthread.new(self._FinishText, complete)

    def _FinishText(self, complete):
        flipCount = 0
        self.hackText.opacity = 0.8
        self.hackText.state = uiconst.UI_HIDDEN
        self.hackText.text = 'HACK COMPLETE!' if complete else 'DISCONNECTING...'
        self.active = False
        while flipCount < 3:
            blue.pyos.synchro.SleepWallclock(500)
            if not self or self.destroyed:
                return
            if self.hackText.state == uiconst.UI_HIDDEN:
                self.hackText.state = uiconst.UI_DISABLED
            else:
                self.hackText.state = uiconst.UI_HIDDEN
                flipCount += 1

        self.state = uiconst.UI_HIDDEN
