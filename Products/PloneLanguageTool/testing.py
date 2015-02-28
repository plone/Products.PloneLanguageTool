from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
# from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from plone.app.testing import TEST_USER_ID
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing.bbb import _createMemberarea

from plone.testing import z2

from zope.configuration import xmlconfig


class PloneLanguageToolLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, 'plone.app.contenttypes')
        z2.installProduct(app, 'Products.PloneLanguageTool')

        # Load ZCML
        import Products.PloneLanguageTool
        xmlconfig.file(
            'configure.zcml',
            Products.PloneLanguageTool,
            context=configurationContext
        )

        import plone.i18n.locales
        xmlconfig.file(
            'configure.zcml',
            plone.i18n.locales,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.PloneLanguageTool:PloneLanguageTool')
        portal.invokeFactory(
            'Folder',
            id='Members',
            title='Members',
        )
        _createMemberarea(portal, TEST_USER_ID)

    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'Products.PloneLanguageTool')


FIXTURE = PloneLanguageToolLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="PloneLanguageToolLayer:Integration"
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneLanguageToolLayer:Functional"
)
