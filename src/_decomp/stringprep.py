#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\stringprep.py
from unicodedata import ucd_3_2_0 as unicodedata

def in_table_a1(code):
    if unicodedata.category(code) != 'Cn':
        return False
    c = ord(code)
    if 64976 <= c < 65008:
        return False
    return c & 65535 not in (65534, 65535)


b1_set = set([173,
 847,
 6150,
 6155,
 6156,
 6157,
 8203,
 8204,
 8205,
 8288,
 65279] + range(65024, 65040))

def in_table_b1(code):
    return ord(code) in b1_set


b3_exceptions = {181: u'\u03bc',
 223: u'ss',
 304: u'i\u0307',
 329: u'\u02bcn',
 383: u's',
 496: u'j\u030c',
 837: u'\u03b9',
 890: u' \u03b9',
 912: u'\u03b9\u0308\u0301',
 944: u'\u03c5\u0308\u0301',
 962: u'\u03c3',
 976: u'\u03b2',
 977: u'\u03b8',
 978: u'\u03c5',
 979: u'\u03cd',
 980: u'\u03cb',
 981: u'\u03c6',
 982: u'\u03c0',
 1008: u'\u03ba',
 1009: u'\u03c1',
 1010: u'\u03c3',
 1013: u'\u03b5',
 1415: u'\u0565\u0582',
 7830: u'h\u0331',
 7831: u't\u0308',
 7832: u'w\u030a',
 7833: u'y\u030a',
 7834: u'a\u02be',
 7835: u'\u1e61',
 8016: u'\u03c5\u0313',
 8018: u'\u03c5\u0313\u0300',
 8020: u'\u03c5\u0313\u0301',
 8022: u'\u03c5\u0313\u0342',
 8064: u'\u1f00\u03b9',
 8065: u'\u1f01\u03b9',
 8066: u'\u1f02\u03b9',
 8067: u'\u1f03\u03b9',
 8068: u'\u1f04\u03b9',
 8069: u'\u1f05\u03b9',
 8070: u'\u1f06\u03b9',
 8071: u'\u1f07\u03b9',
 8072: u'\u1f00\u03b9',
 8073: u'\u1f01\u03b9',
 8074: u'\u1f02\u03b9',
 8075: u'\u1f03\u03b9',
 8076: u'\u1f04\u03b9',
 8077: u'\u1f05\u03b9',
 8078: u'\u1f06\u03b9',
 8079: u'\u1f07\u03b9',
 8080: u'\u1f20\u03b9',
 8081: u'\u1f21\u03b9',
 8082: u'\u1f22\u03b9',
 8083: u'\u1f23\u03b9',
 8084: u'\u1f24\u03b9',
 8085: u'\u1f25\u03b9',
 8086: u'\u1f26\u03b9',
 8087: u'\u1f27\u03b9',
 8088: u'\u1f20\u03b9',
 8089: u'\u1f21\u03b9',
 8090: u'\u1f22\u03b9',
 8091: u'\u1f23\u03b9',
 8092: u'\u1f24\u03b9',
 8093: u'\u1f25\u03b9',
 8094: u'\u1f26\u03b9',
 8095: u'\u1f27\u03b9',
 8096: u'\u1f60\u03b9',
 8097: u'\u1f61\u03b9',
 8098: u'\u1f62\u03b9',
 8099: u'\u1f63\u03b9',
 8100: u'\u1f64\u03b9',
 8101: u'\u1f65\u03b9',
 8102: u'\u1f66\u03b9',
 8103: u'\u1f67\u03b9',
 8104: u'\u1f60\u03b9',
 8105: u'\u1f61\u03b9',
 8106: u'\u1f62\u03b9',
 8107: u'\u1f63\u03b9',
 8108: u'\u1f64\u03b9',
 8109: u'\u1f65\u03b9',
 8110: u'\u1f66\u03b9',
 8111: u'\u1f67\u03b9',
 8114: u'\u1f70\u03b9',
 8115: u'\u03b1\u03b9',
 8116: u'\u03ac\u03b9',
 8118: u'\u03b1\u0342',
 8119: u'\u03b1\u0342\u03b9',
 8124: u'\u03b1\u03b9',
 8126: u'\u03b9',
 8130: u'\u1f74\u03b9',
 8131: u'\u03b7\u03b9',
 8132: u'\u03ae\u03b9',
 8134: u'\u03b7\u0342',
 8135: u'\u03b7\u0342\u03b9',
 8140: u'\u03b7\u03b9',
 8146: u'\u03b9\u0308\u0300',
 8147: u'\u03b9\u0308\u0301',
 8150: u'\u03b9\u0342',
 8151: u'\u03b9\u0308\u0342',
 8162: u'\u03c5\u0308\u0300',
 8163: u'\u03c5\u0308\u0301',
 8164: u'\u03c1\u0313',
 8166: u'\u03c5\u0342',
 8167: u'\u03c5\u0308\u0342',
 8178: u'\u1f7c\u03b9',
 8179: u'\u03c9\u03b9',
 8180: u'\u03ce\u03b9',
 8182: u'\u03c9\u0342',
 8183: u'\u03c9\u0342\u03b9',
 8188: u'\u03c9\u03b9',
 8360: u'rs',
 8450: u'c',
 8451: u'\xb0c',
 8455: u'\u025b',
 8457: u'\xb0f',
 8459: u'h',
 8460: u'h',
 8461: u'h',
 8464: u'i',
 8465: u'i',
 8466: u'l',
 8469: u'n',
 8470: u'no',
 8473: u'p',
 8474: u'q',
 8475: u'r',
 8476: u'r',
 8477: u'r',
 8480: u'sm',
 8481: u'tel',
 8482: u'tm',
 8484: u'z',
 8488: u'z',
 8492: u'b',
 8493: u'c',
 8496: u'e',
 8497: u'f',
 8499: u'm',
 8510: u'\u03b3',
 8511: u'\u03c0',
 8517: u'd',
 13169: u'hpa',
 13171: u'au',
 13173: u'ov',
 13184: u'pa',
 13185: u'na',
 13186: u'\u03bca',
 13187: u'ma',
 13188: u'ka',
 13189: u'kb',
 13190: u'mb',
 13191: u'gb',
 13194: u'pf',
 13195: u'nf',
 13196: u'\u03bcf',
 13200: u'hz',
 13201: u'khz',
 13202: u'mhz',
 13203: u'ghz',
 13204: u'thz',
 13225: u'pa',
 13226: u'kpa',
 13227: u'mpa',
 13228: u'gpa',
 13236: u'pv',
 13237: u'nv',
 13238: u'\u03bcv',
 13239: u'mv',
 13240: u'kv',
 13241: u'mv',
 13242: u'pw',
 13243: u'nw',
 13244: u'\u03bcw',
 13245: u'mw',
 13246: u'kw',
 13247: u'mw',
 13248: u'k\u03c9',
 13249: u'm\u03c9',
 13251: u'bq',
 13254: u'c\u2215kg',
 13255: u'co.',
 13256: u'db',
 13257: u'gy',
 13259: u'hp',
 13261: u'kk',
 13262: u'km',
 13271: u'ph',
 13273: u'ppm',
 13274: u'pr',
 13276: u'sv',
 13277: u'wb',
 64256: u'ff',
 64257: u'fi',
 64258: u'fl',
 64259: u'ffi',
 64260: u'ffl',
 64261: u'st',
 64262: u'st',
 64275: u'\u0574\u0576',
 64276: u'\u0574\u0565',
 64277: u'\u0574\u056b',
 64278: u'\u057e\u0576',
 64279: u'\u0574\u056d',
 119808: u'a',
 119809: u'b',
 119810: u'c',
 119811: u'd',
 119812: u'e',
 119813: u'f',
 119814: u'g',
 119815: u'h',
 119816: u'i',
 119817: u'j',
 119818: u'k',
 119819: u'l',
 119820: u'm',
 119821: u'n',
 119822: u'o',
 119823: u'p',
 119824: u'q',
 119825: u'r',
 119826: u's',
 119827: u't',
 119828: u'u',
 119829: u'v',
 119830: u'w',
 119831: u'x',
 119832: u'y',
 119833: u'z',
 119860: u'a',
 119861: u'b',
 119862: u'c',
 119863: u'd',
 119864: u'e',
 119865: u'f',
 119866: u'g',
 119867: u'h',
 119868: u'i',
 119869: u'j',
 119870: u'k',
 119871: u'l',
 119872: u'm',
 119873: u'n',
 119874: u'o',
 119875: u'p',
 119876: u'q',
 119877: u'r',
 119878: u's',
 119879: u't',
 119880: u'u',
 119881: u'v',
 119882: u'w',
 119883: u'x',
 119884: u'y',
 119885: u'z',
 119912: u'a',
 119913: u'b',
 119914: u'c',
 119915: u'd',
 119916: u'e',
 119917: u'f',
 119918: u'g',
 119919: u'h',
 119920: u'i',
 119921: u'j',
 119922: u'k',
 119923: u'l',
 119924: u'm',
 119925: u'n',
 119926: u'o',
 119927: u'p',
 119928: u'q',
 119929: u'r',
 119930: u's',
 119931: u't',
 119932: u'u',
 119933: u'v',
 119934: u'w',
 119935: u'x',
 119936: u'y',
 119937: u'z',
 119964: u'a',
 119966: u'c',
 119967: u'd',
 119970: u'g',
 119973: u'j',
 119974: u'k',
 119977: u'n',
 119978: u'o',
 119979: u'p',
 119980: u'q',
 119982: u's',
 119983: u't',
 119984: u'u',
 119985: u'v',
 119986: u'w',
 119987: u'x',
 119988: u'y',
 119989: u'z',
 120016: u'a',
 120017: u'b',
 120018: u'c',
 120019: u'd',
 120020: u'e',
 120021: u'f',
 120022: u'g',
 120023: u'h',
 120024: u'i',
 120025: u'j',
 120026: u'k',
 120027: u'l',
 120028: u'm',
 120029: u'n',
 120030: u'o',
 120031: u'p',
 120032: u'q',
 120033: u'r',
 120034: u's',
 120035: u't',
 120036: u'u',
 120037: u'v',
 120038: u'w',
 120039: u'x',
 120040: u'y',
 120041: u'z',
 120068: u'a',
 120069: u'b',
 120071: u'd',
 120072: u'e',
 120073: u'f',
 120074: u'g',
 120077: u'j',
 120078: u'k',
 120079: u'l',
 120080: u'm',
 120081: u'n',
 120082: u'o',
 120083: u'p',
 120084: u'q',
 120086: u's',
 120087: u't',
 120088: u'u',
 120089: u'v',
 120090: u'w',
 120091: u'x',
 120092: u'y',
 120120: u'a',
 120121: u'b',
 120123: u'd',
 120124: u'e',
 120125: u'f',
 120126: u'g',
 120128: u'i',
 120129: u'j',
 120130: u'k',
 120131: u'l',
 120132: u'm',
 120134: u'o',
 120138: u's',
 120139: u't',
 120140: u'u',
 120141: u'v',
 120142: u'w',
 120143: u'x',
 120144: u'y',
 120172: u'a',
 120173: u'b',
 120174: u'c',
 120175: u'd',
 120176: u'e',
 120177: u'f',
 120178: u'g',
 120179: u'h',
 120180: u'i',
 120181: u'j',
 120182: u'k',
 120183: u'l',
 120184: u'm',
 120185: u'n',
 120186: u'o',
 120187: u'p',
 120188: u'q',
 120189: u'r',
 120190: u's',
 120191: u't',
 120192: u'u',
 120193: u'v',
 120194: u'w',
 120195: u'x',
 120196: u'y',
 120197: u'z',
 120224: u'a',
 120225: u'b',
 120226: u'c',
 120227: u'd',
 120228: u'e',
 120229: u'f',
 120230: u'g',
 120231: u'h',
 120232: u'i',
 120233: u'j',
 120234: u'k',
 120235: u'l',
 120236: u'm',
 120237: u'n',
 120238: u'o',
 120239: u'p',
 120240: u'q',
 120241: u'r',
 120242: u's',
 120243: u't',
 120244: u'u',
 120245: u'v',
 120246: u'w',
 120247: u'x',
 120248: u'y',
 120249: u'z',
 120276: u'a',
 120277: u'b',
 120278: u'c',
 120279: u'd',
 120280: u'e',
 120281: u'f',
 120282: u'g',
 120283: u'h',
 120284: u'i',
 120285: u'j',
 120286: u'k',
 120287: u'l',
 120288: u'm',
 120289: u'n',
 120290: u'o',
 120291: u'p',
 120292: u'q',
 120293: u'r',
 120294: u's',
 120295: u't',
 120296: u'u',
 120297: u'v',
 120298: u'w',
 120299: u'x',
 120300: u'y',
 120301: u'z',
 120328: u'a',
 120329: u'b',
 120330: u'c',
 120331: u'd',
 120332: u'e',
 120333: u'f',
 120334: u'g',
 120335: u'h',
 120336: u'i',
 120337: u'j',
 120338: u'k',
 120339: u'l',
 120340: u'm',
 120341: u'n',
 120342: u'o',
 120343: u'p',
 120344: u'q',
 120345: u'r',
 120346: u's',
 120347: u't',
 120348: u'u',
 120349: u'v',
 120350: u'w',
 120351: u'x',
 120352: u'y',
 120353: u'z',
 120380: u'a',
 120381: u'b',
 120382: u'c',
 120383: u'd',
 120384: u'e',
 120385: u'f',
 120386: u'g',
 120387: u'h',
 120388: u'i',
 120389: u'j',
 120390: u'k',
 120391: u'l',
 120392: u'm',
 120393: u'n',
 120394: u'o',
 120395: u'p',
 120396: u'q',
 120397: u'r',
 120398: u's',
 120399: u't',
 120400: u'u',
 120401: u'v',
 120402: u'w',
 120403: u'x',
 120404: u'y',
 120405: u'z',
 120432: u'a',
 120433: u'b',
 120434: u'c',
 120435: u'd',
 120436: u'e',
 120437: u'f',
 120438: u'g',
 120439: u'h',
 120440: u'i',
 120441: u'j',
 120442: u'k',
 120443: u'l',
 120444: u'm',
 120445: u'n',
 120446: u'o',
 120447: u'p',
 120448: u'q',
 120449: u'r',
 120450: u's',
 120451: u't',
 120452: u'u',
 120453: u'v',
 120454: u'w',
 120455: u'x',
 120456: u'y',
 120457: u'z',
 120488: u'\u03b1',
 120489: u'\u03b2',
 120490: u'\u03b3',
 120491: u'\u03b4',
 120492: u'\u03b5',
 120493: u'\u03b6',
 120494: u'\u03b7',
 120495: u'\u03b8',
 120496: u'\u03b9',
 120497: u'\u03ba',
 120498: u'\u03bb',
 120499: u'\u03bc',
 120500: u'\u03bd',
 120501: u'\u03be',
 120502: u'\u03bf',
 120503: u'\u03c0',
 120504: u'\u03c1',
 120505: u'\u03b8',
 120506: u'\u03c3',
 120507: u'\u03c4',
 120508: u'\u03c5',
 120509: u'\u03c6',
 120510: u'\u03c7',
 120511: u'\u03c8',
 120512: u'\u03c9',
 120531: u'\u03c3',
 120546: u'\u03b1',
 120547: u'\u03b2',
 120548: u'\u03b3',
 120549: u'\u03b4',
 120550: u'\u03b5',
 120551: u'\u03b6',
 120552: u'\u03b7',
 120553: u'\u03b8',
 120554: u'\u03b9',
 120555: u'\u03ba',
 120556: u'\u03bb',
 120557: u'\u03bc',
 120558: u'\u03bd',
 120559: u'\u03be',
 120560: u'\u03bf',
 120561: u'\u03c0',
 120562: u'\u03c1',
 120563: u'\u03b8',
 120564: u'\u03c3',
 120565: u'\u03c4',
 120566: u'\u03c5',
 120567: u'\u03c6',
 120568: u'\u03c7',
 120569: u'\u03c8',
 120570: u'\u03c9',
 120589: u'\u03c3',
 120604: u'\u03b1',
 120605: u'\u03b2',
 120606: u'\u03b3',
 120607: u'\u03b4',
 120608: u'\u03b5',
 120609: u'\u03b6',
 120610: u'\u03b7',
 120611: u'\u03b8',
 120612: u'\u03b9',
 120613: u'\u03ba',
 120614: u'\u03bb',
 120615: u'\u03bc',
 120616: u'\u03bd',
 120617: u'\u03be',
 120618: u'\u03bf',
 120619: u'\u03c0',
 120620: u'\u03c1',
 120621: u'\u03b8',
 120622: u'\u03c3',
 120623: u'\u03c4',
 120624: u'\u03c5',
 120625: u'\u03c6',
 120626: u'\u03c7',
 120627: u'\u03c8',
 120628: u'\u03c9',
 120647: u'\u03c3',
 120662: u'\u03b1',
 120663: u'\u03b2',
 120664: u'\u03b3',
 120665: u'\u03b4',
 120666: u'\u03b5',
 120667: u'\u03b6',
 120668: u'\u03b7',
 120669: u'\u03b8',
 120670: u'\u03b9',
 120671: u'\u03ba',
 120672: u'\u03bb',
 120673: u'\u03bc',
 120674: u'\u03bd',
 120675: u'\u03be',
 120676: u'\u03bf',
 120677: u'\u03c0',
 120678: u'\u03c1',
 120679: u'\u03b8',
 120680: u'\u03c3',
 120681: u'\u03c4',
 120682: u'\u03c5',
 120683: u'\u03c6',
 120684: u'\u03c7',
 120685: u'\u03c8',
 120686: u'\u03c9',
 120705: u'\u03c3',
 120720: u'\u03b1',
 120721: u'\u03b2',
 120722: u'\u03b3',
 120723: u'\u03b4',
 120724: u'\u03b5',
 120725: u'\u03b6',
 120726: u'\u03b7',
 120727: u'\u03b8',
 120728: u'\u03b9',
 120729: u'\u03ba',
 120730: u'\u03bb',
 120731: u'\u03bc',
 120732: u'\u03bd',
 120733: u'\u03be',
 120734: u'\u03bf',
 120735: u'\u03c0',
 120736: u'\u03c1',
 120737: u'\u03b8',
 120738: u'\u03c3',
 120739: u'\u03c4',
 120740: u'\u03c5',
 120741: u'\u03c6',
 120742: u'\u03c7',
 120743: u'\u03c8',
 120744: u'\u03c9',
 120763: u'\u03c3'}

