from unittest.mock import MagicMock
from util import ClassTester, WalkMocker
from proj import plugin

class TestPluginManager(ClassTester):
    def setUp(self):
        mock_project = MagicMock()
        self.i = plugin.PluginManager(mock_project)

    def test_find_plugins(self):
        with patch("proj.plugin.walk") as m_walk:
            def traverse(path):
                pass

        with WalkMocker("proj.plugin") as walk_mocker:
            pass

