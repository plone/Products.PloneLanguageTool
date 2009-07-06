from Testing import ZopeTestCase

from Products.PloneLanguageTool.LanguageTool import LanguageTool
from Products.PloneLanguageTool.tests.layer import ZCML


ZopeTestCase.installProduct('PloneLanguageTool')
ZopeTestCase.installProduct('SiteAccess')


class TestCase(ZopeTestCase.ZopeTestCase):
    """Simple test case
    """
    layer = ZCML

    def afterSetUp(self):
        self.folder._setObject(LanguageTool.id, LanguageTool())
        self.tool = self.folder._getOb(LanguageTool.id)


class FunctionalTestCase(TestCase, ZopeTestCase.FunctionalTestCase):
    """Simple test case for functional tests
    """
    layer = ZCML
