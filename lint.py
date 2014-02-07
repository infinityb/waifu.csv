import sys
import unittest
from functools import partial, reduce
import yaml
import yaml.constructor

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict


def _comp_apply(f, g, *args, **kwargs):
    return f(g(*args, **kwargs))


def compose(*fx):
    return reduce(partial(partial, _comp_apply), fx)


# why, pyyaml devs..

class YAMLLoader(yaml.Loader):
    def __init__(self, *args, **kwargs):
        object_pairs_hook = kwargs.pop('object_pairs_hook', None)
        super(YAMLLoader, self).__init__(*args, **kwargs)
        if object_pairs_hook is not None:
            self._object_pairs_hook = object_pairs_hook
            self.add_constructor(u'tag:yaml.org,2002:map',
                    compose(object_pairs_hook, self.__map_yielder))
            self.add_constructor(u'tag:yaml.org,2002:omap',
                    compose(object_pairs_hook, self.__map_yielder))
    @staticmethod
    def __map_yielder(loader, node, deep=False):
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            value = loader.construct_object(value_node, deep=deep)
            yield key, value


def yaml_loader_factory(**kwargs):
    return partial(YAMLLoader, **kwargs)


OrderedDictYAMLLoader = yaml_loader_factory(object_pairs_hook=OrderedDict)
ListMapYAMLLoader = yaml_loader_factory(object_pairs_hook=list)


class SortedTest(unittest.TestCase):
    def setUp(self):
        with open('waifu.yaml', encoding='utf8') as fh:
            self.doc = yaml.load(fh, Loader=OrderedDictYAMLLoader)

    def test_series_sorted(self):
        series = list(self.doc.keys())
        self.assertListEqual(series, sorted(series))

    def test_characters_sorted(self):
        for anime_name in self.doc:
            chars = self.doc[anime_name]['characters']
            self.assertListEqual(chars, sorted(chars))


class UniqueTest(unittest.TestCase):
    def setUp(self):
        with open('waifu.yaml', encoding='utf8') as fh:
            self.doc = yaml.load(fh, Loader=ListMapYAMLLoader)

    def test_series_unique(self):
        series = list(series_name for (series_name, _) in self.doc)
        self.assertCountEqual(series, list(set(series)))

    def test_characters_unique(self):
        for anime_name, data in self.doc:
            chars = dict(data)['characters']
            self.assertCountEqual(chars, list(set(chars)))


if __name__ == '__main__':
    unittest.main()
