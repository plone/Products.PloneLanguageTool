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

def addLanguageSelectorSlot(self,out):
    # add language selector portlet
    slot = "here/languageSelectorMacro/macros/globalLanguageSelector"

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
    install_subskin(self, out)
    addLanguageSelectorSlot(self,out)
    return out.getvalue()


