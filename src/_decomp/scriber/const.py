#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\scriber\const.py
import re
LOGGER_NAME = 'scriber'
EMAIL_TAG_GRABBER = re.compile('<(/?[\\w._%+-]+@[\\w.-]+\\.[\\S]{2,4} ?/?)>')
EMAIL_TAG_REPLACE_HTML = '&lt;\\1&gt;'
EMAIL_TAG_REPLACE_BRACKET = '[\\1]'
URL_MATCHER = re.compile('^(?:(?:(?P<schema>(?:[a-z][a-z0-9+\\-.]*):)?//(?P<host>[^/?#\\s]*))?)?(?P<path>/?[^?#\\s]*)(?:\\?(?P<querystr>[^#\\s]*))?(?:#(?P<fragment>\\S*))?')
HOST_MATCHER = re.compile('^(?:(?P<user>[^@:\\s]*)(?::(?P<pass>[^@\\s]*))?@)?(?P<host>[^:\\s]+)(?::(?P<port>[\\d]+))?$')
EXTRA_AMP_MATCHER = re.compile('(?i)&amp;#([0-9a-z]{2,8});')
EXTRA_AMP_REPLACER = '&#\\1;'
PETITION_LINK_NOTE_PATTERN = '\\b(?=\\w)(?i)(pet(?:ition)?|tic(?:ket)?)([: ]{1,2})(\\d+)\\b(?!\\w)'
PETITION_LINK_NOTE_REPLACE = '<a href="/gm/petitionClient.py?action=ViewPetition&petitionID=\\3">\\1\\2\\3</a>'
NOTE_LINK_A_HREF_MATCHER = re.compile('(?i)(<a(?:[ >]|[\\w =\'"]*>)[^<]*</a>)')
NOTE_LINK_AUTO_LINKER = re.compile('(?i)\\b(pet(?:ition)?|tic(?:ket)?)([: ]{1,2}[#]?)(\\d+)(?![\\w<])')
NOTE_LINK_AUTO_LINK = '<a href="{url}">{text}</a>'
NOTE_LINK_MARKDOWN_PATTERN = '(?i)\\[([^\\t\\r\\n\\<\\(]+)]\\(((http[s]?://)?([\\w.]+)?(?::(\\d+))?([\\w./:?&=#%,-]+))\\)'
NOTE_LINK_MARKDOWN_REPLACE = '<a href="\\2">\\1</a>'
SHOW_INFO_PATTERN = '(?i)<url=showinfo([^>]+)>(.*?)</url>'
SHOW_INFO_REPLACE = '<loc><url=showinfo\\1>\\2</url></loc>'
EVEML_FONTSIZE_PATTERN = '(?i)<fontsize=([^>]+)>(.*?)</fontsize>'
EVEML_FONTSIZE_REPLACE = '<span style="font-size:\\1px;">\\2</span>'
EVEML_FONT_PATTERN = '(?i)<font size=\\"(\\d+)\\" color=\\"([^>]+)\\">(.*?)</font>'
EVEML_FONT_REPLACE = '<span style="font-size":"\\1px"; "color":"\\2">\\3</span>'
EVEML_COLOR_PATTERN = '(?i)<color=0x\\w{2}(\\w{2})(\\w{2})(\\w{2})>(.*?)</color>'
EVEML_COLOR_REPLACE = '<span style="color:#\\1\\2\\3;">\\4</span>'
EVEML_URL_PATTERN = '(?i)<url=([^>]+)>(.*?)</url>'
EVEML_URL_REPLACE = '<a href="#" title="\\1">\\2</a>'
EVEML_SHOWINFO_PATTERN = '(?i)<a href="[^:]+:([^>]+)//([^>]+)">(.*?)</a>'
EVEML_SHOWINFO_REPLACE = '<a href="/gm/inventory.py?action=Item&itemID=\\2&">\\3</a>'
VALID_USERNAME_REGEX = '(?i)^(?:[a-z]|[0-9]|[-_.#:])+$'
VALID_IP_REGEX = '(?i)^(?:[0-9]{1,3}\\.){3}[0-9]{1,3}$'
VALID_EMAIL_REGEX = '(?i)^[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}$'
VALID_CHARACTER_NAME_REGEX = "(?i)^(?:[a-z]|[0-9]|[ '-])+$"
OLD_TICKET_ID_THRESHOLD = 1000000
OLD_TICKET_URL = '/gm/petitionClient.py?action=ViewPetition&petitionID={ticketID}'
TICKET_URL = 'https://ccpcommunity.zendesk.com/agent/tickets/{ticketID}'
MIME_TYPE_DEFAULT = 'application/octet-stream'
MIME_TYPE_BY_EXTENSION = {'css': 'text/css',
 'csv': 'text/csv',
 'dtd': 'application/xml-dtd',
 'eml': 'message/rfc822',
 'htc': 'text/x-component',
 'htm': 'text/html',
 'html': 'text/html',
 'js': 'application/x-javascript',
 'json': 'application/json',
 'rtx': 'text/richtext',
 'sgml': 'text/sgml',
 'tsv': 'text/tab-separated-values',
 'txt': 'text/plain',
 'uls': 'text/iuls',
 'xhtml': 'application/xhtml+xml',
 'xml': 'text/xml',
 'xslt': 'application/xslt+xml',
 'yaml': 'text/yaml',
 'bmp': 'image/bmp',
 'gif': 'image/gif',
 'ico': 'image/x-icon',
 'jpeg': 'image/jpeg',
 'jpg': 'image/jpeg',
 'png': 'image/png',
 'psd': 'image/vnd.adobe.photoshop',
 'svg': 'image/svg+xml',
 'tif': 'image/tiff',
 'tiff': 'image/tiff',
 'wbmp': 'image/vnd.wap.wbmp',
 'xbm': 'image/xbm',
 'aif': 'audio/x-aiff',
 'au': 'audio/basic',
 'm3u': 'audio/x-mpegurl',
 'mid': 'audio/midi',
 'mp3': 'audio/mpeg',
 'mp4a': 'audio/mp4',
 'mpga': 'audio/mpeg',
 'ogg': 'audio/vorbis',
 'ram': 'audio/x-pn-realaudio',
 'wav': 'audio/wav',
 'wax': 'audio/x-ms-wax',
 'wma': 'audio/x-ms-wma',
 'eot': 'application/vnd.ms-fontobject',
 'otf': 'application/x-font-otf',
 'ttf': 'application/x-font-ttf',
 'woff': 'application/x-font-woff',
 'woff2': 'application/font-woff2',
 'gz': 'application/x-gzip',
 'rar': 'application/octet-stream',
 'sit': 'application/x-stuffit',
 'tar': 'application/x-tar',
 'tgz': 'application/x-compressed',
 'z': 'application/x-compress',
 'zip': 'application/x-zip-compressed',
 '3g2': 'video/3gpp2',
 '3gp': 'video/3gpp',
 'asf': 'video/x-ms-asf',
 'avi': 'video/x-msvideo',
 'dir': 'application/x-director',
 'f4v': 'video/x-f4v',
 'flv': 'video/x-flv',
 'h264': 'video/h264',
 'm4v': 'video/x-m4v',
 'mov': 'video/quicktime',
 'movie': 'video/x-sgi-movie',
 'mp4': 'video/mp4',
 'mpeg': 'video/mpeg',
 'mxu': 'video/vnd.mpegurl',
 'qt': 'video/quicktime',
 'swf': 'application/x-shockwave-flash',
 'wmv': 'video/x-ms-wmv',
 'wmx': 'video/x-ms-wmx',
 'doc': 'application/msword',
 'docm': 'application/vnd.ms-word.document.macroEnabled.12',
 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
 'dot': 'application/msword',
 'dotm': 'application/vnd.ms-word.template.macroEnabled.12',
 'dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
 'latex': 'application/x-latex',
 'pdf': 'application/pdf',
 'pot': 'application/vnd.ms-powerpoint',
 'potm': 'application/vnd.ms-powerpoint.template.macroEnabled.12',
 'potx': 'application/vnd.openxmlformats-officedocument.presentationml.template',
 'ppa': 'application/vnd.ms-powerpoint',
 'ppam': 'application/vnd.ms-powerpoint.addin.macroEnabled.12',
 'pps': 'application/vnd.ms-powerpoint',
 'ppsm': 'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
 'ppsx': 'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
 'ppt': 'application/vnd.ms-powerpoint',
 'pptm': 'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
 'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
 'xla': 'application/vnd.ms-excel',
 'xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
 'xls': 'application/vnd.ms-excel',
 'xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
 'xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
 'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
 'xlt': 'application/vnd.ms-excel',
 'xltm': 'application/vnd.ms-excel.template.macroEnabled.12',
 'xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
 '323': 'text/h323',
 'aip': 'text/x-audiosoft-intra',
 'cat': 'application/vnd.ms-pki.seccat',
 'cdf': 'application/x-cdf',
 'cer': 'application/x-x509-ca-cert',
 'co': 'application/x-cult3d-object',
 'crl': 'application/pkix-crl',
 'fdf': 'application/vnd.fdf',
 'fif': 'application/fractals',
 'hqx': 'application/mac-binhex40',
 'iii': 'application/x-iphone',
 'ins': 'application/x-internet-signup',
 'ipu': 'application/x-ipulse-command',
 'ivf': 'video/x-ivf',
 'man': 'application/x-troff-man',
 'nix': 'application/x-mix-transfer',
 'p10': 'application/pkcs10',
 'p12': 'application/x-pkcs12',
 'p7b': 'application/x-pkcs7-certificates',
 'p7m': 'application/pkcs7-mime',
 'p7r': 'application/x-pkcs7-certreqresp',
 'p7s': 'application/pkcs7-signature',
 'pko': 'application/vnd.ms-pki.pko',
 'ps': 'application/postscript',
 'qtl': 'application/x-quicktimeplayer',
 'rmf': 'application/vnd.rmf',
 'setpay': 'application/set-payment-initiation',
 'setreg': 'application/set-registration-initiation',
 'spl': 'application/futuresplash',
 'sst': 'application/vnd.ms-pki.certstore',
 'stl': 'application/vnd.ms-pki.stl',
 'vcf': 'text/x-vcard'}
