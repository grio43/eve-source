#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\battleground_capture_point_ui\client\state.py


class TimerGaugeState(object):

    def __init__(self):
        self.timer_gauge = None
        self._camera_facing_gauge = None

    def SetTimerValue(self, value, animate = True):
        self.timer_gauge.SetValue(value, animate=animate)

    def IsReady(self):
        return self.timer_gauge is not None

    def NotifyTimerReset(self):
        pass

    def enter(self):
        return None

    def exit(self):
        return None

    def close(self):
        return None


class StateMachine(object):

    def __init__(self):
        self.state = None

    def move_to(self, new_state):
        if self.state:
            self.state.exit()
        self.state = new_state
        self.state.enter()
        return self.state
