#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\packages\evegraphics\controllers\expressiontree.py
import re

class ExpressionNode(object):

    def __init__(self, inputs = 0):
        self._inputs = []
        if inputs > 0:
            self._inputs = [None] * inputs
        self.startPosition = -1

    def Store(self):
        pass

    def BuildExpression(self):
        pass

    def GetTitle(self):
        pass

    def GetInputs(self):
        return self._inputs

    def GetPrecedence(self):
        return 100

    def SetInput(self, index, inputValue):
        self._inputs[index] = inputValue

    def SetInputs(self, inputs):
        for i, x in enumerate(inputs):
            self._inputs[i] = x

    def GetTextTemplate(self):
        return ('', '')

    def Dump(self, indent = 0):
        print '%s%s' % (' ' * indent, self.GetTitle())
        for each in self._inputs:
            each.Dump(indent + 2)


class Variable(ExpressionNode):

    def __init__(self, name):
        super(Variable, self).__init__()
        self.name = name

    def Store(self):
        return ['Variable', self.name]

    def GetTitle(self):
        return self.name

    def BuildExpression(self):
        return self.name

    def GetTextTemplate(self):
        return (self.name, '')


class NumericConstant(ExpressionNode):

    def __init__(self, number):
        super(NumericConstant, self).__init__()
        self.number = number

    def Store(self):
        return ['NumericConstant', self.number]

    def GetTitle(self):
        return str(self.number)

    def BuildExpression(self):
        return str(self.number)

    def GetTextTemplate(self):
        return (str(self.number), '')


class UnaryOperator(ExpressionNode):

    def __init__(self, operator, precedence = 10):
        super(UnaryOperator, self).__init__(1)
        self.operator = operator
        self.precedence = precedence

    def Store(self):
        return ['UnaryOperator', self.operator]

    def GetTitle(self):
        return self.operator

    def BuildExpression(self):
        e = self.GetInputs()[0].BuildExpression()
        if self.GetInputs()[0].GetPrecedence() < self.GetPrecedence():
            e = '(%s)' % e
        return '%s%s' % (self.operator, e)

    def GetPrecedence(self):
        return self.precedence

    def GetTextTemplate(self):
        return (self.operator, '')


def GetOperatorPrecedence(operator):
    for i, each in enumerate(OP_PRIORITIES):
        if operator in each:
            return i

    return 0


class Operator(ExpressionNode):

    def __init__(self, operator):
        super(Operator, self).__init__(2)
        self.operator = operator

    def Store(self):
        return ['Operator', self.operator]

    def GetTitle(self):
        return self.operator

    def BuildExpression(self):
        e0 = self.GetInputs()[0].BuildExpression()
        if self.GetInputs()[0].GetPrecedence() < self.GetPrecedence():
            e0 = '(%s)' % e0
        e1 = self.GetInputs()[1].BuildExpression()
        if self.GetInputs()[1].GetPrecedence() < self.GetPrecedence():
            e1 = '(%s)' % e1
        return '%s %s %s' % (e0, self.operator, e1)

    def GetPrecedence(self):
        return GetOperatorPrecedence(self.operator)

    def GetTextTemplate(self):
        return (self.operator, '')


class FunctionCall(ExpressionNode):

    def __init__(self, name, paramsCount):
        super(FunctionCall, self).__init__(paramsCount)
        self.name = name

    def Store(self):
        return ['FunctionCall', self.name, len(self._inputs)]

    def GetTitle(self):
        return self.name

    def BuildExpression(self):
        args = [ x.BuildExpression() for x in self.GetInputs() ]
        return '%s(%s)' % (self.name, ', '.join(args))

    def GetTextTemplate(self):
        return ('%s(' % self.name, ')')


class StringFunctionCall(ExpressionNode):

    def __init__(self, name, param):
        super(StringFunctionCall, self).__init__(0)
        self.name = name
        self.param = param
        self.paramStartPosition = -1

    def Store(self):
        return ['StringFunctionCall', self.name, self.param]

    def GetTitle(self):
        return '%s\n%s' % (self.name, self.param[1:-1])

    def BuildExpression(self):
        return '%s(%s)' % (self.name, self.param)

    def GetTextTemplate(self):
        return ('%s("' % self.name, '")')


class ResultExpression(ExpressionNode):

    def __init__(self):
        super(ResultExpression, self).__init__(1)

    def Store(self):
        return ['ResultExpression']

    def GetTitle(self):
        return 'Result'

    def BuildExpression(self):
        return self.GetInputs()[0].BuildExpression()


