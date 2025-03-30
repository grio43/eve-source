#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\environmentTemplateSwitcher.py
import blue
from carbonui import uiconst
from carbonui.control.combo import Combo
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from carbonui.control.window import Window
from eveexceptions import UserError
from evegraphics.environments.environmentManager import EnvironmentManager
from fsdBuiltData.client.environmentTemplates import GetEnvironmentTemplates
from carbonui.button.group import ButtonGroup
from tacticalNavigation.ballparkFunctions import ConvertPositionToGlobalSpace
from carbonui.control.checkbox import Checkbox
from carbonui.control.buttonIcon import ButtonIcon
from carbonui.control.button import Button
ENVIRONMENT_NAME = 'DEBUG_ENVIRONMENT_'

class EnvironmentTemplateSwitcher(object):
    ENVIRONMENT_COUNTER = 0

    def __init__(self):
        self.name = 'Environment Template Switcher'
        self.windowID = 'Environment_Template_' + self.name
        self.state = {}
        self.sortedOptionList = []
        self.activeEnvironments = []

    def OnClose(self, *args):
        em = EnvironmentManager.GetInstance()
        for env in self.activeEnvironments:
            em.RemoveEnvironment(env)

    def GetOptions(self):
        templates = GetEnvironmentTemplates()
        templateOptions = [ (template.description, templateID) for templateID, template in templates.iteritems() ]
        templateOptions.sort(key=lambda x: x[0])
        return [('None', -1)] + templateOptions

    def ShowUI(self):
        wnd = Window.Open(windowID=self.windowID)
        wnd.SetMinSize([400, 200])
        wnd.SetCaption(self.name)
        wnd._OnClose = self.OnClose
        main = wnd.GetMainArea()
        self.sortedOptionList = [ templateID for _, templateID in self.GetOptions() ]
        ballIdInputContainer = Container(name='ballIdInputC', parent=main, align=uiconst.TOTOP, height=20, padLeft=10)
        refreshContainer = Container(name='refreshC', parent=main, align=uiconst.TOBOTTOM, height=20, padRight=5, padBottom=5)
        environmentTemplateContainer = Container(name='templateC', parent=main, align=uiconst.TOLEFT, padLeft=5, width=5)
        self.MakeEnvInput(main)
        shipID = session.shipid
        self.ballID = SingleLineEditText(name='ballID', parent=ballIdInputContainer, align=uiconst.TOALL, width=30, height=15, setvalue=str(shipID), hint='default: your shipID')
        Button(name='RefreshButton', align=uiconst.TORIGHT, parent=refreshContainer, label='Refresh', func=self.Refresh)
        Button(name='CreateEnvInput', align=uiconst.TOLEFT, parent=refreshContainer, label='Add new template row', func=lambda *args: self.MakeEnvInput(main), padLeft=5)

    def Refresh(self, *args):
        Window.CloseIfOpen(windowID=self.windowID)
        Window.Open(windowID=self.windowID)
        self.state = {}
        self.activeEnvironments = []
        self.ShowUI()

    def MakeEnvInput(self, parent):
        inputContainer = Container(name='inputContainer', parent=parent, align=uiconst.TOTOP, padTop=10, padBottom=10, padLeft=10, padRight=10, height=20)
        self.ENVIRONMENT_COUNTER = self.ENVIRONMENT_COUNTER + 1
        index = self.ENVIRONMENT_COUNTER
        ButtonIcon(name='DeleteTemplateRow', parent=inputContainer, align=uiconst.CENTERLEFT, width=14, height=14, iconSize=14, texturePath='res:/UI/Texture/Icons/25_64_12.png', func=lambda : self.RemoveEnvInput(index, inputContainer))
        envtemplateCombo = Combo(name='myCombo', parent=inputContainer, options=self.GetOptions(), callback=lambda *args: self.OnEnvironmentSelected(index), align=uiconst.TOLEFT, width=180, padLeft=20)
        toggle = Checkbox(name='Toggle', parent=inputContainer, hint='Toggle on/off', checked=True, callback=lambda *args: self.ToggleEnv(index), align=uiconst.TORIGHT, padLeft=10)
        buttonGroup = ButtonGroup(name='buttonGroup', parent=inputContainer, align=uiconst.TORIGHT, padLeft=10)
        buttonGroup.AddButton('Previous', lambda *args: self.OnPrev(index))
        buttonGroup.AddButton('Next', lambda *args: self.OnNext(index))
        self.state[index] = (envtemplateCombo, toggle)

    def RemoveEnvInput(self, index, container):
        container.Close()
        del self.state[index]
        self.RemoveActiveEnvironment(index)

    def ToggleEnv(self, index):
        toggle = self.state[index][1]
        if toggle.GetValue():
            templateID = self.GetSelectedTemplateID(index)
            self._SetTemplate(index, templateID)
        else:
            self.RemoveActiveEnvironment(index)

    def GetSelectedTemplateID(self, index):
        currEnvTemplate = self.state[index][0]
        templateID = currEnvTemplate.GetValue()
        return templateID

    def OnEnvironmentSelected(self, index):
        templateID = self.GetSelectedTemplateID(index)
        self._SetTemplate(index, templateID)

    def OnPrev(self, index):
        templateID = self.GetSelectedTemplateID(index)
        prevTemplateIndex = self.sortedOptionList.index(templateID) - 1
        newTemplateID = self.sortedOptionList[prevTemplateIndex]
        self._SetTemplate(index, newTemplateID)

    def OnNext(self, index):
        templateID = self.GetSelectedTemplateID(index)
        nextTemplateIndex = self.sortedOptionList.index(templateID) + 1
        nextTemplateIndex = nextTemplateIndex % len(self.sortedOptionList)
        newTemplateID = self.sortedOptionList[nextTemplateIndex]
        self._SetTemplate(index, newTemplateID)

    def _SetTemplate(self, index, templateID):
        toggle = self.state[index][1]
        em = EnvironmentManager.GetInstance()
        self.RemoveActiveEnvironment(index)
        self.state[index][0].SetValue(templateID)
        if templateID < 0 or not toggle.GetValue():
            return
        ball = sm.GetService('michelle').GetBall(long(self.ballID.GetValue()))
        if ball is None:
            raise UserError('Please enter a valid id!')
        ballPos = ball.GetVectorAt(blue.os.GetSimTime())
        pos = (ballPos.x, ballPos.y, ballPos.z)
        envPos = ConvertPositionToGlobalSpace(pos)
        em.AddEnvironment(ENVIRONMENT_NAME + str(index), envPos, templateId=templateID, solarSystemId=session.solarsystemid, anchorTranslationCurve=ball)
        self.activeEnvironments.append(ENVIRONMENT_NAME + str(index))

    def RemoveActiveEnvironment(self, index):
        em = EnvironmentManager.GetInstance()
        em.RemoveEnvironment(ENVIRONMENT_NAME + str(index))
        if ENVIRONMENT_NAME + str(index) in self.activeEnvironments:
            envIndex = self.activeEnvironments.index(ENVIRONMENT_NAME + str(index))
            del self.activeEnvironments[envIndex]
