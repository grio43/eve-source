#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\itertoolsext\StaticVariables.py


def StaticVariables(**kwargs):

    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])

        return func

    return decorate


static_variables = StaticVariables
