#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\monolithdisconnectlogger\logger.py
import monolithmetrics
import mdlconst

class MonolithDisconnectLogger(object):

    @staticmethod
    def log_disconnect(ipaddress = None):
        tags = MonolithDisconnectLogger.get_geo_tags(ipaddress)
        return monolithmetrics.increment(metric=mdlconst.DISCONNECT, tags=tags)

    @staticmethod
    def log_player_user_requested_disconnect(ipaddress = None):
        tags = MonolithDisconnectLogger.get_geo_tags(ipaddress)
        monolithmetrics.increment(metric=mdlconst.USER_REQUESTED, tags=tags)

    @staticmethod
    def log_player_char_requested_disconnect(ipaddress = None):
        tags = MonolithDisconnectLogger.get_geo_tags(ipaddress)
        monolithmetrics.increment(metric=mdlconst.CHAR_REQUESTED, tags=tags)

    @staticmethod
    def log_player_usurped_disconnect(ipaddress = None):
        tags = MonolithDisconnectLogger.get_geo_tags(ipaddress)
        monolithmetrics.increment(metric=mdlconst.USURPED, tags=tags)

    @staticmethod
    def log_server_shutdown_disconnect(ipaddress = None):
        tags = MonolithDisconnectLogger.get_geo_tags(ipaddress)
        monolithmetrics.increment(metric=mdlconst.SERVER_SHUTDOWN, tags=tags)

    @staticmethod
    def get_geo_tags(ipaddress):
        if ipaddress:
            if ':' in ipaddress:
                ipaddress = ipaddress.split(':')[0]
            tag = monolithmetrics.get_geo_tags(ipaddress)
            return tag
        else:
            return None
