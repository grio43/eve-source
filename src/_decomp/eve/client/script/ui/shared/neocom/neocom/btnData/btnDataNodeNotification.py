#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\neocom\neocom\btnData\btnDataNodeNotification.py
from eve.client.script.ui.shared.neocom.neocom import neocomConst
from eve.client.script.ui.shared.neocom.neocom.btnData.btnDataNode import BtnDataNode

class BtnDataNodeNotification(BtnDataNode):
    default_btnType = neocomConst.BTNTYPE_NOTIFICATION
    default_cmdName = None
    default_iconPath = None
    default_btnID = None
    default_isBlinking = True
    default_label = None
    default_isRemovable = False
    default_isDraggable = False
    default_labelAbbrev = None
    default_wndCls = None
    default_children = None

    def __init__(self, parent = None, iconPath = None, label = None, btnID = None, isBlinking = None, cmdName = None, btnType = None, isRemovable = None, labelAbbrev = None, wndCls = None, isDraggable = None, children = None, **kwargs):
        BtnDataNode.__init__(self, parent=parent, children=optional(children, self.default_children), iconPath=optional(iconPath, self.default_iconPath), label=optional(label, self.default_label), btnID=optional(btnID, self.default_btnID), btnType=optional(btnType, self.default_btnType), isOpen=False, isBlinking=optional(isBlinking, self.default_isBlinking), isRemovable=optional(isRemovable, self.default_isRemovable), isDraggable=optional(isDraggable, self.default_isDraggable), cmdName=optional(cmdName, self.default_cmdName), labelAbbrev=optional(labelAbbrev, self.default_labelAbbrev), wndCls=optional(wndCls, self.default_wndCls), **kwargs)


def optional(value, default):
    if value is not None:
        return value
    return default
