from zope.interface import Interface

# BBB Plone 4.0
from zope.deprecation import __show__
__show__.off()
try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable
__show__.on()

class ILanguageTool(Interface):
    """Marker interface for the portal_languages tool.
    """
