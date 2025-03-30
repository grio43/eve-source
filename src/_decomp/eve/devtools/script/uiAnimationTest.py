#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\devtools\script\uiAnimationTest.py
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.scrollentries import ScrollEntryNode, SE_GenericCore
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditInteger import SingleLineEditInteger
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.transform import Transform
from carbonui.primitives.sprite import Sprite
from carbonui.primitives.container import Container
from carbonui.control.button import Button
from carbonui.control.checkbox import Checkbox
from carbonui.control.radioButton import RadioButton
from carbonui.uicore import uicore
from eve.client.script.ui.control.eveScroll import Scroll
from carbonui.control.window import Window
MODE_NORMAL = 1
MODE_INPUT = 2
MODE_CODE = 3

class TestAnimationsWnd(Window):
    __guid__ = 'form.UIAnimationTest'
    __notifyevents__ = ['OnUITestAnimationSelected', 'OnTestAnimationsPlayAnimation']
    default_minSize = (500, 300)
    default_caption = 'UI Animations'
    default_windowID = 'UIAnimationTest'

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        if self.sr.main is None:
            self.sr.main = Container(parent=self.sr.maincontainer)
        self.mainItem = None
        self.mainSprite = None
        self.mainTransform = None
        self.inputObj = attributes.get('animObj', None)
        self.codeEdit = None
        self.duration = 0.5
        self.loops = 1
        self.curveSet = None
        if self.inputObj:
            self.mode = MODE_INPUT
        else:
            self.mode = MODE_NORMAL
        self.topCont = Container(name='topCont', parent=self.sr.main, align=uiconst.TOTOP, height=20)
        self.mainCont = Container(name='mainCont', parent=self.sr.main, align=uiconst.TOTOP, height=200)
        self.topRightCont = Container(name='topRightCont', parent=self.mainCont, align=uiconst.TORIGHT, width=100)
        self.spriteCont = Container(name='spriteCont', parent=self.mainCont)
        from carbonui.primitives.gridcontainer import GridContainer
        self.buttonCont = GridContainer(name='buttonCont', parent=self.sr.main, align=uiconst.TOBOTTOM, height=30, columns=3, lines=1)
        self.bottomCont = Container(name='bottomCont', parent=self.sr.main)
        self.ConstructTopCont()
        self.ConstructTopRightCont()
        self.ConstructBottomCont()
        self.ConstructMainCont()
        btns = [('Uncheck all', self.UncheckAll, ()), ('Stop all', self.StopAllAnimations, ()), ('Play selected', self.PlaySelected, ())]
        for label, func, args in btns:
            Button(parent=Container(parent=self.buttonCont), label=label, func=func, align=uiconst.CENTER)

    def ConstructTopCont(self):
        checkBoxes = [(MODE_NORMAL, 'Normal'), (MODE_CODE, 'Code')]
        if self.inputObj:
            checkBoxes.append((MODE_INPUT, 'Input object'))
        for retval, text in checkBoxes:
            RadioButton(parent=self.topCont, text=text, groupname='radioGroup', align=uiconst.TOLEFT, checked=retval == self.mode, callback=self.OnRadioButtonsChanged, retval=retval, width=100)

    def ConstructTopRightCont(self):
        self.durationEdit = SingleLineEditFloat(parent=self.topRightCont, name='durationEdit', align=uiconst.TOPRIGHT, label='duration', maxValue=10.0, setvalue=self.duration, pos=(5, 14, 100, 0), OnChange=self.OnDurationEditChanged)
        self.loopsEdit = SingleLineEditInteger(parent=self.topRightCont, name='loopEdit', align=uiconst.TOPRIGHT, label='loops', minValue=-1, maxValue=20, setvalue=self.loops, pos=(5, 52, 100, 0), OnChange=self.OnLoopEditChanged)
        options = [ (funcName, getattr(uiconst, funcName)) for funcName in dir(uiconst) if funcName.startswith('ANIM_') and funcName != 'ANIM_LOOPCYCLE' ]
        self.curveTypeCombo = Combo(parent=self.topRightCont, label='curveType', options=options, name='AnimationCurveTypeCombo', align=uiconst.TOPRIGHT, pos=(5, 92, 100, 0), width=100)

    def ConstructMainCont(self):
        self.spriteCont.Flush()
        self.mainItem = None
        self.mainTransform = None
        self.mainSprite = None
        self.codeEdit = None
        if self.mode is MODE_NORMAL:
            self.mainTransform = Transform(parent=self.spriteCont, align=uiconst.CENTER, pos=(0, 0, 128, 128))
            self.mainSprite = Sprite(parent=self.mainTransform, align=uiconst.CENTER, pos=(0, 0, 128, 128), texturePath='res:/UI/Texture/CorpLogoLibs/419.png', texturePathSecondary='res:/UI/Texture/colorgradient.dds')
        elif self.mode is MODE_CODE:
            self.codeEdit = SingleLineEditText(parent=self.spriteCont, align=uiconst.TOTOP, label='Code that returns a UI object:', heigt=15, padding=(10, 30, 150, 0), setvalue=settings.user.ui.Get('TestAnimationsWndCode', 'uicore.layer.sidePanels'))
            Button(parent=self.spriteCont, align=uiconst.TOPLEFT, label='Assign result', top=60, left=5, func=self.OnAssignCodeBtn)
        elif self.mode is MODE_INPUT:
            self.mainItem = self.inputObj

    def OnDurationEditChanged(self, value):
        self.duration = float(value.replace(',', '.'))

    def OnLoopEditChanged(self, value):
        try:
            self.loops = int(value)
        except:
            self.loops = 0.5

    def ConstructBottomCont(self):
        self.scroll = Scroll(parent=self.bottomCont, multiselect=True)
        self.LoadScroll()

    def LoadScroll(self):
        scrolllist = []
        for funcName in dir(uicore.animations):
            if funcName.startswith('_'):
                continue
            func = getattr(uicore.animations, funcName)
            if not callable(func):
                continue
            node = ScrollEntryNode(decoClass=TestAnimationsCheckbox, label=funcName, animFunc=func)
            scrolllist.append(node)

        self.scroll.Load(contentList=scrolllist)

    def OnRadioButtonsChanged(self, button):
        self.mode = button.GetGroupValue()
        self.ConstructMainCont()

    def OnAssignCodeBtn(self, *args):
        exec 'self.mainItem=%s' % self.codeEdit.GetValue()
        settings.user.ui.Get('TestAnimationsWndCode', self.codeEdit.GetValue())

    def OnUITestAnimationSelected(self, animFunc):
        animFunc(self.mainItem)

    def PlaySelected(self, *args):
        if self.curveSet:
            self.curveSet.Stop()
        nodes = self.scroll.GetNodes()
        for node in nodes:
            if node.checked:
                self.PlayAnimation(node.animFunc, node.label)

    def StopAllAnimations(self, *args):
        for obj in (self.mainItem,
         self.mainTransform,
         self.mainSprite,
         self.inputObj):
            if obj:
                obj.StopAnimations()

    def PlayAnimation(self, animFunc, funcName):
        if self.mode == MODE_NORMAL:
            if self.mainSprite and funcName.startswith('Sp'):
                obj = self.mainSprite
            else:
                obj = self.mainTransform
        else:
            obj = self.mainItem
        if obj:
            self.curveSet = animFunc(obj, duration=self.duration, loops=self.loops, curveType=self.curveTypeCombo.GetValue())

    def OnTestAnimationsPlayAnimation(self, animFunc, funcName):
        self.PlayAnimation(animFunc, funcName)

    def UncheckAll(self, *args):
        self.LoadScroll()

    def SetAnimationObject(self, animObj):
        self.mainItem = self.inputObj = animObj


class TestAnimationsCheckbox(SE_GenericCore):
    __guid__ = 'uicls.SE_TestAnimationsCheckbox'
    default_state = uiconst.UI_PICKCHILDREN

    def ApplyAttributes(self, attributes):
        SE_GenericCore.ApplyAttributes(self, attributes)
        self.checkbox = Checkbox(parent=self, align=uiconst.CENTERLEFT, pos=(45, 0, 16, 16), idx=0)
        self.checkbox.OnChange = self.CheckBoxChange
        self.btn = Button(parent=self, align=uiconst.TOLEFT, fixedwidth=45, label='Play', func=self.PlayAnimation)

    def CheckBoxChange(self, checkbox):
        self.sr.node.checked = checkbox.checked

    def Load(self, *args):
        SE_GenericCore.Load(self, *args)
        self.sr.label.left = 60

    def PlayAnimation(self, *args):
        sm.ScatterEvent('OnTestAnimationsPlayAnimation', self.sr.node.animFunc, self.sr.node.label)
