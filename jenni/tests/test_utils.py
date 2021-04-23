from unittest import TestCase

from jenni.utils import quote1or3xs, quote3xs, quote_list


class Tests(TestCase):
    def test_quote3xs(self):
        self.assertEqual("""''''''""", quote3xs(""))
        self.assertEqual("""'''x'''""", quote3xs("x"))
        self.assertEqual("""'''\n'''""", quote3xs("\n"))
        self.assertEqual("""'''x\\\\x'''""", quote3xs("x\\x"))
        self.assertEqual("""'''\\''''''""", quote3xs("""'''"""))
        self.assertEqual("""''''x'''''""", quote3xs("""'x''"""))

    def test_quote1or3xs(self):
        self.assertEqual("""''""", quote1or3xs(""))
        self.assertEqual("""'x'""", quote1or3xs("x"))
        self.assertEqual("""'''\n'''""", quote1or3xs("\n"))
        self.assertEqual("""'x\\\\x'""", quote1or3xs("x\\x"))
        self.assertEqual("""'\\'\\'\\''""", quote1or3xs("""'''"""))
        self.assertEqual("""'\\'x\\'\\''""", quote1or3xs("""'x''"""))

    def test_quote_list(self):
        self.assertEqual("""[]""", quote_list([]))
        self.assertEqual("""['']""", quote_list([""]))
        self.assertEqual("""['x']""", quote_list(["x"]))
        self.assertEqual("""['x', '''\n''']""", quote_list(["x", "\n"]))
