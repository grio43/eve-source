#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\behaviors\trees\sleep.py
from behaviors.actions import WaitAction
from behaviors.behaviortree import BehaviorTree
from brennivin.itertoolsext import Bundle

def CreateSleepBehaviorTree():
    root = WaitAction(Bundle(name='Sleep forever my pretty'))
    behaviorTree = BehaviorTree()
    behaviorTree.StartRootTask(root)
    return behaviorTree
