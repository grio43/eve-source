#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\htmllib.py
from warnings import warnpy3k
warnpy3k('the htmllib module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
import sgmllib
from formatter import AS_IS
__all__ = ['HTMLParser', 'HTMLParseError']

class HTMLParseError(sgmllib.SGMLParseError):
    pass


class HTMLParser(sgmllib.SGMLParser):
    from htmlentitydefs import entitydefs

    def __init__(self, formatter, verbose = 0):
        sgmllib.SGMLParser.__init__(self, verbose)
        self.formatter = formatter

    def error(self, message):
        raise HTMLParseError(message)

    def reset(self):
        sgmllib.SGMLParser.reset(self)
        self.savedata = None
        self.isindex = 0
        self.title = None
        self.base = None
        self.anchor = None
        self.anchorlist = []
        self.nofill = 0
        self.list_stack = []

    def handle_data(self, data):
        if self.savedata is not None:
            self.savedata = self.savedata + data
        elif self.nofill:
            self.formatter.add_literal_data(data)
        else:
            self.formatter.add_flowing_data(data)

    def save_bgn(self):
        self.savedata = ''

    def save_end(self):
        data = self.savedata
        self.savedata = None
        if not self.nofill:
            data = ' '.join(data.split())
        return data

    def anchor_bgn(self, href, name, type):
        self.anchor = href
        if self.anchor:
            self.anchorlist.append(href)

    def anchor_end(self):
        if self.anchor:
            self.handle_data('[%d]' % len(self.anchorlist))
            self.anchor = None

    def handle_image(self, src, alt, *args):
        self.handle_data(alt)

    def start_html(self, attrs):
        pass

    def end_html(self):
        pass

    def start_head(self, attrs):
        pass

    def end_head(self):
        pass

    def start_body(self, attrs):
        pass

    def end_body(self):
        pass

    def start_title(self, attrs):
        self.save_bgn()

    def end_title(self):
        self.title = self.save_end()

    def do_base(self, attrs):
        for a, v in attrs:
            if a == 'href':
                self.base = v

    def do_isindex(self, attrs):
        self.isindex = 1

    def do_link(self, attrs):
        pass

    def do_meta(self, attrs):
        pass

    def do_nextid(self, attrs):
        pass

    def start_h1(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font(('h1', 0, 1, 0))

    def end_h1(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()

    def start_h2(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font(('h2', 0, 1, 0))

    def end_h2(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()

    def start_h3(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font(('h3', 0, 1, 0))

    def end_h3(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()

    def start_h4(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font(('h4', 0, 1, 0))

    def end_h4(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()

    def start_h5(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font(('h5', 0, 1, 0))

    def end_h5(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()

    def start_h6(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font(('h6', 0, 1, 0))

    def end_h6(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()

    def do_p(self, attrs):
        self.formatter.end_paragraph(1)

    def start_pre(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_font((AS_IS,
         AS_IS,
         AS_IS,
         1))
        self.nofill = self.nofill + 1

    def end_pre(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_font()
        self.nofill = max(0, self.nofill - 1)

    def start_xmp(self, attrs):
        self.start_pre(attrs)
        self.setliteral('xmp')

    def end_xmp(self):
        self.end_pre()

    def start_listing(self, attrs):
        self.start_pre(attrs)
        self.setliteral('listing')

    def end_listing(self):
        self.end_pre()

    def start_address(self, attrs):
        self.formatter.end_paragraph(0)
        self.formatter.push_font((AS_IS,
         1,
         AS_IS,
         AS_IS))

    def end_address(self):
        self.formatter.end_paragraph(0)
        self.formatter.pop_font()

    def start_blockquote(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_margin('blockquote')

    def end_blockquote(self):
        self.formatter.end_paragraph(1)
        self.formatter.pop_margin()

    def start_ul(self, attrs):
        self.formatter.end_paragraph(not self.list_stack)
        self.formatter.push_margin('ul')
        self.list_stack.append(['ul', '*', 0])

    def end_ul(self):
        if self.list_stack:
            del self.list_stack[-1]
        self.formatter.end_paragraph(not self.list_stack)
        self.formatter.pop_margin()

    def do_li(self, attrs):
        self.formatter.end_paragraph(0)
        if self.list_stack:
            dummy, label, counter = top = self.list_stack[-1]
            top[2] = counter = counter + 1
        else:
            label, counter = ('*', 0)
        self.formatter.add_label_data(label, counter)

    def start_ol(self, attrs):
        self.formatter.end_paragraph(not self.list_stack)
        self.formatter.push_margin('ol')
        label = '1.'
        for a, v in attrs:
            if a == 'type':
                if len(v) == 1:
                    v = v + '.'
                label = v

        self.list_stack.append(['ol', label, 0])

    def end_ol(self):
        if self.list_stack:
            del self.list_stack[-1]
        self.formatter.end_paragraph(not self.list_stack)
        self.formatter.pop_margin()

    def start_menu(self, attrs):
        self.start_ul(attrs)

    def end_menu(self):
        self.end_ul()

    def start_dir(self, attrs):
        self.start_ul(attrs)

    def end_dir(self):
        self.end_ul()

    def start_dl(self, attrs):
        self.formatter.end_paragraph(1)
        self.list_stack.append(['dl', '', 0])

    def end_dl(self):
        self.ddpop(1)
        if self.list_stack:
            del self.list_stack[-1]

    def do_dt(self, attrs):
        self.ddpop()

    def do_dd(self, attrs):
        self.ddpop()
        self.formatter.push_margin('dd')
        self.list_stack.append(['dd', '', 0])

    def ddpop(self, bl = 0):
        self.formatter.end_paragraph(bl)
        if self.list_stack:
            if self.list_stack[-1][0] == 'dd':
                del self.list_stack[-1]
                self.formatter.pop_margin()

    def start_cite(self, attrs):
        self.start_i(attrs)

    def end_cite(self):
        self.end_i()

    def start_code(self, attrs):
        self.start_tt(attrs)

    def end_code(self):
        self.end_tt()

    def start_em(self, attrs):
        self.start_i(attrs)

    def end_em(self):
        self.end_i()

    def start_kbd(self, attrs):
        self.start_tt(attrs)

    def end_kbd(self):
        self.end_tt()

    def start_samp(self, attrs):
        self.start_tt(attrs)

    def end_samp(self):
        self.end_tt()

    def start_strong(self, attrs):
        self.start_b(attrs)

    def end_strong(self):
        self.end_b()

    def start_var(self, attrs):
        self.start_i(attrs)

    def end_var(self):
        self.end_i()

    def start_i(self, attrs):
        self.formatter.push_font((AS_IS,
         1,
         AS_IS,
         AS_IS))

    def end_i(self):
        self.formatter.pop_font()

    def start_b(self, attrs):
        self.formatter.push_font((AS_IS,
         AS_IS,
         1,
         AS_IS))

    def end_b(self):
        self.formatter.pop_font()

    def start_tt(self, attrs):
        self.formatter.push_font((AS_IS,
         AS_IS,
         AS_IS,
         1))

    def end_tt(self):
        self.formatter.pop_font()

    def start_a(self, attrs):
        href = ''
        name = ''
        type = ''
        for attrname, value in attrs:
            value = value.strip()
            if attrname == 'href':
                href = value
            if attrname == 'name':
                name = value
            if attrname == 'type':
                type = value.lower()

        self.anchor_bgn(href, name, type)

    def end_a(self):
        self.anchor_end()

    def do_br(self, attrs):
        self.formatter.add_line_break()

    def do_hr(self, attrs):
        self.formatter.add_hor_rule()

    def do_img(self, attrs):
        align = ''
        alt = '(image)'
        ismap = ''
        src = ''
        width = 0
        height = 0
        for attrname, value in attrs:
            if attrname == 'align':
                align = value
            if attrname == 'alt':
                alt = value
            if attrname == 'ismap':
                ismap = value
            if attrname == 'src':
                src = value
            if attrname == 'width':
                try:
                    width = int(value)
                except ValueError:
                    pass

            if attrname == 'height':
                try:
                    height = int(value)
                except ValueError:
                    pass

        self.handle_image(src, alt, ismap, align, width, height)

    def do_plaintext(self, attrs):
        self.start_pre(attrs)
        self.setnomoretags()

    def unknown_starttag(self, tag, attrs):
        pass

    def unknown_endtag(self, tag):
        pass


def test(args = None):
    import sys, formatter
    if not args:
        args = sys.argv[1:]
    silent = args and args[0] == '-s'
    if silent:
        del args[0]
    if args:
        file = args[0]
    else:
        file = 'test.html'
    if file == '-':
        f = sys.stdin
    else:
        try:
            f = open(file, 'r')
        except IOError as msg:
            print file, ':', msg
            sys.exit(1)

    data = f.read()
    if f is not sys.stdin:
        f.close()
    if silent:
        f = formatter.NullFormatter()
    else:
        f = formatter.AbstractFormatter(formatter.DumbWriter())
    p = HTMLParser(f)
    p.feed(data)
    p.close()


if __name__ == '__main__':
    test()
