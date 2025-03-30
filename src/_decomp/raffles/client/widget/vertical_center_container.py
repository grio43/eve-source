#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\vertical_center_container.py
import eveui

class VerticalCenteredContainer(eveui.Container):

    def UpdateAlignment(self, *args, **kwds):
        result = super(VerticalCenteredContainer, self).UpdateAlignment(*args, **kwds)
        if self.children:
            _, container_height = self.GetCurrentAbsoluteSize()
            content_height = 0
            for i, child in enumerate(self.children):
                content_height += child.height + child.padTop + child.padBottom
                if i > 0:
                    content_height += child.top

            adjusted_top = int(round((container_height - content_height) / 2.0))
            self.children[0].top = adjusted_top
        return result