class Token(object):

    def __init__(self, token, string, startPosition):
        self.token = token
        self.string = string
        self.startPosition = startPosition

    def __eq__(self, other):
        return isinstance(other, Token) and self.token == other.token and self.string == other.string

    def __ne__(self, other):
        return not isinstance(other, Token) or self.token != other.token or self.string != other.string


class Stream(object):

    def __init__(self, string):
        self._string = string
        self._position = 0
        self._length = len(string)

    def Eof(self):
        return self._position >= self._length

    def Peek(self, length):
        return self._string[self._position:self._position + length]

    def Consume(self, length):
        result = self.Peek(length)
        self._position += len(result)
        return result

    def GetPosition(self):
        return self._position

    def PeekAll(self):
        return self._string[self._position:]


_TOKENS = re.compile('\\A\\s*((&&|\\|\\||>=|<=|!=|==|[+\\-*/^%><=!()])|([a-zA-Z_][a-zA-Z_0-9]*)|(\\"[^\\"]*\\")|(-?(([0-9]*\\.[0-9]*)|[0-9]+)([eE][+\\-]?[0-9]+)?))')

def _GetToken(stream):
    pos = stream.GetPosition()
    if stream.Eof():
        return Token('', '', pos)
    elif stream.Peek(2) in ('&&', '||', '<=', '>=', '!=', '=='):
        return Token('OP', stream.Consume(2), pos)
    elif stream.Peek(1) in ('+', '-', '*', '/', '^', '%', '>', '<', '=', '!', '(', ')', ','):
        return Token('OP', stream.Consume(1), pos)
    m = _TOKENS.match(stream.PeekAll())
    if not m:
        raise ValueError(repr(stream.PeekAll()))
    stream.Consume(len(m.group(0)))
    if m.group(2):
        return Token('OP', m.group(2), pos)
    elif m.group(3):
        return Token('ID', m.group(3), pos)
    elif m.group(4):
        return Token('STR', m.group(4), pos)
    else:
        return Token('NUM', m.group(5), pos)


OP_PRIORITIES = [('=',),
 (),
 ('||',),
 ('&&',),
 ('<=', '>=', '!=', '==', '>', '<'),
 ('+', '-'),
 ('*', '/', '%'),
 ('^',)]
_OPEN_PAREN = Token('OP', '(', 0)
_CLOSE_PAREN = Token('OP', ')', 0)
_COMA = Token('OP', ',', 0)

def _Term(token, stream):
    if token.token == 'ID':
        name = token.string
        start = token.startPosition
        token = _GetToken(stream)
        if token == _OPEN_PAREN:
            r = None
            args = []
            while True:
                token = _GetToken(stream)
                if token.token == 'STR':
                    r = StringFunctionCall(name, token.string)
                    r.startPosition = start
                    r.paramStartPosition = token.startPosition
                    token = _GetToken(stream)
                    if token != _CLOSE_PAREN:
                        raise ValueError()
                    break
                elif token == _CLOSE_PAREN:
                    break
                arg, token = _Expr(token, stream, 0)
                args.append(arg)
                if token == _CLOSE_PAREN:
                    break
                elif token != _COMA:
                    raise ValueError()

            if not r:
                r = FunctionCall(name, len(args))
                r.startPosition = start
            r.SetInputs(args)
            token = _GetToken(stream)
        else:
            r = Variable(name)
            r.startPosition = start
        return (r, token)
    if token.token == 'NUM':
        e = NumericConstant(float(token.string))
        e.startPosition = token.startPosition
        return (e, _GetToken(stream))
    if token.string in ('+', '-'):
        e = UnaryOperator(token.string, 10)
        e.startPosition = token.startPosition
        r, token = _Term(_GetToken(stream), stream)
        e.SetInput(0, r)
        return (e, token)
    if token == _OPEN_PAREN:
        result, token = _Expr(_GetToken(stream), stream, 0)
        if token != _CLOSE_PAREN:
            raise ValueError()
        return (result, _GetToken(stream))
    raise ValueError()


def _Expr(token, stream, priority):
    left, token = _Term(token, stream) if priority + 1 >= len(OP_PRIORITIES) else _Expr(token, stream, priority + 1)
    while token.string in OP_PRIORITIES[priority]:
        op = Operator(token.string)
        op.startPosition = token.startPosition
        op.SetInput(0, left)
        token = _GetToken(stream)
        right, token = _Term(token, stream) if priority + 1 >= len(OP_PRIORITIES) else _Expr(token, stream, priority + 1)
        op.SetInput(1, right)
        left = op

    return (left, token)


