#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\scriber\htmlutils.py
import re
import HTMLParser
import datetime
import datetimeutils
import typeutils
from scriber import const
from inventorycommon import const as iconst

class TolerantParser(HTMLParser.HTMLParser):
    ON_ERROR_THROW = 0
    ON_ERROR_REPLACE = 1
    ON_ERROR_SKIP = 2

    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.on_error = self.ON_ERROR_REPLACE
        self.parse_errors = []

    def on_error_replace_with(self):
        return '&lt;'

    def parse_starttag(self, i):
        try:
            return HTMLParser.HTMLParser.parse_starttag(self, i)
        except HTMLParser.HTMLParseError as e:
            self.parse_errors.append(e)
            if self.on_error == self.ON_ERROR_REPLACE:
                self.handle_data(self.on_error_replace_with())
                return i + 1
            if self.on_error == self.ON_ERROR_SKIP:
                return i + 1
            raise

    def parse_endtag(self, i):
        try:
            return HTMLParser.HTMLParser.parse_endtag(self, i)
        except HTMLParser.HTMLParseError as e:
            self.parse_errors.append(e)
            if self.on_error == self.ON_ERROR_REPLACE:
                self.handle_data(self.on_error_replace_with())
                return i + 1
            if self.on_error == self.ON_ERROR_SKIP:
                return i + 1
            raise

    def unknown_decl(self, data):
        pass

    def goahead(self, end):
        rawdata = self.rawdata
        i = 0
        n = len(rawdata)
        while i < n:
            match = self.interesting.search(rawdata, i)
            if match:
                j = match.start()
            else:
                j = n
            if i < j:
                self.handle_data(rawdata[i:j])
            i = self.updatepos(i, j)
            if i == n:
                break
            startswith = rawdata.startswith
            if startswith('<', i):
                if HTMLParser.starttagopen.match(rawdata, i):
                    k = self.parse_starttag(i)
                elif startswith('</', i):
                    k = self.parse_endtag(i)
                elif startswith('<!--', i):
                    k = self.parse_comment(i)
                elif startswith('<?', i):
                    k = self.parse_pi(i)
                elif startswith('<!', i):
                    k = self.parse_declaration(i)
                elif i + 1 < n:
                    self.handle_data('<')
                    k = i + 1
                else:
                    break
                if k < 0:
                    if end:
                        self.error('EOF in middle of construct')
                    break
                i = self.updatepos(i, k)
            elif startswith('&#', i):
                match = HTMLParser.charref.match(rawdata, i)
                if match:
                    name = match.group()[2:-1]
                    k = match.end()
                    if not startswith(';', k - 1):
                        self.handle_data('&#' + name)
                        k = k - 1
                    else:
                        self.handle_charref(name)
                    i = self.updatepos(i, k)
                    continue
                else:
                    if ';' in rawdata[i:]:
                        self.handle_data(rawdata[0:2])
                        i = self.updatepos(i, 2)
                    break
            elif startswith('&', i):
                match = HTMLParser.entityref.match(rawdata, i)
                if match:
                    name = match.group(1)
                    k = match.end()
                    if not startswith(';', k - 1):
                        self.handle_data('&' + name)
                        k = k - 1
                    else:
                        self.handle_entityref(name)
                    i = self.updatepos(i, k)
                    continue
                match = HTMLParser.incomplete.match(rawdata, i)
                if match:
                    self.handle_data(rawdata[i:])
                    if end and match.group() == rawdata[i:]:
                        self.error('EOF in middle of entity or char ref')
                    break
                elif i + 1 < n:
                    self.handle_data('&')
                    i = self.updatepos(i, i + 1)
                else:
                    self.handle_data('&')
                    break

        if end and i < n:
            self.handle_data(rawdata[i:n])
            i = self.updatepos(i, n)
        self.rawdata = rawdata[i:]


