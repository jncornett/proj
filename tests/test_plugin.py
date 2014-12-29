import logging
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
from proj import plugin

PROJECT_SINGLE = ("Project",)

class TestPluginManager(TestCase):
    def setUp(self):
        self.cls = plugin.PluginManager
        self.init_args = [
            PROJECT_SINGLE,
            ["/usr/local/proj/plugins", "~/plugins"]
            ]

        file_ = self.mock_file = MagicMock()

        listdir = self.mock_listdir = MagicMock()
        listdir.return_value = [
            "foo.py",
            "bar.py",
            "bar.pyc",
            "buzz"
            ]

        find_mod = self.mock_find_mod = MagicMock()
        find_mod.return_value = (0, 0, file_, 0)

        load_mod = self.mock_load_mod = MagicMock()
        load_mod.side_effect = lambda b, *a: b


    def test_get_modules(self):
        with patch('os.listdir', self.mock_listdir), \
            patch('imp.find_module', self.mock_find_mod), \
            patch('imp.load_module', self.mock_load_mod):

            i = self.cls(*self.init_args)
            rv = list(i._get_modules("foo/bar"))

            self.mock_find_mod.assert_has_calls([
                call("foo", "foo/bar"),
                call("bar", "foo/bar"),
                call("buzz", "foo/bar")
                ])
            
            self.mock_load_mod.assert_has_calls([
                call("foo", 0, 0, self.mock_file, 0),
                call("bar", 0, 0, self.mock_file, 0),
                call("buzz", 0, 0, self.mock_file, 0)
                ])

            self.assertEquals(rv, ["foo", "bar", "buzz"])

    def test_load_plugins(self):
        i = self.cls(MagicMock(), [])
        get_mod = i._get_modules = MagicMock()
        get_mod.return_value = [1, 2, 3]
        rv = list(i._load_plugins([0, 0]))
        self.assertEquals(rv, [1, 2, 3, 1, 2, 3])

    def test_init_plugins(self):
        class A_Plugin(plugin.Plugin):
            pass

        i = self.cls(MagicMock(), [])
        i.modules = [mod_A] = [MagicMock()]
        mod_A.A_Plugin = A_Plugin
        rv = list(i._init_plugins())
        self.assertIsInstance(rv[0], A_Plugin)



