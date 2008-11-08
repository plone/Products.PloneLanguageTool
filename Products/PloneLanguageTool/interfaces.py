from zope.interface import Interface

try:
    from Products.LinguaPlone.interfaces import ITranslatable
except ImportError:
    class ITranslatable(Interface):
        pass

class ILanguageTool(Interface):
    """Marker interface for the portal_languages tool.
    """
