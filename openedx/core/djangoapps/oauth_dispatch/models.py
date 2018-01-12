"""
Specialized models for oauth_dispatch djangoapp
"""

from datetime import datetime
from django.db import models
from pytz import utc

from oauth2_provider.settings import oauth2_settings


class RestrictedApplication(models.Model):
    """
    This model lists which django-oauth-toolkit Applications are considered 'restricted'
    and thus have a limited ability to use various APIs.

    A restricted Application will only get expired token/JWT payloads
    so that they cannot be used to call into APIs.
    """

    application = models.ForeignKey(oauth2_settings.APPLICATION_MODEL, null=False)

    def __unicode__(self):
        """
        Return a unicode representation of this object
        """
        return u"<RestrictedApplication '{name}'>".format(
            name=self.application.name
        )

    @classmethod
    def set_access_token_as_expired(cls, access_token):
        """
        For access_tokens for RestrictedApplications, put the expire timestamp into the beginning of the epoch
        which is Jan. 1, 1970
        """
        access_token.expires = datetime(1970, 1, 1, tzinfo=utc)

    @classmethod
    def verify_access_token_as_expired(cls, access_token):
        """
        For access_tokens for RestrictedApplications, make sure that the expiry date
        is set at the beginning of the epoch which is Jan. 1, 1970
        """
        return access_token.expires == datetime(1970, 1, 1, tzinfo=utc)

    @classmethod
    def is_token_a_restricted_application(cls, token):
        """
        Returns if token is issued to a RestriectedApplication
        """

        if isinstance(token, basestring):
            # if string is passed in, do the look up
            token_obj = AccessToken.objects.get(token=token)
        else:
            token_obj = token

        return cls.get_restricted_application(token_obj.application) is not None

    @classmethod
    def get_restricted_application(cls, application):
        """
        For a given application, get the related restricted application
        """
        return RestrictedApplication.objects.filter(application=application.id).first()