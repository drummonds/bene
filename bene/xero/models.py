from django.db import models


class ContactGroup(models.Model):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField('Name of ContactGroup', blank=True, max_length=255)
    xero_id = models.CharField('', blank=True, max_length=255)  # store the guid

    def __str__(self):
        return self.name

    #def get_absolute_url(self):
    #    return reverse('users:detail', kwargs={'username': self.username})
