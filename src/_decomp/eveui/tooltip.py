#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveui\tooltip.py
from carbonui.uicore import uicore

def show_persistent_tooltip(owner, load_function = None, tooltip_class = None):
    return uicore.uilib.tooltipHandler.LoadPersistentTooltip(owner=owner, loadFunction=load_function, customTooltipClass=tooltip_class)