class TagStripper(TolerantParser):

    def __init__(self, tag_list = tuple(), preserve_content_list = tuple()):
        TolerantParser.__init__(self)
        self._stripped = []
        self.tag_list = tag_list
        self.preserve_content_list = preserve_content_list
        self.ignore_content_until = None

    def handle_data(self, data):
        if not self.ignore_content_until:
            self._stripped.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in self.tag_list:
            if tag not in self.preserve_content_list:
                self.ignore_content_until = tag
        else:
            attributes = ''
            if attrs:
                attributes = ' %s' % attr_str(attrs)
            self._stripped.append('<%s%s>' % (tag, attributes))

    def handle_endtag(self, tag):
        if self.ignore_content_until == tag:
            self.ignore_content_until = None
        if tag not in self.tag_list:
            self._stripped.append('</%s>' % tag)

    def handle_entityref(self, name):
        if not self.ignore_content_until:
            self._stripped.append('&%s;' % name)

    def handle_charref(self, name):
        if not self.ignore_content_until:
            self._stripped.append('&#%s;' % name)

    def get_stripped(self):
        return ''.join(self._stripped)

    def flush_stripped(self):
        text = self.get_stripped()
        self._stripped = []
        return text


class HTMLStripper(TolerantParser):
    HTML_WHITESPACE = '[ \\t\\r\\n]+'
    HTML_BREAKS = '( \\n|\\n )'
    HTML_NON_CONTENT_TAGS = ['head',
     'script',
     'style',
     'embed',
     'frameset',
     'object',
     'iframe',
     'source',
     'track',
     'video',
     'audio',
     'canvas',
     'meta']

    def __init__(self, preserve_links = True, preserve_images = False, decode_chars = True, error_tolerance = True):
        TolerantParser.__init__(self)
        self._text = []
        self.preserve_links = preserve_links
        self.preserve_images = preserve_images
        self.decode_chars = decode_chars
        self.error_tolerance = error_tolerance
        self.link = ''
        self.ignore_content_until = None

    def handle_data(self, data):
        if not self.ignore_content_until:
            self._text.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in self.HTML_NON_CONTENT_TAGS:
            self.ignore_content_until = tag
        if tag == 'a':
            if self.preserve_links and attrs:
                attrs = dict(attrs)
                self.link = attrs.get('href', '')
        if tag == 'img':
            if self.preserve_images and attrs:
                attrs = dict(attrs)
                self._text.append('[%s]' % attrs.get('src', ''))
        elif tag == 'br':
            self._add_linefeed()

    def handle_endtag(self, tag):
        if self.ignore_content_until == tag:
            self.ignore_content_until = None
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self._add_linefeed(2)
        elif tag == 'a' and self.preserve_links and self.link:
            self._text.append(' [%s]' % self.link)
            self.link = ''

    def handle_entityref(self, name):
        if not self.ignore_content_until:
            code = '&%s;' % name
            if self.decode_chars:
                code = self.unescape(code)
            self._text.append(code)

    def handle_charref(self, name):
        if not self.ignore_content_until:
            code = '&#%s;' % name
            if self.decode_chars:
                code = self.unescape(code)
            self._text.append(code)

    def on_error_replace_with(self):
        if self.decode_chars:
            return '['
        else:
            return '&lt;'

    def _add_linefeed(self, count = 1):
        self._text.append('{{LF}}' * count)

    def get_text(self):
        text = ''.join(self._text)
        text = re.sub(self.HTML_WHITESPACE, ' ', text)
        text = text.replace('{{LF}}', '\n')
        text = re.sub(self.HTML_BREAKS, '\n', text)
        return text.strip()

    def flush_text(self):
        text = self.get_text()
        self._text = []
        return text


class AbstractCleaner(object):

    def __init__(self, markup):
        self.markup = markup
        self.ok = True
        self.clean_markup = ''
        self.missing_tags = None
        self.break_idx = -1
        self.fixed_markup = None
        self.html = ''
        self.length = 0

    def cleanup(self):
        if self.markup and isinstance(self.markup, (str, unicode)):
            self.length = len(self.markup)
            self.ok, self.missing_tags, self.break_idx = validate_evemarkup(self.markup)
            self.clean_markup = remove_loc_tags(self.markup)
            self.clean_markup = remove_empty_formatting_tags(self.clean_markup)
            if not self.ok:
                motd_ok2, missing_tags2, break_idx2 = validate_evemarkup(self.clean_markup)
                if not motd_ok2:
                    self.fixed_markup = fix_broken_markup(self.clean_markup, missing_tags2, break_idx2)
                    self.html = evemarkup_to_html(self.fixed_markup)
                else:
                    self.html = evemarkup_to_html(self.clean_markup)
            else:
                self.html = evemarkup_to_html(self.clean_markup)


