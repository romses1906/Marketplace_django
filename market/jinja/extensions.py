from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.utils.encoding import force_str
from jinja2 import TemplateSyntaxError
from jinja2 import nodes
from jinja2.ext import Extension


class FragmentCacheExtension(Extension):
    """ Класс кастомного расширения для кеширования фрагмента шаблона jinja2 """

    tags = {"cache"}

    def parse(self, parser):
        """ Метод для разбора потока токенов и получения искомых синтаксических конструкций (искомых тегов) """

        lineno = next(parser.stream).lineno
        expire_time = parser.parse_expression()
        fragment_name = parser.parse_expression()
        vary_on = []

        while not parser.stream.current.test('block_end'):
            vary_on.append(parser.parse_expression())

        body = parser.parse_statements(['name:endcache'], drop_needle=True)

        return nodes.CallBlock(
            self.call_method('_cache_support',
                             [expire_time, fragment_name,
                              nodes.List(vary_on), nodes.Const(lineno)]),
            [], [], body).set_lineno(lineno)

    def _cache_support(self, expire_time, fragm_name, vary_on, lineno, caller):
        """ Метод кеширования блока шаблона jinja2, обращенного в теги cache endcache """

        try:
            if expire_time is not None:
                expire_time = int(expire_time)
        except (ValueError, TypeError):
            raise TemplateSyntaxError(
                f'"{list(self.tags)[0]}" tag got a non-integer timeout value: {expire_time!r}',
                lineno,
            )

        cache_key = make_template_fragment_key(fragm_name, vary_on)

        value = cache.get(cache_key)
        if value is None:
            value = caller()
            cache.set(cache_key, force_str(value), expire_time)
        else:
            actual_value = caller()
            if force_str(value) != force_str(actual_value):
                cache.delete(cache_key)
                value = force_str(actual_value)
                cache.set(cache_key, value, expire_time)
        return value
