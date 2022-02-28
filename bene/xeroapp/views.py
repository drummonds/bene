import datetime as dt
from dateutil.parser import parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.views.generic import TemplateView, RedirectView
from requests_oauthlib import OAuth1Session

from xero import Xero as PyXero
from xero.auth import PublicCredentials
from xero.exceptions import XeroException, XeroBadRequest

from bene.celery import reload_task
from .models import Invoice
from sereports.models import (
    Company,
)  # This could be bene.serports but Django likes this better and needs to match

# settings

# You should use redis or a file based persistent
# storage handler if you are running multiple servers.
OAUTH_PERSISTENT_SERVER_STORAGE = {}


def get_oauth(request):
    xero_obj = OAuth1Session(
        settings.XERO_CONSUMER_KEY,
        client_secret=settings.XERO_CONSUMER_SECRET,
        resource_owner_key=request.session["oauth_token"],
        resource_owner_secret=request.session["oauth_secret"],
    )
    return xero_obj


class XHomeView(LoginRequiredMixin, TemplateView):
    """Xero Home view, starting point to go to a number of Routines which intereact with Xero and do some job.
    eg Updating the database, test data, last months report etc"""

    template_name = "xeroapp/home.html"
    redirect_field_name = ""

    def get_context_data(self, **kwargs):
        context = super(XHomeView, self).get_context_data(**kwargs)

        c = Company.objects.first()
        try:
            company_name = c.name
        except:
            company_name = "No company set up yet"

        # Display an error message for onetime if presents
        if hasattr(self.request.session, "auth_error"):
            messages.error(self.request, self.request.session["auth_error"])
            del self.request.session["auth_error"]
            self.request.session.modified = True
        try:
            inv = Invoice.objects.latest("updated_date_utc")
            last_updated = inv.updated_date_utc.strftime("%Y-%m-%d %H:%M")
        except Invoice.DoesNotExist:
            last_updated = "No data so no DB update"

        context.update(
            {
                "company": company_name,
                "authorization_url": reverse("xeroapp:do_auth"),
                "version": settings.VERSION,
                "last_updated": last_updated,
            }
        )
        return context


class DoAuthView(LoginRequiredMixin, RedirectView):
    """Needs a parameter to show which report you aim to run after authorisation."""

    redirect_field_name = ""
    permanent = False
    query_string = True
    # pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        try:
            self.request.session["xero_report"] = self.request.GET["report"]
        except:
            self.request.session["xero_report"] = reverse("xeroapp:xero")

        # Get and approved the request token
        credentials = PublicCredentials(
            settings.XERO_CONSUMER_KEY,
            settings.XERO_CONSUMER_SECRET,
            callback_uri=self.request.build_absolute_uri(reverse("xeroapp:oauth")),
        )
        # Save request token and secret and other OAuth session data
        self.request.session["oauth_persistent"] = encode_oauth(credentials.state)
        self.request.session.modified = True
        # Redirect to Xero at url provided by credentials generation
        return credentials.url


class OAuthView(LoginRequiredMixin, RedirectView):
    redirect_field_name = ""
    permanent = False
    query_string = True
    # pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        params = self.request.GET
        if (
            "oauth_token" not in params
            or "oauth_verifier" not in params
            or "org" not in params
        ):
            self.request.session[
                "auth_error"
            ] = f"OAuthView Error Missing parameters required. {params}"
            return reverse("xeroapp:index")

        OAUTH_PERSISTENT_SERVER_STORAGE = decode_oauth(
            self.request.session["oauth_persistent"]
        )
        stored_values = OAUTH_PERSISTENT_SERVER_STORAGE
        credentials = PublicCredentials(**stored_values)

        try:
            credentials.verify(params["oauth_verifier"])

            # Resave our verified credentials
            for key, value in credentials.state.items():
                OAUTH_PERSISTENT_SERVER_STORAGE.update({key: value})
            self.request.session["oauth_persistent"] = encode_oauth(
                OAUTH_PERSISTENT_SERVER_STORAGE
            )
            self.request.session.modified = True

        except XeroException as e:
            self.request.session["auth_error"] = "{}: {}".format(e.__class__, e.message)
            return reverse("xeroapp:index")

        # Once verified, api can be invoked with xero = Xero(credentials)
        return self.request.session["xero_report"]


def encode_oauth(raw_data):
    """Use like OAUTH_PERSISTENT_SERVER_STORAGE = encode_oauth(credentials.state)
    Used because you need to parse datetime to store as json data."""
    result = {}
    for key, value in raw_data.items():
        if key in ("oauth_authorization_expires_at", "oauth_expires_at"):
            result.update({key: value.isoformat()})
        else:
            result.update({key: value})
    return result


def decode_oauth(raw_data):
    """Use like OAUTH_PERSISTENT_SERVER_STORAGE = decode_oauth(self.request.session['oauth_persistent'])
    Used because you need to parse datetime to store as json data."""
    result = {}
    for key, value in raw_data.items():
        if key in ("oauth_authorization_expires_at", "oauth_expires_at"):
            result.update(
                {key: parse(value)}
            )  # parse datetime in ISO str format to datetime object
        else:
            result.update({key: value})
    return result


class TestXeroView(LoginRequiredMixin, TemplateView):
    template_name = "xeroapp/xero_result.html"
    redirect_field_name = ""

    def get_context_data(self, **kwargs):
        context = super(TestXeroView, self).get_context_data(**kwargs)

        stored_values = decode_oauth(self.request.session["oauth_persistent"])
        credentials = PublicCredentials(**stored_values)

        try:
            self.xero = PyXero(credentials)

        except XeroException as e:
            self.request.session[
                "auth_error"
            ] = f"TestXeroView Error {e.__class__}: {e.message}"
            return reverse("xeroapp:index")

        # self.ais_action(dry_run=False)

        orgs = self.xero.organisations.all()
        context["xero_test"] = orgs[0]  # Just get the dictionary

        return context


class DBUpdateView(LoginRequiredMixin, TemplateView):
    template_name = "xeroapp/xero_db_update.html"
    redirect_field_name = ""

    def get_context_data(self, **kwargs):
        context = super(DBUpdateView, self).get_context_data(**kwargs)

        stored_values = decode_oauth(self.request.session["oauth_persistent"])
        credentials = PublicCredentials(**stored_values)

        try:
            self.xero = PyXero(credentials)

        except XeroException as e:
            self.request.session[
                "auth_error"
            ] = f"TestXeroView Error {e.__class__}: {e.message}"
            return reverse("xeroapp:index")

        # self.ais_action(dry_run=False)

        # reload_task.apply_async(stored_values)
        reload_task.delay(stored_values)

        # context['xero_groups'] = groups
        print("DBUpdateView has got groups - placeholder for DB update")

        return context
