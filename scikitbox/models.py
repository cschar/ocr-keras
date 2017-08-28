from django.db import models

# Create your models here.

class ImageNetList(models.Model):
    list_text = models.CharField(max_length=10000)
    pub_date = models.DateTimeField('date published')


class RightsSupport(models.Model):

    class Meta:

        managed = False  # No database table creation or deletion operations \
                         # will be performed for this model.

        permissions = (
            ('image_rights', 'rights to fetch/normalize images'),
        )