import unittest

import test_api
import models


class Test(unittest.TestCase):
    def setUp(self):
        models.init_db()

    def test_main(self):
        xrate = models.XRate.get(id=1)
        self.assertEqual(xrate.rate, 1.0)
        test_api.update_xrates(840, 980)
        xrate = models.XRate.get(id=1)

        self.assertEqual(xrate.rate, 1.01)


if __name__ == '__main__':
    unittest.main()
