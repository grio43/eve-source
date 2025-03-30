#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\langutils\comfylang.py
import logging
log = logging.getLogger(__name__)

class ComfyLanguage(object):
    __slots__ = ('name', 'native', 'code', 'code3', 'code3b', 'sub', 'sub_name', 'win_id', 'win_primary_id', 'win_sub_id', 'db_num', 'is_valid')

    def __init__(self, name, native, code, code3, sub, sub_name, win_id, code3b = '', win_primary_id = 0, win_sub_id = 1, db_num = 0):
        self.name = name
        self.native = native
        self.code = code
        self.code3 = code3
        self.code3b = code3b or self.code3
        self.sub = sub
        self.sub_name = sub_name
        self.win_id = win_id
        self.win_primary_id = win_primary_id or self.win_id & 255
        self.win_sub_id = win_sub_id
        self.db_num = db_num or self.win_id

    def __unicode__(self):
        return u'%s' % self.code

    def __str__(self):
        return self.code

    def __repr__(self):
        return u'<ComfyLanguage code=%s, name=%s, win_id=%s, db_num=%s>' % (self.code,
         self.name,
         self.win_id,
         self.db_num)

    def __hash__(self):
        return hash(self.mls_language_id())

    def __int__(self):
        return self.win_id

    def __long__(self):
        return self.win_id

    def __eq__(self, other):
        if isinstance(other, ComfyLanguage):
            return other.code == self.code
        from langutils import logic
        casted_other = logic.any_to_comfy_language(other, None)
        if isinstance(casted_other, ComfyLanguage):
            return casted_other.code == self.code
        return False

    def mls_language_id(self):
        return self.code.upper()

    def zlocalization_numeric_language_id(self):
        return self.db_num

    def cerberus_code(self):
        return self.code

    def zlocalization_language_id(self):
        if self.code == 'en':
            return 'en-us'
        return self.code
