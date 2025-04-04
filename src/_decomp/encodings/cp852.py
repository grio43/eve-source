#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\cp852.py
import codecs

class Codec(codecs.Codec):

    def encode(self, input, errors = 'strict'):
        return codecs.charmap_encode(input, errors, encoding_map)

    def decode(self, input, errors = 'strict'):
        return codecs.charmap_decode(input, errors, decoding_table)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final = False):
        return codecs.charmap_encode(input, self.errors, encoding_map)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final = False):
        return codecs.charmap_decode(input, self.errors, decoding_table)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='cp852', encode=Codec().encode, decode=Codec().decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)


decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({128: 199,
 129: 252,
 130: 233,
 131: 226,
 132: 228,
 133: 367,
 134: 263,
 135: 231,
 136: 322,
 137: 235,
 138: 336,
 139: 337,
 140: 238,
 141: 377,
 142: 196,
 143: 262,
 144: 201,
 145: 313,
 146: 314,
 147: 244,
 148: 246,
 149: 317,
 150: 318,
 151: 346,
 152: 347,
 153: 214,
 154: 220,
 155: 356,
 156: 357,
 157: 321,
 158: 215,
 159: 269,
 160: 225,
 161: 237,
 162: 243,
 163: 250,
 164: 260,
 165: 261,
 166: 381,
 167: 382,
 168: 280,
 169: 281,
 170: 172,
 171: 378,
 172: 268,
 173: 351,
 174: 171,
 175: 187,
 176: 9617,
 177: 9618,
 178: 9619,
 179: 9474,
 180: 9508,
 181: 193,
 182: 194,
 183: 282,
 184: 350,
 185: 9571,
 186: 9553,
 187: 9559,
 188: 9565,
 189: 379,
 190: 380,
 191: 9488,
 192: 9492,
 193: 9524,
 194: 9516,
 195: 9500,
 196: 9472,
 197: 9532,
 198: 258,
 199: 259,
 200: 9562,
 201: 9556,
 202: 9577,
 203: 9574,
 204: 9568,
 205: 9552,
 206: 9580,
 207: 164,
 208: 273,
 209: 272,
 210: 270,
 211: 203,
 212: 271,
 213: 327,
 214: 205,
 215: 206,
 216: 283,
 217: 9496,
 218: 9484,
 219: 9608,
 220: 9604,
 221: 354,
 222: 366,
 223: 9600,
 224: 211,
 225: 223,
 226: 212,
 227: 323,
 228: 324,
 229: 328,
 230: 352,
 231: 353,
 232: 340,
 233: 218,
 234: 341,
 235: 368,
 236: 253,
 237: 221,
 238: 355,
 239: 180,
 240: 173,
 241: 733,
 242: 731,
 243: 711,
 244: 728,
 245: 167,
 246: 247,
 247: 184,
 248: 176,
 249: 168,
 250: 729,
 251: 369,
 252: 344,
 253: 345,
 254: 9632,
 255: 160})
