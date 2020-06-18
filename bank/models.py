from django.db import models
from django.views.generic.base import TemplateView


class Post(models.Model):
    NAME_B = models.CharField(max_length=200, default='1')
    SIM_R = models.BigIntegerField(default=1)
    SIM_V = models.BigIntegerField(default=1)
    SIM_ITOGO = models.BigIntegerField(default=1)
    REGN = models.CharField(max_length=200, default='1')
    DT = models.DateField(default=2019 / 10 / 12)


class tabl(models.Model):
    text = models.TextField(default='1', max_length=3000)


class decoding(models.Model):
    values = models.TextField(default='1', max_length=3000)

    def str(self):
        return self.title
