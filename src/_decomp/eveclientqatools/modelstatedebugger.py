#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\modelstatedebugger.py
import weakref
import blue
import trinity
import uthread2
from carbonui import uiconst
from carbonui.control.checkbox import Checkbox
from carbonui.control.combo import Combo
from carbonui.control.scrollContainer import ScrollContainer
from carbonui.control.singlelineedits.singleLineEditFloat import SingleLineEditFloat
from carbonui.control.singlelineedits.singleLineEditText import SingleLineEditText
from carbonui.primitives.container import Container
from datetime import datetime
from carbonui.control.button import Button
from eve.client.script.ui.control.eveLabel import Label
from carbonui.control.window import Window

def CreateScrollContainer(name, width, height, parent, align = uiconst.TOTOP):
    container = ScrollContainer(name=name + '_scrollContainer', align=align, width=width, height=height, padLeft=5, padRight=5, padTop=10, parent=parent)
    return container


def CreateLabel(name, width, height, parent, padLeft = 5, padTop = 0, align = uiconst.TOLEFT, padBottom = 0):
    container = CreateContainer(name, parent)
    label = Label(name=name, text=name, align=align, width=width, height=height, padLeft=padLeft, padRight=5, padTop=padTop, padBottom=padBottom, parent=container)
    return label


def CreateInput(label, value, callback, parent, padLeft = 5, align = uiconst.TOLEFT):
    name = label
    container = CreateContainer(name, parent, padLeft=padLeft)
    inputField = _CreateInput(name, value, callback, label, container, align)
    return inputField


def _CreateInput(name, value, callback, label, parent, padLeft = 5, align = uiconst.TOLEFT, padBottom = 0, minValue = None, maxValue = None):
    return SingleLineEditFloat(name=name + '_input', align=align, label=label, parent=parent, width=150, height=18, padBottom=padBottom, padLeft=padLeft, setvalue=value, OnFocusLost=callback, minValue=minValue, maxValue=maxValue, OnReturn=callback)


def _CreateTextInput(name, value, callback, label, parent, padLeft = 5, align = uiconst.TOLEFT, padBottom = 0):
    return SingleLineEditText(name=name + '_input', align=align, label=label, parent=parent, width=150, height=18, padBottom=padBottom, padLeft=padLeft, setvalue=value, OnFocusLost=callback, OnReturn=callback)


def CreateContainer(name, parent, padTop = 16, padBottom = 0, align = uiconst.TOTOP, padLeft = 5):
    return Container(name=name + '_container', parent=parent, align=align, height=18, padTop=padTop, padBottom=padBottom, padLeft=padLeft, padRight=5)


def CreateCombo(name, values, callback, select, label, parent, padLeft = 8, align = uiconst.TOLEFT, width = 220, padBottom = 0):
    container = CreateContainer(name, parent, padBottom=padBottom)
    return Combo(name=name + '_combo', align=align, width=width, height=18, parent=container, label=label, options=[ (name, i) for i, name in enumerate(values) ], callback=callback, select=select, padLeft=padLeft)


