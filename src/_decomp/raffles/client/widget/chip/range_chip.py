#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\raffles\client\widget\chip\range_chip.py
from .chip import Chip

class RangeChip(Chip):
    default_name = 'RangeChip'
    equals_format = u'{label} = {min}'
    min_max_format = u'{min} \u2264 {label} \u2264 {max}'
    min_format = u'{min} \u2264 {label}'
    max_format = u'{label} \u2264 {max}'

    def __init__(self, label, min = None, max = None, **kwargs):
        super(RangeChip, self).__init__(**kwargs)
        self._min = None
        self._max = None
        self._label = label
        if min or max:
            self.update(min, max)

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, min):
        self.update(min, self.max)

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, max):
        self.update(self.min, max)

    def update(self, min, max):
        self._min = min
        self._max = max
        if not min and not max:
            self.clear()
            return
        if min and max:
            if min == max:
                text_format = self.equals_format
            else:
                text_format = self.min_max_format
        elif min:
            text_format = self.min_format
        else:
            text_format = self.max_format
        self.text = text_format.format(label=self._label, min=min, max=max)
