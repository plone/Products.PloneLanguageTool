# $Id: LanguageTool.py,v 1.50 2004/10/08 17:00:40 longsleep Exp $ (Author: $Author: longsleep $)

import os, re
from types import StringType, UnicodeType
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, package_home
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.Expression import Expression
from Products.CMFCore.CMFCorePermissions  import ManagePortal, ModifyPortalContent, View
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import aq_base
from ZPublisher import BeforeTraverse
from ZPublisher.HTTPRequest import HTTPRequest
from interfaces import ITranslatable

try:
    from Products.PlacelessTranslationService.Negotiator import registerLangPrefsMethod
    _hasPTS = 1
except:
    _hasPTS = None

import availablelanguages

class LanguageTool(UniqueObject, ActionProviderBase, SimpleItem):
    '''
    Language Administration Tool For Plone
    '''

    id  = 'portal_languages'
    title = 'Manages available languages'
    meta_type = 'Plone Language Tool'

    security = ClassSecurityInfo()

    supported_langs = ['en']
    local_available_langs = {}
    local_available_countries = {}
    
    use_path_negotiation = 1
    use_cookie_negotiation = 1
    use_request_negotiation = 1
    use_combined_language_codes = 0
    display_flags = 1


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
        ({ 'label'  : 'LanguageConfig',
           'action' : 'manage_configForm',
           },
         ) + SimpleItem.manage_options
        +  ActionProviderBase.manage_options
        )

    manage_configForm = PageTemplateFile('www/config', globals())

    def __init__(self):
        self.id = 'portal_languages'

        self.use_path_negotiation = 1
        self.use_cookie_negotiation  = 1
        self.use_request_negotiation = 1
        self.force_language_urls = 1
        self.allow_content_language_fallback = 0
        self.display_flags = 1

    def __call__(self, container, req):
        '''
        The __before_publishing_traverse__ hook.
        '''
        if req.__class__ is not HTTPRequest:
            return None
        if not req[ 'REQUEST_METHOD' ] in ( 'HEAD', 'GET', 'PUT', 'POST' ):
            return None
        if req.environ.has_key( 'WEBDAV_SOURCE_PORT' ):
            return None

        # bind the languages
        self.setLanguageBindings()

    security.declareProtected(ManagePortal, 'manage_setLanguageSettings')
    def manage_setLanguageSettings(self, defaultLanguage, supportedLanguages, 
                                   setCookieN=None, setRequestN=None, 
                                   setPathN=None, setForcelanguageUrls=None,
                                   setAllowContentLanguageFallback=None,
                                   setUseCombinedLanguageCodes=None, displayFlags=None, REQUEST=None):
        '''
        stores the tool settings
        '''

        self.setDefaultLanguage(defaultLanguage)

        if supportedLanguages and type(supportedLanguages) == type([]):
            self.supported_langs = supportedLanguages
  
        if setCookieN:
            self.use_cookie_negotiation = 1
        else:
            self.use_cookie_negotiation = 0
            
        if setRequestN:
            self.use_request_negotiation = 1
        else:
            self.use_request_negotiation = 0

        if setPathN:
            self.use_path_negotiation = 1
        else:
            self.use_path_negotiation = 0
            
        if setForcelanguageUrls:
            self.force_language_urls = 1
        else:
            self.force_language_urls = 0
            
        if setAllowContentLanguageFallback:
            self.allow_content_language_fallback = 1
        else:
            self.allow_content_language_fallback = 0

        if setUseCombinedLanguageCodes:
            self.use_combined_language_codes = 1
        else:
            self.use_combined_language_codes = 0

        if displayFlags:
            self.display_flags = 1
        else:
            self.display_flags = 0
            
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declarePublic('showFlags')
    def showFlags(self):
        """ show flags in language listings or not"""
        return self.display_flags

    security.declareProtected(View, 'listSupportedLanguages')
    def listSupportedLanguages(self):
        '''
        return a list of supported language names
        '''
        r = []
        for i in self.supported_langs:
            r.append((i,self.getAvailableLanguages()[i]))
        return r

    security.declareProtected(View, 'getSupportedLanguages')
    def getSupportedLanguages(self):
        '''
        return a list of supported language codes
        '''
        return self.supported_langs

    security.declarePublic('listAvailableLanguages')
    def listAvailableLanguages(self):
        '''
        return sorted list of available languages (code, name)
        '''
        items = list(self.getAvailableLanguages().items())
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        '''
        return dictionary of available languages
        '''
        langs = availablelanguages.languages.copy()
        if self.use_combined_language_codes:
            # add the combined codes in
            langs.update(availablelanguages.combined)
        if self.local_available_langs.keys():
            langs.update(self.local_available_langs)
        return langs

    security.declareProtected(View, 'getDefaultLanguage')
    def getDefaultLanguage(self):
        '''
        return our default language
        '''
        portal_properties = getToolByName(self, 'portal_properties')
        portal=getToolByName(self, 'portal_url').getPortalObject()
        if portal_properties.site_properties.hasProperty('default_language'):
            return portal_properties.site_properties.getProperty('default_language')
        if portal.hasProperty('default_language'):
            return portal.getProperty('default_language')
        return getattr(self, 'default_lang', 'en')

    security.declareProtected(ManagePortal, 'setDefaultLanguage')
    def setDefaultLanguage(self, langCode):
        '''
        set our default language
        '''
        portal_properties=getToolByName(self, 'portal_properties')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        if portal_properties.site_properties.hasProperty('default_language'):
            return portal_properties.site_properties._updateProperty('default_language', langCode)
        if portal.hasProperty('default_language'): 
            return portal._updateProperty('default_language', langCode)
        self.default_lang = langCode
    
    security.declareProtected(ManagePortal, 'addLanguage')
    def addLanguage(self, langCode, langDescription):
        '''
        add a custom language to this tool. This can override predefined ones
        '''
        self.local_available_langs[langCode] = langDescription
        self._p_changed = 1

    security.declareProtected(View, 'getNameForLanguageCode')
    def getNameForLanguageCode(self, langCode):
        '''
        return name for language code
        '''
        return self.getAvailableLanguages().get(langCode, langCode)
    
    # some convenience functions to improve the UI:
    security.declareProtected(ManagePortal, 'addSupportedLanguage')
    def addSupportedLanguage(self, langCode):
        '''
        register code as supported
        '''
        alist = self.supported_langs[:]
        if (langCode in self.getAvailableLanguages().keys()) and not langCode in alist:
            alist.append(langCode) 
            self.supported_langs = alist
            
    security.declareProtected(ManagePortal, 'removeSupportedLanguages')
    def removeSupportedLanguages(self, langCodes):
        '''
        unregister code as supported
        '''
        alist = self.supported_langs[:]
        for i in langCodes:
            alist.remove(i)
        self.supported_langs = alist

    security.declareProtected(View, 'setLanguageCookie')
    def setLanguageCookie(self, lang=None, REQUEST=None, noredir=None):
        '''
        sets a cookie for overriding language negotiation
        '''
        res = None
        portal_url = getToolByName(self, 'portal_url')()
        cur = self.getLanguageCookie()
        if lang and lang in self.getSupportedLanguages():
            if lang != cur: self.REQUEST.RESPONSE.setCookie('I18N_LANGUAGE',lang,path='/')
            res = lang
        if noredir is None:                
            if REQUEST:
                REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
        return res
                
    security.declareProtected(View, 'getLanguageCookie')
    def getLanguageCookie(self):
        '''
        get the preferred cookie language
        '''
        if not hasattr(self, 'REQUEST'): return None
        langCookie = self.REQUEST.cookies.get('I18N_LANGUAGE')
        if langCookie is not None and langCookie in self.getSupportedLanguages():
            return langCookie
        else:
            return None

    security.declareProtected(View, 'getPreferredLanguage')
    def getPreferredLanguage(self):
        '''
        get the preferred site language
        '''
        l = self.getLanguageBindings()
        if l[0]:
            return l[0]
        else:
            return l[1] # this is the default language
       
    def manage_beforeDelete(self, item, container):
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            BeforeTraverse.unregisterBeforeTraverse(container, handle)

    def manage_afterAdd(self, item, container):
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            container = container.this()
            nc = BeforeTraverse.NameCaller(self.getId())
            BeforeTraverse.registerBeforeTraverse(container, nc, handle)

    security.declarePublic('getPathLanguage')
    def getPathLanguage(self):
        '''
        check if a language is part of the current path
        '''
        if not hasattr(self, 'REQUEST'): return []
        items = self.REQUEST.get('TraversalRequestNameStack')
        try:
            for item in items:
                if len(item) == 2:
                    if item in self.getSupportedLanguages():
                        return item
        except: pass
        return None
 
    security.declareProtected(View, 'getRequestLanguages')        
    def getRequestLanguages(self):
        '''
        parse the request and return language list
        '''
        
        if not hasattr(self, 'REQUEST'): return []
        
        # get browser accept languages
        browser_pref_langs = self.REQUEST.get('HTTP_ACCEPT_LANGUAGE', '')
        browser_pref_langs = browser_pref_langs.split(',')
                                                                                
        langs = []
        i = 0
        length = len(browser_pref_langs)
                                                                                
        # parse quality strings and build a tuple
        # like ((float(quality), lang), (float(quality), lang))
        # which is sorted afterwards
        # if no quality string is given then the list order
        # is used as quality indicator
        for lang in browser_pref_langs:
            lang = lang.strip().lower().replace('_','-')
            if lang:
                l = lang.split(';', 2)
                quality = []
                                                                                
                if len(l) == 2:
                    try:
                        q = l[1]
                        if q.startswith('q='):
                            q = q.split('=', 2)[1]
                            quality = float(q)
                    except: pass
                                                                                
                if quality == []:
                    quality = float(length-i)
                                                                                
                language = l[0]
                if language in self.getSupportedLanguages():
                    # if allowed the add language
                    langs.append((quality, language))
                i = i + 1
                                                                                
        # sort and reverse it
        langs.sort()
        langs.reverse()

        # filter quality string
        langs = map(lambda x: x[1], langs)
        
        return langs            

    security.declareProtected(View, 'setLanguageBindings')
    def setLanguageBindings(self):
        # setup the current language stuff  

        usePath = self.use_path_negotiation
        useCookie = self.use_cookie_negotiation
        useRequest = self.use_request_negotiation
        useDefault = 1 # this should never be disabled

        if not hasattr(self, 'REQUEST'): return
        
        binding = self.REQUEST.get('LANGUAGE_TOOL', None)
        if not isinstance(binding, LanguageBinding):
            # create new binding instance
            binding = LanguageBinding(self)
       
        # bind languages
        lang = binding.setLanguageBindings(usePath, useCookie, useRequest, useDefault)
        
        # set LANGUAGE to request
        self.REQUEST['LANGUAGE'] = lang
        
        # set bindings instance to request
        self.REQUEST['LANGUAGE_TOOL'] = binding
        
        return lang

    security.declareProtected(View, 'getLanguageBindings')    
    def getLanguageBindings(self):
        # return the bound languages
        # (language, default_language, languages_list)
       
        if not hasattr(self, 'REQUEST'):
            return (None, self.getDefaultLanguage(), []) # cant do anything
        binding = self.REQUEST.get('LANGUAGE_TOOL', None)
        if not isinstance(binding, LanguageBinding):
            # not bound -> bind
            self.setLanguageBindings()
            binding = self.REQUEST.get('LANGUAGE_TOOL')
            
        return binding.getLanguageBindings()

    security.declarePublic('isTranslatable')
    def isTranslatable(self, obj):
        return ITranslatable.isImplementedBy(obj)

    security.declarePublic('getAvailableCountries')
    def getAvailableCountries(self):
        '''
        return dictionary of available countries
        '''
        countries = availablelanguages.countries.copy()
        if self.local_available_countries.keys():
            countries.update(self.local_available_countries)
        return countries

    security.declarePublic('listAvailableCountries')
    def listAvailableCountries(self):
        '''
        return sorted list of available countries (code, name)
        '''
        items = list(self.getAvailableCountries().items())
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items
        
    security.declareProtected(View, 'getNameForCountryCode')
    def getNameForCountryCode(self, countryCode):
        '''
        return name for country code
        '''
        return self.getAvailableCountries().get(countryCode, countryCode)

    security.declareProtected(ManagePortal, 'addCountry')
    def addCountry(self, countryCode, countryDescription):
        '''
        add a custom country to this tool. This can override predefined ones
        '''
        self.local_available_countries[countryCode] = countryDescription
        self._p_changed = 1


