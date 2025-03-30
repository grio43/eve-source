#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\eve\client\script\ui\shared\systemMenu\systemMenuColumn.py
from carbonui.control.section import ChildBypassMixin
from carbonui.primitives.container import Container

class SystemMenuColumn(ChildBypassMixin, Container):
    default_name = 'SystemMenuColumn'
    default_padLeft = 0
    default_padRight = 0

    def ApplyAttributes(self, attributes):
        super(SystemMenuColumn, self).ApplyAttributes(attributes)
        self.isTabOrderGroup = 1
        self.mainCont = Container(name='mainCont', parent=self)
        self.TurnOnBypassToMainCont()
