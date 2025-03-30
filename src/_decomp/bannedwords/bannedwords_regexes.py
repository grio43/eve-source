#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\bannedwords\bannedwords_regexes.py
import re
import blue
from eveexceptions import UserError
import logging
from bannedwords.bannedwords_marker_stripper import format_stripper
MAX_CHECK_LENGTH = 200
OVERLAPPING_CHOP = 20

class Regexes:

    def __init__(self, fetch_method, reg_type):
        self.regex_list = []
        self.pattern_list = []
        self.reg_type = reg_type
        self.fetch_method = fetch_method
        self._logger = logging.getLogger('bannedwords.regexes')

    def fetch_and_compile(self):
        self._logger.info('fetching regexes for banned words...')
        try:
            result = self.fetch_method(self.reg_type)
        except Exception as e:
            self._logger.exception('Failed getting banned words from external server %s', str(e))
            return

        self._logger.info('done fetching %s regexes for banned words about to compile', len(result))
        self.update_compile(result, self.reg_type)

    def update_compile(self, reg_list, regex_type):
        if not reg_list:
            return
        if len(reg_list) > 0:
            deleted = [ d['hash'] for d in self.regex_list if d not in reg_list ]
            added = [ a for a in reg_list if a not in self.regex_list ]
            for r in self.regex_list:
                if r['hash'] in deleted:
                    self.regex_list.remove(r)

            for p in self.pattern_list:
                if p['hash'] in deleted:
                    self.pattern_list.remove(p)

            number_added = len(added)
            for idx, new in enumerate(added):
                reg = new['regex']
                hash = new['hash']
                try:
                    pattern = re.compile(reg)
                except:
                    self._logger.error('[banned words] Failed to compile regex %s', reg)

                if pattern:
                    self.regex_list.append(new)
                    self.pattern_list.append({'hash': hash,
                     'pattern': pattern})
                self._logger.info('done compiling %s of %s', idx + 1, number_added)

        self._logger.info('done compiling regexes')

    def filter_and_slice_words(self, words):
        filtered_words = format_stripper(words)
        str_l = len(filtered_words)
        if str_l > MAX_CHECK_LENGTH:
            return [ filtered_words[i:i + MAX_CHECK_LENGTH] for i in range(0, str_l, MAX_CHECK_LENGTH - OVERLAPPING_CHOP) ]
        return [filtered_words]

    def check_words_allowed(self, words, err_message = 'LocationNameInvalidBannedWord'):
        if not words:
            return
        if not self.pattern_list:
            raise UserError('BannedWordsDown')
        words_list = self.filter_and_slice_words(words)
        for w in words_list:
            for p in self.pattern_list:
                blue.pyos.BeNice()
                if p['pattern'].search(w) is not None:
                    raise UserError(err_message)
