from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.Expression import Expression
from zope.interface import implements
# BBB CMF < 1.5
try:
    from Products.CMFCore.permissions import ManagePortal
    from Products.CMFCore.permissions import View
except ImportError:
    from Products.CMFCore.CMFCorePermissions import ManagePortal
    from Products.CMFCore.CMFCorePermissions import View

from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher import BeforeTraverse
from ZPublisher.HTTPRequest import HTTPRequest
from Products.PloneLanguageTool.tldmap import tld_to_language
from Products.PloneLanguageTool.interfaces import ILanguageTool

try:
    from Products.CMFPlone.interfaces.Translatable import ITranslatable
except ImportError:
    from interfaces import ITranslatable

try:
    from Products.PlacelessTranslationService.Negotiator import registerLangPrefsMethod
    _hasPTS = 1
except ImportError:
    _hasPTS = 0

import logging
logger = logging.getLogger('PloneLanguageTool')

import availablelanguages


class LanguageTool(UniqueObject, ActionProviderBase, SimpleItem):
    """Language Administration Tool For Plone."""

    implements(ILanguageTool)

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
    use_cctld_negotiation = 0
    use_combined_language_codes = 0
    display_flags = 1
    start_neutral = 1

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
        self.use_cctld_negotiation = 0
        self.force_language_urls = 1
        self.allow_content_language_fallback = 0
        self.display_flags = 1
        self.start_neutral = 1

    def __call__(self, container, req):
        """The __before_publishing_traverse__ hook."""
        if req.__class__ is not HTTPRequest:
            return None
        if not req['REQUEST_METHOD'] in ('HEAD', 'GET', 'PUT', 'POST'):
            return None
        if req.environ.has_key('WEBDAV_SOURCE_PORT'):
            return None
        # Bind the languages
        self.setLanguageBindings()

    security.declareProtected(ManagePortal, 'manage_setLanguageSettings')
    def manage_setLanguageSettings(self, defaultLanguage, supportedLanguages,
                                   setCookieN=None, setRequestN=None,
                                   setPathN=None, setForcelanguageUrls=None,
                                   setAllowContentLanguageFallback=None,
                                   setUseCombinedLanguageCodes=None,
                                   displayFlags=None, startNeutral=None,
                                   setCcTLDN=None,
                                   REQUEST=None):
        """Stores the tool settings."""
        if supportedLanguages and type(supportedLanguages) == type([]):
            self.supported_langs = supportedLanguages

        if defaultLanguage in self.supported_langs:
            self.setDefaultLanguage(defaultLanguage)
        else:
            self.setDefaultLanguage(self.supported_langs[0])

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

        if setCcTLDN:
            self.use_cctld_negotiation = 1
        else:
            self.use_cctld_negotiation = 0

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

        if startNeutral:
            self.start_neutral = 1
        else:
            self.start_neutral = 0

        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declarePublic('startNeutral')
    def startNeutral(self):
        """Checks if the content start as language neutral or using the
        preferred language.
        """
        return self.start_neutral

    security.declarePublic('showFlags')
    def showFlags(self):
        """Shows the flags in language listings or not."""
        return self.display_flags

    security.declareProtected(View, 'listSupportedLanguages')
    def listSupportedLanguages(self):
        """Returns a list of supported language names."""
        r = []
        for i in self.supported_langs:
            r.append((i,self.getAvailableLanguages()[i]))
        return r

    security.declareProtected(View, 'getSupportedLanguages')
    def getSupportedLanguages(self):
        """Returns a list of supported language codes."""
        return self.supported_langs

    security.declarePublic('listAvailableLanguages')
    def listAvailableLanguages(self):
        """Returns sorted list of available languages (code, name)."""
        items = list(self.getAvailableLanguages().items())
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        """Returns the dictionary of available languages.
        The dict should have the form: {code : {native, english, flag}}.
        """
        langs = availablelanguages.getNativeLanguageNames()
        if self.use_combined_language_codes:
            langs.update(availablelanguages.getCombinedLanguageNames())
        if self.local_available_langs.keys():
            langs.update(self.local_available_langs)
        return langs

    security.declarePublic('listAvailableLanguageInformation')
    def listAvailableLanguageInformation(self):
        """Returns list of available languages."""
        langs = self.getAvailableLanguageInformation()
        new_langs = []
        for lang in langs:
            # add language-code to dict
            langs[lang]['code'] = lang
            # flatten outer dict to list to make it sortable
            new_langs.append(langs[lang])
        new_langs.sort(lambda x, y: cmp(x.get('native', x.get('english')), y.get('native', y.get('english'))))
        return new_langs

    security.declarePublic('getAvailableLanguageInformation')
    def getAvailableLanguageInformation(self):
        """Returns the dictionary of available languages."""
        langs = availablelanguages.getLanguages()
        if self.use_combined_language_codes:
            langs.update(availablelanguages.getCombined())
        if self.local_available_langs.keys():
            langs.update(self.local_available_langs)
        for lang in langs:
            if lang in self.supported_langs:
                langs[lang]['selected'] = True
            else:
                langs[lang]['selected'] = False
        return langs

    security.declareProtected(View, 'getDefaultLanguage')
    def getDefaultLanguage(self):
        """Returns the default language."""
        portal_properties = getToolByName(self, 'portal_properties')
        site_properties = portal_properties.site_properties
        if site_properties.hasProperty('default_language'):
            return site_properties.getProperty('default_language')
        portal = getToolByName(self, 'portal_url').getPortalObject()
        if portal.hasProperty('default_language'):
            return portal.getProperty('default_language')
        return getattr(self, 'default_lang', 'en')

    security.declareProtected(ManagePortal, 'setDefaultLanguage')
    def setDefaultLanguage(self, langCode):
        """Sets the default language."""
        portal_properties = getToolByName(self, 'portal_properties')
        site_properties = portal_properties.site_properties
        if site_properties.hasProperty('default_language'):
            return site_properties._updateProperty('default_language', langCode)
        portal = getToolByName(self, 'portal_url').getPortalObject()
        if portal.hasProperty('default_language'):
            return portal._updateProperty('default_language', langCode)
        self.default_lang = langCode

    security.declareProtected(ManagePortal, 'addLanguage')
    def addLanguage(self, langCode, langDescription):
        """Adds a custom language to the tool.

        This can override predefined ones.
        """
        logger.log(logging.WARNING, 'Deprecation Warning: The addLanguage '
            'method is deprecated and will be removed in PLT 2.0.')
        self.local_available_langs[langCode] = langDescription
        self._p_changed = 1

    security.declareProtected(ManagePortal, 'removeLanguage')
    def removeLanguage(self, langCode):
        """Removes a custom language from the tool."""
        logger.log(logging.WARNING, 'Deprecation Warning: The removeLanguage '
            'method is deprecated and will be removed in PLT 2.0.')
        if langCode in self.local_available_langs:
            del self.local_available_langs[langCode]
            self._p_changed = 1

    security.declareProtected(View, 'getNameForLanguageCode')
    def getNameForLanguageCode(self, langCode):
        """Returns the name for a language code."""
        return self.getAvailableLanguages().get(langCode, langCode)

    security.declareProtected(View, 'getFlagForLanguageCode')
    def getFlagForLanguageCode(self, langCode):
        """Returns the name of the flag for a language code."""
        info = self.getAvailableLanguageInformation().get(langCode, None)
        if info is not None:
            return info.get('flag', None)
        return None

    security.declareProtected(ManagePortal, 'addSupportedLanguage')
    def addSupportedLanguage(self, langCode):
        """Registers a language code as supported."""
        alist = self.supported_langs[:]
        if (langCode in self.getAvailableLanguages().keys()) and not langCode in alist:
            alist.append(langCode)
            self.supported_langs = alist

    security.declareProtected(ManagePortal, 'removeSupportedLanguages')
    def removeSupportedLanguages(self, langCodes):
        """Unregisters language codes from supported."""
        alist = self.supported_langs[:]
        for i in langCodes:
            alist.remove(i)
        self.supported_langs = alist

    security.declareProtected(View, 'setLanguageCookie')
    def setLanguageCookie(self, lang=None, REQUEST=None, noredir=None):
        """Sets a cookie for overriding language negotiation."""
        res = None
        if lang and lang in self.getSupportedLanguages():
            if lang != self.getLanguageCookie():
                self.REQUEST.RESPONSE.setCookie('I18N_LANGUAGE', lang, path='/')
            res = lang
        if noredir is None:
            if REQUEST:
                REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
        return res

    security.declareProtected(View, 'getLanguageCookie')
    def getLanguageCookie(self):
        """Gets the preferred cookie language."""
        if not hasattr(self, 'REQUEST'):
            return None
        langCookie = self.REQUEST.cookies.get('I18N_LANGUAGE')
        if langCookie in self.getSupportedLanguages():
            return langCookie
        return None

    security.declareProtected(View, 'getPreferredLanguage')
    def getPreferredLanguage(self):
        """Gets the preferred site language."""
        l = self.getLanguageBindings()
        if l[0]:
            if not self.use_combined_language_codes:
                return l[0].split('-')[0]
            else:
                return l[0]
            return l[0]
        # this is the default language
        return l[1]

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
        """Checks if a language is part of the current path."""
        if not hasattr(self, 'REQUEST'):
            return []
        items = self.REQUEST.get('TraversalRequestNameStack')
        # XXX Why this try/except?
        try:
            for item in items:
                if item in self.getSupportedLanguages():
                    return item
        except:
            pass
        return None

    security.declareProtected(View, 'getCcTLDLanguages')
    def getCcTLDLanguages(self):
        if not hasattr(self, 'REQUEST'):
            return None
        request = self.REQUEST
        if not "HTTP_HOST" in request:
            return None
        host=request["HTTP_HOST"].split(":")[0].lower()
        tld=host.split(".")[-1]
        wanted = tld_to_language.get(tld, [])
        allowed = self.getSupportedLanguages()
        return [lang for lang in wanted if lang in allowed]

    security.declareProtected(View, 'getRequestLanguages')
    def getRequestLanguages(self):
        """Parses the request and return language list."""

        if not hasattr(self, 'REQUEST'):
            return None

        # Get browser accept languages
        browser_pref_langs = self.REQUEST.get('HTTP_ACCEPT_LANGUAGE', '')
        browser_pref_langs = browser_pref_langs.split(',')

        i = 0
        langs = []
        length = len(browser_pref_langs)

        # Parse quality strings and build a tuple like
        # ((float(quality), lang), (float(quality), lang))
        # which is sorted afterwards
        # If no quality string is given then the list order
        # is used as quality indicator
        for lang in browser_pref_langs:
            lang = lang.strip().lower().replace('_', '-')
            if lang:
                l = lang.split(';', 2)
                quality = []

                if len(l) == 2:
                    try:
                        q = l[1]
                        if q.startswith('q='):
                            q = q.split('=', 2)[1]
                            quality = float(q)
                    except:
                        pass

                if quality == []:
                    quality = float(length-i)

                language = l[0]
                if self.use_combined_language_codes:
                    if language in self.getSupportedLanguages():
                        # If allowed the add language
                        langs.append((quality, language))
                else:
                    # if we only use simply language codes, we should recognize
                    # combined codes as their base code. So 'de-de' is treated
                    # as 'de'.
                    baselanguage = language.split('-')[0]
                    if baselanguage in self.getSupportedLanguages():
                        langs.append((quality, baselanguage))
                i = i + 1

        # Sort and reverse it
        langs.sort()
        langs.reverse()

        # Filter quality string
        langs = map(lambda x: x[1], langs)

        return langs

    security.declareProtected(View, 'setLanguageBindings')
    def setLanguageBindings(self):
        """Setups the current language stuff."""
        useCcTLD = self.use_cctld_negotiation
        usePath = self.use_path_negotiation
        useCookie = self.use_cookie_negotiation
        useRequest = self.use_request_negotiation
        useDefault = 1 # This should never be disabled
        if not hasattr(self, 'REQUEST'):
            return
        binding = self.REQUEST.get('LANGUAGE_TOOL', None)
        if not isinstance(binding, LanguageBinding):
            # Create new binding instance
            binding = LanguageBinding(self)
        # Bind languages
        lang = binding.setLanguageBindings(usePath, useCookie, useRequest, useDefault, useCcTLD)
        # Set LANGUAGE to request
        self.REQUEST['LANGUAGE'] = lang
        # Set bindings instance to request
        self.REQUEST['LANGUAGE_TOOL'] = binding
        return lang

    security.declareProtected(View, 'getLanguageBindings')
    def getLanguageBindings(self):
        """Returns the bound languages.

        (language, default_language, languages_list)
        """
        if not hasattr(self, 'REQUEST'):
            # Can't do anything
            return (None, self.getDefaultLanguage(), [])
        binding = self.REQUEST.get('LANGUAGE_TOOL', None)
        if not isinstance(binding, LanguageBinding):
            # Not bound -> bind
            self.setLanguageBindings()
            binding = self.REQUEST.get('LANGUAGE_TOOL')
        return binding.getLanguageBindings()

    security.declarePublic('isTranslatable')
    def isTranslatable(self, obj):
        """Checks if ITranslatable interface is implemented."""
        return ITranslatable.isImplementedBy(obj)

    security.declarePublic('getAvailableCountries')
    def getAvailableCountries(self):
        """Returns the dictionary of available countries."""
        countries = availablelanguages.countries.copy()
        if self.local_available_countries.keys():
            countries.update(self.local_available_countries)
        return countries

    security.declarePublic('listAvailableCountries')
    def listAvailableCountries(self):
        """Returns the sorted list of available countries (code, name)."""
        items = list(self.getAvailableCountries().items())
        items.sort(lambda x, y: cmp(x[1], y[1]))
        return items

    security.declareProtected(View, 'getNameForCountryCode')
    def getNameForCountryCode(self, countryCode):
        """Returns the name for a country code."""
        return self.getAvailableCountries().get(countryCode, countryCode)

    security.declareProtected(ManagePortal, 'addCountry')
    def addCountry(self, countryCode, countryDescription):
        """Adds a custom country to the tool.

        This can override predefined ones.
        """
        logger.log(logging.WARNING, 'Deprecation Warning: The addCountry '
            'method is deprecated and will be removed in PLT 2.0.')
        self.local_available_countries[countryCode] = countryDescription
        self._p_changed = 1

    security.declareProtected(ManagePortal, 'removeCountry')
    def removeCountry(self, countryCode):
        """Removes a custom country from the tool."""
        logger.log(logging.WARNING, 'Deprecation Warning: The removeCountry '
            'method is deprecated and will be removed in PLT 2.0.')
        if countryCode in self.local_available_countries:
            del self.local_available_countries[countryCode]
            self._p_changed = 1


