from zope.testing.cleanup import cleanUp

from Products.Five import zcml
from Testing.ZopeTestCase.layer import ZopeLite


class ZCML(ZopeLite):

    def setUp(cls):
        '''Sets up the CA by loading etc/site.zcml.'''
        cleanUp()
        zcml.load_site()

        import plone.i18n.locales
        zcml.load_config('configure.zcml', plone.i18n.locales)

        import Products.PloneLanguageTool
        zcml.load_config('configure.zcml', Products.PloneLanguageTool)

        import Products.PloneLanguageTool
        zcml.load_config('overrides.zcml', Products.PloneLanguageTool)

    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        cleanUp()
    tearDown = classmethod(tearDown)
