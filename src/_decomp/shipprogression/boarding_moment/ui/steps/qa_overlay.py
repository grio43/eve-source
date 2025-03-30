#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\steps\qa_overlay.py
import evetypes
import uthread2
import time
from carbonui import TextBody, Align, TextHeader, TextColor
from carbonui.primitives.container import Container
from shipprogression.boarding_moment.ui.steps.base import _BoardingUIStepBase
from shipprogression.boarding_moment import qa as boarding_moment_qa

class _QAOverlay(_BoardingUIStepBase):
    default_opacity = 1

    def _construct_layout(self):
        size_and_shape = TextBody(parent=self, align=Align.TOPLEFT, top=16, left=16, text=self.get_size_and_shape_string())
        TextBody(parent=self, align=Align.TOPLEFT, top=16 + size_and_shape.height, left=16, text=self.get_radius_and_shield_string())
        self._timer = TextHeader(parent=self, align=Align.TOPLEFT, top=64, left=16, text='00:00:00.000')
        self._step_timer = TextHeader(parent=self, align=Align.TOPLEFT, top=92, left=16, text='00:00:00.000')
        self._stopwatch = Stopwatch()
        self._step_stopwatch = Stopwatch()
        self._construct_moment_rundown()

    def _sequence(self):
        uthread2.StartTasklet(self._timer_task)

    def _timer_task(self):
        while not self.destroyed:
            self._timer.text = self._stopwatch.get_elapsed_time()
            self._step_timer.text = self._step_stopwatch.get_elapsed_time()
            uthread2.Sleep(0.1)

        self._stopwatch.stop()
        self._step_stopwatch.stop()

    def _construct_moment_rundown(self):
        moments = self.data['moments']
        moment_cont = Container(parent=self, align=Align.TOPLEFT, width=128, height=500, padTop=12, padLeft=16, top=112)
        self._moment_indicators = {}
        for moment in moments:
            step_id = moment['step']
            step_name = boarding_moment_qa.MOMENT_STEP_STRINGS.get(step_id, 'UNKNOWN')
            step_cont = Container(parent=moment_cont, align=Align.TOTOP, height=24, padBottom=4)
            step = TextBody(parent=step_cont, align=Align.CENTERLEFT, text=step_name, color=TextColor.SECONDARY)
            self._moment_indicators[step_id] = step

    def update(self, moment):
        step_id = moment['step']
        for indicator in self._moment_indicators.itervalues():
            indicator.color = TextColor.SECONDARY

        if step_id in self._moment_indicators:
            self._moment_indicators[step_id].color = TextColor.SUCCESS
        if not self._stopwatch.running:
            self._stopwatch.start()
        self._step_stopwatch.reset()
        self._step_stopwatch.start()

    def get_size_and_shape_string(self):
        shape = self.data['shape']
        size = self.data['size']
        return u'{name} ({typeID}) is {size} {shape}'.format(name=evetypes.GetName(self.typeID), typeID=self.typeID, size=boarding_moment_qa.SIZE_STRINGS.get(size, 'UNKNOWN'), shape=boarding_moment_qa.SHAPE_STRINGS.get(shape, 'UNKNOWN'))

    def get_radius_and_shield_string(self):
        model = self.data['model']
        x, y, z = model.generatedShapeEllipsoidRadius
        return u'ShapeEllipsoidRadius: x: {x:.2f}, y: {y:.2f}, z: {z:.2f}'.format(x=x, y=y, z=z)


class Stopwatch:

    def __init__(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed_time += time.time() - self.start_time
            self.running = False

    def reset(self):
        self.start_time = None
        self.elapsed_time = 0
        self.running = False

    def get_elapsed_time(self):
        if self.running:
            total_time = self.elapsed_time + (time.time() - self.start_time)
        else:
            total_time = self.elapsed_time
        hours = int(total_time // 3600)
        minutes = int(total_time % 3600 // 60)
        seconds = int(total_time % 60)
        milliseconds = int(total_time * 1000 % 1000)
        return '{:02}:{:02}:{:02}.{:03}'.format(hours, minutes, seconds, milliseconds)
