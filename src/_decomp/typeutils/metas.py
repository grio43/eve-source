#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\typeutils\metas.py


class Singleton(type):
    __instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            setattr(cls.__instances[cls], '_singleton_reload', Singleton.wrapper(cls))
        return cls.__instances[cls]

    @staticmethod
    def wrapper(cls):

        def _singleton_reload():
            if cls in cls.__instances:
                del cls.__instances[cls]
            return cls()

        return _singleton_reload
