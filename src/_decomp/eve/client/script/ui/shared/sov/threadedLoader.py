#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\sov\threadedLoader.py
import uthread2

class ThreadedLoader(object):

    def __init__(self, name = None):
        self.name = name or 'ThreadedLoader'
        self.debugDisplayName = name
        self.threadDict = {}

    def StartLoading(self, func, classInstance, *args):
        funcName = '%s_%s' % (func.func_name, id(classInstance))
        existingThread = self.threadDict.pop(funcName, None)
        if existingThread:
            existingThread.kill()
        self.threadDict[funcName] = uthread2.start_tasklet(self._CallFunc_thread, func, funcName, *args)

    def _CallFunc_thread(self, func, funcName, *args):
        try:
            func(*args)
        finally:
            self.threadDict.pop(funcName, None)
