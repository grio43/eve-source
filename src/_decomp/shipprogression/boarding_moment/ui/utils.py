#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\shipprogression\boarding_moment\ui\utils.py
import uthread2
import random
from carbonui import TextColor

def roll_in(label, actual_string, delay, duration, onEnd = None, onStart = None):
    char_duration = min(0.05, duration / float(len(actual_string)))
    uthread2.Sleep(delay)
    if onStart:
        onStart()
    for idx in range(len(actual_string) + 1):
        uthread2.Sleep(char_duration)
        label.text = roll_in_step(idx, actual_string)

    if onEnd:
        onEnd()


def roll_in_step(idx, actual_string):
    ret = ''
    for i in range(len(actual_string)):
        if i < idx:
            ret += actual_string[i]

    return ret


def unscramble_triglavian(label, actual_string, delay, duration, onEnd = None, onStart = None):
    char_duration = min(0.05, duration / float(len(actual_string)))
    uthread2.Sleep(delay)
    if onStart:
        onStart()
    for idx in range(len(actual_string) + 1):
        uthread2.Sleep(char_duration)
        label.text = unscramble_triglavian_step(idx, actual_string)

    if onEnd:
        onEnd()


def unscramble_triglavian_step(idx, actual_string):
    unscrambled = ''
    scrambled = ''
    for i in range(len(actual_string)):
        if i < idx:
            unscrambled += actual_string[i]
        elif len(actual_string) > i:
            scrambled += actual_string[i]

    return u"{normal}<font file='Triglavian.ttf'>{triglavian}</font>".format(normal=unscrambled, triglavian=scrambled)


def unscramble(label, actual_string, delay, duration, onEnd = None, onStart = None):
    char_duration = min(0.05, duration / float(len(actual_string)))
    uthread2.Sleep(delay)
    if onStart:
        onStart()
    for idx in range(len(actual_string) + 1):
        uthread2.Sleep(char_duration)
        label.text = unscramble_string_step(idx, actual_string)

    if onEnd:
        onEnd()


def unscramble_string_step(idx, actual_string):
    unscrambled = ''
    scrambled = ''
    for i in range(len(actual_string)):
        if i < idx:
            unscrambled += actual_string[i]
        else:
            scrambled += chr(random.randint(ord('a'), ord('z')))

    return u'{unscrambled}<color={scrambledColor}>{scrambled}</color>'.format(unscrambled=unscrambled, scrambled=scrambled, scrambledColor=TextColor.DISABLED)


def scramble_string(actual_string):
    ret = ''
    for i in range(len(actual_string)):
        ret += chr(random.randint(ord('a'), ord('z')))

    return ret
