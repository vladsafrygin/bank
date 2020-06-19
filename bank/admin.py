from django.contrib import admin
from .models import Post
from dal import autocomplete
from django import forms

"""
Автор: Козлов Даниил
Цель: регистрация классов в админ-панели
"""


class PostAdmin(admin.ModelAdmin):
    model = Post


class form(forms.ModelForm):
    class Meta:
        widgets = {'bank': autocomplete.ModelSelect2(url='bank-autocomplete')}


admin.site.register(Post, PostAdmin)
