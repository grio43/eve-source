#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\tutorial\page\page.py


class Page(object):

    def __init__(self, caption, text, button_label, enter_animation = None, exit_animation = None):
        self.caption = caption
        self.text = text
        self.button_label = button_label
        self.enter_animation = enter_animation
        self.exit_animation = exit_animation
