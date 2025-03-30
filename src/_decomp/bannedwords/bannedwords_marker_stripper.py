#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\bannedwords\bannedwords_marker_stripper.py
import re
import logging

def compile_pattern(tag):
    return re.compile('(?i)<%s(?P<attrs>[^>]*)>(?P<inner>.*?)</%s>' % (tag, tag))


def compile_attribute_pattern(attribute_name, valid_value_regex):
    return re.compile('(?i)%s\\="?%s"?' % (attribute_name, valid_value_regex))


STRIPPER_MAP = {'font': {'pattern': compile_pattern('font'),
          'attributes': {'size': compile_attribute_pattern('size', '\\d{1,2}'),
                         'color': compile_attribute_pattern('color', '(#|0x)[\\dabcdef]{6,8}')}},
 'a': {'pattern': compile_pattern('a'),
       'attributes': {'href': compile_attribute_pattern('href', '(fitting|joinchannel|overviewpreset|showinfo|killreport)\\:[\\dabcdef/;:-]+')}},
 'color': {'pattern': compile_pattern('color'),
           'attributes': {'__none__': compile_attribute_pattern('', '(#|0x)[\\dabcdef]{6,8}')}},
 'fontsize': {'pattern': compile_pattern('fontsize'),
              'attributes': {'__none__': compile_attribute_pattern('', '\\d{1,2}')}},
 'u': {'pattern': compile_pattern('u'),
       'attributes': {}},
 'i': {'pattern': compile_pattern('i'),
       'attributes': {}},
 'b': {'pattern': compile_pattern('b'),
       'attributes': {}},
 'loc': {'pattern': compile_pattern('loc'),
         'attributes': {}},
 'url': {'pattern': compile_pattern('url'),
         'attributes': {'__none__': compile_attribute_pattern('', '(fitting|joinchannel|overviewpreset|showinfo|killreport)\\:[\\dabcdef/;:-]+')}}}

def format_stripper(markup):
    try:
        working_text = markup.replace('<br>', '')
        for tag, data in STRIPPER_MAP.iteritems():
            pattern = data.get('pattern', None)
            buff = []
            i = 0
            m = pattern.search(working_text)
            while m:
                buff.append(working_text[i:m.start()])
                attrs = m.group('attrs') or ''
                if attrs:
                    attribute_patterns = data.get('attributes', None)
                    if attribute_patterns:
                        for attr_name, attr_pattern in attribute_patterns.iteritems():
                            attrs = attr_pattern.sub('', attrs)

                    attrs = attrs.strip()
                if attrs:
                    buff.append(attrs)
                inner = m.group('inner') or ''
                if inner:
                    buff.append(inner)
                i = m.end()
                m = pattern.search(working_text, i)

            if i:
                buff.append(working_text[i:])
            if buff:
                working_text = u''.join(buff)

        return working_text
    except Exception as ex:
        logging.warn('Failed to strip text marker, error: {!r}'.format(str(ex)))
        return markup
