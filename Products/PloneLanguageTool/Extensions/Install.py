from Products.PloneLanguageTool import lang_globals
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews
from Products.Archetypes.Extensions.utils import install_subskin

_globals = globals()

def install_tools(self, out):
    if not hasattr(self, "portal_languages"):
        addTool = self.manage_addProduct['PloneLanguageTool'].manage_addTool
        addTool('Plone Language Tool')

def install_actions(self, out):
    at = getToolByName(self, "portal_actions")
    at.manage_aproviders('portal_languages', add_provider=1)

def addLanguageSelectorSlot(self,out):
    # add language selector portlet
    
    # old portlet with i18nLayer support:
    # slot = "here/languageSelectorMacro/macros/globalLanguageSelector"
    
    slot = "here/portlet_languages/macros/portlet"

    left_slots=getattr(self,'left_slots', None)
    right_slots=getattr(self, 'right_slots', ())

    if left_slots != None:
        if slot not in left_slots and slot not in right_slots:
            left_slots=list(left_slots)+[slot,]
            self.left_slots=left_slots
            print >> out, 'Added Language selector portlet to left_slots property.\n'


def install(self):
    out = StringIO()
    print >>out, "Installing PloneLanguageTool"

    install_tools(self, out)
    install_actions(self, out)
    install_subskin(self, out, lang_globals)
    addLanguageSelectorSlot(self,out)
    return out.getvalue()

#
# Uninstall methods
#

def unregisterActionProvider(self, out):
    actionTool = getToolByName(self, 'portal_actions', None)
    if actionTool:
        actionTool.deleteActionProvider('portal_languages')
        out.write('Removed action provider\n')

# The uninstall is used by the CMFQuickInstaller for uninstalling.
# CMFQuickInstaller uninstalls skins.
def uninstall(self):
    out=StringIO()
    unregisterActionProvider(self, out)
    return out.getvalue()
