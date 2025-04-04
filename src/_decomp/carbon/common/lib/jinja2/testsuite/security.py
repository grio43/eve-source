#Embedded file name: C:\BuildAgent\work\ba3dced9a47cf95a\eve\release\V22.02\carbon\common\lib\jinja2\testsuite\security.py
import unittest
from jinja2.testsuite import JinjaTestCase
from jinja2 import Environment
from jinja2.sandbox import SandboxedEnvironment, ImmutableSandboxedEnvironment, unsafe
from jinja2 import Markup, escape
from jinja2.exceptions import SecurityError, TemplateSyntaxError, TemplateRuntimeError

class PrivateStuff(object):

    def bar(self):
        return 23

    @unsafe
    def foo(self):
        return 42

    def __repr__(self):
        return 'PrivateStuff'


class PublicStuff(object):
    bar = lambda self: 23
    _foo = lambda self: 42

    def __repr__(self):
        return 'PublicStuff'


class SandboxTestCase(JinjaTestCase):

    def test_unsafe(self):
        env = SandboxedEnvironment()
        self.assert_raises(SecurityError, env.from_string('{{ foo.foo() }}').render, foo=PrivateStuff())
        self.assert_equal(env.from_string('{{ foo.bar() }}').render(foo=PrivateStuff()), '23')
        self.assert_raises(SecurityError, env.from_string('{{ foo._foo() }}').render, foo=PublicStuff())
        self.assert_equal(env.from_string('{{ foo.bar() }}').render(foo=PublicStuff()), '23')
        self.assert_equal(env.from_string('{{ foo.__class__ }}').render(foo=42), '')
        self.assert_equal(env.from_string('{{ foo.func_code }}').render(foo=lambda : None), '')
        self.assert_raises(SecurityError, env.from_string('{{ foo.__class__.__subclasses__() }}').render, foo=42)

    def test_immutable_environment(self):
        env = ImmutableSandboxedEnvironment()
        self.assert_raises(SecurityError, env.from_string('{{ [].append(23) }}').render)
        self.assert_raises(SecurityError, env.from_string('{{ {1:2}.clear() }}').render)

    def test_restricted(self):
        env = SandboxedEnvironment()
        self.assert_raises(TemplateSyntaxError, env.from_string, '{% for item.attribute in seq %}...{% endfor %}')
        self.assert_raises(TemplateSyntaxError, env.from_string, '{% for foo, bar.baz in seq %}...{% endfor %}')

    def test_markup_operations(self):
        unsafe = '<script type="application/x-some-script">alert("foo");</script>'
        safe = Markup('<em>username</em>')
        x = Markup('foo')

        class Foo(object):

            def __html__(self):
                return '<em>awesome</em>'

            def __unicode__(self):
                return 'awesome'

    def test_template_data(self):
        env = Environment(autoescape=True)
        t = env.from_string('{% macro say_hello(name) %}<p>Hello {{ name }}!</p>{% endmacro %}{{ say_hello("<blink>foo</blink>") }}')
        escaped_out = '<p>Hello &lt;blink&gt;foo&lt;/blink&gt;!</p>'

    def test_attr_filter(self):
        env = SandboxedEnvironment()
        tmpl = env.from_string('{{ cls|attr("__subclasses__")() }}')
        self.assert_raises(SecurityError, tmpl.render, cls=int)

    def test_binary_operator_intercepting(self):

        def disable_op(left, right):
            raise TemplateRuntimeError('that operator so does not work')

        for expr, ctx, rv in (('1 + 2', {}, '3'), ('a + 2', {'a': 2}, '4')):
            env = SandboxedEnvironment()
            env.binop_table['+'] = disable_op
            t = env.from_string('{{ %s }}' % expr)
            env.intercepted_binops = frozenset(['+'])
            t = env.from_string('{{ %s }}' % expr)
            try:
                t.render(ctx)
            except TemplateRuntimeError as e:
                pass
            else:
                self.fail('expected runtime error')

    def test_unary_operator_intercepting(self):

        def disable_op(arg):
            raise TemplateRuntimeError('that operator so does not work')

        for expr, ctx, rv in (('-1', {}, '-1'), ('-a', {'a': 2}, '-2')):
            env = SandboxedEnvironment()
            env.unop_table['-'] = disable_op
            t = env.from_string('{{ %s }}' % expr)
            env.intercepted_unops = frozenset(['-'])
            t = env.from_string('{{ %s }}' % expr)
            try:
                t.render(ctx)
            except TemplateRuntimeError as e:
                pass
            else:
                self.fail('expected runtime error')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SandboxTestCase))
    return suite
