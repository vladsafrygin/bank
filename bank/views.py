import csv
import io
import pickle
from audioop import reverse
from tokenize import Comment
from django.http import HttpResponse
import os
from django.contrib import messages
from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Post, tabl, decoding
import pandas as pd
from dal import autocomplete


def index(request):
    return render(request, 'index.html')


class BankAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated():
            return Post.objects.none()
        qs = Post.objects.all()
        if self.q:
            qs = qs.filter(title__istartswith=self.q)
        return qs


def profile_upload(request):
    """
    Автор:
    Цель:

    :param request:
    :return: рендер шаблона
    """
    # declaring template
    template = "profile_upload.html"
    data = Post.objects.all()
    # prompt is a context variable that can have different values      depending on their context
    prompt = {
        'order': 'Order of the CSV should be name, email, address,    phone, profile',
        'profiles': data
    }
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template, prompt)
    csv_file = request.FILES['file']
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    data_set = csv_file.read().decode('cp1251')
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=';', quotechar="|"):
        _, created = Post.objects.update_or_create(
            NAME_B=column[0],
            SIM_R=column[1],
            SIM_V=column[2],
            SIM_ITOGO=column[3],
            REGN=column[4],
            DT=column[5],
        )
    context = {}
    return render(request, template, context)


def choises(request):
    """
    Автор: Сафрыгин Владислав
    Цель: передать значение выбора пользователя по виду отчета
    :param request:
    :return: рендер шаблона 'index.html', словарь с выбранным типом отчета и списком банков
    """
    results = request.GET.get("choises")
    bank_list = Post.objects.all()
    return render(request, 'index.html', {'choises': results, 'bank': '', 'bank_list': bank_list})


# def input_bank(request):
#  results1: object = request.GET.get('input_bank')
# print(results1)
#  bank_one = Post.objects.filter(NAME_B=results1)
# return render(request, 'includes/dopmain2.html',
#           {'input_name': results1, 'bank': '', 'bank_one': bank_one})


def input_bank(request):
    """

    :param request:
    :return:
    """
    try:
        bank_name = Post.objects.filter(NAME_B=request.GET.get("bank"))[0]
        if (request.method == "GET") and ('bank' in request.GET) and (
                request.GET['bank'] == bank_name.NAME_B):
            print('4444444444444444444444444444444444444444444444')
            tabl.objects.create(text=bank_name.NAME_B)
            print('555555555555555555555555555555555555555')
            return render(request, 'includes/main2_dop.html',
                          {'bank': str(request.GET['bank']), 'col_banks': decoding.values})
    except Exception:
        return render(request, 'includes/bank_not_found.html', {'bank': request.GET['bank']})





