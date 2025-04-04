#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\cp857.py
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
    return codecs.CodecInfo(name='cp857', encode=Codec().encode, decode=Codec().decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)


decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({128: 199,
 129: 252,
 130: 233,
 131: 226,
 132: 228,
 133: 224,
 134: 229,
 135: 231,
 136: 234,
 137: 235,
 138: 232,
 139: 239,
 140: 238,
 141: 305,
 142: 196,
 143: 197,
 144: 201,
 145: 230,
 146: 198,
 147: 244,
 148: 246,
 149: 242,
 150: 251,
 151: 249,
 152: 304,
 153: 214,
 154: 220,
 155: 248,
 156: 163,
 157: 216,
 158: 350,
 159: 351,
 160: 225,
 161: 237,
 162: 243,
 163: 250,
 164: 241,
 165: 209,
 166: 286,
 167: 287,
 168: 191,
 169: 174,
 170: 172,
 171: 189,
 172: 188,
 173: 161,
 174: 171,
 175: 187,
 176: 9617,
 177: 9618,
 178: 9619,
 179: 9474,
 180: 9508,
 181: 193,
 182: 194,
 183: 192,
 184: 169,
 185: 9571,
 186: 9553,
 187: 9559,
 188: 9565,
 189: 162,
 190: 165,
 191: 9488,
 192: 9492,
 193: 9524,
 194: 9516,
 195: 9500,
 196: 9472,
 197: 9532,
 198: 227,
 199: 195,
 200: 9562,
 201: 9556,
 202: 9577,
 203: 9574,
 204: 9568,
 205: 9552,
 206: 9580,
 207: 164,
 208: 186,
 209: 170,
 210: 202,
 211: 203,
 212: 200,
 213: None,
 214: 205,
 215: 206,
 216: 207,
 217: 9496,
 218: 9484,
 219: 9608,
 220: 9604,
 221: 166,
 222: 204,
 223: 9600,
 224: 211,
 225: 223,
 226: 212,
 227: 210,
 228: 245,
 229: 213,
 230: 181,
 231: None,
 232: 215,
 233: 218,
 234: 219,
 235: 217,
 237: 255,
 238: 175,
 239: 180,
 240: 173,
 241: 177,
 242: None,
 243: 190,
 244: 182,
 245: 167,
 246: 247,
 247: 184,
 248: 176,
 249: 168,
 250: 183,
 251: 185,
 252: 179,
 253: 178,
 254: 9632,
 255: 160})
decoding_table = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\xc7\xfc\xe9\xe2\xe4\xe0\xe5\xe7\xea\xeb\xe8\xef\xee\u0131\xc4\xc5\xc9\xe6\xc6\xf4\xf6\xf2\xfb\xf9\u0130\xd6\xdc\xf8\xa3\xd8\u015e\u015f\xe1\xed\xf3\xfa\xf1\xd1\u011e\u011f\xbf\xae\xac\xbd\xbc\xa1\xab\xbb\u2591\u2592\u2593\u2502\u2524\xc1\xc2\xc0\xa9\u2563\u2551\u2557\u255d\xa2\xa5\u2510\u2514\u2534\u252c\u251c\u2500\u253c\xe3\xc3\u255a\u2554\u2569\u2566\u2560\u2550\u256c\xa4\xba\xaa\xca\xcb\xc8\ufffe\xcd\xce\xcf\u2518\u250c\u2588\u2584\xa6\xcc\u2580\xd3\xdf\xd4\xd2\xf5\xd5\xb5\ufffe\xd7\xda\xdb\xd9\xec\xff\xaf\xb4\xad\xb1\ufffe\xbe\xb6\xa7\xf7\xb8\xb0\xa8\xb7\xb9\xb3\xb2\u25a0\xa0'
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
 161: 173,
 162: 189,
 163: 156,
 164: 207,
 165: 190,
 166: 221,
 167: 245,
 168: 249,
 169: 184,
 170: 209,
 171: 174,
 172: 170,
 173: 240,
 174: 169,
 175: 238,
 176: 248,
 177: 241,
 178: 253,
 179: 252,
 180: 239,
 181: 230,
 182: 244,
 183: 250,
 184: 247,
 185: 251,
 186: 208,
 187: 175,
 188: 172,
 189: 171,
 190: 243,
 191: 168,
 192: 183,
 193: 181,
 194: 182,
 195: 199,
 196: 142,
 197: 143,
 198: 146,
 199: 128,
 200: 212,
 201: 144,
 202: 210,
 203: 211,
 204: 222,
 205: 214,
 206: 215,
 207: 216,
 209: 165,
 210: 227,
 211: 224,
 212: 226,
 213: 229,
 214: 153,
 215: 232,
 216: 157,
 217: 235,
 218: 233,
 219: 234,
 220: 154,
 223: 225,
 224: 133,
 225: 160,
 226: 131,
 227: 198,
 228: 132,
 229: 134,
 230: 145,
 231: 135,
 232: 138,
 233: 130,
 234: 136,
 235: 137,
 236: 236,
 237: 161,
 238: 140,
 239: 139,
 241: 164,
 242: 149,
 243: 162,
 244: 147,
 245: 228,
 246: 148,
 247: 246,
 248: 155,
 249: 151,
 250: 163,
 251: 150,
 252: 129,
 255: 237,
 286: 166,
 287: 167,
 304: 152,
 305: 141,
 350: 158,
 351: 159,
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
