#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\analysisbeacon\client\state.py


class State(object):

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
