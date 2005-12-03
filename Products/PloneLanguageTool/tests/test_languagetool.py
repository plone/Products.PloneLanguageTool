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
from Products.PloneLanguageTool import availablelanguages

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
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                   setCookieN=False, setRequestN=False,
                                   setPathN=False, setForcelanguageUrls=False,
                                   setAllowContentLanguageFallback=True,
                                   setUseCombinedLanguageCodes=True,
                                   startNeutral=False, displayFlags=False)

        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.use_cookie_negotiation==False)
        self.failUnless(self.ltool.use_request_negotiation==False)
        self.failUnless(self.ltool.use_path_negotiation==False)
        self.failUnless(self.ltool.force_language_urls==False)
        self.failUnless(self.ltool.allow_content_language_fallback==True)
        self.failUnless(self.ltool.use_combined_language_codes==True)
        self.failUnless(self.ltool.startNeutral()==False)
        self.failUnless(self.ltool.showFlags()==False)


class TestLanguageTool(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                              setUseCombinedLanguageCodes=False)
        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(len(self.ltool.listSupportedLanguages())==len(supportedLanguages))

    def testSupportedLanguages(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

        self.ltool.removeSupportedLanguages(supportedLanguages)
        self.failUnless(self.ltool.getSupportedLanguages()==[])

        for lang in supportedLanguages:
            self.ltool.addSupportedLanguage(lang)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

    def testDefaultLanguage(self):
        supportedLanguages = ['de','no']

        self.ltool.manage_setLanguageSettings('no', supportedLanguages)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.getDefaultLanguage()=='no')

        # default not in supported languages, should set to first supported
        self.ltool.manage_setLanguageSettings('nl', supportedLanguages)

        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.getDefaultLanguage()=='de')


class TestLocalLanguages(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testAddRemove(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                              setUseCombinedLanguageCodes=False)

        # Warning: Addition of languages persists between tests
        before = self.ltool.getAvailableLanguages()
        self.ltool.addLanguage('xy', 'Test language')
        after = self.ltool.getAvailableLanguages()
        self.failUnless(len(before)+1==len(after))
        self.failUnless('xy' in after)

        self.failUnless(self.ltool.getNameForLanguageCode('xy')=='Test language')
        self.failUnless(self.ltool.getNameForLanguageCode('de')=='Deutsch')

        self.ltool.removeLanguage('xy')
        after = self.ltool.getAvailableLanguages()
        self.failUnless(len(before)==len(after))
        self.failUnless('xy' not in after)

    def beforeTearDown(self):
        self.ltool.removeLanguage('xy')


class TestLocalCountries(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testAddRemove(self):

        # Warning: Addition of countries persists between tests
        before = self.ltool.getAvailableCountries()
        self.ltool.addCountry('qq', 'Test country')
        after = self.ltool.getAvailableCountries()
        self.failUnless(len(before)+1==len(after))
        self.failUnless('qq' in after)

        self.failUnless(self.ltool.getNameForCountryCode('qq')=='Test country')
        self.failUnless(self.ltool.getNameForCountryCode('DE')=='Germany')

        self.ltool.removeCountry('qq')
        after = self.ltool.getAvailableCountries()
        self.failUnless(len(before)==len(after))
        self.failUnless('qq' not in after)

    def beforeTearDown(self):
        self.ltool.removeCountry('qq')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLanguageToolExists))
    suite.addTest(makeSuite(TestLanguageToolSettings))
    suite.addTest(makeSuite(TestLanguageTool))
    suite.addTest(makeSuite(TestLocalLanguages))
    suite.addTest(makeSuite(TestLocalCountries))
    return suite

if __name__ == '__main__':
    framework()

