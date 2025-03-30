#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\google\protobuf\text_encoding.py
import re
import six
_cescape_chr_to_symbol_map = {}
_cescape_chr_to_symbol_map[9] = '\\t'
_cescape_chr_to_symbol_map[10] = '\\n'
_cescape_chr_to_symbol_map[13] = '\\r'
_cescape_chr_to_symbol_map[34] = '\\"'
_cescape_chr_to_symbol_map[39] = "\\'"
_cescape_chr_to_symbol_map[92] = '\\\\'
_cescape_unicode_to_str = [ chr(i) for i in range(0, 256) ]
for byte, string in _cescape_chr_to_symbol_map.items():
    _cescape_unicode_to_str[byte] = string

_cescape_byte_to_str = [ '\\%03o' % i for i in range(0, 32) ] + [ chr(i) for i in range(32, 127) ] + [ '\\%03o' % i for i in range(127, 256) ]
for byte, string in _cescape_chr_to_symbol_map.items():
    _cescape_byte_to_str[byte] = string

del byte
del string

def CEscape(text, as_utf8):
    if six.PY3:
        text_is_unicode = isinstance(text, str)
        if as_utf8 and text_is_unicode:
            return text.translate(_cescape_chr_to_symbol_map)
        ord_ = ord if text_is_unicode else (lambda x: x)
    else:
        ord_ = ord
    if as_utf8:
        return ''.join((_cescape_unicode_to_str[ord_(c)] for c in text))
    return ''.join((_cescape_byte_to_str[ord_(c)] for c in text))


_CUNESCAPE_HEX = re.compile('(\\\\+)x([0-9a-fA-F])(?![0-9a-fA-F])')

def CUnescape(text):

    def ReplaceHex(m):
        if len(m.group(1)) & 1:
            return m.group(1) + 'x0' + m.group(2)
        return m.group(0)

    result = _CUNESCAPE_HEX.sub(ReplaceHex, text)
    if six.PY2:
        return result.decode('string_escape')
    return result.encode('utf-8').decode('unicode_escape').encode('raw_unicode_escape')
