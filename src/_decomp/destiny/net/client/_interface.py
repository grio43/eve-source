#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\destiny\net\client\_interface.py
import abc

class ClientTickerInterface:
    __metaclass__ = abc.ABCMeta

    def set_ballpark(self, ballpark):
        self._ballpark = ballpark

    @abc.abstractmethod
    def on_set_state(self):
        pass

    @abc.abstractmethod
    def on_ballpark_local_action(self, func_name, args):
        pass

    @abc.abstractmethod
    def should_log_actions(self):
        pass

    @abc.abstractmethod
    def get_ball_destruction_delay(self, ball, is_terminal = False):
        pass

    @abc.abstractmethod
    def get_ball_destruction_delays(self, ball_ids, is_release = False):
        pass

    @abc.abstractmethod
    def clean_up_after_ball_removal(self, ball_id, ball, is_terminal = False):
        pass

    @abc.abstractmethod
    def clean_up_after_multiple_ball_removal(self, ball_ids, is_release = False):
        pass


class TickErrorHandlerInterface:
    __metaclass__ = abc.ABCMeta

    def set_ballpark(self, ballpark):
        self._ballpark = ballpark

    @abc.abstractmethod
    def on_fatal_desync(self):
        pass

    @abc.abstractmethod
    def on_recoverable_desync(self):
        pass