class Tr2ControllerView(object):

    def __init__(self, tr2Controller):
        self.tr2Controller = tr2Controller
        self.parent = None
        self.variableViews = []

    def Setup(self, parent):
        self.parent = parent
        hasEvents = len(self.tr2Controller.eventHandlers) > 0
        hasVariables = len(self.tr2Controller.variables) > 0
        controllerLabel = CreateLabel(name=self.tr2Controller.name, width=200, height=12, parent=parent)
        if hasEvents or hasVariables:
            self.SetupEvents(parent)
            self.SetupVariables(parent)
        else:
            controllerLabel.SetText(self.tr2Controller.name + ' ( has not variables or events )')

    def SetupVariables(self, parent):
        for variable in self.tr2Controller.variables:
            uiElem = None
            if variable.variableType == 2:
                container = CreateContainer(name=variable.name, parent=parent, padTop=0)
                uiElem = Checkbox(name=variable.name, align=uiconst.TOLEFT, width=300, height=18, padLeft=30, padTop=0, padBottom=8, parent=container, text=variable.name + '[' + self.VariableTypeToString(variable.variableType) + ']', callback=self.OnBooleanVariableChanged(variable))
            elif variable.variableType == 3:
                uiElem = CreateCombo(name=variable.name, values=[ str(i) for i in range(0, len(variable.enumValues.split(','))) ], callback=self.OnEnumVariableChanged(variable), select=int(variable.value), label=variable.name + '(' + variable.enumValues + ')' + '[' + self.VariableTypeToString(variable.variableType) + ']', parent=parent, padBottom=8, padLeft=30)
            else:
                uiElem = CreateInput(variable.name + '[' + self.VariableTypeToString(variable.variableType) + ']', str(variable.value), self.OnNumericVariableChanged(variable), parent, 30)
            self.variableViews.append(uiElem)

    def OnEnumVariableChanged(self, variable):

        def _OnVariableChanged(comboBox, value, index):
            variable.value = int(index)

        return _OnVariableChanged

    def OnBooleanVariableChanged(self, variable):

        def _OnVariableChanged(checkBox):
            variable.value = 1 if checkBox._checked else 0

        return _OnVariableChanged

    def OnNumericVariableChanged(self, variable):

        def _OnVariableChanged(*args):
            if len(args) > 0:
                try:
                    variable.value = float(args[0].text)
                except:
                    pass

        return _OnVariableChanged

    def VariableTypeToString(self, variableTypeID):
        if variableTypeID == 1:
            return 'Integer'
        if variableTypeID == 2:
            return 'Boolean'
        if variableTypeID == 3:
            return 'Enum'
        return 'Float'

    def SetupEvents(self, parent):
        for event in self.tr2Controller.eventHandlers:
            eventHandlerButtonContainer = CreateContainer('eventHandler', parent, padTop=8, padLeft=30)
            eventButton = Button(name=event.name, align=uiconst.TOLEFT, parent=eventHandlerButtonContainer, label=event.name, func=self.PlayEvent(event.name, self.tr2Controller, 1), height=30, width=100)
            eventButton50 = Button(name='x50', align=uiconst.TOLEFT, parent=eventHandlerButtonContainer, label='x50', func=self.PlayEvent(event.name, self.tr2Controller, 50), height=30, width=100)

    def PlayEvent(self, eventName, tr2Controller, times):

        def _PlayEventOnGate(*args):
            for _ in range(0, times):
                tr2Controller.HandleEvent(eventName)

        return _PlayEventOnGate

    def SetState(self, initialVariables):
        for i in range(0, len(initialVariables)):
            initialVariableValue = initialVariables[i]
            uiElem = self.variableViews[i]
            if type(uiElem) is Checkbox:
                isChecked = True if initialVariableValue == 1 else False
                uiElem.SetChecked(isChecked)
            elif type(uiElem) is Combo:
                uiElem.SelectItemByIndex(int(initialVariableValue))
            else:
                uiElem.SetValue(str(initialVariableValue))


class OverrideView(object):

    def __init__(self, parent):
        self.parent = parent
        self.overridesEnabledBox = None
        self.serverTimeInput = None
        self.shipSpeedInput = None
        self.shipMaxSpeedInput = None

    def Setup(self):
        overridesLabel = CreateLabel(name='Overrides', width=300, height=12, padBottom=25, parent=self.parent)
        self.overridesEnabledBox = Checkbox(name='Enable overrides', width=150, height=18, padLeft=30, padTop=0, padBottom=20, parent=self.parent, text='Enable overrides', callback=self.OnOverridesToggled())
        self.shipSpeedInput = _CreateInput(name='Ship Speed Input', value='0', label='Ship Speed', parent=self.parent, align=uiconst.TOTOP, padBottom=20, minValue=0.0, maxValue=999999.0, callback=self.OnShipSpeedInputChanged)
        self.shipMaxSpeedInput = _CreateInput(name='Max Ship Speed Input', value='0', label='Max Ship Speed', parent=self.parent, align=uiconst.TOTOP, padBottom=20, minValue=0.0, maxValue=999999.0, callback=self.OnShipSpeedInputChanged)
        self.serverTimeInput = _CreateTextInput(name='Server time[default is bogus, only correct formatting works]', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), label='Server time', parent=self.parent, align=uiconst.TOTOP, padBottom=20, callback=self.OnServerTimeInputChanged)

    def OnServerTimeInputChanged(self, *args, **kwargs):
        try:
            dt = datetime.strptime(self.serverTimeInput.text, '%Y-%m-%d %H:%M:%S')
            t = blue.os.GetTimeFromParts(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, 0)
            trinity.settings.SetValue('controllerServerTime', t)
        except:
            pass

    def OnShipSpeedInputChanged(self, *args, **kwargs):
        self.SetVarWithArg(args, 'controllerShipSpeed')

    def OnShipMaxSpeedInputChanged(self, *args, **kwargs):
        self.SetVarWithArg(args, 'controllerShipMaxSpeed')

    def SetVarWithArg(self, args, paramName):
        if len(args) > 0:
            try:
                asNumeric = float(args[0].text)
                trinity.settings.SetValue(paramName, asNumeric)
            except:
                pass

    def OnOverridesToggled(self):

        def _OnOverridesToggled(check):
            trinity.settings.SetValue('controllerFunctionOverrideEnabled', self.overridesEnabledBox._checked)
            if self.overridesEnabledBox._checked:
                self.OnServerTimeInputChanged()
                self.OnShipSpeedInputChanged(self.shipSpeedInput, 'controllerShipSpeed')
                self.OnShipMaxSpeedInputChanged(self.shipMaxSpeedInput, 'controllerShipMaxSpeed')

        return _OnOverridesToggled


