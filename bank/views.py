import csv
import io
import sys, traceback
from audioop import reverse
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render
from .models import Post
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import re
from dbfread import DBF
from time import localtime, strftime
import xlwt
from tqdm import tqdm


def index(request):
    """
    Автор: Козлов Даниил
    Цель: подключить основную html страницу
    :param request:
    :return: рендер шаблона 'index.html'
    """
    return render(request, 'index.html')


def profile_upload(request):
    """
    Автор: Козлов Даниил
    Цель: Загрузка БД

    :param request:
    :return: рендер шаблона
    """
    print('11111111111111111111111111')
    # declaring template
    template = "profile_upload.html"
    data = Post.objects.all()
    print('222222222222222222222222')
    # prompt is a context variable that can have different values      depending on their context
    # GET request returns the value of the data with the specified key.
    if request.method == "GET":
        return render(request, template)
    print('333333333333333333333333333333333333333')
    csv_file = request.FILES['file']
    print('4444444444444444444444444444444444444444444444444')
    # let's check if it is a csv file
    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'THIS IS NOT A CSV FILE')
    print('55555555555555555555555555555555')
    data_set = csv_file.read().decode('cp1251')
    print(data_set.count('\n'))
    # setup a stream which is when we loop through each line we are able to handle a data in a stream
    io_string = io.StringIO(data_set)
    next(io_string)
    y = 1
    j = 0
    for column in tqdm(csv.reader(io_string, delimiter=';', quotechar="|")):
        _, created = Post.objects.update_or_create(
            Number=column[0],
            REGN=column[1],
            NAME_B=column[2],
            ROOT=column[3],
            SIM_R=column[4],
            SIM_V=column[5],
            SIM_ITOGO=column[6],
            DT=column[7],
        )
        j += 1
    context = {'index': j}
    return render(request, 'index.html', context, {'flag': y})


def new_report(request):
    """
    Автор: Козлов Даниил
    Цель: проверить наличие новой отчетности
    :param request:
    :return: в зависимости от наличия новой отчености возвращает рендер шаблона, а также показатель ее наличия
    """
    try:
        button = request.GET.get("new_report")
        result = requests.get('https://cbr.ru/banking_sector/otchetnost-kreditnykh-organizaciy/')
        html = result.text
        soup = BeautifulSoup(html, 'html.parser')
        s = soup.select("div")[158].get_text()
        s = str(s)
        result = re.findall(r'\d{2}\.\d{2}', s)
        obj = Post.objects.all()[0]
        r_name = obj.NAME_B
        qr_dates = Post.objects.filter(NAME_B=r_name)
        datess = []
        for record in qr_dates:
            if str(record.DT) not in datess:
                datess.append(str(record.DT))
        if result[0] == '01.04':
            itog = 'not'
        return render(request, 'index.html', {'itog': itog, 'datess': datess})
    except Exception as e:
        print(e)
        itog = 'yes'
        return render(request, 'includes/index_new_report.html', {'itog': itog})

codes = []

def list_of_banks(request):
    try:
        f = 1
        obj = Post.objects.all()[0]
        r_date = obj.DT
        qr_banks = Post.objects.filter(DT=r_date)
        bankes = []
        for record in qr_banks:
            if str(record.NAME_B) not in bankes:
                bankes.append(str(record.NAME_B))
        return render(request, 'index.html', {'result': f, 'bankes': bankes})
    except Exception as e:
        print(e)
        return render(request, 'includes/index_new_report.html', {'rort': f})


def new_database(request):
    csv_file = 'bank/BD1.csv'
    with open(csv_file) as f:
        data_set = f.read()
    io_string = io.StringIO(data_set)
    for column in tqdm(csv.reader(io_string, delimiter=';', quotechar="|"), total=data_set.count('\n') - 1):
        _, created = Post.objects.update_or_create(
            Number=column[0],
            REGN=column[1],
            NAME_B=column[2],
            ROOT=column[3],
            SIM_R=column[4],
            SIM_V=column[5],
            SIM_ITOGO=column[6],
            DT=column[7],
        )
    context = {}
    return render(request, 'index.html', context)


