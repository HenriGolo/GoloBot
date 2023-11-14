import unittest


class TestMisc(unittest.TestCase):

    def test_import(self):
        from GoloBot.Auxilliaire import pack, unpack

        e = 42
        p = pack(e, 1)
        self.assertEqual(p, [e])

        u = unpack(p)
        self.assertEqual(u, e)

    def test_aux_math(self):
        from GoloBot.Auxilliaire.aux_maths import factorielle

        self.assertEqual(factorielle(1), 1)
        self.assertEqual(factorielle(2), 2)
        self.assertEqual(factorielle(3), 6)
        self.assertEqual(factorielle(10), 3628800)


if __name__ == '__main__':
    unittest.main()
