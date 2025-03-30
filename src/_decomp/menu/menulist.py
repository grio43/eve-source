#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\menu\menulist.py
from menu.menuLabel import MenuLabel

class MenuList(list):

    def __init__(self, seq = ()):
        self.reasonsWhyNotAvailable = {}
        list.__init__(self, seq)

    def extend(self, iterable):
        list.extend(self, iterable)
        self.reasonsWhyNotAvailable.update(getattr(iterable, 'reasonsWhyNotAvailable', {}))

    def filter(self, filterLabels):
        if not isinstance(filterLabels, (list, set)):
            filterLabels = [filterLabels]
        filter_labels = set()
        for label in filterLabels:
            if isinstance(label, MenuLabel):
                label = label[0]
            filter_labels.add(label)

        ret = MenuList((entry for entry in self if not self._filtered(filter_labels, entry)))
        ret.reasonsWhyNotAvailable.update(self.reasonsWhyNotAvailable)
        return ret

    @staticmethod
    def _filtered(filterLabels, entry):
        label = entry
        while isinstance(label, (MenuLabel, list, tuple)):
            label = label[0]

        return label in filterLabels
