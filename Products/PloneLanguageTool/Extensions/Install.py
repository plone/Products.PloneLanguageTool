from Products.PloneLanguageTool import lang_globals
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.Archetypes.Extensions.utils import install_subskin
from Products.CMFCore.permissions import ManagePortal

_globals = globals()

configlets = \
( { 'id'         : 'PloneLanguageTool'
  , 'name'       : 'Language Settings'
  , 'action'     : 'string:${portal_url}/portal_languages/prefs_languages'
  , 'category'   : 'Plone'
  , 'appId'      : 'PloneLanguageTool'
  , 'permission' : ManagePortal
  , 'imageUrl'   : 'flag-plone.gif'
  },
)

def install_tools(self, out):
    if not hasattr(self, 'portal_languages'):
        addTool = self.manage_addProduct['PloneLanguageTool'].manage_addTool
        addTool('Plone Language Tool')

def install_actions(self, out):
    at = getToolByName(self, 'portal_actions')
    at.manage_aproviders('portal_languages', add_provider=1)

def addLanguageSelectorSlot(self,out):
    # portlet
    slot = 'here/portlet_languages/macros/portlet'

    left_slots = getattr(self, 'left_slots', None)
    right_slots = getattr(self, 'right_slots', ())

    if left_slots != None:
        if slot not in left_slots and slot not in right_slots:
            left_slots = list(left_slots) + [slot]
            self.left_slots = left_slots
            print >> out, 'Added Language selector portlet to left_slots property.\n'

def addConfiglets(self, out):
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            out.write('Adding configlet %s\n' % conf['id'])
            configTool.registerConfiglet(**conf)

def install(self):
    out = StringIO()
    print >>out, 'Installing PloneLanguageTool'

    install_tools(self, out)
    install_actions(self, out)
    install_subskin(self, out, lang_globals)
    addConfiglets(self, out)
    # Re-enable this if you want the language portlet.
    # Superceded by the language selector.
    # addLanguageSelectorSlot(self,out)
    return out.getvalue()

#
# Uninstall methods
#

def unregisterActionProvider(self, out):
    actionTool = getToolByName(self, 'portal_actions', None)
    if actionTool:
        actionTool.deleteActionProvider('portal_languages')
        out.write('Removed action provider\n')

def removeConfiglets(self, out):
    configTool = getToolByName(self, 'portal_controlpanel', None)
    if configTool:
        for conf in configlets:
            out.write('Removing configlet %s\n' % conf['id'])
            configTool.unregisterConfiglet(conf['id'])

def uninstall(self):
    out=StringIO()
    unregisterActionProvider(self, out)
    removeConfiglets(self, out)
    return out.getvalue()
