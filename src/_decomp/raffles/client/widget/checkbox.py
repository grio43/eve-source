#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\checkbox.py
import eveui
import uthread

class Checkbox(eveui.Container):
    default_height = 20
    default_clipChildren = True

    def __init__(self, text = '', checked = False, callback = None, groupname = None, **kwargs):
        super(Checkbox, self).__init__(**kwargs)
        checkbox_container = eveui.Container(parent=self, align=eveui.Align.to_left, width=20, padRight=6)
        self.checkbox = eveui.Checkbox(parent=checkbox_container, align=eveui.Align.center, width=20, height=20, checked=checked, groupname=groupname, callback=callback)
        label_container = eveui.Container(parent=self)
        label = eveui.EveLabelMedium(parent=label_container, state=eveui.State.normal, align=eveui.Align.center_left, text=text)
        label.OnClick = self._label_click
        label.OnMouseEnter = self.checkbox.OnMouseEnter
        label.OnMouseExit = self.checkbox.OnMouseExit

    @property
    def checked(self):
        return self.checkbox.checked

    @checked.setter
    def checked(self, checked):
        if checked != self.checkbox.checked:
            self.checkbox.SetChecked(checked)

    def _label_click(self, *args, **kwargs):
        uthread.new(self.checkbox.ToggleState)
