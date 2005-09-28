#
# PloneLanguageTool TestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Products.PloneLanguageTool import availablelanguages

ZopeTestCase.installProduct('PloneLanguageTool')

class TestAvailableLanguages(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        pass

    def testLanguages(self):
        self.failUnless(availablelanguages.languages==availablelanguages.getLanguages())

    def testNativeLanguageNames(self):
        names = availablelanguages.getNativeLanguageNames()
        self.failUnless(len(availablelanguages.languages)==len(names))

    def testCombined(self):
        self.failUnless(availablelanguages.combined==availablelanguages.getCombined())

    def testCombinedLanguageNames(self):
        names = availablelanguages.getCombinedLanguageNames()
        self.failUnless(len(availablelanguages.combined)==len(names))

    def testCountries(self):
        self.failUnless(len(availablelanguages.countries)==len(availablelanguages.getCountries()))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAvailableLanguages))
    return suite

if __name__ == '__main__':
    framework()