def parser(request):
    """
    Автор:Козлов Даниил
    Цель: Обновление БД
    :param request:
    :return: обновленную базу данных в фромате DataFrame
    """
    result = requests.get('https://cbr.ru/banking_sector/otchetnost-kreditnykh-organizaciy/')
    html = result.text
    soup = BeautifulSoup(html)
    # читаем старую базу данных (в CSV)
    data = pd.read_csv('BD.csv')
    # парсинг сайта ЦБ, находим, есть ли данные на определённый период времени, если нет, то s == []
    s2 = soup.find_all('a', href="/vfs/credit/forms/102-20200401.rar")
    s1 = soup.find_all('a', href="/vfs/credit/forms/102-20200101.rar")
    s3 = soup.find_all('a', href="/vfs/credit/forms/102-20200701.rar")
    s4 = soup.find_all('a', href="/vfs/credit/forms/102-20201001.rar")
    if s1 == []:
        print('Нет данных на 01.01 2020')
    elif s2 == []:
        print('Нет данных на 04.01 2020')
    elif s3 == []:
        print('Нет данных на 07.01 2020')
        # Выгружаем данные за прошлый период времени
        # Необходимо скачать rar архив с сайта ЦБ по ссылке https://cbr.ru/vfs/credit/forms/102-20200401.rar
        # и распаковать оттуда два файла NP1 и P1
        table1 = DBF('22020NP1.DBF', load=True, encoding='cp866')
        frame1 = pd.DataFrame(iter(table1))
        table2 = DBF('22020_P1.DBF', load=True, encoding='cp866')
        frame2 = pd.DataFrame(iter(table2))
        frame2 = frame2.fillna(0)
        result = pd.merge(frame1, frame2, on='REGN')
        new = result.groupby(['NAME_B']).sum().reset_index()
        new = new.drop(['REGN'], axis=1)
        new_result = pd.merge(new, frame1, on='NAME_B')
        new_result['DT'] = '2020-04-01'
        final = pd.concat([new_result, data], ignore_index=True)
        final.to_csv('BD.csv')
    elif s4 == []:
        # Необходимо скачать rar архив с сайта ЦБ по ссылке https://cbr.ru/vfs/credit/forms/102-20200701.rar
        # и распаковать оттуда два файла NP1 и P1
        print('Нет данных на 10.01 2020')
        table1 = DBF('32020NP1.DBF', load=True, encoding='cp866')
        frame1 = pd.DataFrame(iter(table1))
        table2 = DBF('32020_P1.DBF', load=True, encoding='cp866')
        frame2 = pd.DataFrame(iter(table2))
        frame2 = frame2.fillna(0)
        result = pd.merge(frame1, frame2, on='REGN')
        new = result.groupby(['NAME_B']).sum().reset_index()
        new = new.drop(['REGN'], axis=1)
        new_result = pd.merge(new, frame1, on='NAME_B')
        new_result['DT'] = '2020-07-01'
        final = pd.concat([new_result, data], ignore_index=True)
        final.to_csv('BD.csv')
    return final


