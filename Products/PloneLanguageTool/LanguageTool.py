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

from Products.Archetypes.debug import log

availableLanguages =  (
            ('aa', 'Afar'),
            ('ab', 'Abkhazian'),
            ('af', 'Afrikaans'),
            ('am', 'Amharic'),
            ('ar', 'Arabic'),
            ('as', 'Assamese'),
            ('ay', 'Aymara'),
            ('az', 'Azerbaijani'),
            ('ba', 'Bashkir'),
            ('be', 'Byelorussian (Belarussian)'),
            ('bg', 'Bulgarian'),
            ('bh', 'Bihari'),
            ('bi', 'Bislama'),
            ('bn', 'Bengali'),
            ('bo', 'Tibetan'),
            ('br', 'Breton'),
            ('ca', 'Catalan'),
            ('co', 'Corsican'),
            ('cs', 'Czech'),
            ('cy', 'Welsh'),
            ('da', 'Danish'),
            ('de', 'German'),
            ('dz', 'Bhutani'),
            ('el', 'Greek'),
            ('en', 'English'),
            ('eo', 'Esperanto'),
            ('es', 'Spanish'),
            ('et', 'Estonian'),
            ('eu', 'Basque'),
            ('fa', 'Persian'),
            ('fi', 'Finnish'),
            ('fj', 'Fiji'),
            ('fo', 'Faroese'),
            ('fr', 'French'),
            ('fy', 'Frisian'),
            ('ga', 'Irish (Irish Gaelic)'),
            ('gd', 'Scots Gaelic (Scottish Gaelic)'),
            ('gl', 'Galician'),
            ('gn', 'Guarani'),
            ('gu', 'Gujarati'),
            ('gv', 'Manx Gaelic'),
            ('ha', 'Hausa'),
            ('he', 'Hebrew'),
            ('hi', 'Hindi'),
            ('hr', 'Croatian'),
            ('hu', 'Hungarian'),
            ('hy', 'Armenian'),
            ('ia', 'Interlingua'),
            ('id', 'Indonesian'),
            ('ie', 'Interlingue'),
            ('ik', 'Inupiak'),
            ('is', 'Icelandic'),
            ('it', 'Italian'),
            ('iu', 'Inuktitut'),
            ('ja', 'Japanese'),
            ('jw', 'Javanese'),
            ('ka', 'Georgian'),
            ('kk', 'Kazakh'),
            ('kl', 'Greenlandic'),
            ('km', 'Cambodian'),
            ('kn', 'Kannada'),
            ('ko', 'Korean'),
            ('ks', 'Kashmiri'),
            ('ku', 'Kurdish'),
            ('kw', 'Cornish'),
            ('ky', 'Kirghiz'),
            ('la', 'Latin'),
            ('lb', 'Luxemburgish'),
            ('ln', 'Lingala'),
            ('lo', 'Laotian'),
            ('lt', 'Lithuanian'),
            ('lv', 'Latvian Lettish'),
            ('mg', 'Malagasy'),
            ('mi', 'Maori'),
            ('mk', 'Macedonian'),
            ('ml', 'Malayalam'),
            ('mn', 'Mongolian'),
            ('mo', 'Moldavian'),
            ('mr', 'Marathi'),
            ('ms', 'Malay'),
            ('mt', 'Maltese'),
            ('my', 'Burmese'),
            ('na', 'Nauru'),
            ('ne', 'Nepali'),
            ('nl', 'Dutch'),
            ('no', 'Norwegian'),
            ('oc', 'Occitan'),
            ('om', 'Oromo'),
            ('or', 'Oriya'),
            ('pa', 'Punjabi'),
            ('pl', 'Polish'),
            ('ps', 'Pashto'),
            ('pt', 'Portuguese'),
            ('qu', 'Quechua'),
            ('rm', 'Rhaeto-Romance'),
            ('rn', 'Kirundi'),
            ('ro', 'Romanian'),
            ('ru', 'Russian'),
            ('rw', 'Kiyarwanda'),
            ('sa', 'Sanskrit'),
            ('sd', 'Sindhi'),
            ('se', 'Northern S&aacute;mi'),
            ('sg', 'Sangho'),
            ('sh', 'Serbo-Croatian'),
            ('si', 'Singhalese'),
            ('sk', 'Slovak'),
            ('sl', 'Slovenian'),
            ('sm', 'Samoan'),
            ('sn', 'Shona'),
            ('so', 'Somali'),
            ('sq', 'Albanian'),
            ('sr', 'Serbian'),
            ('ss', 'Siswati'),
            ('st', 'Sesotho'),
            ('su', 'Sudanese'),
            ('sv', 'Swedish'),
            ('sw', 'Swahili'),
            ('ta', 'Tamil'),
            ('te', 'Telugu'),
            ('tg', 'Tajik'),
            ('th', 'Thai'),
            ('ti', 'Tigrinya'),
            ('tk', 'Turkmen'),
            ('tl', 'Tagalog'),
            ('tn', 'Setswana'),
            ('to', 'Tonga'),
            ('tr', 'Turkish'),
            ('ts', 'Tsonga'),
            ('tt', 'Tatar'),
            ('tw', 'Twi'),
            ('ug', 'Uigur'),
            ('uk', 'Ukrainian'),
            ('ur', 'Urdu'),
            ('uz', 'Uzbek'),
            ('vi', 'Vietnamese'),
            ('vo', 'Volap&uuml;k'),
            ('wo', 'Wolof'),
            ('xh', 'Xhosa'),
            ('yi', 'Yiddish'),
            ('yo', 'Yorouba'),
            ('za', 'Zhuang'),
            ('zh', 'Chinese'),
            ('zu', 'Zulu')
        )


class LanguageTool(UniqueObject, ActionProviderBase, SimpleItem):
    """ CMF Syndication Client  """

    id        = 'portal_languages'
    meta_type = 'Plone Language Tool'

    security = ClassSecurityInfo()

    supported_langs = []
    default_lang = 'en'
    fallback_lang = 'en'
    # copy global available_langs to class variable
    available_langs = list(availableLanguages)
    supported_langs = [l[0] for l in available_langs]

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
        if type(supportedLanguages) == type([]):
            self.supported_langs=supportedLanguages
        else:
            self.supported_langs=[supportedLanguages]


        if REQUEST:
	    REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def listAvailableLanguages(self):
        return self.available_langs

    def listSupportedLanguages(self):
        #FIXME: return supported languages
        return self.available_langs

    def getSupportedLanguages(self):
        #FIXME: return supported languages
        return self.available_langs

    def getAvailableLanguages(self):
        return self.available_langs

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

InitializeClass(LanguageTool)