def Parse(input):
    stream = Stream(input)
    r, t = _Expr(_GetToken(stream), stream, 0)
    if t.token != '':
        raise ValueError(t.string)
    return r


class NodeGroup(object):

    def __init__(self, title, children):
        self.title = title
        self.children = list(children)
        self.description = ''


class NodeDescription(object):

    def __init__(self, title, factory, description = ''):
        self.title = title
        self.factory = factory
        self.description = description


NODE_DESCRIPTIONS = (NodeGroup('Operators', (NodeDescription('-x', lambda : UnaryOperator('-', 10)),
  NodeDescription('x ^ y', lambda : Operator('^')),
  NodeDescription('x * y', lambda : Operator('*')),
  NodeDescription('x / y', lambda : Operator('/')),
  NodeDescription('x + y', lambda : Operator('+')),
  NodeDescription('x - y', lambda : Operator('-')),
  NodeDescription('x == y', lambda : Operator('==')),
  NodeDescription('x != y', lambda : Operator('!=')),
  NodeDescription('x > y', lambda : Operator('>')),
  NodeDescription('x < y', lambda : Operator('<')),
  NodeDescription('x >= y', lambda : Operator('>=')),
  NodeDescription('x <= y', lambda : Operator('<=')),
  NodeDescription('x % y', lambda : Operator('%')),
  NodeDescription('AND', lambda : Operator('&&')),
  NodeDescription('OR', lambda : Operator('||')))), NodeGroup('Math', (NodeDescription('abs', lambda : FunctionCall('abs', 1), 'abs(x) - absolute value (drop the sign)'),
  NodeDescription('sqrt', lambda : FunctionCall('sqrt', 1), 'sqrt(x) - square root of x'),
  NodeDescription('sign', lambda : FunctionCall('sign', 1), 'sign(x) - sign (-1, 0 or 1) of the argument'),
  NodeDescription('log2', lambda : FunctionCall('log2', 1), 'log2(x) - base 2 logarithm'),
  NodeDescription('log10', lambda : FunctionCall('log10', 1), 'log10(x) - base 10 logarithm'),
  NodeDescription('log', lambda : FunctionCall('log', 1), 'log(x) - natural logarithm'),
  NodeDescription('ln', lambda : FunctionCall('ln', 1), 'ln(x) - natural logarithm'),
  NodeDescription('exp', lambda : FunctionCall('exp', 1), 'exp(x) - natural exponent'),
  NodeDescription('rint', lambda : FunctionCall('rint', 1), 'rint(x) - round value to an integer'),
  NodeDescription('sin', lambda : FunctionCall('sin', 1), 'sin(x) - sine'),
  NodeDescription('cos', lambda : FunctionCall('cos', 1), 'cos(x) - cosine'),
  NodeDescription('tan', lambda : FunctionCall('tan', 1), 'tan(x) - tangent'),
  NodeDescription('asin', lambda : FunctionCall('asin', 1), 'asin(x) - arcsine'),
  NodeDescription('acos', lambda : FunctionCall('acos', 1), 'acos(x) - arccosine'),
  NodeDescription('atan', lambda : FunctionCall('atan', 1), 'atan(x) - argtangent'),
  NodeDescription('sinh', lambda : FunctionCall('sinh', 1), 'sinh(x) - hyperbolic sine'),
  NodeDescription('cosh', lambda : FunctionCall('cosh', 1), 'cosh(x) - hyperbolic cosine'),
  NodeDescription('tanh', lambda : FunctionCall('tanh', 1), 'tanh(x) - hyperbolic tangent'),
  NodeDescription('asinh', lambda : FunctionCall('asinh', 1), 'asinh(x) - hyperbolic arcsine'),
  NodeDescription('acosh', lambda : FunctionCall('acosh', 1), 'acosh(x) - hyperbolic arccosine'),
  NodeDescription('atanh', lambda : FunctionCall('atanh', 1), 'atanh(x) - hyperbolic arctangent'),
  NodeDescription('min', lambda : FunctionCall('min', 0), 'min(arg1...) - minimum of all arguments (one or more)'),
  NodeDescription('max', lambda : FunctionCall('max', 0), 'max(arg1...) - maximum of all arguments (one or more)'),
  NodeDescription('sum', lambda : FunctionCall('sum', 0), 'sum(arg1...) - sum of all arguments (one or more)'),
  NodeDescription('avg', lambda : FunctionCall('avg', 0), 'avg(arg1...) - average of all arguments (one or more)'))))
