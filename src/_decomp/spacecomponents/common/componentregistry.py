#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\spacecomponents\common\componentregistry.py
from collections import defaultdict
from ccpProfile import TimedFunction
from componentmessenger import ComponentMessenger
from eveexceptions.exceptionEater import ExceptionEater
from spacecomponents.common.componentclass import ComponentClass
from spacecomponents.common.data import get_space_component_names_for_type, get_space_component_for_type

class UnregisteredComponentError(Exception):
    pass


class ComponentInstanceAlreadyExists(Exception):
    pass


def ExportCall(func):
    func.isExportedComponentCall = True
    return func


class ComponentRegistry(object):
    asyncFuncs = None

    def __init__(self, asyncFuncs, eventLogger, componentClassTypes, typeIDToClassMapping):
        self.asyncFuncs = asyncFuncs
        self.eventLogger = eventLogger
        self.componentClassTypes = {componentName:ComponentClass(componentName, componentClass) for componentName, componentClass in componentClassTypes.iteritems()}
        self.componentNames = tuple(self.componentClassTypes.keys())
        self.typeIDToClassMapping = typeIDToClassMapping
        self.itemIDToComponentInstances = {}
        self.componentNameToItemIDs = defaultdict(dict)
        self.messenger = ComponentMessenger()

    @TimedFunction('SpaceComponent::ComponentRegistry::GetComponentClassesForTypeID')
    def GetComponentClassesForTypeID(self, typeID):
        componentClassesForTypeID = self.typeIDToClassMapping.get(typeID, None)
        if componentClassesForTypeID is None:
            componentClassesForTypeID = self.RegisterComponentsForType(typeID)
        return componentClassesForTypeID

    @TimedFunction('SpaceComponent::ComponentRegistry::RegisterComponentsForType')
    def RegisterComponentsForType(self, typeID):
        componentNames = get_space_component_names_for_type(typeID, component_names=self.componentNames)
        componentClassesForTypeID = []
        for componentName in componentNames:
            componentClassesForTypeID.append(self.componentClassTypes[componentName])

        self.typeIDToClassMapping[typeID] = componentClassesForTypeID
        return componentClassesForTypeID

    def GetComponentsByItemID(self, itemID):
        return self.itemIDToComponentInstances[itemID]

    def CreateComponentInstances(self, itemID, typeID):
        componentClassesForTypeID = self.GetComponentClassesForTypeID(typeID)
        components = self._GetComponentsByItemId(itemID)
        for componentClass in componentClassesForTypeID:
            if componentClass.componentName in components:
                continue
            attributes = get_space_component_for_type(typeID, componentClass.componentName)
            with ExceptionEater('Error creating a component %s' % componentClass.componentName):
                instance = componentClass.factoryMethod(itemID, typeID, attributes, self)
                components[componentClass.componentName] = instance
                self.componentNameToItemIDs[componentClass.componentName][itemID] = instance

        return components

    def _GetComponentsByItemId(self, itemId):
        if itemId in self.itemIDToComponentInstances:
            components = self.itemIDToComponentInstances[itemId]
        else:
            components = {}
            self.itemIDToComponentInstances[itemId] = components
        return components

    def AddComponentInstanceToItem(self, componentName, itemId, typeID, attributes):
        components = self._GetComponentsByItemId(itemId)
        componentClass = self.componentClassTypes[componentName]
        instance = componentClass.factoryMethod(itemId, typeID, attributes, self)
        components[componentName] = instance
        self.componentNameToItemIDs[componentName][itemId] = instance
        return instance

    def DeleteComponentInstances(self, itemID):
        self.messenger.DeleteSubscriptionsForItem(itemID)
        instance = self.itemIDToComponentInstances.pop(itemID)
        for componentName in instance:
            del self.componentNameToItemIDs[componentName][itemID]

    def GetInstancesWithComponentClass(self, componentName):
        return self.componentNameToItemIDs[componentName].values()

    def SendMessageToItem(self, itemID, messageName, *args, **kwargs):
        self.messenger.SendMessageToItem(itemID, messageName, *args, **kwargs)

    def SendMessageToAllItems(self, messageName, *args, **kwargs):
        self.messenger.SendMessageToAllItems(messageName, *args, **kwargs)

    def SubscribeToItemMessage(self, itemID, messageName, messageHandler):
        self.GetComponentsByItemID(itemID)
        self.messenger.SubscribeToItemMessage(itemID, messageName, messageHandler)

    def GetComponentForItem(self, itemID, componentClassID):
        return self.itemIDToComponentInstances[itemID][componentClassID]

    def UnsubscribeFromItemMessage(self, itemID, messageName, messageHandler):
        self.messenger.UnsubscribeFromItemMessage(itemID, messageName, messageHandler)

    def CallComponent(self, session, itemID, componentClassName, methodName, *args, **kwargs):
        try:
            component = self.GetComponentForItem(itemID, componentClassName)
        except KeyError:
            return

        method = getattr(component, methodName)
        if not getattr(method, 'isExportedComponentCall', False):
            raise RuntimeError("The method '%s' is not exported on component '%s'" % (methodName, componentClassName))
        return method(session, *args, **kwargs)

    @staticmethod
    def GetServiceForComponent(serviceName):
        return sm.GetService(serviceName)
