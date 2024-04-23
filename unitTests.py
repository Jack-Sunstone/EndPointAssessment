import unittest

import SQL

class MyTestCase(unittest.TestCase):
    def test1(self):
        self.assertRaises(Exception, SQL.updateUnit("ARC0001","Sunstone","Sunstone","3"))
