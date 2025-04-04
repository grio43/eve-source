#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\localization\parser.py
import re
import eveLocalization
from pytelemetry import zoning as telemetry
ARG_TO_MODIFIER = {'linkify': eveLocalization.TOKEN_FLAG.LINKIFY,
 'capitalize': eveLocalization.TOKEN_FLAG.CAPITALIZE,
 'uppercase': eveLocalization.TOKEN_FLAG.UPPERCASE,
 'lowercase': eveLocalization.TOKEN_FLAG.LOWERCASE,
 'titlecase': eveLocalization.TOKEN_FLAG.TITLECASE,
 'useGrouping': eveLocalization.TOKEN_FLAG.USEGROUPING}
VARIABLE_TYPE_CHOOSER = {'generic': eveLocalization.VARIABLE_TYPE.GENERIC,
 'character': eveLocalization.VARIABLE_TYPE.CHARACTER,
 'npcorganization': eveLocalization.VARIABLE_TYPE.NPCORGANIZATION,
 'item': eveLocalization.VARIABLE_TYPE.ITEM,
 'location': eveLocalization.VARIABLE_TYPE.LOCATION,
 'characterlist': eveLocalization.VARIABLE_TYPE.CHARACTERLIST,
 'messageid': eveLocalization.VARIABLE_TYPE.MESSAGE,
 'datetime': eveLocalization.VARIABLE_TYPE.DATETIME,
 'formattedtime': eveLocalization.VARIABLE_TYPE.FORMATTEDTIME,
 'timeinterval': eveLocalization.VARIABLE_TYPE.TIMEINTERVAL,
 'numeric': eveLocalization.VARIABLE_TYPE.NUMERIC}
topLevelTagsRE = re.compile('(\\{(?!\\{).*?\\})')
tokensRE = re.compile('(""|"[^"]+"|->|[:.,=\\[\\]])')
validVariableNameRE = re.compile('[a-zA-Z_]+\\w?')
validAttributeNameRE = re.compile('[\\.[a-zA-Z_]+\\w*]*')
quoteWrappedStringRE = re.compile('"[^"]*"')

