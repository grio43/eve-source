#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveexceptions\exceptionEater.py
import logging

class ExceptionEater(object):

    def __init__(self, message = '', channel = None):
        self.message = message
        self.channel = channel

    def __enter__(self):
        pass

    def __exit__(self, eType, eVal, tb):
        if eType is not None:
            logger = None
            if self.channel:
                logger = logging.getLogger(self.channel)
            else:
                logger = logging.getLogger(__name__)
            logger.exception(self.message)
        return True


class EatsExceptions(object):

    def __init__(self, message = None, channel = None):
        self.message = message
        self.channel = channel

    def __call__(self, func, *args, **kwargs):

        def wrapper(*args, **kwargs):
            if self.message is None:
                message = 'Exception eaten in %s::%s' % (func.__module__, func.func_name)
            else:
                message = self.message
            with ExceptionEater(message=message, channel=self.channel):
                return func(*args, **kwargs)

        return wrapper
