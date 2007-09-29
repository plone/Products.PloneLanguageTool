from zope.interface import Interface

# BBB Plone 4.0
try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable


class ILanguageTool(Interface):
    """Marker interface for the portal_languages tool.
    """
