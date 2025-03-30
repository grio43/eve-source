#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\tournamentmanagement\client\tournamentDropShadowElement.py


class DropShadowElement(object):

    def __init__(self, classOfThingToShadow, *args, **kwargs):
        self.main = classOfThingToShadow(*args, **kwargs)
        self.shad1 = classOfThingToShadow(*args, **kwargs)
        self.shad2 = classOfThingToShadow(*args, **kwargs)
        self.shad3 = classOfThingToShadow(*args, **kwargs)
        self.RePosition()
        self.ReColor()

    def RePosition(self):
        self.shad1.left = self.main.left + 2
        self.shad1.top = self.main.top + 2
        self.shad2.left = self.main.left + 2
        self.shad2.top = self.main.top + 1
        self.shad3.left = self.main.left + 1
        self.shad3.top = self.main.top + 2

    def ReColor(self):
        shadowColor = (0,
         0,
         0,
         self.main.opacity * 0.25)
        self.shad1.color = shadowColor
        self.shad2.color = shadowColor
        self.shad3.color = shadowColor

    @property
    def left(self):
        return self.main.left

    @left.setter
    def left(self, value):
        self.main.left = value
        self.RePosition()

    @property
    def top(self):
        return self.main.top

    @top.setter
    def top(self, value):
        self.main.top = value
        self.RePosition()

    @property
    def width(self):
        return self.main.width

    @property
    def height(self):
        return self.main.height

    @property
    def pos(self):
        return self.main.pos

    @pos.setter
    def pos(self, value):
        self.main.pos = value
        self.RePosition()

    @property
    def text(self):
        return self.main.text

    @text.setter
    def text(self, value):
        self.main.text = value
        self.shad1.text = value
        self.shad2.text = value
        self.shad3.text = value

    @property
    def color(self):
        return self.main.color

    @color.setter
    def color(self, value):
        self.main.color = value
        self.ReColor()
