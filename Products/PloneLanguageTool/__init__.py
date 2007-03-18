from Products.CMFCore.utils import ToolInit
from Products.PloneLanguageTool import LanguageTool

ADD_CONTENT_PREMISSIONS = 'Manage Portal'
lang_globals = globals()

PKG_NAME = 'PloneLanguageTool'

def initialize(context):
    ToolInit('Plone Language Tool',
             tools=(LanguageTool.LanguageTool,),
             icon='tool.gif',
    ).initialize(context)
