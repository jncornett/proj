from unittest import TestCase
from unittest.mock import mock_open, patch, MagicMock

class ClassTester(TestCase):

    @property
    def i(self):
        return self._instance


    @i.setter
    def i(self, value):
        self._instance = value


    def tearDown(self):
        self.i = None


class Mocker(object):

    target = None

    def __init__(self, namespace):
        self.patch_target = "{}.{}".format(
            namespace,
            self.target
            )

    def get_mock(self):
        return MagicMock()

    def __enter__(self):
        self.mocker = mocker = self.get_mock()
        self.patch = patch(
            self.patch_target,
            self.mocker,
            create=True
            )

        return self.patch.__enter__()

    def __exit__(self, *args, **kwargs):
        self.patch.__exit__(*args, **kwargs)


class OpenMocker(Mocker):

    target = "open"

    def get_mock(self):
        return mock_open()


class PopenMocker(Mocker):

    target = "Popen"


class CheckCallMocker(Mocker):

    target = "check_call"


class WalkMocker(object):
    def __init__(self, namespace):
        self.patch_target = "{}.{}".format(namespace, "walk")
        self.mock_walk = MagicMock()

    def walk(self, *args, **kwargs):
        self.mock_walk(*args, **kwargs)

    def __enter__(self):
        self.patch = patch(
            self.patch_target,
            self.walk
            )

        self.patch.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self.patch.__exit__(*args, **kwargs)