@telemetry.ZONE_FUNCTION
def _Tokenize(sourceText):
    sourceText = sourceText.replace('\r\n', ' ').replace('\n', ' ')
    tags = dict([ (each, None) for each in topLevelTagsRE.findall(sourceText) ])
    for tag in tags.keys()[:]:
        errors = []
        originalTag = tag
        tag = tag[1:-1]
        if not len(tag.strip()):
            del tags[originalTag]
            continue
        tokens = tokensRE.split(tag)
        originalTokens = [ token for token in tokens if token ]
        tokens = [ token.strip() for token in tokens if token and token.strip() ]
        dp = None
        tp = None
        try:
            variableName = None
            variableType = 'generic'
            propertyName = None
            tagArgs = 0
            tagKwargs = {}
            conditionalValues = []
            token = tokens.pop(0)
            if token == '[':
                variableType = tokens.pop(0)
                if variableType not in VARIABLE_TYPE_DATA:
                    raise SyntaxError, "'" + variableType + "' is not a valid variable type"
                next = tokens.pop(0)
                if next != ']':
                    raise SyntaxError, "Expected ']' but got '%s'" % next
                variableName = tokens.pop(0)
            else:
                variableType = 'generic'
                variableName = token
            if not _IsValidVariableName(variableName):
                raise SyntaxError, 'Variable names must be alphanumeric, and begin with a letter or underscore'
            for tagName, tagInfo in [ (tagName, tagInfo) for tagName, tagInfo in tags.iteritems() if tagInfo ]:
                if tagInfo['variableName'] == variableName and tagInfo['variableType'] != VARIABLE_TYPE_CHOOSER[variableType.lower().encode('ascii')]:
                    raise TypeError, "'" + variableName + "' already declared as type '" + tagInfo['variableType'] + "'."

            if tokens:
                next = tokens.pop(0)
                if next == '.':
                    propertyName = tokens.pop(0)
                    if variableType == 'numeric':
                        tagArgs |= eveLocalization.TOKEN_FLAG.QUANTITY
                    if tokens:
                        next = tokens.pop(0)
            if tokens:
                if next == '->':
                    tagArgs |= eveLocalization.TOKEN_FLAG.CONDITIONAL
                    if VARIABLE_TYPE_DATA[variableType.encode('ascii')]['conditionalProperties'][propertyName] == CONDITIONAL_TYPE_QUANTITY:
                        tagArgs |= eveLocalization.TOKEN_FLAG.QUANTITY
                    if variableType in VARIABLE_TYPE_DATA and 'conditionalProperties' in VARIABLE_TYPE_DATA[variableType] and propertyName not in VARIABLE_TYPE_DATA[variableType]['conditionalProperties']:
                        raise TypeError, 'You cannot use ' + unicode(variableName) + '.' + unicode(propertyName) + ' in conditional statements.  Valid properties for this variable type are: ' + str(VARIABLE_TYPE_DATA[variableType]['conditionalProperties'])
                    conditionalValue = tokens.pop(0)
                    if not _IsQuoteWrappedString(conditionalValue):
                        raise SyntaxError, "Error parsing conditional value '" + conditionalValue + "'"
                    conditionalValues.append(conditionalValue[1:-1])
                    while tokens:
                        next = tokens.pop(0)
                        if next != ',':
                            raise SyntaxError, "Expected ',' but got '%s'" % next
                        conditionalValue = tokens.pop(0)
                        if not _IsQuoteWrappedString(conditionalValue):
                            raise SyntaxError, "Error parsing conditional value '" + conditionalValue + "'"
                        conditionalValues.append(conditionalValue[1:-1])

                elif next == ',':
                    while tokens:
                        arg = tokens.pop(0).encode('ascii')
                        next = tokens.pop(0) if len(tokens) else None
                        if next in (',', None):
                            if arg not in VARIABLE_TYPE_DATA[variableType]['args']:
                                raise SyntaxError, "Modifier '" + arg + "' cannot be used with variables of type '" + variableType + "'"
                            tagArgs |= ARG_TO_MODIFIER[arg]
                        elif next == '=':
                            kwargValue = tokens.pop(0)
                            if _IsQuoteWrappedString(kwargValue):
                                kwargValue = kwargValue[1:-1]
                            elif not kwargValue.isalnum():
                                raise ValueError, 'Conditional arguments must be an alphanumeric value or double-quoted string'
                            if arg not in VARIABLE_TYPE_DATA[variableType]['kwargs']:
                                raise SyntaxError, "Modifier '" + arg + "' cannot be used with variables of type '" + variableType + "'"
                            if arg in ('decimalPlaces', 'leadingZeroes'):
                                tagKwargs[arg] = int(kwargValue)
                                if arg == 'decimalPlaces':
                                    tagArgs |= eveLocalization.TOKEN_FLAG.DECIMALPLACES
                            elif arg == 'timeFormat':
                                if kwargValue == 'short':
                                    tagKwargs['format'] = u'%Y.%m.%d %H:%M'
                                else:
                                    tagKwargs['format'] = u'%Y.%m.%d %H:%M:%S'
                            elif arg == 'format':
                                tagKwargs[arg] = unicode(kwargValue)
                            elif arg in ('date', 'time') and variableType.lower() == 'datetime':
                                if arg == 'date':
                                    if kwargValue == 'long':
                                        dp = u'%B %d, %Y'
                                    elif kwargValue == 'full':
                                        dp = u'%#c'
                                    elif kwargValue == 'medium':
                                        dp = u'%b %d, %Y'
                                    elif kwargValue == 'short':
                                        dp = u'%Y.%m.%d'
                                elif kwargValue == 'short':
                                    tp = u'%H:%M'
                                elif kwargValue.lower() != 'none':
                                    tp = u'%H:%M:%S'
                                if dp and tp:
                                    if dp == u'%#c':
                                        if tp != '%H:%M':
                                            tagKwargs['format'] = dp
                                        else:
                                            tagKwargs['format'] = u'%#x ' + tp
                                    else:
                                        tagKwargs['format'] = dp + u' ' + tp
                                elif dp and not tp:
                                    if dp == u'%#c':
                                        tagKwargs['format'] = u'%#x'
                                    else:
                                        tagKwargs['format'] = dp
                                elif tp and not dp:
                                    tagKwargs['format'] = tp
                            else:
                                tagKwargs[arg] = kwargValue.encode('ascii')
                            next = tokens.pop(0) if len(tokens) else None
                            if next not in (',', None):
                                raise SyntaxError, "Expected ',' but got '%s'" % next
                        else:
                            raise SyntaxError, "Expected ',' or '=' but got '%s'" % next

                else:
                    raise SyntaxError, "Expected ',' but got '%s'" % next
        except (TypeError,
         ValueError,
         SyntaxError,
         IndexError) as e:
            partialTag = '{' + ''.join([ originalTokens[i] for i in xrange(len(originalTokens) - len(tokens)) ])
            message1 = 'Tokenizer error: ' + repr(e) + ' -- Stopped parsing at: ' + partialTag
            message2 = "Source tag '" + originalTag + "' Source string: '" + sourceText + "'"
            errors.append(message1)
            errors.append(message2)
            raise

        tags[originalTag] = {'variableType': VARIABLE_TYPE_CHOOSER[variableType.lower().encode('ascii')],
         'variableName': variableName.encode('ascii') if variableName is not None else None,
         'propertyName': propertyName.encode('ascii') if propertyName is not None else None,
         'conditionalValues': conditionalValues,
         'args': tagArgs,
         'kwargs': tagKwargs}

    return tags


