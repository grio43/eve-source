#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveclientqatools\sofpreviewer\statemachinecontroller.py
import eveSpaceObject.spaceobjanimation as soanimation

class StateMachineController:

    def __init__(self):
        self._states = {}
        self._currentStates = {}
        self._model = None
        self._variables = {}
        self._variableTypes = {}
        self._variableEnumValues = {}

    def _ClearAll(self):
        self._states = {}
        self._currentStates = {}
        self._model = None

    def SetupForHullAndModel(self, hull, model):
        self._ClearAll()
        self._model = model
        soanimation.TriggerDefaultStates(model)
        self._variables = {}
        if hasattr(self._model, 'controllers'):
            for each in self._model.controllers:
                for var in getattr(each, 'variables', []):
                    self._variables[var.name] = var.value
                    self._variableTypes[var.name] = var.variableType
                    self._variableEnumValues[var.name] = var.enumValues

    def GetVariables(self):
        return self._variables

    def GetVariableType(self, name):
        return self._variableTypes.get(name, 0)

    def GetEnumValues(self, name):
        if self._variableTypes.get(name, 0) != 3:
            return []
        result = []
        for each in self._variableEnumValues.get(name, '').split(','):
            try:
                k, v = each.strip().rsplit('=', 1)
                v = float(v)
            except ValueError:
                continue

            result.append((k, v))

        return result

    def SetVariable(self, name, value):
        self._variables[name] = float(value)
        self._model.SetControllerVariable(name, float(value))

    def ApplyTo(self, model):
        for name, value in self._variables.items():
            model.SetControllerVariable(name, value)

    def OnControllerVariable(self, edit):
        edit.SetText(edit.text, 1)
        name = edit.name
        value = float(edit.text)
        self.SetVariable(name, value)

    def OnControllerBoolVariable(self, cb):
        name = cb.name
        value = cb.GetValue()
        self.SetVariable(name, 1.0 if value else 0.0)

    def OnControllerEnumVariable(self, cb):
        name = cb.name
        value = cb.GetValue()
        self.SetVariable(name, value)
