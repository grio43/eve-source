#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\shaderDebugger.py
import logging
import trinity
import uthread
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.window import Window
from carbonui.primitives.container import Container
from carbonui.primitives.containerAutoSize import ContainerAutoSize
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import EveCaptionLarge
from evegraphics.graphicEffects.effectDebug import EffectDebugger
from fsdBuiltData.common.graphicIDs import GetGraphicFile
from evegraphics.utils import BuildSOFDNAFromGraphicID
log = logging.getLogger(__name__)

class ShaderDebugger(Window):
    default_caption = 'ShaderDebugger'
    default_windowID = 'ShaderDebugger'
    default_minSize = (350, 220)
    __notifyevents__ = ['OnLoadScene']

    def ApplyAttributes(self, attributes):
        Window.ApplyAttributes(self, attributes)
        self.spaceObject = attributes.Get('object', None)
        graphicID = attributes.Get('graphicID', None)
        graphicFile = GetGraphicFile(graphicID)
        dna = BuildSOFDNAFromGraphicID(graphicID)
        self.attributeLookup = {}
        descriptor = graphicFile or dna or getattr(self.spaceObject, '__bluetype__', 'Unknown')
        self.debugger = EffectDebugger(self.spaceObject, sm.GetService('sceneManager').GetActiveScene())
        mainContainer = ContainerAutoSize(name='mainContainer', align=uiconst.TOALL, parent=self.content)
        nameContainer = Container(name='nameContainer', parent=mainContainer, align=uiconst.TOTOP, height=45, padBottom=16)
        EveCaptionLarge(name='name', parent=nameContainer, align=uiconst.TOALL, text=descriptor, left=4)
        Button(name='refresh', align=uiconst.TORIGHT, parent=nameContainer, padLeft=2, padRight=2, label='Refresh', func=self.OnRefresh)
        for i, (debugOption, values) in enumerate(self.debugger.GetDebugOptions().iteritems()):
            container = Container(name='optionContainer%d' % i, parent=mainContainer, align=uiconst.TOTOP, height=60, padBottom=5)
            c2 = Container(name='restContainer%d' % i, parent=container, align=uiconst.TOALL, height=30, padRight=130)
            toggleContainer = Container(name='toggleContainer%d' % i, parent=container, align=uiconst.TORIGHT, width=120, height=40, top=-5, padLeft=2)
            buttonContainer = Container(name='buttonContaier%d' % i, parent=c2, align=uiconst.TORIGHT, width=75, height=30)
            rightArrow = Button(name='right_%s' % debugOption, align=uiconst.TORIGHT, parent=buttonContainer, padLeft=2, padRight=2, texturePath='res:/UI/Texture/Shared/triangleRight.png', func=self.OnRight)
            leftArrow = Button(name='left_%s' % debugOption, align=uiconst.TORIGHT, parent=buttonContainer, padLeft=2, padRight=2, texturePath='res:/UI/Texture/Shared/triangleLeft.png', func=self.OnLeft)
            debugToggle = Checkbox(parent=toggleContainer, name='toggle_%s' % debugOption, text='Debug', align=uiconst.TOTOP, checked=True, callback=self.OnToggle)
            displayToggle = Checkbox(parent=toggleContainer, name='display_%s' % debugOption, text='Display', align=uiconst.TOTOP, checked=True, callback=self.OnDisplayToggle)
            combo = Combo(parent=c2, name='combo_%s' % debugOption, label=self.debugger.GetDescriptiveName(debugOption), padRight=74, height=30, align=uiconst.TOALL, callback=self.OnComboChange, options=[ (label, value) for label, value in values.iteritems() ], idx=0)
            combo.SetValue(self.debugger.GetDebugValue(debugOption))
            self.attributeLookup[debugOption] = [combo,
             leftArrow,
             rightArrow,
             debugToggle,
             displayToggle]

    def Close(self, setClosed = False, *args, **kwds):
        super(ShaderDebugger, self).Close()
        self.spaceObject = None
        self.debugger.CleanUp()
        self.debugger = None

    def OnComboChange(self, combo, __, value):
        debugOption = combo.name.replace('combo_', '')
        self.debugger.ApplyDebugByValue(debugOption, value)

    def OnRight(self, button):
        optionName = button.name.replace('right_', '')
        combo = self.attributeLookup[optionName][0]
        nextIndex = (combo.GetIndex() + 1) % len(combo.GetSelectableEntries())
        combo.SelectItemByIndex(nextIndex)
        self.debugger.ApplyDebugByValue(optionName, combo.GetValue())

    def OnLeft(self, button):
        optionName = button.name.replace('left_', '')
        combo = self.attributeLookup[optionName][0]
        prevIndex = combo.GetIndex() - 1
        combo.SelectItemByIndex(prevIndex)
        self.debugger.ApplyDebugByValue(optionName, combo.GetValue())

    def OnToggle(self, checkbox):
        optionName = checkbox.name.replace('toggle_', '')
        combo, left, right, _, __ = self.attributeLookup[optionName]
        if checkbox.GetValue():
            self.debugger.Enable(optionName)
            combo.Enable()
            left.Enable()
            right.Enable()
        else:
            self.debugger.Disable(optionName)
            combo.Disable()
            left.Disable()
            right.Disable()

    def OnDisplayToggle(self, checkbox):
        optionName = checkbox.name.replace('display_', '')
        combo, left, right, _, __ = self.attributeLookup[optionName]
        if checkbox.GetValue():
            self.debugger.Show(optionName)
            combo.Enable()
            left.Enable()
            right.Enable()
        else:
            self.debugger.Hide(optionName)
            combo.Disable()
            left.Disable()
            right.Disable()

    def OnRefresh(self, *args):
        self.debugger.Update(True)

    def OnLoadScene(self, *args):
        if isinstance(self.spaceObject, trinity.EveSpaceScene):
            uthread.new(self._PostSceneLoad)

    def _PostSceneLoad(self):
        trinity.WaitForResourceLoads()
        self.spaceObject = sm.GetService('sceneManager').GetActiveScene()
        self.debugger = EffectDebugger(self.spaceObject, sm.GetService('sceneManager').GetActiveScene())
        for optionName, elements in self.attributeLookup.iteritems():
            combo, _, __, debug, display = elements
            self.debugger.ApplyDebugByValue(optionName, combo.GetValue())
            if not debug.GetValue():
                self.debugger.Disable(optionName)
            if not display.GetValue():
                self.debugger.Hide(optionName)
