from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, RedirectView
from requests_oauthlib import OAuth1Session

from xero import Xero
from xero.auth import PublicCredentials
from xero.constants import (
    XERO_BASE_URL, REQUEST_TOKEN_URL, AUTHORIZE_URL, ACCESS_TOKEN_URL
)
from xero.exceptions import XeroException, XeroBadRequest

# You should use redis or a file based persistent
# storage handler if you are running multiple servers.
OAUTH_PERSISTENT_SERVER_STORAGE = {}

from sereports.models import Company

def get_oauth(request):
    xero = OAuth1Session(
        settings.XERO_CONSUMER_KEY,
        client_secret=settings.XERO_CONSUMER_SECRET,
        resource_owner_key=request.session['oauth_token'],
        resource_owner_secret=request.session['oauth_secret']
    )
    return xero


class SyncView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/sync.html'

    def get_context_data(self, **kwargs):
        context = super(SyncView, self).get_context_data(**kwargs)

        c = Company.objects.first()
        try:
            company_name = c.name
        except:
            company_name = 'No company set up yet'

        xero = OAuth1Session(
            settings.XERO_CONSUMER_KEY,
            client_secret=settings.XERO_CONSUMER_SECRET,
            callback_uri=reverse('xero:authorize')
        )


        fetch_response = xero.fetch_request_token(XERO_BASE_URL + REQUEST_TOKEN_URL)
        authorization_url = xero.authorization_url(XERO_BASE_URL + AUTHORIZE_URL)

        self.request.session['oauth_token'] = fetch_response.get('oauth_token')
        self.request.session['oauth_secret'] = fetch_response.get('oauth_token_secret')
        self.request.session.modified = True

        test_xero = 'Checking'

        context.update({'company': company_name, 'xero_sync' : test_xero, 'authorization_url' : authorization_url})
        return context

class AuthorizationView(RedirectView, LoginRequiredMixin):
    permanent = False
    query_string = True
    #pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        credentials = PublicCredentials(
            settings.XERO_CONSUMER_KEY, settings.XERO_CONSUMER_SECRET,
            callback_uri='xero:oauth')

        # Save generated credentials details to persistent storage
        for key, value in credentials.state.items():
            OAUTH_PERSISTENT_SERVER_STORAGE.update({key: value})

        return credentials.url


class OAuthView(RedirectView, LoginRequiredMixin):
    permanent = False
    query_string = True
    #pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        if 'oauth_token' not in kwargs or 'oauth_verifier' not in kwargs or 'org' not in kwargs:
            self.send_error(500, message='Missing parameters required.')
            return

        stored_values = OAUTH_PERSISTENT_SERVER_STORAGE
        credentials = PublicCredentials(**stored_values)

        try:
            credentials.verify(kwargs['oauth_verifier'])

            # Resave our verified credentials
            for key, value in credentials.state.items():
                OAUTH_PERSISTENT_SERVER_STORAGE.update({key: value})

        except XeroException as e:
            self.send_error(500, message='{}: {}'.format(e.__class__, e.message))
            return

        # Once verified, api can be invoked with xero = Xero(credentials)
        return reverse('xero:xero')


class XeroView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/authorization.html'

    def get_context_data(self, **kwargs):
        context = super(XeroView, self).get_context_data(**kwargs)

        xero = get_oauth(self.request)

        xero_json = xero.get("https://api.xero.com/api.xro/2.0/organisation")
        context['xero_json'] = xero_json.json()

        return context
