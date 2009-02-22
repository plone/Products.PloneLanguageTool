from Products.PloneLanguageTool import LanguageTool
from Products.PloneLanguageTool.tests import base


class TestLanguageToolExists(base.TestCase):

    def testLanguageToolExists(self):
        self.failUnless(LanguageTool.id in self.folder.objectIds())


class TestLanguageToolSettings(base.TestCase):

    def testLanguageToolType(self):
        self.failUnless(self.tool.meta_type == LanguageTool.meta_type)

    def testSetLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.tool.manage_setLanguageSettings(
            defaultLanguage, supportedLanguages, setContentN=False,
            setCookieN=False, setRequestN=False, setPathN=False,
            setForcelanguageUrls=False, setAllowContentLanguageFallback=True,
            setUseCombinedLanguageCodes=True, startNeutral=False,
            displayFlags=False, setCcTLDN=True, setSubdomainN=True,
            setAuthOnlyN=True)

        self.failUnless(self.tool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.tool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.tool.use_content_negotiation==False)
        self.failUnless(self.tool.use_cookie_negotiation==False)
        self.failUnless(self.tool.use_request_negotiation==False)
        self.failUnless(self.tool.use_path_negotiation==False)
        self.failUnless(self.tool.force_language_urls==False)
        self.failUnless(self.tool.allow_content_language_fallback==True)
        self.failUnless(self.tool.use_combined_language_codes==True)
        self.failUnless(self.tool.startNeutral()==False)
        self.failUnless(self.tool.showFlags()==False)
        self.failUnless(self.tool.use_cctld_negotiation==True)
        self.failUnless(self.tool.use_subdomain_negotiation==True)
        self.failUnless(self.tool.authenticated_users_only==True)


class TestLanguageTool(base.TestCase):

    def testLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.tool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                             setUseCombinedLanguageCodes=False)
        self.failUnless(self.tool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.tool.getSupportedLanguages()==supportedLanguages)

    def testSupportedLanguages(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.tool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        self.failUnless(self.tool.getSupportedLanguages()==supportedLanguages)

        self.tool.removeSupportedLanguages(supportedLanguages)
        self.failUnless(self.tool.getSupportedLanguages()==[])

        for lang in supportedLanguages:
            self.tool.addSupportedLanguage(lang)
        self.failUnless(self.tool.getSupportedLanguages()==supportedLanguages)

    def testDefaultLanguage(self):
        supportedLanguages = ['de','no']

        self.tool.manage_setLanguageSettings('no', supportedLanguages)
        self.failUnless(self.tool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.tool.getDefaultLanguage()=='no')

        # default not in supported languages, should set to first supported
        self.tool.manage_setLanguageSettings('nl', supportedLanguages)

        self.failUnless(self.tool.getSupportedLanguages()==supportedLanguages)
        self.failUnless(self.tool.getDefaultLanguage()=='de')

    def testAvailableLanguage(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.tool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        availableLanguages = self.tool.getAvailableLanguageInformation()
        for lang in availableLanguages:
            if lang in supportedLanguages:
                self.failUnless(availableLanguages[lang]['selected'] == True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLanguageToolExists))
    suite.addTest(makeSuite(TestLanguageToolSettings))
    suite.addTest(makeSuite(TestLanguageTool))
    return suite
