import csv
import io
from audioop import reverse
from tokenize import Comment
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from .models import Post, decoding
import pandas as pd
from dal import autocomplete
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import re


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


def new_report(request):
    """

    :param request:
    :return:
    """
    try:
        button = request.GET.get("new_report")
        result = requests.get('https://cbr.ru/banking_sector/otchetnost-kreditnykh-organizac..')
        html = result.text
        soup = BeautifulSoup(html)
        s = soup.find('div', class_="versions_items _active")
        print(s)
        print('5')
        s = str(s)
        print(s)
        result = re.findall(r'\d{2}.\d{2}', s)
        print(result)
        itog = 'yes'
        return render(request, 'index.html', {'itog': itog})
    except Exception as e:
        print(e)
        itog = 'not'
        return render(request, 'index.html', {'itog':itog})


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

df = pd.DataFrame(columns=['NAME_B', 'SIM_R', 'SIM_V', 'SIM_ITOGO', 'REGN', 'DT'])


def input_bank(request):
    """

    :param request:
    :return:
    """
    try:
        bank_name = Post.objects.filter(NAME_B=request.GET.get("bank"))[0]
        if (request.method == "GET") and ('bank' in request.GET) and (
                request.GET['bank'] == bank_name.NAME_B):
            i = -1
            for obj in Post.objects.filter(NAME_B=request.GET.get('bank')):
                i += 1
                df.loc[i, 'NAME_B'] = obj.NAME_B
                df.loc[i, 'SIM_R'] = obj.SIM_R
                df.loc[i, 'SIM_V'] = obj.SIM_V
                df.loc[i, 'SIM_ITOGO'] = obj.SIM_ITOGO
                df.loc[i, 'REGN'] = obj.REGN
                df.loc[i, 'DT'] = obj.DT
            df.to_excel('report.xls')
            return render(request, 'includes/main2_dop.html',
                          {'bank': str(request.GET['bank']), 'col_banks': decoding.values})
    except Exception as e:
        print(e)
        return render(request, 'includes/bank_not_found.html', {'bank': request.GET['bank']})


def input_date(request):
    """

    :param request:
    :return:
    """
    try:
        if request.method == 'GET' and 'date' in request.GET:
            date = str(request.GET['date']).replace('.', '-')
            filtered_by_date = Post.objects.filter(DT=date)

            dataframe = pd.DataFrame(columns=['NAME_B',
                                              'SIM_R',
                                              'SIM_V',
                                              'SIM_ITOGO',
                                              'REGN',
                                              'DT'
                                              ])
            i = -1
            for obj in filtered_by_date:
                i += 1
                dataframe.loc[i, 'NAME_B'] = obj.NAME_B
                dataframe.loc[i, 'SIM_R'] = obj.SIM_R
                dataframe.loc[i, 'SIM_V'] = obj.SIM_V
                dataframe.loc[i, 'SIM_ITOGO'] = obj.SIM_ITOGO
                dataframe.loc[i, 'REGN'] = obj.REGN
                dataframe.loc[i, 'DT'] = obj.DT
            dataframe.to_excel('report_by_date.xls')
            return render(request, 'includes/main1_dop.html', {'date': date})

    except Exception as e:
        print('exception:', e)
        return render(request, 'includes/date_not_found.html', {'date': request.GET['date']})


def graphic(request):
    """

    :param request:
    :return:
    """
    results = request.GET.get("graphic")
    plt.ioff()
    if results == 'Сумма в рублях':
        df.plot(kind='line', y='SIM_R', x='DT')
        plt.savefig('main2_dop.png')
    elif results == 'Сумма в иностранных валютах':
        df.plot(kind='line', y='SIM_V', x='DT')
        plt.savefig('main2_dop.png')
    elif results == 'Итоговая сумма':
        df.plot(kind='line', y='SIM_ITOGO', x='DT')
        plt.savefig('main2_dop.png')
    return render(request, 'includes/graphic.html')


def my_image(request):
    """

    :param request:
    :return:
    """
    image_data = open("main2_dop.png", "rb").read()
    return HttpResponse(image_data, content_type="image/png")