decoding_table = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\xc7\xfc\xe9\xe2\xe4\u016f\u0107\xe7\u0142\xeb\u0150\u0151\xee\u0179\xc4\u0106\xc9\u0139\u013a\xf4\xf6\u013d\u013e\u015a\u015b\xd6\xdc\u0164\u0165\u0141\xd7\u010d\xe1\xed\xf3\xfa\u0104\u0105\u017d\u017e\u0118\u0119\xac\u017a\u010c\u015f\xab\xbb\u2591\u2592\u2593\u2502\u2524\xc1\xc2\u011a\u015e\u2563\u2551\u2557\u255d\u017b\u017c\u2510\u2514\u2534\u252c\u251c\u2500\u253c\u0102\u0103\u255a\u2554\u2569\u2566\u2560\u2550\u256c\xa4\u0111\u0110\u010e\xcb\u010f\u0147\xcd\xce\u011b\u2518\u250c\u2588\u2584\u0162\u016e\u2580\xd3\xdf\xd4\u0143\u0144\u0148\u0160\u0161\u0154\xda\u0155\u0170\xfd\xdd\u0163\xb4\xad\u02dd\u02db\u02c7\u02d8\xa7\xf7\xb8\xb0\xa8\u02d9\u0171\u0158\u0159\u25a0\xa0'
encoding_map = {0: 0,
 1: 1,
 2: 2,
 3: 3,
 4: 4,
 5: 5,
 6: 6,
 7: 7,
 8: 8,
 9: 9,
 10: 10,
 11: 11,
 12: 12,
 13: 13,
 14: 14,
 15: 15,
 16: 16,
 17: 17,
 18: 18,
 19: 19,
 20: 20,
 21: 21,
 22: 22,
 23: 23,
 24: 24,
 25: 25,
 26: 26,
 27: 27,
 28: 28,
 29: 29,
 30: 30,
 31: 31,
 32: 32,
 33: 33,
 34: 34,
 35: 35,
 36: 36,
 37: 37,
 38: 38,
 39: 39,
 40: 40,
 41: 41,
 42: 42,
 43: 43,
 44: 44,
 45: 45,
 46: 46,
 47: 47,
 48: 48,
 49: 49,
 50: 50,
 51: 51,
 52: 52,
 53: 53,
 54: 54,
 55: 55,
 56: 56,
 57: 57,
 58: 58,
 59: 59,
 60: 60,
 61: 61,
 62: 62,
 63: 63,
 64: 64,
 65: 65,
 66: 66,
 67: 67,
 68: 68,
 69: 69,
 70: 70,
 71: 71,
 72: 72,
 73: 73,
 74: 74,
 75: 75,
 76: 76,
 77: 77,
 78: 78,
 79: 79,
 80: 80,
 81: 81,
 82: 82,
 83: 83,
 84: 84,
 85: 85,
 86: 86,
 87: 87,
 88: 88,
 89: 89,
 90: 90,
 91: 91,
 92: 92,
 93: 93,
 94: 94,
 95: 95,
 96: 96,
 97: 97,
 98: 98,
 99: 99,
 100: 100,
 101: 101,
 102: 102,
 103: 103,
 104: 104,
 105: 105,
 106: 106,
 107: 107,
 108: 108,
 109: 109,
 110: 110,
 111: 111,
 112: 112,
 113: 113,
 114: 114,
 115: 115,
 116: 116,
 117: 117,
 118: 118,
 119: 119,
 120: 120,
 121: 121,
 122: 122,
 123: 123,
 124: 124,
 125: 125,
 126: 126,
 127: 127,
 160: 255,
 164: 207,
 167: 245,
 168: 249,
 171: 174,
 172: 170,
 173: 240,
 176: 248,
 180: 239,
 184: 247,
 187: 175,
 193: 181,
 194: 182,
 196: 142,
 199: 128,
 201: 144,
 203: 211,
 205: 214,
 206: 215,
 211: 224,
 212: 226,
 214: 153,
 215: 158,
 218: 233,
 220: 154,
 221: 237,
 223: 225,
 225: 160,
 226: 131,
 228: 132,
 231: 135,
 233: 130,
 235: 137,
 237: 161,
 238: 140,
 243: 162,
 244: 147,
 246: 148,
 247: 246,
 250: 163,
 252: 129,
 253: 236,
 258: 198,
 259: 199,
 260: 164,
 261: 165,
 262: 143,
 263: 134,
 268: 172,
 269: 159,
 270: 210,
 271: 212,
 272: 209,
 273: 208,
 280: 168,
 281: 169,
 282: 183,
 283: 216,
 313: 145,
 314: 146,
 317: 149,
 318: 150,
 321: 157,
 322: 136,
 323: 227,
 324: 228,
 327: 213,
 328: 229,
 336: 138,
 337: 139,
 340: 232,
 341: 234,
 344: 252,
 345: 253,
 346: 151,
 347: 152,
 350: 184,
 351: 173,
 352: 230,
 353: 231,
 354: 221,
 355: 238,
 356: 155,
 357: 156,
 366: 222,
 367: 133,
 368: 235,
 369: 251,
 377: 141,
 378: 171,
 379: 189,
 380: 190,
 381: 166,
 382: 167,
 711: 243,
 728: 244,
 729: 250,
 731: 242,
 733: 241,
 9472: 196,
 9474: 179,
 9484: 218,
 9488: 191,
 9492: 192,
 9496: 217,
 9500: 195,
 9508: 180,
 9516: 194,
 9524: 193,
 9532: 197,
 9552: 205,
 9553: 186,
 9556: 201,
 9559: 187,
 9562: 200,
 9565: 188,
 9568: 204,
 9571: 185,
 9574: 203,
 9577: 202,
 9580: 206,
 9600: 223,
 9604: 220,
 9608: 219,
 9617: 176,
 9618: 177,
 9619: 178,
 9632: 254}
