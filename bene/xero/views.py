from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from requests_oauthlib import OAuth1Session

from xero import Xero
from xero.auth import PublicCredentials

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
            callback_uri=reverse('xero_authorize')
        )

        fetch_response = xero.fetch_request_token(settings.OAUTH_TOKEN_URL)
        authorization_url = xero.authorization_url(settings.OAUTH_AUTHORIZATION_URL)

        self.request.session['oauth_token'] = fetch_response.get('oauth_token')
        self.request.session['oauth_secret'] = fetch_response.get('oauth_token_secret')
        self.request.session.modified = True

        test_xero = 'Checking'

        context.update({'company': company_name, 'xero_sync' : test_xero, 'authorization_url' : authorization_url})
        return context

class AuthorizationView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/authorization.html'

    def get_context_data(self, **kwargs):
        context = super(AuthorizationView, self).get_context_data(**kwargs)

        openbank = OAuth1Session(
            settings.OAUTH_CLIENT_KEY,
            client_secret=settings.OAUTH_CLIENT_SECRET,
            resource_owner_key=self.request.session['oauth_token'],
            resource_owner_secret=self.request.session['oauth_secret']
        )

        openbank.parse_authorization_response(self.request.build_absolute_uri())

        fetch_response = openbank.fetch_access_token(settings.OAUTH_ACCESS_TOKEN_URL)


        self.request.session['oauth_token'] = fetch_response.get('oauth_token')
        self.request.session['oauth_secret'] = fetch_response.get('oauth_token_secret')

        context['xero_json'] = fetch_response
        return context

class XeroView(TemplateView, LoginRequiredMixin):
    template_name = 'xero/authorization.html'

    def get_context_data(self, **kwargs):
        context = super(XeroView, self).get_context_data(**kwargs)

        openbank = get_oauth(self.request)

        xero_json = openbank.get("https://api.xero.com/api.xro/2.0/organisation")
        context['xero_json'] = xero_json.json()

        return context
