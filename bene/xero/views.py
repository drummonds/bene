from dateutil.parser import parse

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



class HomeView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        c = Company.objects.first()
        try:
            company_name = c.name
        except:
            company_name = 'No company set up yet'

        context.update({'company': company_name,
                        'authorization_url' : reverse('xero:do_auth'),
                        'ob_authorization_url' : reverse('xero:ob_authorize'),})
        return context


class DoAuthView(RedirectView, LoginRequiredMixin):
    permanent = False
    query_string = True
    #pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        # Get and approved the request token
        print('Callback URI = |{}|'.format(self.request.build_absolute_uri(reverse('xero:oauth'))))
        credentials = PublicCredentials(
            settings.XERO_CONSUMER_KEY, settings.XERO_CONSUMER_SECRET,
            callback_uri=self.request.build_absolute_uri(reverse('xero:oauth')))
        # Save request token and secret and other OAuth session data
        print(f'In DoAuthView credentials before redirect are : {credentials.state}')
        self.request.session['oauth_persistent'] = encode_oauth(credentials.state)
        self.request.session.modified = True
        # Redirect to Xero at url provided by credentials generation
        return credentials.url


class OAuthView(RedirectView, LoginRequiredMixin):
    permanent = False
    query_string = True
    #pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        if 'oauth_token' not in kwargs or 'oauth_verifier' not in kwargs or 'org' not in kwargs:
            self.send_error(500, message='Missing parameters required.')
            return

        OAUTH_PERSISTENT_SERVER_STORAGE = decode_oauth(self.request.session['oauth_persistent'])
        print(f'In OAuthView credentials after redirect are : {credentials.state}')
        stored_values = OAUTH_PERSISTENT_SERVER_STORAGE
        credentials = PublicCredentials(**stored_values)

        try:
            credentials.verify(kwargs['oauth_verifier'])

            # Resave our verified credentials
            for key, value in credentials.state.items():
                OAUTH_PERSISTENT_SERVER_STORAGE.update({key: value})
            self.request.session['oauth_persistent'] = encode_oauth(OAUTH_PERSISTENT_SERVER_STORAGE)
            self.request.session.modified = True

        except XeroException as e:
            self.send_error(500, message='{}: {}'.format(e.__class__, e.message))
            return

        # Once verified, api can be invoked with xero = Xero(credentials)
        return reverse('xero:xero')


def encode_oauth(raw_data):
    """Use like OAUTH_PERSISTENT_SERVER_STORAGE = encode_oauth(credentials.state)
    Used because you need to parse datetime to store as json data."""
    result = {}
    for key, value in raw_data.items():
        if key in ('oauth_authorization_expires_at', 'oauth_expires_at'):
            result.update({key: value.isoformat()})
        else:
            result.update({key: value})
    return result


def decode_oauth(raw_data):
    """Use like OAUTH_PERSISTENT_SERVER_STORAGE = decode_oauth(self.request.session['oauth_persistent'])
    Used because you need to parse datetime to store as json data."""
    result = {}
    for key, value in raw_data.items():
        if key in ('oauth_authorization_expires_at', 'oauth_expires_at'):
            result.update({key: parse(value)})  # parse datetime in ISO str format to datetime object
        else:
            result.update({key: value})
    return result


class XeroView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/authorization.html'

    def get_context_data(self, **kwargs):
        context = super(XeroView, self).get_context_data(**kwargs)

        stored_values = decode_oauth(self.request.session['oauth_persistent'])
        credentials = PublicCredentials(**stored_values)

        try:
            self.xero = Xero(credentials)

        except XeroException as e:
            self.send_error(500, message='{}: {}'.format(e.__class__, e.message))
            return

        # self.ais_action(dry_run=False)

        xero_json = self.xero.get("https://api.xero.com/api.xro/2.0/organisation")
        context['xero_json'] = xero_json.json()

        return context


class AuthorizationView(RedirectView, LoginRequiredMixin):
    permanent = False
    query_string = True
    #pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        credentials = PublicCredentials(
            settings.XERO_CONSUMER_KEY, settings.XERO_CONSUMER_SECRET,
            callback_uri=reverse('xero:oauth'))

        # Save generated credentials details to persistent storage
        for key, value in credentials.state.items():
            OAUTH_PERSISTENT_SERVER_STORAGE.update({key: value})

        print('Second redirect to |{}|'.format(credentials.url))
        return credentials.url


# =============================================
# Using the openbankproject authorisaction view
# =============================================

class OBIndexView(TemplateView):
    template_name = "ob_index.html"

    def get_context_data(self, **kwargs):
        context = super(OBIndexView, self).get_context_data(**kwargs)

        openbank = OAuth1Session(
            settings.OAUTH_CLIENT_KEY,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            callback_uri=settings.OAUTH_CALLBACK_URI
        )

        fetch_response = openbank.fetch_request_token(settings.OAUTH_TOKEN_URL)
        authorization_url = openbank.authorization_url(settings.OAUTH_AUTHORIZATION_URL)

        self.request.session['oauth_token'] = fetch_response.get('oauth_token')
        self.request.session['oauth_secret'] = fetch_response.get('oauth_token_secret')
        self.request.session.modified = True

        context['authorization_url'] = authorization_url
        context['token'] = self.request.session['oauth_token']
        return context

class OBAuthorizationView(TemplateView):
    template_name = "ob_authorization.html"

    def get_context_data(self, **kwargs):
        context = super(OBAuthorizationView, self).get_context_data(**kwargs)

        xero_session = OAuth1Session(
            settings.XERO_CONSUMER_KEY,
            settings.XERO_CONSUMER_SECRET,
            resource_owner_key=self.request.session['oauth_token'],
            resource_owner_secret=self.request.session['oauth_secret']
        )

        xero_session.parse_authorization_response(self.request.build_absolute_uri())

        fetch_response = xero_session.fetch_access_token(settings.OAUTH_ACCESS_TOKEN_URL)


        self.request.session['oauth_token'] = fetch_response.get('oauth_token')
        self.request.session['oauth_secret'] = fetch_response.get('oauth_token_secret')

        context['xero_json'] = fetch_response
        return context

class OBXeroView(TemplateView):
    template_name = "ob_authorization.html"

    def get_context_data(self, **kwargs):
        context = super(OBXeroView, self).get_context_data(**kwargs)

        openbank = get_oauth(self.request)

        xero_json = openbank.get("https://api.xero.com/api.xro/2.0/organisation")
        context['xero_json'] = xero_json.json()

        return context
