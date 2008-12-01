from Testing import ZopeTestCase
from Testing.ZopeTestCase.functional import Functional

from Products.CMFTestCase import CMFTestCase
from Products.CMFTestCase.ctc import setupCMFSite

from Products.PloneLanguageTool.tests.layer import SiteLayer

# setup a CMF site
ZopeTestCase.installProduct('PloneLanguageTool')

setupCMFSite(
    extension_profiles=['Products.PloneLanguageTool:PloneLanguageTool'])


class TestCase(CMFTestCase.CMFTestCase):
    """Simple test case
    """
    layer = SiteLayer

class FunctionalTestCase(Functional, CMFTestCase.CMFTestCase):
    """Simple test case for functional tests
    """
    layer = SiteLayer
