#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\graphs\pool.py


class Pool:

    def __init__(self, instance_type, *args, **kwargs):
        self._positional_attributes = args
        self._keyword_attributes = kwargs
        self.instance_type = instance_type
        self.pool = []

    def get_instance(self):
        if len(self.pool) > 0:
            return self.pool.pop(0)
        return self.instance_type(*self._positional_attributes, **self._keyword_attributes)

    def return_instance(self, instance):
        if not isinstance(instance, self.instance_type):
            return
        instance.SetParent(None)
        self.pool.append(instance)

    def empty(self):
        for instance in self.pool:
            instance.Close()

        self.pool = []
