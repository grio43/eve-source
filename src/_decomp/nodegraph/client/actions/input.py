#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\nodegraph\client\actions\input.py
from .base import Action

class SetMousePosition(Action):
    atom_id = 481

    def __init__(self, ui_element_object = None, **kwargs):
        super(SetMousePosition, self).__init__(**kwargs)
        self.ui_element_object = ui_element_object

    def start(self, **kwargs):
        super(SetMousePosition, self).start(**kwargs)
        if not self.ui_element_object:
            return
        import trinity
        x, y = self.ui_element_object.GetAbsolutePosition()
        width, height = self.ui_element_object.GetAbsoluteSize()
        trinity.mainWindow.SetCursorPos(x + width / 2, y + height / 2)
        from carbonui.uicore import uicore
        uicore.registry.SetFocus(self.ui_element_object)
        import uthread2
        uthread2.sleep(0.1)


class MouseLeftClick(Action):
    atom_id = 482

    def __init__(self, ui_element_object = None, **kwargs):
        super(MouseLeftClick, self).__init__(**kwargs)
        self.ui_element_object = ui_element_object

    def start(self, **kwargs):
        super(MouseLeftClick, self).start(**kwargs)
        if self.ui_element_object:
            SetMousePosition(ui_element_object=self.ui_element_object).start()
        import trinity
        trinity.mainWindow.onMouseDown(0, None, None)
        trinity.mainWindow.onMouseUp(0, None, None)
        import uthread2
        uthread2.sleep(0.1)


class MouseRightClick(Action):
    atom_id = 483

    def __init__(self, ui_element_object = None, **kwargs):
        super(MouseRightClick, self).__init__(**kwargs)
        self.ui_element_object = ui_element_object

    def start(self, **kwargs):
        super(MouseRightClick, self).start(**kwargs)
        if self.ui_element_object:
            SetMousePosition(ui_element_object=self.ui_element_object).start()
        import trinity
        trinity.mainWindow.onMouseDown(1, None, None)
        trinity.mainWindow.onMouseUp(1, None, None)
        import uthread2
        uthread2.sleep(0.1)


class MouseScrollWheel(Action):
    atom_id = 484

    def __init__(self, amount = None, time = None, down = None, **kwargs):
        super(MouseScrollWheel, self).__init__(**kwargs)
        self.amount = self.get_atom_parameter_value('amount', amount)
        self.time = self.get_atom_parameter_value('time', time)
        self.down = self.get_atom_parameter_value('down', down)

    def start(self, **kwargs):
        super(MouseScrollWheel, self).start(**kwargs)
        import trinity
        import uthread2
        counter = self.amount / 120
        wait_time = float(self.time) / counter
        scroll_step = -120 if self.down else 120
        while counter > 0:
            trinity.mainWindow.onMouseWheel(scroll_step)
            counter -= 1
            uthread2.sleep(wait_time)
