import logging
import os
from unittest import TestCase
from unittest.mock import MagicMock, call, patch, mock_open
from util import ClassTester, OpenMocker, \
        PopenMocker, CheckCallMocker

from proj import core

class TestNode(ClassTester):
    
    class Klass(core.Node):

        log_info_string = "Foo %s"

        def render(self):
            self.rendered = True


    config_kwargs = {"foo": "bar"}
    data_kwargs = {}

    def setUp(self):
        self.logger = logging.getLogger("MockNodeLogger")
        self.logger.isEnabledFor = MagicMock(return_value=True)
        self.logger.log = MagicMock()
        self.i = self.Klass(logger=self.logger,
                            **self.config_kwargs)


    def test__getattr___(self):
        self.assertIsNone(self.i.doesntexist)
                

    def test_make(self):
        self.i.make(**self.data_kwargs)
        self.assertTrue(self.i.rendered)
        self.assertDictContainsSubset(self.data_kwargs, 
                                      self.i.data)

        self.logger.log.assert_has_calls([
            call(logging.INFO, self.i.log_info_string, {})
            ])


    def test_dry_run(self):
        self.i.make(dry_run=True, **self.data_kwargs)
        self.assertFalse(self.i.rendered)
        self.logger.log.assert_has_calls([
            call(logging.INFO, self.i.log_info_string, {})
            ])


class TestBranch(ClassTester):
    class Klass(core.Branch):
        def render(self):
            self.rendered = True

        def log_info(self):
            return ("INFO",)

        def log_debug(self):
            return ("DEBUG",)


    config_kwargs = {"foo": "bar"}
    data_kwargs = {
        "buzz": "bat",
        "module": "a/b",
        "name": "c"
        }


    def setUp(self):
        self.logger = logging.getLogger("MockBranchLogger")
        self.logger.isEnabledFor = MagicMock(return_value=True)
        self.logger.log = MagicMock()
        self.contents = [
            MagicMock(data={"name": "A"}, make=MagicMock()),
            MagicMock(data={"name": "B"}, make=MagicMock()),
            ]
        self.i = self.Klass(logger=self.logger,
                            contents=self.contents,
                            **self.config_kwargs)


    def test_make(self):
        self.i.make(**self.data_kwargs)
        self.assertTrue(self.i.rendered)
        self.logger.log.assert_has_calls([
            call(logging.INFO, "INFO"),
            call(logging.DEBUG, "DEBUG")
            ])

        x = dict(self.i.data, module="a/b/c")
        for item in self.contents:
            item.make.assert_called_with(dry_run=False, **x)


    def test_dry_run(self):
        self.i.make(dry_run=True, **self.data_kwargs)
        self.assertFalse(self.i.rendered)
        self.logger.log.assert_has_calls([
            call(logging.INFO, "INFO"),
            call(logging.DEBUG, "DEBUG")
            ])
        
        x = dict(self.i.data, module="a/b/c")
        for item in self.contents:
            item.make.assert_called_with(dry_run=True, **x)


class TestFile(ClassTester):
    def setUp(self):
        self.i = core.File("foo.txt")


    def test_render(self):
        with patch("proj.core.touch") as mock_touch:
            self.i.make(**{
                "name": "bar.txt",
                "module": "c",
                "root": "a/b"
                })

            mock_touch.assert_called_with("a/b/c/foo.txt", None)


class TestDirectory(ClassTester):

    def setUp(self):
        self.children = children = [
            MagicMock(make=MagicMock()),
            MagicMock(make=MagicMock()),
            MagicMock(make=MagicMock()),
            ]

        self.i = core.Directory("bat", contents=children)

    def test_render(self):
        with patch("proj.core.mkdirp") as mock_mkdirp:
            self.i.make(**{
                "name": "notbat",
                "module": "c",
                "root": "a/b"
                })

            mock_mkdirp.assert_called_with("a/b/c/bat")

            for item in self.children:
                item.make.assert_called_with(**dict(
                    root="a/b",
                    module="c/bat",
                    dry_run=False,
                    name="bat"
                    ))

    
class TestTemplate(ClassTester):

    def setUp(self):
        self.i = core.Template(
            "foo.txt",
            "{module}, {foo}, {name}"
            )

    def test_render(self):
        with OpenMocker("proj.core") as m_open:
            self.i.make(**dict(
                root="d/e",
                module="f",
                foo="buzz"
                ))

            m_open.assert_called_with("d/e/f/foo.txt", "w")
            m_open().write.assert_called_with(
                    "f, buzz, foo.txt")


class TestShellCommand(ClassTester):

    def setUp(self):
        self.i = core.ShellCommand(["ls", "{foo}"])

    def test_format(self):
        self.i.data["foo"] = "bar"
        self.assertEquals(self.i._format_cmd(), ["ls", "bar"])

    def test_render(self):
        with CheckCallMocker("proj.core") as m_popen:
            self.i.make(**dict(
                root="a/b",
                module="c",
                foo="batt"
                ))

            m_popen.assert_called_with(
                ["ls", "batt"],
                cwd="a/b/c"
                )


class TestMaker(TestCase):
    class Klass(core.Maker):
        def __init__(self):
            pass

    def setUp(self):
        self.i = self.Klass()
        self.i.config = {}
        self.i.data = {}

    def test_get_template(self):
        with OpenMocker("proj.core") as m_open, \
                patch("os.path.relpath") as m_relpath:
            self.i.template_path = "foo/bar"
            m_relpath.return_value = "foo/buzz"
            m_open().read.return_value = "foobar\n"
            rv = self.i._get_template("../buzz")

            m_relpath.assert_called_with("foo/bar", "../buzz")
            m_open.assert_called_with("foo/buzz")
            m_open().read.assert_called_with()
            self.assertEqual(rv, "foobar\n")

    def test_build(self):
        self.i.hooks = MagicMock(trigger=MagicMock())
        self.i.hooks.trigger.return_value = None
        structure = [
            {
                "afile": None,
                "anemptydir": {},
                "anotheremptydir": [],
                "adirwithstuff": {
                    "cmd": "!ls foobar",
                    "template": "@footemplate",
                    "afilestuff": "buzzbat"
                    }
                },
            {
                "bfile": None
                }
            ]

        self.i._get_template = MagicMock(return_value="fizz{name}")
        rv = list(self.i._build(structure))
        for item in rv:
            self.assertIsInstance(item, core.Node)

        self.assertEqual(rv[-1].name, 'bfile')

        self.i.hooks.trigger.assert_has_calls([
            call('parse_structure', 'adirwithstuff', structure[0]['adirwithstuff']),
            call('parse_structure', 'cmd', '!ls foobar'),
            call('parse_structure', 'afilestuff', 'buzzbat'),
            call('parse_structure', 'template', '@footemplate'),
            call('parse_structure', 'anotheremptydir', []),
            call('parse_structure', 'afile', None),
            call('parse_structure', 'anemptydir', {}),
            call('parse_structure', 'bfile', None)
            ])

    
    def test_make(self):
        self.i.hooks = MagicMock(trigger=MagicMock())
        self.i.root = MagicMock(make=MagicMock())

        self.i.make(fuzz="buzz")
        self.i.hooks.trigger.assert_called_with("augment_data", {"fuzz": "buzz"}, {})

