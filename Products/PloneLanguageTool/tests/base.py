from plone.app.testing import bbb
from plone.app import testing
from plone.testing import z2

class PloneTestCaseFixture(bbb.PloneTestCaseFixture):

    defaultBases = (bbb.PTC_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, 'Products.PloneLanguageTool')
        import plone.i18n.locales
        self.loadZCML(package=plone.i18n.locales)

    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'Products.PloneLanguageTool:PloneLanguageTool')

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.PloneLanguageTool')

PLT_FIXTURE = PloneTestCaseFixture()
PLT_FUNCTIONAL_TESTING = testing.FunctionalTesting(
    bases=(PLT_FIXTURE,), name='PloneLanguageToolTestCase:Functional')

class TestCase(bbb.PloneTestCase):
    """Simple test case
    """
    layer = PLT_FUNCTIONAL_TESTING

class FunctionalTestCase(TestCase):
    """Simple test case for functional tests
    """
