
res=context.portal_languages.i18nifyObject(context)
return context.REQUEST.RESPONSE.redirect(res.absolute_url())
