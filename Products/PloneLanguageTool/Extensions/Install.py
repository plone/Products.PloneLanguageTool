from Products.PloneLanguageTool import lang_globals
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.DirectoryView import addDirectoryViews

SKIN_NAME = "LanguageTool"
_globals = globals()

def install_tools(self, out):
    if not hasattr(self, "portal_languages"):
        addTool = self.manage_addProduct['PloneLanguageTool'].manage_addTool
        addTool('Plone Language Tool')

def install_actions(self, out):
    at = getToolByName(self, "portal_actions")
    at.manage_aproviders('portal_languages', add_provider=1)

def install_subskin(self, out, skin_name=SKIN_NAME, globals=lang_globals):
    skinstool=getToolByName(self, 'portal_skins')
    if skin_name not in skinstool.objectIds():
        addDirectoryViews(skinstool, 'skins', globals)

    for skinName in skinstool.getSkinSelections():
        path = skinstool.getSkinPath(skinName)
        path = [i.strip() for i in  path.split(',')]
        try:
            if skin_name not in path:
                path.insert(path.index('custom') +1, skin_name)
        except ValueError:
            if skin_name not in path:
                path.append(skin_name)

        path = ','.join(path)
        skinstool.addSkinSelection( skinName, path)

def install(self):
    out = StringIO()
    print >>out, "Installing PloneLanguageTool"

    install_tools(self, out)
    install_actions(self, out)
    install_subskin(self, out)
    return out.getvalue()