def map_table_b3(code):
    r = b3_exceptions.get(ord(code))
    if r is not None:
        return r
    return code.lower()


def map_table_b2(a):
    al = map_table_b3(a)
    b = unicodedata.normalize('NFKC', al)
    bl = u''.join([ map_table_b3(ch) for ch in b ])
    c = unicodedata.normalize('NFKC', bl)
    if b != c:
        return c
    else:
        return al


def in_table_c11(code):
    return code == u' '


def in_table_c12(code):
    return unicodedata.category(code) == 'Zs' and code != u' '


def in_table_c11_c12(code):
    return unicodedata.category(code) == 'Zs'


def in_table_c21(code):
    return ord(code) < 128 and unicodedata.category(code) == 'Cc'


c22_specials = set([1757,
 1807,
 6158,
 8204,
 8205,
 8232,
 8233,
 65279] + range(8288, 8292) + range(8298, 8304) + range(65529, 65533) + range(119155, 119163))

def in_table_c22(code):
    c = ord(code)
    if c < 128:
        return False
    if unicodedata.category(code) == 'Cc':
        return True
    return c in c22_specials


def in_table_c21_c22(code):
    return unicodedata.category(code) == 'Cc' or ord(code) in c22_specials


def in_table_c3(code):
    return unicodedata.category(code) == 'Co'


def in_table_c4(code):
    c = ord(code)
    if c < 64976:
        return False
    if c < 65008:
        return True
    return ord(code) & 65535 in (65534, 65535)


def in_table_c5(code):
    return unicodedata.category(code) == 'Cs'


c6_set = set(range(65529, 65534))

def in_table_c6(code):
    return ord(code) in c6_set


c7_set = set(range(12272, 12284))

def in_table_c7(code):
    return ord(code) in c7_set


c8_set = set([832,
 833,
 8206,
 8207] + range(8234, 8239) + range(8298, 8304))

def in_table_c8(code):
    return ord(code) in c8_set


c9_set = set([917505] + range(917536, 917632))

def in_table_c9(code):
    return ord(code) in c9_set


def in_table_d1(code):
    return unicodedata.bidirectional(code) in ('R', 'AL')


def in_table_d2(code):
    return unicodedata.bidirectional(code) == 'L'
