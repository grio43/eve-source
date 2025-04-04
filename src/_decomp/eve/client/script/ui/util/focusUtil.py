#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\util\focusUtil.py
import carbonui.const as uiconst
import trinity
import logging
from eveexceptions.exceptionEater import ExceptionEater
from carbonui.uicore import uicore
logger = logging.getLogger(__name__)
isFocused = False
registeredToFocusEvent = False
postponedFunctionCalls = []

def RegisterToFocusEvent():
    global registeredToFocusEvent
    global isFocused
    if not registeredToFocusEvent:
        registeredToFocusEvent = True
        isFocused = trinity.app.IsActive()
        uicore.event.RegisterForTriuiEvents(uiconst.UI_ACTIVE, HandleAppFocus)


def CallPostponedFunctions():
    global postponedFunctionCalls
    if len(postponedFunctionCalls) > 0:
        logger.debug('Running postponed functions')
        for function, args, kwargs in postponedFunctionCalls:
            with ExceptionEater('Failed to run a postponed function'):
                function(*args, **kwargs)

        postponedFunctionCalls = []


def HandleAppFocus(wnd, msgID, vkey):
    global isFocused
    isFocused = vkey[0]
    if isFocused:
        CallPostponedFunctions()
    return 1


def postponeUntilFocus(func):

    def wrappedFunc(*args, **kwargs):
        RegisterToFocusEvent()
        if not isFocused:
            postponedFunctionCalls.append((func, args, kwargs))
        else:
            func(*args, **kwargs)

    return wrappedFunc
