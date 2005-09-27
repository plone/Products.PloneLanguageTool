#
# PloneLanguageTool TestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

PloneTestCase.installProduct('PloneLanguageTool')
PRODUCTS = ['PloneLanguageTool']

PloneTestCase.setupPloneSite(products=PRODUCTS)
from Products.PloneLanguageTool import LanguageTool

class TestLanguageToolExists(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id

    def testLanguageToolExists(self):
        self.failUnless(self.id in self.portal.objectIds())


class TestLanguageToolSettings(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testLanguageToolType(self):
        self.failUnless(self.ltool.meta_type == LanguageTool.meta_type)

    def testSetLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                   setCookieN=False, setRequestN=False,
                                   setPathN=False, setForcelanguageUrls=False,
                                   setAllowContentLanguageFallback=True,
                                   setUseCombinedLanguageCodes=True,
                                   displayFlags=False)

        self.failUnless(self.ltool.use_cookie_negotiation==False)
        self.failUnless(self.ltool.use_request_negotiation==False)
        self.failUnless(self.ltool.use_path_negotiation==False)
        self.failUnless(self.ltool.force_language_urls==False)
        self.failUnless(self.ltool.allow_content_language_fallback==True)
        self.failUnless(self.ltool.use_combined_language_codes==True)
        self.failUnless(self.ltool.showFlags()==False)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLanguageToolExists))
    suite.addTest(makeSuite(TestLanguageToolSettings))
    return suite

if __name__ == '__main__':
    framework()