class MotdCleaner(AbstractCleaner):

    def __init__(self, live_motd, channel):
        super(MotdCleaner, self).__init__(live_motd)
        self.channel = channel
        self.db_motd_length = 0
        self.has_loc = None

    def cleanup(self):
        if self.markup:
            self.has_loc = '<loc>' in self.markup
        else:
            self.has_loc = False
        if self.channel.motd:
            self.db_motd_length = len(self.channel.motd)
        super(MotdCleaner, self).cleanup()


class EveMailCleaner(AbstractCleaner):

    def __init__(self, body):
        super(EveMailCleaner, self).__init__(body)


def strip_html(html_string, preserve_links = True, preserve_images = False, decode_chars = True):
    stripper = HTMLStripper(preserve_links, preserve_images, decode_chars)
    stripper.feed(html_string)
    return stripper.get_text()


def newline_to_html(string):
    return '<p>%s</p>' % reduce(lambda h, n: h.replace(*n), (('\r', ''), ('\n\n', '</p><p>'), ('\n', '<br />')), string)


def sanitize(html_string, keep_amp = False):
    if not keep_amp:
        html_string = html_string.replace('&', '&amp;')
    return reduce(lambda string, params: string.replace(*params), (('<', '&lt;'), ('>', '&gt;')), html_string)


def unsanitize(string):
    return reduce(lambda string, params: string.replace(*params), (('&gt;', '>'), ('&lt;', '<'), ('&amp;', '&')), string)


def esc_email_tags(html, replacer = const.EMAIL_TAG_REPLACE_HTML):
    return const.EMAIL_TAG_GRABBER.sub(replacer, html)


def strip_bad_tags(html_string):
    stripper = TagStripper(HTMLStripper.HTML_NON_CONTENT_TAGS)
    stripper.feed(html_string)
    return stripper.get_stripped()


def attr_str(attribute_list, xhtml_strict = False):
    buff = []
    if isinstance(attribute_list, dict):
        attribute_list = attribute_list.items()
    for attr in attribute_list:
        if len(attr) > 1:
            buff.append('%s="%s"' % (attr[0], attr[1]))
        elif xhtml_strict:
            buff.append('%s="%s"' % (attr[0], attr[0]))
        else:
            buff.append('%s' % attr[0])

    return ' '.join(buff)


def parse_user_notes(raw_notes, note_date = datetime.datetime.now()):
    raw_notes = sanitize(raw_notes, keep_amp=True)
    raw_notes = parse_markdown_link(raw_notes)
    note_date = datetimeutils.any_to_datetime(note_date)
    i = 0
    parsed_notes = []
    for m in const.NOTE_LINK_A_HREF_MATCHER.finditer(raw_notes):
        parsed_notes.append(parse_note_auto_link(raw_notes[i:m.start()], note_date))
        parsed_notes.append(m.group(0))
        i = m.end()

    parsed_notes.append(parse_note_auto_link(raw_notes[i:], note_date))
    return ''.join(parsed_notes).replace('\n', '<br>')


def parse_markdown_link(raw_text):
    return re.sub(const.NOTE_LINK_MARKDOWN_PATTERN, const.NOTE_LINK_MARKDOWN_REPLACE, raw_text)


def parse_note_auto_link(raw_text, note_date):
    i = 0
    parsed_text = []
    for m in const.NOTE_LINK_AUTO_LINKER.finditer(raw_text):
        parsed_text.append(raw_text[i:m.start()])
        parsed_text.append(const.NOTE_LINK_AUTO_LINK.format(url=_get_ticket_url(m.group(3), note_date), text='%s%s%s' % (m.group(1), m.group(2), m.group(3))))
        i = m.end()

    parsed_text.append(raw_text[i:])
    return ''.join(parsed_text)


def _get_ticket_url(ticket_id, note_date):
    ticket_id = typeutils.int_eval(ticket_id)
    if ticket_id > const.OLD_TICKET_ID_THRESHOLD and note_date.year < 2016:
        return const.OLD_TICKET_URL.format(ticketID=ticket_id)
    return const.TICKET_URL.format(ticketID=ticket_id)


