#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\eveformat\tags.py
import re
import chroma

def center(text):
    return u'<center>{}</center>'.format(text)


def color(text, color):
    return u'<color={}>{}</color>'.format(chroma.Color.from_any(color).hex_argb, text)


def bold(text):
    return u'<b>{}</b>'.format(text)


def italic(text):
    return u'<i>{}</i>'.format(text)


def underline(text):
    return u'<u>{}</u>'.format(text)


def font_size(text, size):
    return u'<fontsize={}>{}</fontsize>'.format(int(size), text)


def hint(text, hint):
    return u'<hint="{}">{}</hint>'.format(hint, text)


def strip_tags(text, tags):
    _validate_tags(tags)
    pattern = _compose_tag_pattern(tags)
    return type(text)('').join(re.split(pattern, text))


def strip_all_tags(text, ignore = None):
    if not ignore:
        return ''.join(re.split('<.*?>', text))
    _validate_tags(ignore)
    pattern = _compose_tag_pattern(ignore)
    all_tags = re.findall('<.*?>', text)
    ignored_tags = re.findall(pattern, text)
    tags_to_strip = [ tag for tag in all_tags if tag not in ignored_tags ]
    for tag in tags_to_strip:
        text = text.replace(tag, '')

    return text


def _compose_tag_pattern(tags):
    return '|'.join([ '</{0}>|<{0}>|<{0} .*?>|<{0} *=.*?>|<{0}/>'.format(tag) for tag in tags ])


def _validate_tags(tags):
    if isinstance(tags, basestring):
        raise TypeError('tags must be a list of strings, got a single string')
    for tag in tags:
        if not _validate_tag(tag):
            raise ValueError('invalid tag: {}'.format(tag))


_valid_tag_pattern = re.compile('\\A[a-zA-Z]+\\Z')

def _validate_tag(tag):
    return bool(_valid_tag_pattern.match(tag))


def replace_text_ignoring_tags(string, old, new):
    split_by_tags = re.split('(<.*?>)', string)
    result = u''
    for part in split_by_tags:
        if part.startswith('<'):
            result += part
            continue
        result += part.replace(old, new)

    return result


def truncate_text_ignoring_tags(string, length, trail = None):
    split_by_tags = re.split('(<.*?>)', string)
    done = False
    result = u''
    counter = 0
    for part in split_by_tags:
        if part.startswith('<'):
            result += part
            continue
        if done:
            continue
        encoded = simple_html_unescape(part)
        for letter in encoded:
            result += simple_html_escape(letter)
            counter += 1
            if counter == length:
                done = True
                if trail:
                    result += trail
                break

    return result


def simple_html_unescape(text):
    return text.replace(u'&gt;', u'>').replace(u'&lt;', u'<').replace(u'&amp;', u'&').replace(u'&AMP;', u'&').replace(u'&GT;', u'>').replace(u'&LT;', u'<')


def simple_html_escape(text):
    return text.replace(u'&', u'&amp;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')
