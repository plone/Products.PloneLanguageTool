import os, os.path
import re
import locale
from types import StringType, UnicodeType

from AccessControl import ClassSecurityInfo
from BTrees.OOBTree import OOBTree

from Globals import InitializeClass, package_home
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.Expression import Expression
from Products.CMFCore.CMFCorePermissions  import ManagePortal, ModifyPortalContent, View
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from StringIO import StringIO
from Acquisition import aq_base
from ComputedAttribute import ComputedAttribute

import availablelanguages

from Products.Archetypes.debug import log


class LanguageTool(UniqueObject, ActionProviderBase, SimpleItem):
    """ CMF Syndication Client  """

    id        = 'portal_languages'
    meta_type = 'Plone Language Tool'

    security = ClassSecurityInfo()

    available_langs = availablelanguages.languages
    supported_langs = availablelanguages.languages.keys()
    default_lang = 'en'
    fallback_lang = 'en'
    # copy global available_langs to class variable

    _actions = [ActionInformation(
        id='languages'
        , title='Portal Languages'
        , action=Expression(text='string: ${portal_url}/portal_languages/langConfig')
        , condition=Expression(text='member')
        , permissions=(ManagePortal,)
        , category='portal_tabs'
        , visible=0
        )]

    manage_options=(
        ({ 'label'   : 'LanguageConfig',
           'action'  : 'manage_configForm',
           },
         ) + SimpleItem.manage_options
        +  ActionProviderBase.manage_options
        )

    manage_configForm = PageTemplateFile('www/config', globals())

    def __init__(self):
        self.id = 'portal_languages'
        log('init')


    security.declareProtected(ManagePortal, 'manage_setLanguageSettings')
    
    def manage_setLanguageSettings(self, defaultLanguage, fallbackLanguage, supportedLanguages, REQUEST=None):
        ''' stores the languages (default, fallback, supported) '''
        self.default_lang=defaultLanguage
        self.fallback_lang=fallbackLanguage

        if supportedLanguages and type(supportedLanguages) == type([]):
            self.supported_langs=supportedLanguages
        #else:
        #    self.supported_langs=[supportedLanguages]
        # removed this one because it makes for unpredictable behavior
        # added :list to the zmi forms instead so editing always returns a list.
        
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])


    def sortedDictItems(self,dict):
        items = list(dict.items())
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items


    def listSupportedLanguages(self):
        r = []
        for i in self.supported_langs:
            r.append((i,self.available_langs[i]))
        return r

    def getSupportedLanguages(self):
        return self.supported_langs

    def listAvailableLanguages(self):
        return self.sortedDictItems(self.available_langs)
    
    def getAvailableLanguages(self):
        return self.available_langs.keys()

    def getDefaultLanguage(self):
        return self.default_lang

    def setDefaultLanguage(self, langCode):
        self.default_lang = langCode

    def getFallbackLanguage(self):
        return self.fallback_lang

    def setFallbackLanguage(self, langCode):
        self.fallback_lang = langCode

    security.declareProtected(ManagePortal, 'addLanguage')
    def addLanguage(self, langCode, langDescription):
        self.available_langs.append((langCode, langDescription))

    def deleteLanguage(self, langCode):
        # FIXME: to implement
        self.available_langs.remove(langCode)


    # the some methods that should be user-available
    def setPreferredLanguageCookie(preferredlanguage=None):
        if preferredlanguage:
            self.REQUEST.RESPONSE.setCookie('languagePreference',preferredlanguage)

InitializeClass(LanguageTool)