def choises(request):
    """
    Автор: Сафрыгин Владислав
    Цель: передать значение выбора пользователя по виду отчета
    :param request:
    :return: рендер шаблона 'index.html', словарь с выбранным типом отчета и списком банков
    """
    results = request.GET.get("choises")
    bank_list = Post.objects.all()
    print(results)
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
    Автор: Сафрыгин Владислав
    Цель: Получения названия банка, проверка наличия такого в БД, загрузка отчета по банку в случае наличия
    :param request:
    :return: рендер нужного шаблона в зависимости от наличия банка в БД, название введенного пользователем банка
    """
    global bank_name
    try:
        bank_name = Post.objects.filter(NAME_B=request.GET.get("bank"))[0]
        if (request.method == "GET") and ('bank' in request.GET) and (
                request.GET['bank'] == bank_name.NAME_B):
            i = -1
            for obj in Post.objects.filter(NAME_B=request.GET.get('bank')):
                i += 1
                df.loc[i, 'ROOT'] = obj.ROOT
                df.loc[i, 'NAME_B'] = obj.NAME_B
                df.loc[i, 'SIM_R'] = obj.SIM_R
                df.loc[i, 'SIM_V'] = obj.SIM_V
                df.loc[i, 'SIM_ITOGO'] = obj.SIM_ITOGO
                df.loc[i, 'REGN'] = obj.REGN
                df.loc[i, 'DT'] = obj.DT
            tm_struct = localtime()
            filename = 'report_one_bank_' + strftime('%Y_%m_%d_%H_%M_%S', tm_struct) + '.xls'
            df.to_excel(filename)
            trfg = 1
            qr_codes = Post.objects.filter(NAME_B=request.GET.get("bank"))
            for record in qr_codes:
                if str(record.ROOT) not in codes:
                    codes.append(str(record.ROOT))
            return render(request, 'includes/main2_dop.html',
                          {'bank': str(request.GET['bank']), 'plot': trfg, 'codes': codes})
    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
        return render(request, 'includes/bank_not_found.html', {'bank': request.GET['bank']})


def input_date(request):
    """
    Автор: Сафрыгин Владислав
    Цель: загрузка отчета по всем банкам за определенную дату
    :param request:
    :return: рендер нужного шаблона в зависимости от резульата, выбранная пользователем дата
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
                dataframe.loc[i, 'ROOT'] = obj.ROOT
                dataframe.loc[i, 'NAME_B'] = obj.NAME_B
                dataframe.loc[i, 'SIM_R'] = obj.SIM_R
                dataframe.loc[i, 'SIM_V'] = obj.SIM_V
                dataframe.loc[i, 'SIM_ITOGO'] = obj.SIM_ITOGO
                dataframe.loc[i, 'REGN'] = obj.REGN
                dataframe.loc[i, 'DT'] = obj.DT
            tm_struct = localtime()
            filename = 'report_by_date_' + strftime('%Y_%m_%d_%H_%M_%S', tm_struct) + '.xls'
            dataframe.to_excel(filename)
            return render(request, 'includes/main1_dop.html', {'date': date})

    except Exception as e:
        print('exception:', e)
        return render(request, 'includes/date_not_found.html', {'date': request.GET['date']})


def graphic(request):
    """
    Автор: Сафрыгин Владислав
    Цель: Построить график на основе показателя выбранного пользователем
    :param request:
    :return: рендер шаблона 'graphic,html'
    """
    try:
        code = Post.objects.filter(ROOT=request.GET.get("graphic"), NAME_B=bank_name.NAME_B)[0]
        codes = Post.objects.filter(ROOT=request.GET.get("graphic"), NAME_B=bank_name.NAME_B)
        plt.ioff()
        i = -1
        dataframe1 = pd.DataFrame(columns=['NAME_B',
                                           'SIM_R',
                                           'SIM_V',
                                           'SIM_ITOGO',
                                           'REGN',
                                           'DT'
                                           ])
        for obj in codes:
            i += 1
            dataframe1.loc[i, 'SIM_ITOGO'] = obj.SIM_ITOGO
            dataframe1.loc[i, 'DT'] = obj.DT
        if dataframe1.shape[0] > 1:
            dataframe1.plot(kind='line', y='SIM_ITOGO', x='DT')
        elif dataframe1.shape[0] == 1:
            dataframe1.plot(kind='scatter', y='SIM_ITOGO', x='DT')
        plt.savefig('main2_dop.png')
        return render(request, 'includes/graphic.html', {'code': code.ROOT})
    except Exception as e:
        print(e)
        return render(request, 'includes/date_not_found.html')


def my_image(request):
    """
    Автор: Сафрыгин Владислав
    Цель: Вывод графика пользователю
    :param request:
    :return:
    """
    image_data = open("main2_dop.png", "rb").read()
    return HttpResponse(image_data, content_type="image/png")