class LanguageBinding:
    '''
    helper which holding language infos in request
    '''
    security = ClassSecurityInfo()
    __allow_access_to_unprotected_subobjects__=1
    
    DEFAULT_LANGUAGE = None
    LANGUAGE = None
    LANGUAGE_LIST = []
    
    def __init__(self, tool):
        self.tool=tool
        
    security.declarePrivate("setLanguageBindings")
    def setLanguageBindings(self, usePath=1, useCookie=1, useRequest=1, useDefault=1):
        # setup the current language stuff
        
        langs = []
        
        if usePath:
            # this one is set if there is an allowed language in the current path        
            langsPath = [self.tool.getPathLanguage()]
        else:langsPath = []
               
        if useCookie:
            # if we are using the cookie stuff we provide the setter here 
            set_language = self.tool.REQUEST.get('set_language', None)
            if set_language:
                langsCookie=[self.tool.setLanguageCookie(set_language),]
            else:
                langsCookie=[self.tool.getLanguageCookie(),] # get from cookie
        else: langsCookie = []
        
        # get langs from request    
        if useRequest:
            langsRequest = self.tool.getRequestLanguages()
        else:
            langsRequest = []
         
        # get default
        if useDefault:
            langsDefault = [self.tool.getDefaultLanguage(),]
        else:
            langsDefault = []
              
        # build list
        langs = langsPath+langsCookie+langsRequest+langsDefault
        
        # filter None languages
        langs = filter(lambda x: x is not None, langs)
        
        self.DEFAULT_LANGUAGE = langs[-1]
        self.LANGUAGE = langs[0]
        self.LANGUAGE_LIST = langs[1:-1]
        
        return self.LANGUAGE
    
    security.declarePublic("getLanguageBindings")
    def getLanguageBindings(self):
        # return bound languages
        # (language, default_language, languages_list)
        
        return (self.LANGUAGE, self.DEFAULT_LANGUAGE, self.LANGUAGE_LIST)
        

class PrefsForPTS:
    '''
    this one should hook into pts
    '''
    def __init__(self, context):
        self._env = context
        self.languages = []

        binding = context.get('LANGUAGE_TOOL')
        if not isinstance(binding, LanguageBinding):
            return None

        self.pref = binding.getLanguageBindings()
        self.languages = [self.pref[0],] + self.pref[2] + [self.pref[1],]

        return None
 
    def getPreferredLanguages(self):
        '''
        return the list of the bound langs
        '''
        try:
            return self.languages
        except:
            return []
    
if _hasPTS is not None:
    registerLangPrefsMethod({'klass':PrefsForPTS, 'priority':100 })

    
InitializeClass(LanguageTool)
