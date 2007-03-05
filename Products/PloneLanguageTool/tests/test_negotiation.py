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


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDefaultLanguageNegotiation))
    suite.addTest(makeSuite(TestNoCombinedLanguageNegotiation))
    return suite

if __name__ == '__main__':
    framework()

