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

    AVAILABLE_LANGUAGES = availablelanguages.languages
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
            r.append((i,self.AVAILABLE_LANGUAGES[i]))
        return r

    def getSupportedLanguages(self):
        return self.supported_langs

    def listAvailableLanguages(self):
        return self.sortedDictItems(self.AVAILABLE_LANGUAGES)
    
    def getAvailableLanguages(self):
        return self.available_langs.keys()

    def getDefaultLanguage(self):
        return self.default_lang

    security.declareProtected(ManagePortal, 'setDefaultLanguage')
    def setDefaultLanguage(self, langCode):
        self.default_lang = langCode

    def getFallbackLanguage(self):
        return self.fallback_lang
    
    security.declareProtected(ManagePortal, 'setFallbackLanguage')
    def setFallbackLanguage(self, langCode):
        self.fallback_lang = langCode
    
    security.declareProtected(ManagePortal, 'addLanguage')
    def addLanguage(self, langCode, langDescription):
        self.AVAILABLE_LANGUAGES.append((langCode, langDescription))

    def deleteLanguage(self, langCode):
        # FIXME: to implement
        self.AVAILABLE_LANGUAGES.remove(langCode)

    # some convenience functions to improve the UI:
    security.declareProtected(ManagePortal, 'addSupportedLanguage')
    def addSupportedLanguage(self, langCode):
        if (langCode in self.AVAILABLE_LANGUAGES.keys()) and not langCode in self.supported_langs:
            self.supported_langs.append(langCode)
            
    security.declareProtected(ManagePortal, 'removeSupportedLanguages')
    def removeSupportedLanguages(self, langCodes):
        for i in LangCodes:
            self.supported_langs.remove(i)

    # some methods that should be user-available
    security.declareProtected(View, 'setPreferredLanguageCookie')
    def setPreferredLanguageCookie(self,lang=None, REQUEST=None,noredir=None):
        ''' sets a cookie for overriding language negotiation '''
        if lang:
            if lang in self.supported_langs:  
                portal_url = getToolByName(self, 'portal_url')()
                self.REQUEST.RESPONSE.setCookie('I18N_CONTENT_LANGUAGE',lang,path='/')

                # set session language as well. this is a hack before we talk well with PTS
                sdm = getattr(self, 'session_data_manager', None)
                if sdm:
                    sd=sdm.getSessionData(create=1)
                    sd.set('preferred_languages', lang)

        if noredir is None:                
            if REQUEST:
                REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
                
    security.declareProtected(View, 'getPreferredLanguage')
    def getPreferredLanguage(self):
        ''' calculate the preferred language for a user'''
        #should take HTTP_ACCEPT_LANGUAGE into consideration, but for now , we just use the cookie or the fallback,
        pref = self.fallback_lang or 'en'
        if self.REQUEST is not None:
            langCookie = self.REQUEST.cookies.get('I18N_CONTENT_LANGUAGE')
            if langCookie in self.supported_langs:
                pref = langCookie
        return pref
            


InitializeClass(LanguageTool)
