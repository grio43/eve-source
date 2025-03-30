#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\bannedwords\client\bannedwords_client.py
import uthread2
from carbon.common.script.sys.service import Service
from ..bannedwords_regexes import Regexes
from caching.memoize import Memoize
import log
import monolithconfig
from eveexceptions import UserError
REGEXES_TYPES = ['blocked', 'intercepted']

class BannedWordsClientService(Service):
    __guid__ = 'svc.bannedwords_client'
    __startupdependencies__ = ['machoNet']
    __notifyevents__ = ['OnSessionChanged']

    def Run(self, memStream = None):
        self.regexes_blocked = Regexes(self.fetch_regexes, REGEXES_TYPES[0])
        self.regexes_intercepted = Regexes(self.fetch_regexes, REGEXES_TYPES[1])
        monolithconfig.add_global_config_callback(self.update_config_values)

    def update_config_values(self):
        self.bw_regex_enabled = monolithconfig.enabled('banned_words_enabled')
        self.bw_search_enabled = monolithconfig.enabled('banned_words_search_enabled')
        bw_banned_character_from_id = monolithconfig.get_value('bw_banned_character_from_id')
        try:
            self.bw_banned_character_from_id = int(bw_banned_character_from_id)
        except:
            log.LogInfo('Could not parse banned_words_banned_character_from_id. Reverting to default : 0 ')
            self.bw_banned_character_from_id = 0

    def fetch_regexes(self, reg_type):
        res = []
        try:
            res = sm.RemoteSvc('bannedwords').fetch_regexes(reg_type)
        except:
            log.LogInfo('bannedwords get Regex from server error')

        return res

    @Memoize(15)
    def update_regexes(self):
        self.regexes_blocked.fetch_and_compile()
        self.regexes_intercepted.fetch_and_compile()

    def check_chat_words_allowed(self, *wordsList, **kwargs):
        if self.bw_regex_enabled:
            self.update_regexes()
            for words in wordsList:
                self.regexes_blocked.check_words_allowed(words, **kwargs)

    def check_chat_character_allowed(self, characterID):
        if self.bw_banned_character_from_id > 0 and self.bw_banned_character_from_id <= characterID:
            raise UserError('NewCharacterBanned')

    def OnSessionChanged(self, isRemote, sess, change):
        log.LogInfo('bannedwords on session changed userid: {}, change: {}'.format(sess.userid, change))
        if sess.userid and 'userid' in change and not change['userid'][0]:
            if self.bw_regex_enabled:
                uthread2.StartTasklet(self.update_regexes)

    def check_words_allowed(self, *wordsList, **kwargs):
        if self.bw_regex_enabled:
            sm.RemoteSvc('bannedwords').check_words_allowed(*wordsList, **kwargs)

    def check_search_words_allowed(self, *wordsList, **kwargs):
        if self.bw_search_enabled:
            sm.RemoteSvc('bannedwords').check_search_words_allowed(*wordsList, **kwargs)
