from django.db import models

# Create your models here.

class ImageNetList(models.Model):
    list_text = models.CharField(max_length=10000)
    pub_date = models.DateTimeField('date published')