def _IsValidVariableName(string):
    results = validVariableNameRE.findall(string)
    return results and results[0] == string


def _IsValidAttributeName(string):
    results = validVariableNameRE.findall(string)
    return results and results[0] == string


def _IsQuoteWrappedString(string):
    matches = quoteWrappedStringRE.findall(string)
    return len(matches) and matches[0] == string


def _FormatErrorMessage(args):
    return ''.join(map(unicode, args))


BASIC_TEXT_MODIFIERS = ['capitalize',
 'uppercase',
 'lowercase',
 'titlecase']
BASIC_TEXT_SETTINGS = ['linkinfo']
CONDITIONAL_TYPE_GENDER = 'gender'
CONDITIONAL_TYPE_GENDERS = 'genders'
CONDITIONAL_TYPE_QUANTITY = 'quantity'
VARIABLE_TYPE_DATA = {'character': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
               'kwargs': BASIC_TEXT_SETTINGS,
               'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER}},
 'npcOrganization': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
                     'kwargs': BASIC_TEXT_SETTINGS,
                     'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER}},
 'item': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
          'kwargs': BASIC_TEXT_SETTINGS + ['quantity'],
          'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER,
                                    'quantity': CONDITIONAL_TYPE_QUANTITY}},
 'location': {'args': BASIC_TEXT_MODIFIERS + ['linkify'],
              'kwargs': BASIC_TEXT_SETTINGS,
              'conditionalProperties': {'gender': CONDITIONAL_TYPE_GENDER}},
 'characterlist': {'args': [],
                   'kwargs': BASIC_TEXT_SETTINGS,
                   'conditionalProperties': {'genders': CONDITIONAL_TYPE_GENDERS,
                                             'quantity': CONDITIONAL_TYPE_QUANTITY}},
 'messageid': {'args': BASIC_TEXT_MODIFIERS,
               'kwargs': BASIC_TEXT_SETTINGS},
 'datetime': {'args': BASIC_TEXT_MODIFIERS,
              'kwargs': BASIC_TEXT_SETTINGS + ['date', 'time']},
 'formattedtime': {'args': BASIC_TEXT_MODIFIERS,
                   'kwargs': BASIC_TEXT_SETTINGS + ['format']},
 'timeinterval': {'args': BASIC_TEXT_MODIFIERS,
                  'kwargs': BASIC_TEXT_SETTINGS + ['from', 'to']},
 'numeric': {'args': ['useGrouping'],
             'kwargs': BASIC_TEXT_SETTINGS + ['decimalPlaces', 'leadingZeroes'],
             'conditionalProperties': {None: CONDITIONAL_TYPE_QUANTITY}},
 'generic': {'args': BASIC_TEXT_MODIFIERS,
             'kwargs': BASIC_TEXT_SETTINGS}}
