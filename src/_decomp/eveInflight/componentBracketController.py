#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveInflight\componentBracketController.py
from spacecomponents.client import factory

class ComponentBracketController(object):

    def __init__(self):
        self.componentsWithBracketFuncs = {}

    def GetBracketIcon(self, bracketData, ballpark, typeID, itemID):
        if not typeID or not itemID:
            return
        componentRegistry = ballpark.componentRegistry
        componentWithBracketFunc = self._GetComponentWithBracket(componentRegistry, typeID)
        if componentWithBracketFunc:
            try:
                instance = componentRegistry.GetComponentForItem(itemID, componentWithBracketFunc)
            except KeyError:
                return

            if instance:
                return instance.GetBracketIcon(bracketData)

    def _GetComponentWithBracket(self, componentRegistry, typeID):
        if typeID not in self.componentsWithBracketFuncs:
            self.componentsWithBracketFuncs[typeID] = None
            components = componentRegistry.GetComponentClassesForTypeID(typeID)
            for c in components:
                componentClass = factory.GetComponentClass(c.componentName)
                if hasattr(componentClass, 'GetBracketIcon'):
                    self.componentsWithBracketFuncs[typeID] = c.componentName
                    break

        return self.componentsWithBracketFuncs[typeID]
