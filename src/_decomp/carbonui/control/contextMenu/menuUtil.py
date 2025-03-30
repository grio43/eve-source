#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\carbonui\control\contextMenu\menuUtil.py
from carbonui import uiconst
from carbonui.control.contextMenu.contextMenuMixin import ContextMenuMixin
from carbonui.primitives.fill import Fill
from carbonui.uianimations import animations
from carbonui.uicore import uicore
from eve.client.script.ui import eveColor

def CloseContextMenus():
    closedMenu = False
    for each in uicore.layer.menu.children[:]:
        if isinstance(each, ContextMenuMixin):
            each.Close()
            closedMenu = True
            sm.ScatterEvent('OnMenuClosed')

    return closedMenu


def HasContextMenu():
    for each in uicore.layer.menu.children:
        if isinstance(each, ContextMenuMixin):
            return True

    return False


def ClearMenuLayer():
    uicore.layer.menu.Flush()


def GetContextMenuOwner():
    contextMenuOwner = getattr(uicore, 'contextMenuOwner', None)
    if contextMenuOwner:
        menuOwner = contextMenuOwner()
        if menuOwner and not menuOwner.destroyed and ObjectHasMenu(menuOwner):
            return menuOwner


def ObjectHasMenu(uiObject):
    if hasattr(uiObject, 'menuObject_weakref'):
        mo = uiObject.menuObject_weakref
        if mo and mo():
            return True
    return False


def FlashEntrySelection(pos):
    fill = Fill(parent=uicore.layer.menu, align=uiconst.ABSOLUTE, color=eveColor.WHITE, pos=pos, outputMode=uiconst.OUTPUT_COLOR_AND_GLOW, glowBrightness=0.3)
    animations.FadeOut(fill, duration=0.15, callback=fill.Close)
