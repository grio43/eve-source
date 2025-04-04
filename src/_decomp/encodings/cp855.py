#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\stdlib\encodings\cp855.py
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
    return codecs.CodecInfo(name='cp855', encode=Codec().encode, decode=Codec().decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter)


decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({128: 1106,
 129: 1026,
 130: 1107,
 131: 1027,
 132: 1105,
 133: 1025,
 134: 1108,
 135: 1028,
 136: 1109,
 137: 1029,
 138: 1110,
 139: 1030,
 140: 1111,
 141: 1031,
 142: 1112,
 143: 1032,
 144: 1113,
 145: 1033,
 146: 1114,
 147: 1034,
 148: 1115,
 149: 1035,
 150: 1116,
 151: 1036,
 152: 1118,
 153: 1038,
 154: 1119,
 155: 1039,
 156: 1102,
 157: 1070,
 158: 1098,
 159: 1066,
 160: 1072,
 161: 1040,
 162: 1073,
 163: 1041,
 164: 1094,
 165: 1062,
 166: 1076,
 167: 1044,
 168: 1077,
 169: 1045,
 170: 1092,
 171: 1060,
 172: 1075,
 173: 1043,
 174: 171,
 175: 187,
 176: 9617,
 177: 9618,
 178: 9619,
 179: 9474,
 180: 9508,
 181: 1093,
 182: 1061,
 183: 1080,
 184: 1048,
 185: 9571,
 186: 9553,
 187: 9559,
 188: 9565,
 189: 1081,
 190: 1049,
 191: 9488,
 192: 9492,
 193: 9524,
 194: 9516,
 195: 9500,
 196: 9472,
 197: 9532,
 198: 1082,
 199: 1050,
 200: 9562,
 201: 9556,
 202: 9577,
 203: 9574,
 204: 9568,
 205: 9552,
 206: 9580,
 207: 164,
 208: 1083,
 209: 1051,
 210: 1084,
 211: 1052,
 212: 1085,
 213: 1053,
 214: 1086,
 215: 1054,
 216: 1087,
 217: 9496,
 218: 9484,
 219: 9608,
 220: 9604,
 221: 1055,
 222: 1103,
 223: 9600,
 224: 1071,
 225: 1088,
 226: 1056,
 227: 1089,
 228: 1057,
 229: 1090,
 230: 1058,
 231: 1091,
 232: 1059,
 233: 1078,
 234: 1046,
 235: 1074,
 236: 1042,
 237: 1100,
 238: 1068,
 239: 8470,
 240: 173,
 241: 1099,
 242: 1067,
 243: 1079,
 244: 1047,
 245: 1096,
 246: 1064,
 247: 1101,
 248: 1069,
 249: 1097,
 250: 1065,
 251: 1095,
 252: 1063,
 253: 167,
 254: 9632,
 255: 160})
decoding_table = u'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\x0c\r\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\u0452\u0402\u0453\u0403\u0451\u0401\u0454\u0404\u0455\u0405\u0456\u0406\u0457\u0407\u0458\u0408\u0459\u0409\u045a\u040a\u045b\u040b\u045c\u040c\u045e\u040e\u045f\u040f\u044e\u042e\u044a\u042a\u0430\u0410\u0431\u0411\u0446\u0426\u0434\u0414\u0435\u0415\u0444\u0424\u0433\u0413\xab\xbb\u2591\u2592\u2593\u2502\u2524\u0445\u0425\u0438\u0418\u2563\u2551\u2557\u255d\u0439\u0419\u2510\u2514\u2534\u252c\u251c\u2500\u253c\u043a\u041a\u255a\u2554\u2569\u2566\u2560\u2550\u256c\xa4\u043b\u041b\u043c\u041c\u043d\u041d\u043e\u041e\u043f\u2518\u250c\u2588\u2584\u041f\u044f\u2580\u042f\u0440\u0420\u0441\u0421\u0442\u0422\u0443\u0423\u0436\u0416\u0432\u0412\u044c\u042c\u2116\xad\u044b\u042b\u0437\u0417\u0448\u0428\u044d\u042d\u0449\u0429\u0447\u0427\xa7\u25a0\xa0'
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
 167: 253,
 171: 174,
 173: 240,
 187: 175,
 1025: 133,
 1026: 129,
 1027: 131,
 1028: 135,
 1029: 137,
 1030: 139,
 1031: 141,
 1032: 143,
 1033: 145,
 1034: 147,
 1035: 149,
 1036: 151,
 1038: 153,
 1039: 155,
 1040: 161,
 1041: 163,
 1042: 236,
 1043: 173,
 1044: 167,
 1045: 169,
 1046: 234,
 1047: 244,
 1048: 184,
 1049: 190,
 1050: 199,
 1051: 209,
 1052: 211,
 1053: 213,
 1054: 215,
 1055: 221,
 1056: 226,
 1057: 228,
 1058: 230,
 1059: 232,
 1060: 171,
 1061: 182,
 1062: 165,
 1063: 252,
 1064: 246,
 1065: 250,
 1066: 159,
 1067: 242,
 1068: 238,
 1069: 248,
 1070: 157,
 1071: 224,
 1072: 160,
 1073: 162,
 1074: 235,
 1075: 172,
 1076: 166,
 1077: 168,
 1078: 233,
 1079: 243,
 1080: 183,
 1081: 189,
 1082: 198,
 1083: 208,
 1084: 210,
 1085: 212,
 1086: 214,
 1087: 216,
 1088: 225,
 1089: 227,
 1090: 229,
 1091: 231,
 1092: 170,
 1093: 181,
 1094: 164,
 1095: 251,
 1096: 245,
 1097: 249,
 1098: 158,
 1099: 241,
 1100: 237,
 1101: 247,
 1102: 156,
 1103: 222,
 1105: 132,
 1106: 128,
 1107: 130,
 1108: 134,
 1109: 136,
 1110: 138,
 1111: 140,
 1112: 142,
 1113: 144,
 1114: 146,
 1115: 148,
 1116: 150,
 1118: 152,
 1119: 154,
 8470: 239,
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
