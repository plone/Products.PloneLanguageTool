from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.utils import getToolInterface
from Products.CMFPlone.interfaces import ILanguageSchema
from Products.PloneLanguageTool import LanguageTool
from Products.PloneLanguageTool.interfaces import ILanguageTool
from Products.PloneLanguageTool.testing import (
    INTEGRATION_TESTING, FUNCTIONAL_TESTING)
from plone.app.testing.bbb import PloneTestCase
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides
import unittest


class TestLanguageToolExists(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ILanguageSchema, prefix="plone")
        self.tool_id = LanguageTool.id

    def testLanguageToolExists(self):
        self.failUnless(self.tool_id in self.portal.objectIds())


class TestLanguageToolSettings(unittest.TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ILanguageSchema, prefix="plone")
        self.tool_id = LanguageTool.id
        self.ltool = self.portal._getOb(self.tool_id)

    def testLanguageToolType(self):
        self.failUnless(self.ltool.meta_type == LanguageTool.meta_type)

    def testSetLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en', 'de', 'no']
        self.ltool.manage_setLanguageSettings(
            defaultLanguage, supportedLanguages,
            setContentN=False,
            setCookieN=False, setCookieEverywhere=False,
            setRequestN=False,
            setPathN=False, setForcelanguageUrls=False,
            setAllowContentLanguageFallback=True,
            setUseCombinedLanguageCodes=True,
            startNeutral=False,
            displayFlags=True,
            setCcTLDN=True, setSubdomainN=True,
            setAuthOnlyN=True)

        self.failUnless(self.ltool.getDefaultLanguage() == defaultLanguage)
        self.failUnless(
            self.ltool.getSupportedLanguages() == supportedLanguages)
        self.failUnless(self.settings.use_content_negotiation == False)
        self.failUnless(self.settings.use_cookie_negotiation == False)
        self.failUnless(self.settings.set_cookie_always == False)
        self.failUnless(self.settings.use_request_negotiation == False)
        self.failUnless(self.settings.use_path_negotiation == False)
        self.failUnless(self.settings.use_combined_language_codes)
        self.failUnless(self.ltool.showFlags())
        self.failUnless(self.settings.use_cctld_negotiation)
        self.failUnless(self.settings.use_subdomain_negotiation)
        self.failUnless(self.settings.authenticated_users_only)


class TestLanguageTool(PloneTestCase):
    layer = FUNCTIONAL_TESTING

    def afterSetUp(self):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            ILanguageSchema, prefix="plone")
        self.tool_id = LanguageTool.id
        self.ltool = self.portal._getOb(self.tool_id)

    def testLanguageSettings(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en', 'de', 'no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages,
                                              setUseCombinedLanguageCodes=False)
        self.failUnless(self.ltool.getDefaultLanguage()==defaultLanguage)
        self.failUnless(self.ltool.getSupportedLanguages()==supportedLanguages)

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

    def testAvailableLanguage(self):
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        availableLanguages = self.ltool.getAvailableLanguageInformation()
        for lang in availableLanguages:
            if lang in supportedLanguages:
                self.failUnless(availableLanguages[lang]['selected'] == True)

    def testGetContentLanguage(self):
        # tests for issue #11263
        defaultLanguage = 'de'
        supportedLanguages = ['en','de','no']
        self.ltool.manage_setLanguageSettings(defaultLanguage, supportedLanguages)
        self.ltool.REQUEST.path = ['Members',]

        content = self.portal.Members
        content.setLanguage('de')
        alsoProvides(content, IDublinCore)
        self.ltool.getContentLanguage()
        self.failUnless(self.ltool.getContentLanguage()=='de')
        self.ltool.REQUEST.path = ['view', 'foo.jpg', 'Members',]
        self.failUnless(self.ltool.getContentLanguage()=='de')
        self.ltool.REQUEST.path = ['foo.jpg', 'Members',]
        self.failUnless(self.ltool.getContentLanguage()==None)
        self.ltool.REQUEST.path = ['foo', 'portal_javascript',]
        self.failUnless(self.ltool.getContentLanguage()==None)

    def testRegisterInterface(self):
        iface = getToolInterface('portal_languages')
        self.assertEqual(iface, ILanguageTool)
