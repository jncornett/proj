from util import ClassTester
from proj import util

class TestChainedDictView(ClassTester):
    def setUp(self):
        self.i = util.ChainedDictView(
            {"a": 1, "b": 2, "c": 3},
            {"c": 4, "d": 5, "e": 6},
            {"e": 7, "f": 8, "g": 9}
            )

    def test_get(self):
        self.assertEqual(self.i.get("a"), 1)
        self.assertEqual(self.i.get("e"), 7)
        self.assertEqual(self.i.get("h", 27), 27)
        self.assertRaises(TypeError, self.i.get, "a", 1, 2)

    def test_items(self):
        self.assertEquals(self.i.items(), {
            ("a", 1), ("b", 2), ("c", 4),
            ("d", 5), ("e", 7), ("f", 8), ("g", 9)
            })


    def test_len(self):
        self.assertEqual(len(self.i), 7)