class LanguageBinding:
    """Helper which holding language infos in request."""
    security = ClassSecurityInfo()
    __allow_access_to_unprotected_subobjects__ = 1

    DEFAULT_LANGUAGE = None
    LANGUAGE = None
    LANGUAGE_LIST = []

    def __init__(self, tool):
        self.tool = tool

    security.declarePrivate('setLanguageBindings')
    def setLanguageBindings(self, usePath=1, useCookie=1, useRequest=1, useDefault=1, useCcTLD=0):
        """Setup the current language stuff."""
        langs = []

        if usePath:
            # This one is set if there is an allowed language in the current path
            langsPath = [self.tool.getPathLanguage()]
        else:
            langsPath = []

        if useCookie:
            # If we are using the cookie stuff we provide the setter here
            set_language = self.tool.REQUEST.get('set_language', None)
            if set_language:
                langsCookie = [self.tool.setLanguageCookie(set_language)]
            else:
                # Get from cookie
                langsCookie = [self.tool.getLanguageCookie()]
        else:
            langsCookie = []

        if useCcTLD:
            langsCcTLD = self.tool.getCcTLDLanguages()
        else:
            langsCcTLD = []

        # Get langs from request
        if useRequest:
            langsRequest = self.tool.getRequestLanguages()
        else:
            langsRequest = []

        # Get default
        if useDefault:
            langsDefault = [self.tool.getDefaultLanguage()]
        else:
            langsDefault = []

        # Build list
        langs = langsPath+langsCookie+langsCcTLD+langsRequest+langsDefault

        # Filter None languages
        langs = [lang for lang in langs if lang is not None]

        self.DEFAULT_LANGUAGE = langs[-1]
        self.LANGUAGE = langs[0]
        self.LANGUAGE_LIST = langs[1:-1]

        return self.LANGUAGE

    security.declarePublic('getLanguageBindings')
    def getLanguageBindings(self):
        """Returns the bound languages.

        (language, default_language, languages_list)
        """
        return (self.LANGUAGE, self.DEFAULT_LANGUAGE, self.LANGUAGE_LIST)


class PrefsForPTS:
    """A preference to hook into PTS."""
    def __init__(self, context):
        self._env = context
        self.languages = []
        binding = context.get('LANGUAGE_TOOL')
        if not isinstance(binding, LanguageBinding):
            return None
        self.pref = binding.getLanguageBindings()
        self.languages = [self.pref[0]] + self.pref[2] + [self.pref[1]]
        return None

    def getPreferredLanguages(self):
        """Returns the list of the bound languages."""
        return self.languages


if _hasPTS:
    registerLangPrefsMethod({'klass':PrefsForPTS, 'priority':100 })

InitializeClass(LanguageTool)
