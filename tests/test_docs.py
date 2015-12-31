#!/usr/bin/python

import os
import sys
import unittest
import time
import subprocess

class CB_TEST_DOCS(unittest.TestCase):
    def test_template(self):
        self.assertTrue("unit tests should be written for this package")

if __name__ == '__main__':
    unittest.main()
