from django.db import models


class Url(models.Model):
    url = models.CharField(verbose_name='原链接', max_length=800)