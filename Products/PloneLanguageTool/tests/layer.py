from zope.testing.cleanup import cleanUp

from Products.CMFCore.testing import FunctionalZCMLLayer
from Products.CMFTestCase import layer as cmf_layer
from Products.Five import zcml


class ZCML(FunctionalZCMLLayer):

    def setUp(cls):
        '''Sets up the CA.'''
        import plone.i18n.locales
        zcml.load_config('configure.zcml', plone.i18n.locales)

        import Products.CMFDefault
        zcml.load_config('configure.zcml', Products.CMFDefault)

        import Products.DCWorkflow
        zcml.load_config('configure.zcml', Products.DCWorkflow)

        import Products.PloneLanguageTool
        zcml.load_config('configure.zcml', Products.PloneLanguageTool)

        import Products.PlacelessTranslationService
        zcml.load_config('configure.zcml', Products.PlacelessTranslationService)

    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        cleanUp()
    tearDown = classmethod(tearDown)


class SiteLayer(ZCML):

    def setUp(cls):
        '''Sets up the CA.'''
        for func, args, kw in cmf_layer._deferred_setup:
            func(*args, **kw)

    setUp = classmethod(setUp)

    def tearDown(cls):
        '''Cleans up the CA.'''
        for func, args, kw in cmf_layer._deferred_cleanup:
            func(*args, **kw)

        # cleanUp()
    tearDown = classmethod(tearDown)