def strip_extra_amp(string):
    return re.sub(const.EXTRA_AMP_MATCHER, const.EXTRA_AMP_REPLACER, string)


def esp_item_link(item):
    if item.item_type.category_id == iconst.categoryOwner:
        if item.item_type.group_id == iconst.groupCharacter:
            return '/gm/character.py?action=Character&characterID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupCorporation:
            return '/gm/corporation.py?action=Corporation&corporationID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupAlliance:
            return '/gm/alliance.py?action=Alliance&allianceID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupFaction:
            return '/gm/faction.py?action=Faction&factionID=%d' % item.item_id
    elif item.item_type.category_id == iconst.categoryCelestial:
        if item.item_type.group_id == iconst.groupRegion:
            return '/gd/universe.py?action=Region&regionID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupConstellation:
            return '/gd/universe.py?action=Constellation&constellationID=%s' % item.item_id
        if item.item_type.group_id == iconst.groupSolarSystem:
            return '/gd/universe.py?action=System&systemID=%d' % item.item_id
        if item.item_type.group_id == iconst.groupAsteroidBelt:
            return '/gd/universe.py?action=AsteroidBelt&asteroidBeltID=%d' % item.item_id
        if item.item_type.group_id in [iconst.groupPlanet, iconst.groupMoon]:
            return '/gd/universe.py?action=Celestial&celestialID=%d' % item.item_id
    elif item.item_type.category_id == iconst.categoryStation:
        if item.item_type.group_id == iconst.groupStation:
            return '/gm/stations.py?action=Station&stationID=%d' % item.item_id
    else:
        if item.item_type.category_id == iconst.categorySovereigntyStructure:
            return '/gm/starbase.py?action=Starbase&towerID=%d' % item.item_id
        if item.item_type.category_id == iconst.categoryShip:
            return '/gm/character.py?action=Ship&characterID=%d&shipID=%d' % (item.owner_id, item.item_id)
    return '/gm/inventory.py?action=Item&itemID=%d' % item.item_id


def validate_evemarkup(markup):
    markup = markup.lower()
    idx = -1
    if '<' in markup:
        idx = markup.rindex('<')
        last_part = markup[idx:]
        if '>' in last_part:
            idx = -1
    if idx > -1:
        markup = markup[:idx]
    start_less_markup = []
    tag_starts_found = []
    p = 0
    for match in re.finditer('<(\\w+)[^>]*>', markup):
        start_less_markup.append(markup[p:match.start()])
        p = match.end()
        tag = match.group(1)
        if tag != 'br':
            tag_starts_found.append(tag)

    start_less_markup.append(markup[p:])
    markup_no_start = ''.join(start_less_markup)
    for match in re.finditer('</(\\w+)>', markup_no_start):
        tag = match.group(1)
        if tag != 'br':
            if tag in tag_starts_found:
                tag_starts_found.remove(tag)

    return (idx == -1 and not tag_starts_found, tag_starts_found, idx)


def fix_broken_markup(markup, close_tags_list = None, index_of_broken_tag = -1):
    if index_of_broken_tag > -1:
        markup = markup[:index_of_broken_tag]
    if close_tags_list:
        append_tags = [ '</%s>' % t for t in close_tags_list ]
        markup = '%s%s' % (markup, ''.join(append_tags))
    return markup


def remove_empty_formatting_tags(markup):
    tag_list = ('fontsize', 'color', 'i', 'u', 'b', 'url')
    for tag in tag_list:
        fixed_markup = []
        p = 0
        for match in re.finditer('(?i)<%s[^>]*></%s>' % (tag, tag), markup):
            fixed_markup.append(markup[p:match.start()])
            p = match.end()

        fixed_markup.append(markup[p:])
        markup = ''.join(fixed_markup)

    return markup


def remove_tags(markup, *args):
    tag_list = []
    if args:
        for t in args:
            if isinstance(t, (list, tuple)):
                tag_list.extend(t)
            else:
                tag_list.append(t)

    for tag in tag_list:
        markup = re.sub('(?i)<%s[^>]*>(.*?)</%s>' % (tag, tag), '\\1', markup)

    return markup


def remove_loc_tags(markup):
    return markup.replace('<loc>', '').replace('</loc>', '')


