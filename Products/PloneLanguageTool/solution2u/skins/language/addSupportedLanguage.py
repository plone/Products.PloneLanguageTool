## Script (Python) "createLanguageObject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lang_code=None
##title=
##
from DateTime import DateTime
from Products.CMFPlone import transaction_note
from string import find
from Products.CMFCore.utils import getToolByName

REQUEST=context.REQUEST

if lang_code is None:
    raise Exception
ltool = getToolByName(context, 'portal_languages')
ltool.addLanguage(lang_code)

return REQUEST.RESPONSE.redirect(context.portal_url() + \
                                             "/portal_languages/langConfig?portal_status_message=Language+added")
