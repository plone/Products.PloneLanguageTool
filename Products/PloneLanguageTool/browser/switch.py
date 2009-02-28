from Products.Five import BrowserView

class LanguageSwitcher(BrowserView):

    def __call__(self, set_language=None):
        here_url=self.context.absolute_url()

        query = {}
        if set_language:
            # no cookie support
            query['cl'] = set_language
            query['set_language']=set_language

        qst="?"
        for k, v in query.items():
            qst = qst + "%s=%s&" % (k, v)
        redirect = here_url + qst[:-1]

        self.request.RESPONSE.redirect(redirect)
