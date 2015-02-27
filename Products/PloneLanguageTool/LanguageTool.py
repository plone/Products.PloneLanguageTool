from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.interfaces import IDublinCore
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import registerToolInterface
from Products.CMFPlone.interfaces import ILanguageSchema
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PloneLanguageTool.interfaces import ILanguageTool
from Products.PloneLanguageTool.interfaces import INegotiateLanguage
from Products.PloneLanguageTool.interfaces import ITranslatable
from Products.SiteAccess.VirtualHostMonster import VirtualHostMonster
from ZODB.POSException import ConflictError
from ZPublisher import BeforeTraverse
from ZPublisher.HTTPRequest import HTTPRequest
from plone.i18n.locales.interfaces import ICcTLDInformation
from plone.i18n.locales.interfaces import IContentLanguageAvailability
from plone.i18n.locales.interfaces import ICountryAvailability
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.deprecation import deprecate
from zope.interface import implements

# BBB Zope before 2.12
try:
    from App.class_init import InitializeClass
except ImportError:
    from Globals import InitializeClass


try:
    from Products.PlacelessTranslationService.Negotiator import registerLangPrefsMethod
    _hasPTS = 1
except ImportError:
    _hasPTS = 0

class LanguageTool(UniqueObject, SimpleItem):
    """Language Administration Tool For Plone."""

    id  = 'portal_languages'
    title = 'Manages available languages'
    meta_type = 'Plone Language Tool'

    implements(ILanguageTool)

    security = ClassSecurityInfo()

    # Used by functional tests.
    always_show_selector = 0

    # resources that must not use language specific URLs
    exclude_paths = frozenset((
                     'portal_css',
                     'portal_javascripts',
                     'portal_kss',
                     'portal_factory'
                 ))
    exclude_exts = frozenset((
         'css',
         'js',
         'kss',
         'xml',
         'gif',
         'jpg',
         'png',
         'jpeg',
     ))

    manage_options=(
        ({ 'label'  : 'LanguageConfig',
           'action' : 'manage_configForm',
           },
         ) + SimpleItem.manage_options
        )

    manage_configForm = PageTemplateFile('www/config', globals())

    def __init__(self):
        # These apply to new instances
        self.id = 'portal_languages'
        # these can be removed, after finished refactoring
        self.supported_langs = ['en']
        self.use_content_negotiation = 0
        self.use_path_negotiation = 0
        self.use_cookie_negotiation = 1
        self.set_cookie_everywhere = 0
        self.authenticated_users_only = 0
        self.use_request_negotiation = 0
        self.use_cctld_negotiation = 0
        self.use_subdomain_negotiation = 0
        self.use_combined_language_codes = 0
        self.force_language_urls = 0
        self.allow_content_language_fallback = 0
        self.display_flags = 0
        self.start_neutral = 0

    def __call__(self, container, req):
        """The __before_publishing_traverse__ hook."""
        # Virtual hosting with the portal as the root causes traversal hooks
        # to be called twice.
        if req.other.has_key('LANGUAGE_TOOL'):
            return None
        if req.__class__ is not HTTPRequest:
            return None
        if not req['REQUEST_METHOD'] in ('HEAD', 'GET', 'PUT', 'POST'):
            return None
        if req.environ.has_key('WEBDAV_SOURCE_PORT'):
            return None
        # Bind the languages
        self.setLanguageBindings()

    security.declareProtected(ManagePortal, 'manage_setLanguageSettings')

    @property
    def settings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(ILanguageSchema, prefix="plone")

    def manage_setLanguageSettings(self, defaultLanguage, supportedLanguages,
                                   setContentN=None,
                                   setCookieN=None, setCookieEverywhere=None,
                                   setRequestN=None,
                                   setPathN=None, setForcelanguageUrls=None,
                                   setAllowContentLanguageFallback=None,
                                   setUseCombinedLanguageCodes=None,
                                   displayFlags=None,
                                   setCcTLDN=None, setSubdomainN=None,
                                   setAuthOnlyN=None, startNeutral=None,
                                   REQUEST=None):
        """Stores the tool settings."""
        if supportedLanguages and type(supportedLanguages) == type([]):
            self.settings.available_languages = supportedLanguages

        if defaultLanguage in self.settings.available_languages:
            self.setDefaultLanguage(defaultLanguage)
        else:
            self.setDefaultLanguage(self.settings.available_languages[0])

        self.settings.use_content_negotiation = bool(setContentN)
        self.settings.use_cookie_negotiation = bool(setCookieN)
        self.settings.set_cookie_always = bool(setCookieEverywhere)
        self.settings.authenticated_users_only = bool(setAuthOnlyN)
        self.settings.use_request_negotiation = bool(setRequestN)
        self.settings.use_path_negotiation = bool(setPathN)
        self.settings.use_cctld_negotiation = bool(setCcTLDN)
        self.settings.use_subdomain_negotiation = bool(setSubdomainN)
        self.settings.use_combined_language_codes = bool(
            setUseCombinedLanguageCodes)
        self.settings.display_flags = bool(displayFlags)

        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    security.declarePublic('showFlags')
    def showFlags(self):
        """Shows the flags in language listings or not."""
        return self.settings.display_flags

    security.declareProtected(View, 'getSupportedLanguages')
    def getSupportedLanguages(self):
        """Returns a list of supported language codes."""
        return self.settings.available_languages

    security.declareProtected(View, 'listSupportedLanguages')
    def listSupportedLanguages(self):
        """Returns a list of supported language names."""
        r = []
        available = self.getAvailableLanguages()
        for i in self.settings.available_languages:
            if available.get(i):
                r.append((i,available[i][u'name']))
        return r

    security.declarePublic('getAvailableLanguages')
    def getAvailableLanguages(self):
        """Returns the dictionary of available languages.
        """
        util = queryUtility(IContentLanguageAvailability)
        if self.settings.use_combined_language_codes:
            languages = util.getLanguages(combined=True)
        else:
            languages = util.getLanguages()
        return languages

    security.declarePublic('getCcTLDInformation')
    def getCcTLDInformation(self):
        util = queryUtility(ICcTLDInformation)
        return util.getTLDs()

    security.declarePublic('listAvailableLanguages')
    def listAvailableLanguages(self):
        """Returns sorted list of available languages (code, name)."""
        util = queryUtility(IContentLanguageAvailability)
        if self.settings.use_combined_language_codes:
            languages = util.getLanguageListing(combined=True)
        else:
            languages = util.getLanguageListing()
        languages.sort(lambda x, y: cmp(x[1], y[1]))
        return languages

    security.declarePublic('listAvailableLanguageInformation')
    def listAvailableLanguageInformation(self):
        """Returns list of available languages."""
        langs = self.getAvailableLanguageInformation()
        new_langs = []
        for lang in langs:
            # add language-code to dict
            langs[lang][u'code'] = lang
            # flatten outer dict to list to make it sortable
            new_langs.append(langs[lang])
        new_langs.sort(lambda x, y: cmp(
            x.get(u'native', x.get(u'name')),
            y.get(u'native', y.get(u'name'))))
        return new_langs

    security.declarePublic('getAvailableLanguageInformation')
    def getAvailableLanguageInformation(self):
        """Returns the dictionary of available languages."""
        util = queryUtility(IContentLanguageAvailability)
        if self.settings.use_combined_language_codes:
            languages = util.getLanguages(combined=True)
        else:
            languages = util.getLanguages()

        for lang in languages:
            languages[lang]['code'] = lang
            if lang in self.settings.available_languages:
                languages[lang]['selected'] = True
            else:
                languages[lang]['selected'] = False
        return languages

    security.declareProtected(View, 'getDefaultLanguage')
    def getDefaultLanguage(self):
        """Returns the default language."""
        registry = queryUtility(IRegistry)
        if not registry:
            return 'en'
        language_settings = registry.forInterface(
            ILanguageSchema,
            prefix='plone'
        )
        return language_settings.default_language

    security.declareProtected(ManagePortal, 'setDefaultLanguage')
    def setDefaultLanguage(self, langCode):
        """Sets the default language."""
        registry = queryUtility(IRegistry)
        if not registry:
            return
        language_settings = registry.forInterface(
            ILanguageSchema,
            prefix='plone'
        )
        language_settings.default_language = langCode

    security.declareProtected(View, 'getNameForLanguageCode')
    def getNameForLanguageCode(self, langCode):
        """Returns the name for a language code."""
        info = self.getAvailableLanguageInformation().get(langCode, None)
        if info is not None:
            return info.get(u'name', None)
        return None

    security.declareProtected(View, 'getFlagForLanguageCode')
    def getFlagForLanguageCode(self, langCode):
        """Returns the name of the flag for a language code."""
        info = self.getAvailableLanguageInformation().get(langCode, None)
        if info is not None:
            return info.get(u'flag', None)
        return None

    security.declareProtected(ManagePortal, 'addSupportedLanguage')
    def addSupportedLanguage(self, langCode):
        """Registers a language code as supported."""
        alist = self.settings.available_languages[:]
        if (langCode in self.getAvailableLanguages().keys()) \
                and langCode not in alist:
            alist.append(langCode)
            self.settings.available_languages = alist

    security.declareProtected(ManagePortal, 'removeSupportedLanguages')
    def removeSupportedLanguages(self, langCodes):
        """Unregisters language codes from supported."""
        alist = self.settings.available_languages[:]
        for i in langCodes:
            alist.remove(i)
        self.settings.available_languages = alist

    security.declareProtected(View, 'setLanguageCookie')
    def setLanguageCookie(self, lang=None, REQUEST=None, noredir=None):
        """Sets a cookie for overriding language negotiation."""
        res = None
        if lang and lang in self.getSupportedLanguages():
            if lang != self.getLanguageCookie():
                self.REQUEST.RESPONSE.setCookie(
                    'I18N_LANGUAGE', lang, path='/')
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
            if not self.settings.use_combined_language_codes:
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

    security.declareProtected(View, 'getPathLanguage')
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
        except (ConflictError, KeyboardInterrupt):
            raise
        except:
            pass
        return None

    security.declarePublic('getContentLanguage')
    def getContentLanguage(self):
        """Checks the language of the current content if not folderish."""
        if not hasattr(self, 'REQUEST'):
            return []
        try:  # This will actually work nicely with browserdefault
            # as we get attribute error...
            contentpath = self.REQUEST.path[:]

            # Now check if we need to exclude from using language specific path
            # See https://dev.plone.org/ticket/11263
            if (
                bool([1 for p in self.exclude_paths if p in contentpath]) or
                bool([1 for p in self.exclude_exts
                      if contentpath[0].endswith(p)])
                    ):
                return None

            obj = self.aq_parent
            traversed = []
            while contentpath:
                name = contentpath.pop()
                if name[0] in '@+':
                    break
                next = obj.unrestrictedTraverse(name, None)
                if next is None:
                    break
                if isinstance(next, VirtualHostMonster):
                    # next element is the VH subpath
                    contentpath.pop()
                    continue
                obj = next
                traversed.append(obj)
            for obj in reversed(traversed):
                if IDublinCore.providedBy(obj):
                    lang = obj.Language()
                    if not lang:
                        continue
                    if lang in self.getSupportedLanguages():
                        return lang
                    else:
                        return None
        except ConflictError:
            raise
        except:
            pass
        return None

    security.declareProtected(View, 'getCcTLDLanguages')
    def getCcTLDLanguages(self):
        if not hasattr(self, 'REQUEST'):
            return None
        request = self.REQUEST
        if "HTTP_HOST" not in request:
            return None
        host=request["HTTP_HOST"].split(":")[0].lower()
        tld=host.split(".")[-1]
        wanted = self.getCcTLDInformation().get(tld, [])
        allowed = self.getSupportedLanguages()
        return [lang for lang in wanted if lang in allowed]

    security.declareProtected(View, 'getSubdomainLanguages')
    def getSubdomainLanguages(self):
        if not hasattr(self, 'REQUEST'):
            return None
        request = self.REQUEST
        if "HTTP_HOST" not in request:
            return None
        host=request["HTTP_HOST"].split(":")[0].lower()
        tld=host.split(".")[0]
        wanted = self.getCcTLDInformation().get(tld, [])
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
                if (self.settings.use_combined_language_codes and
                        language in self.getSupportedLanguages()):
                    # If allowed add the language
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
        if not hasattr(self, 'REQUEST'):
            return
        settings = getMultiAdapter(
            (getSite(), self.REQUEST), INegotiateLanguage)
        binding = self.REQUEST.get('LANGUAGE_TOOL', None)
        if not isinstance(binding, LanguageBinding):
            # Create new binding instance
            binding = LanguageBinding(self)
            # Set bindings instance to request here to avoid infinite recursion
            self.REQUEST['LANGUAGE_TOOL'] = binding
        # Bind languages
        binding.LANGUAGE = lang = settings.language
        binding.DEFAULT_LANGUAGE = settings.default_language
        binding.LANGUAGE_LIST = list(settings.language_list)
        # Set LANGUAGE to request
        self.REQUEST['LANGUAGE'] = lang
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
    @deprecate("The isTranslatable method of the language tool is deprecated "
               "and will be removed in Plone 4. Check for the ITranslatable "
               "interface instead.")
    def isTranslatable(self, obj):
        """Checks if ITranslatable interface is implemented."""
        try:
            if obj.checkCreationFlag():
                return False
        except NameError:
            pass
        return ITranslatable.isProvidedBy(obj)

    security.declarePublic('getAvailableCountries')
    def getAvailableCountries(self):
        """Returns the dictionary of available countries."""
        util = queryUtility(ICountryAvailability)
        return util.getCountries()

    security.declarePublic('listAvailableCountries')
    def listAvailableCountries(self):
        """Returns the sorted list of available countries (code, name)."""
        util = queryUtility(ICountryAvailability)
        countries = util.getCountryListing()
        countries.sort(lambda x, y: cmp(x[1], y[1]))
        return countries

    security.declareProtected(View, 'getNameForCountryCode')
    def getNameForCountryCode(self, countryCode):
        """Returns the name for a country code."""
        return self.getAvailableCountries().get(countryCode, countryCode)

    security.declarePrivate('isAnonymousUser')
    def isAnonymousUser(self):
        from AccessControl import getSecurityManager
        user = getSecurityManager().getUser()
        return not user.has_role('Authenticated')

    security.declarePublic('showSelector')
    def showSelector(self):
        """Returns True if the selector viewlet should be shown."""
        if self.settings.display_flags:
            return True
        if (self.settings.use_cookie_negotiation and
            not (self.settings.authenticated_users_only and self.isAnonymousUser())):
            return True
        return False


