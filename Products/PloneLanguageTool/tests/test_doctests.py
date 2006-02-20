"""
   PloneLanguageTool doctests.
"""

import unittest
from zope.testing.doctestunit import DocTestSuite

def test_suite():
    return unittest.TestSuite((
	    DocTestSuite('Products.PloneLanguageTool.availablelanguages'),
	    ))

if __name__ == '__main__':
    unittest.main(defaultTest="test_suite")
