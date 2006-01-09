from AccessControl import ModuleSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.DirectoryView import registerDirectory
import Products.CMFCore.utils

ADD_CONTENT_PREMISSIONS = 'Manage Portal'
lang_globals = globals()
registerDirectory('skins', lang_globals)

PKG_NAME = "PloneLanguageTool"

from Products.PloneLanguageTool.LanguageTool import LanguageTool
tools = (LanguageTool,)

def initialize(context):
    Products.CMFCore.utils.ToolInit("Plone Language Tool", tools=tools,
                   product_name=PKG_NAME,
                   icon="tool.gif",
                   ).initialize(context)

types_globals=globals()
