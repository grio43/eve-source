#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menucheckers\decorators.py
from inspect import getmembers, ismethod

def decorated_checker(cls):
    for methodName, method in getmembers(cls, ismethod):
        if not methodName[0].isalpha():
            continue
        if method.__name__ == 'failure_label_wrapper':
            continue
        if methodName[0].isupper():
            method = __cached_call(method, methodName)
            if methodName.startswith('Offer'):
                method = __clear_failure_label(method)
            else:
                method = __set_default_failure_label(method)
        else:
            method = __set_default_failure_label(method)
        setattr(cls, methodName, method)

    return cls


def explain_failure_with(label, **labelArgs):

    def set_failure_label_deco(func):

        def failure_label_wrapper(self, *args, **kwargs):
            retval = func(self, *args, **kwargs)
            self.failure_label = label
            self._label_arguments = labelArgs
            return retval

        if func.__name__[0].isupper():
            func = __cached_call(func, func.__name__)
        return failure_label_wrapper

    return set_failure_label_deco


def needs_ballpark_item(method):

    def needs_ballpark_item_deco(self, *args, **kwargs):
        if self.GetBallpark() is None:
            return False
        if not self.IsSpecificItem():
            return False
        ball = self.GetBall()
        if ball is None:
            return False
        return method(self, *args, **kwargs)

    return needs_ballpark_item_deco


def __clear_failure_label(method):

    def clear_failure_label_deco(self, *args, **kwargs):
        self.failure_label = None
        return method(self, *args, **kwargs)

    return clear_failure_label_deco


def __set_default_failure_label(func):

    def failure_label_wrapper(self, *args, **kwargs):
        retval = func(self, *args, **kwargs)
        self.failure_label = None
        return retval

    return failure_label_wrapper


def __cached_call(func, methodName):
    key = methodName

    def check_cache_or_call_function(self, *args, **kwargs):
        if key not in self.cache:
            self.cache[key] = func(self, *args, **kwargs)
        return self.cache[key]

    return check_cache_or_call_function