class LanguageBinding:
    """Helper which holding language infos in request."""
    security = ClassSecurityInfo()
    __allow_access_to_unprotected_subobjects__ = 1

    DEFAULT_LANGUAGE = None
    LANGUAGE = None
    LANGUAGE_LIST = []

    def __init__(self, tool):
        self.tool = tool

    security.declarePublic('getLanguageBindings')
    def getLanguageBindings(self):
        """Returns the bound languages.

        (language, default_language, languages_list)
        """
        return (self.LANGUAGE, self.DEFAULT_LANGUAGE, self.LANGUAGE_LIST)


class NegotiateLanguage(object):
    """Perform default language negotiation"""
    implements(INegotiateLanguage)

    def __init__(self, site, request):
        """Setup the current language stuff."""
        tool = getToolByName(site, 'portal_languages')
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix="plone")
        langs = []
        useContent = settings.use_content_negotiation
        useCcTLD = settings.use_cctld_negotiation
        useSubdomain = settings.use_subdomain_negotiation
        usePath = settings.use_path_negotiation
        useCookie = settings.use_cookie_negotiation
        setCookieAlways = settings.set_cookie_always
        authOnly = settings.authenticated_users_only
        useRequest = settings.use_request_negotiation
        useDefault = 1  # This should never be disabled
        langsCookie = None

        if usePath:
            # This one is set if there is an allowed language in the current path
            langs.append(tool.getPathLanguage())

        if useContent:
            langs.append(tool.getContentLanguage())
        if useCookie and not (authOnly and tool.isAnonymousUser()):
            # If we are using the cookie stuff we provide the setter here
            set_language = tool.REQUEST.get('set_language', None)
            if set_language:
                langsCookie = tool.setLanguageCookie(set_language)
            else:
                # Get from cookie
                langsCookie = tool.getLanguageCookie()
            langs.append(langsCookie)

        if useSubdomain:
            langs.extend(tool.getSubdomainLanguages())

        if useCcTLD:
            langs.extend(tool.getCcTLDLanguages())

        # Get langs from request
        if useRequest:
            langs.extend(tool.getRequestLanguages())

        # Get default
        if useDefault:
            langs.append(tool.getDefaultLanguage())

        # Filter None languages
        langs = [lang for lang in langs if lang is not None]

        # Set cookie language to language
        if setCookieAlways and useCookie and langs[0] != langsCookie:
            tool.setLanguageCookie(langs[0], noredir=True)

        self.default_language = langs[-1]
        self.language = langs[0]
        self.language_list= langs[1:-1]


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
registerToolInterface('portal_languages', ILanguageTool)