def add_loc_tags(markup):
    return re.sub(const.SHOW_INFO_PATTERN, const.SHOW_INFO_REPLACE, markup)


def evemarkup_to_html(markup):
    markup = remove_loc_tags(markup)
    markup = re.sub(const.EVEML_SHOWINFO_PATTERN, const.EVEML_SHOWINFO_REPLACE, markup)
    markup = re.sub(const.EVEML_FONT_PATTERN, const.EVEML_FONT_REPLACE, markup)
    markup = re.sub(const.EVEML_FONTSIZE_PATTERN, const.EVEML_FONTSIZE_REPLACE, markup)
    markup = re.sub(const.EVEML_COLOR_PATTERN, const.EVEML_COLOR_REPLACE, markup)
    markup = re.sub(const.EVEML_URL_PATTERN, const.EVEML_URL_REPLACE, markup)
    return markup


def markup_syntax_html(markup):
    pass


if __name__ == '__main__':
    s1 = "<fontsize=36>Stuff</fontsize><br><fontsize=36></fontsize><br><fontsize=14>* <b>Here's</b> a <loc><url=http://mbl.is>thin</loc>g</url><br>* Here's another <loc><url=showinfo:1373//90000012>thin</loc>g</url><br>* More <loc><url=showinfo:5//30000142>stuf</loc>f</url><br>* And <i>some</i> <loc><url=showinfo:54//60014839>stuff</url></loc> to <color=0xff00ff00>boot</color><br>* Wny &gt; no <loc><url=showinfo:2//98000002>type</url></loc>?!?<br>* Let's try <loc><color=0xffff0000>type</loc> again!</fontsize></color>"
    s2 = "<fontsize=36>Stuff</fontsize><br><br><fontsize=14>* <b>Here's</b> a <loc><url=http://mbl.is>thin</loc>g</url><br>* Here's another <loc><url=showinfo:1373//90000012>thin</loc>g</url><br>* More <loc><url=showinfo:5//30000142>stuf</loc>f</url><br>* And <i>some</i> <loc><url=showinfo:54//60014839>stuff</url></loc> to <color=0xff00ff00>boot</color><br>* Wny &gt; no <loc><url=showinfo:2//98000002>type</url></loc>?!?<br>* Let's try <loc><color=0xffff0000>type</loc> again!"
    s3 = "<fontsize=36>Stuff</fontsize><br><br><b>Here's</b> a <loc"
    s4 = "<fontsize=36>Stuff<br><br><b>Here's</b> a <loc"
    nl1 = remove_loc_tags(s1)
    nl2 = remove_loc_tags(s2)
    nl3 = remove_loc_tags(s3)
    nl4 = remove_loc_tags(s4)
    print 'validate_evemarkup'
    ok1, tl1, ix1 = validate_evemarkup(nl1)
    print ok1, tl1, ix1
    ok2, tl2, ix2 = validate_evemarkup(nl2)
    print ok2, tl2, ix2
    ok3, tl3, ix3 = validate_evemarkup(nl3)
    print ok3, tl3, ix3
    ok4, tl4, ix4 = validate_evemarkup(nl4)
    print ok4, tl4, ix4
    print 'fix_broken_markup'
    f1 = fix_broken_markup(nl1, tl1, ix1)
    print f1
    f2 = fix_broken_markup(nl3, tl3, ix3)
    print f2
    f3 = fix_broken_markup(nl2, tl2, ix2)
    print f3
    f4 = fix_broken_markup(nl4, tl4, ix4)
    print f4
    print 'remove_empty_formatting_tags'
    ff1 = remove_empty_formatting_tags(f1)
    print ff1
    ff2 = remove_empty_formatting_tags(f2)
    print ff2
    ff3 = remove_empty_formatting_tags(f3)
    print ff3
    ff4 = remove_empty_formatting_tags(f4)
    print ff4
    print 'add_loc_tags'
    fi1 = add_loc_tags(ff1)
    print fi1
    fi2 = add_loc_tags(ff2)
    print fi2
    fi3 = add_loc_tags(ff3)
    print fi3
    fi4 = add_loc_tags(ff4)
    print fi4
    print '----'
    print remove_tags(fi1, 'fontsize', 'color')
