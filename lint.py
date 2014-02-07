import unittest
import yaml
import yaml.constructor

# why, pyyaml devs..

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict


class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """
    # From http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


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
            self.doc = yaml.load(fh, Loader=OrderedDictYAMLLoader)

    def test_series_unique(self):
        series = list(self.doc.keys())
        self.assertCountEqual(series, list(set(series)))

    def test_characters_unique(self):
        for anime_name in self.doc:
            chars = self.doc[anime_name]['characters']
            self.assertCountEqual(chars, list(set(chars)))


if __name__ == '__main__':
    unittest.main()
