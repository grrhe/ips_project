from time import sleep

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from settings import TOTALLY_NOT_A_PARSER


def get_tickers():
    '''Функция возвращающая список тикеров всех акций,
    торгуемых на американских биржах (NYSE, NASDAQ, AMEX)'''
    df = pd.read_csv("tickers_screener.csv")
    return df['Symbol']


def parse_yf_esg(start=0, stop=len(get_tickers())):
    '''Функция возвращающая словарь из esg рисков
    после парсинга значений с сайта Yahoo Finance'''
    esg_scores = {
        'Environment Risk Score': [],
        'Social Risk Score': [],
        'Governance Risk Score': []
    }
    tickers = get_tickers()[start:stop]
    for item in tickers:
        url = f'https://finance.yahoo.com/quote/{item}/sustainability?p={item}'
        headers = {'User-Agent': TOTALLY_NOT_A_PARSER}
        try:
            page = requests.get(url, headers=headers, timeout=10)
        except:
            page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            esg_scores['Environment Risk Score'].append(
                float(
                    soup.find_all(
                        'div',
                        class_='D(ib) Fz(23px) smartphone_Fz(22px) Fw(600)'
                    )[0].text
                )
            )
            esg_scores['Social Risk Score'].append(
                float(
                    soup.find_all(
                        'div',
                        class_='D(ib) Fz(23px) smartphone_Fz(22px) Fw(600)'
                    )[1].text
                )
            )
            esg_scores['Governance Risk Score'].append(
                float(
                    soup.find_all(
                        'div',
                        class_='D(ib) Fz(23px) smartphone_Fz(22px) Fw(600)'
                    )[0].text
                )
            )
        except IndexError:
            esg_scores['Environment Risk Score'].append(None)
            esg_scores['Social Risk Score'].append(None)
            esg_scores['Governance Risk Score'].append(None)
        sleep(0.1)
    return esg_scores


def parse_mc(tickers):
    '''Функция возвращающая словарь из прибылей и капитализации
    после парсинга значений с сайта Market cap'''
    errors = {'year': []}
    year_mod = {'2023': 2, '2022': 1, '2021': 0}
    multp = {'млн': 10**6, 'млрд': 10**9, 'трлн': 10**12, 'тыс.': 10**3}
    profit = {
        'Компания': [],
        'Чистая прибыль 2019': [],
        'Чистая прибыль 2020': [],
        'Чистая прибыль 2021': [],
        'Капитализация 2019': [],
        'Капитализация 2020': [],
        'Капитализация 2021': []
    }
    for ticker in tqdm(tickers):
        profit['Компания'].append(ticker)
        url = f'https://marketcap.ru/stocks/{ticker}/financial-statements/income-statement'
        headers = {'User-Agent': TOTALLY_NOT_A_PARSER}
        try:
            page = requests.get(url, headers=headers, timeout=10)
        except:
            page = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(page.text, "html.parser")
        base_table = soup.find_all(
            'table',
            class_='table table-striped table-detail-stocks table-responsive table-responsive-sm table-responsive-md table-responsive-lg table-responsive-xl'
        )[0]
        try:
            body = base_table.tbody.find_all('tr')
            head = base_table.thead.tr
            i = year_mod[head.find_all('th', class_='numeric-sort')[0].text]
            resume = True
        except:
            errors['year'].append((ticker, head.find_all('th', class_='numeric-sort')[0].text))
            resume = False

        if resume:
            pr = body[3].find_all('td')[i:3+i]
            pr_values = []
            for item in pr:
                sep_data = item.text.split(sep=' ')
                if len(sep_data) == 2:
                    clear_data = float(sep_data[0])*multp[sep_data[1]]
                    pr_values.append(clear_data)
                else:
                    pr_values.append(None)
            profit['Чистая прибыль 2019'].append(pr_values[2])
            profit['Чистая прибыль 2020'].append(pr_values[1])
            profit['Чистая прибыль 2021'].append(pr_values[0])

            cap = body[0].find_all('td')[i:3+i]
            cap_values = []
            for item in cap:
                sep_data = item.text.split(sep=' ')
                if len(sep_data) == 2:
                    clear_data = float(sep_data[0])*multp[sep_data[1]]
                    cap_values.append(clear_data)
                else:
                    cap_values.append(None)
            profit['Капитализация 2019'].append(pr_values[2])
            profit['Капитализация 2020'].append(pr_values[1])
            profit['Капитализация 2021'].append(pr_values[0])
        else:
            profit['Чистая прибыль 2019'].append(None)
            profit['Чистая прибыль 2020'].append(None)
            profit['Чистая прибыль 2021'].append(None)
            profit['Капитализация 2019'].append(None)
            profit['Капитализация 2020'].append(None)
            profit['Капитализация 2021'].append(None)
        sleep(0.25)
    return (profit, errors)
