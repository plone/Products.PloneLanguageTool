## Script (Python) "switchLanguage"
##title=
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=set_language=None
REQUEST=context.REQUEST

if set_language:
    lang=set_language

here_url=context.absolute_url()

query = {}
if lang:
    # no cookie support
    query['cl']=lang

if set_language:
    query['set_language']=lang

qst="?"
for k, v in query.items():
    qst=qst+"%s=%s&" % (k, v)
redirect=here_url+qst[:-1]

REQUEST.RESPONSE.redirect(redirect)