class ModelStateDebuggerView(object):

    def __init__(self):
        self.name = 'Model State Debugger'
        self.controllerDelegate = None
        self.tr2ControllerViews = []
        self.wnd = None

    def Setup(self, visualModel, tr2Controllers):
        wnd = Window.Open()
        wnd.SetMinSize([450, 550])
        wnd.SetMaxSize([450, 850])
        wnd.SetCaption(self.name)
        wnd._OnClose = self.controllerDelegate.ResetTr2Controllers
        main = wnd.GetMainArea()
        self.wnd = wnd
        container = CreateScrollContainer('test', 450, 500, main)
        spaceObjectLabel = CreateLabel(name='SpaceObject: ' + visualModel().name + ' (' + getattr(visualModel(), 'dna', '') + ')', width=300, height=12, parent=container)
        for tr2Controller in tr2Controllers:
            tr2ControllerView = Tr2ControllerView(tr2Controller)
            tr2ControllerView.Setup(container)
            self.tr2ControllerViews.append(tr2ControllerView)

        buttonContainer = CreateContainer(name='ResetButtonContainer', parent=container, padLeft=15)
        overrides = OverrideView(container)
        overrides.Setup()
        resetButton = Button(name='Reset', align=uiconst.TOLEFT, parent=buttonContainer, label='Reset', func=self.controllerDelegate.ResetTr2Controllers, height=30, width=100)

    def SetState(self, initalVariablesPerController):
        for i in range(0, len(initalVariablesPerController)):
            self.tr2ControllerViews[i].SetState(initalVariablesPerController[i])


class ModelStateDebuggerController(object):

    def __init__(self, itemID = None):
        if itemID is None:
            scene = sm.GetService('sceneManager').GetActiveScene()
            self.model = weakref.ref(scene.objects[0])
        else:
            bp = sm.GetService('michelle').GetBallpark()
            ball = bp.GetBall(itemID)
            self.ball = weakref.ref(ball)
            if ball is None:
                self.SetUserError('Unable to open model state debugger. Selected item has no ball')
                return
            self.model = weakref.ref(getattr(ball, 'model'))
            if self.model() is None:
                self.SetUserError('Unable to open model state debugger. Selected item has no model')
                return
        self.tr2Controllers = self.model().Find('trinity.Tr2Controller')
        if self.tr2Controllers is None:
            self.SetUserError('Model state debugger found no controllers on object')
            return
        self.initialVariableStates = []
        for controller in self.tr2Controllers:
            states = [ variable.value for variable in controller.variables ]
            self.initialVariableStates.append(states)

        self.view = ModelStateDebuggerView()
        self.view.controllerDelegate = self
        self.closeTasklet = None

    def ShowUI(self):
        self.view.Setup(self.model, self.tr2Controllers)
        if session.stationid is None:
            self.closeTasklet = uthread2.StartTasklet(self._CheckIfShouldClose)

    def SetUserError(self, message):
        errorWindow = ErrorWindow()
        errorWindow.Setup(message)

    def _CheckIfShouldClose(self):
        while self.model() is not None:
            try:
                id = self.ball().id
            except:
                self.view.wnd.Close()
                del self.model().observers[:]
                self.view = None

            blue.synchro.SleepWallclock(200)

    def ResetTr2Controllers(self, *args):
        for i in range(0, len(self.tr2Controllers)):
            initialVariablesPerController = self.initialVariableStates[i]
            statefulController = self.tr2Controllers[i]
            for j in range(0, len(statefulController.variables)):
                initialVariable = initialVariablesPerController[j]
                statefulVariable = statefulController.variables[j]
                statefulVariable.value = initialVariable

        self.view.SetState(self.initialVariableStates)


class ErrorWindow(object):

    def __init__(self):
        self.wnd = None

    def Setup(self, errorText):
        wnd = Window.Open()
        wnd.SetMinSize([400, 400])
        wnd.SetCaption('Error opening Model state debugger')
        main = wnd.GetMainArea()
        self.wnd = wnd
        label = CreateLabel(name=errorText, width=400, height=100, parent=main)
