#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\registry\__init__.py
COMPOSITE = 'composite'
ACTION = 'action'
CONDITION = 'condition'
DECORATOR = 'decorator'
MONITOR = 'monitor'

def get_task_registry():
    import composites
    import actions
    import conditions
    import decorators
    import monitors
    from registrator import REGISTRY
    return REGISTRY
