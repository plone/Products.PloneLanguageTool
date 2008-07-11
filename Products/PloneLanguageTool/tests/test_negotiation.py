import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import default_user
from Products.PloneTestCase.PloneTestCase import default_password

PloneTestCase.setupPloneSite()
from Products.PloneLanguageTool import LanguageTool


class LanguageNegotiationTestCase(PloneTestCase.FunctionalTestCase):

    def afterSetUp(self):
        self.basic_auth = '%s:%s' % (default_user, default_password)
        self.portal_path = self.portal.absolute_url(1)
        self.tool = self.portal[LanguageTool.id]


class TestDefaultLanguageNegotiation(LanguageNegotiationTestCase):

    def testLanguageNegotiation(self):
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'pt'})

        self.assertEquals(response.getStatus(), 200)
        # Once PLT is installed only English is allowed as a language
        self.assertEquals(response.headers['content-language'], 'en')


class TestNoCombinedLanguageNegotiation(LanguageNegotiationTestCase):

    def afterSetUp(self):
        LanguageNegotiationTestCase.afterSetUp(self)
        # set some allowed languages and make sure we don't use combined
        # language codes
        self.tool.supported_langs = ['en', 'pt', 'de']
        self.tool.use_combined_language_codes = 0
        self.tool.display_flags = 0

    def testLanguageNegotiation(self):
        # Test simple supported codes
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'pt'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="pt">'
            in response.getBody())

        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'de'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="de">'
            in response.getBody())

        # Test combined unsupported codes, should fall back
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'pt-br'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="pt">'
            in response.getBody())


class TestCombinedLanguageNegotiation(LanguageNegotiationTestCase):

    def afterSetUp(self):
        LanguageNegotiationTestCase.afterSetUp(self)
        # set some allowed languages and make sure we don't use combined
        # language codes
        self.tool.supported_langs = ['en', 'pt', 'de', 'pt-br']
        self.tool.use_combined_language_codes = 1
        self.tool.display_flags = 0

    def testLanguageNegotiation(self):
        # Test simple supported codes
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'pt'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="pt">'
            in response.getBody())

        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'de'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="de">'
            in response.getBody())

        # Test combined supported codes
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'pt-br'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="pt-br">'
            in response.getBody())

        # Test combined unsupported codes, should fall back
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_ACCEPT_LANGUAGE': 'de-de'})

        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="de">'
            in response.getBody())


class TestCcTLDLanguageNegotiation(LanguageNegotiationTestCase):
    def afterSetUp(self):
        LanguageNegotiationTestCase.afterSetUp(self)
        self.tool.supported_langs = ['en', 'nl', 'fr']
        self.tool.use_cctld_negotiation = 1
        self.tool.display_flags = 0

    def checkLanguage(self, response, language):
        self.assertEquals(response.getStatus(), 200)
        self.failUnless('<option selected="selected" value="%s">' % language
            in response.getBody())

    def testSimpleHostname(self):
        # For a simple hostname without ccTLD the canonical language is used
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_HOST': 'localhost'})
        self.checkLanguage(response, "en")

    def testIPAddress(self):
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_HOST': '127.0.0.1'})
        self.checkLanguage(response, "en")

    def testDutchDomain(self):
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_HOST': 'plone.nl'})
        self.checkLanguage(response, "nl")

    def testAcceptedLanguages(self):
        # Brazil uses Portugese, which is not in the accepted languages list
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_HOST': 'plone.br'})
        self.checkLanguage(response, "en")

    def testMultiLingualCountries(self):
        # Some countries refuse to pick a single language. Belgium
        # uses both Dutch and French, with a preference for Dutch.

        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_HOST': 'plone.be'})
        self.checkLanguage(response, "nl")

        # If we stop allowing Dutch we should now fall back to French
        self.tool.supported_langs = ['en', 'fr']
        response = self.publish(self.portal_path, self.basic_auth,
                                env={'HTTP_HOST': 'plone.be'})
        self.checkLanguage(response, "fr")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultLanguageNegotiation))
    suite.addTest(makeSuite(TestNoCombinedLanguageNegotiation))
    suite.addTest(makeSuite(TestCombinedLanguageNegotiation))
    suite.addTest(makeSuite(TestCcTLDLanguageNegotiation))
    return suite

if __name__ == '__main__':
    framework()

