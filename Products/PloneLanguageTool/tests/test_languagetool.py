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
                                   displayFlags=False)

        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.ltool.use_cookie_negotiation==False)
        self.failUnless(self.ltool.use_request_negotiation==False)
        self.failUnless(self.ltool.use_path_negotiation==False)
        self.failUnless(self.ltool.force_language_urls==False)
        self.failUnless(self.ltool.allow_content_language_fallback==True)
        self.failUnless(self.ltool.use_combined_language_codes==True)
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

    def testSupportedCountries(self):
        self.failUnless(len(self.ltool.getAvailableCountries())==len(availablelanguages.getCountries()))
        self.failUnless(len(self.ltool.listAvailableCountries())==len(availablelanguages.getCountries()))

        self.ltool.addCountry('XY', 'MyTestPlace')
        self.failUnless(len(self.ltool.getAvailableCountries())==len(availablelanguages.getCountries())+1)
        self.failUnless(self.ltool.getNameForCountryCode('XY')=='MyTestPlace')
        self.failUnless(self.ltool.getNameForCountryCode('DE')=='Germany')

    def testAvailableLanguage(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        availableLanguages = self.ltool.getAvailableLanguageInformation()
        self.failUnless(len(availableLanguages)==len(availablelanguages.getLanguages()))
        for lang in availableLanguages:
            if lang in supportedLanguages:
                self.failUnless(availableLanguages[lang]['selected'] == True)


class TestAddingLanguage(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.id = LanguageTool.id
        self.ltool = self.portal._getOb(self.id)

    def testAddingLocalLanguages(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                              setUseCombinedLanguageCodes=False)
        # Warning: Addition of languages persists between tests
        self.ltool.addLanguage('xy', 'Test language')
        self.failUnless(len(self.ltool.getAvailableLanguages())==len(availablelanguages.getLanguages())+1)

        self.failUnless(self.ltool.getNameForLanguageCode('xy')=='Test language')
        self.failUnless(self.ltool.getNameForLanguageCode('de')=='Deutsch')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLanguageToolExists))
    suite.addTest(makeSuite(TestLanguageToolSettings))
    suite.addTest(makeSuite(TestLanguageTool))
    suite.addTest(makeSuite(TestAddingLanguage))
    return suite

if __name__ == '__main__':
    framework()

