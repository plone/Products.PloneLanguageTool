from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ToolInit

ADD_CONTENT_PREMISSIONS = 'Manage Portal'
lang_globals = globals()
registerDirectory('skins', lang_globals)

PKG_NAME = 'PloneLanguageTool'

from Products.PloneLanguageTool.LanguageTool import LanguageTool
tools = (LanguageTool,)

def initialize(context):
    ToolInit('Plone Language Tool',
             tools=tools,
             icon='tool.gif',
    ).initialize(context)
