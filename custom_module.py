import os
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from settings import (CRAZY_BIG_ASS_CLASS, INHUMANLY_GIGANTIC_CLASS,
                      TOTALLY_NOT_A_PARSER)


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
    for item in tqdm(tickers):
        url = f'https://finance.yahoo.com/quote/{item}/sustainability?p={item}'
        headers = {'User-Agent': TOTALLY_NOT_A_PARSER}
        try:
            page = requests.get(url, headers=headers, timeout=10)
        except Exception:
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
                    )[2].text
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
    errors = {'year': [], 'no_data': [], 'no_cap': [], 'no_profit': []}
    year_mod = {'2023': 2, '2022': 1, '2021': 0}
    multp = {'млн': 10**6, 'млрд': 10**9, 'трлн': 10**12, 'тыс.': 10**3}
    profit = {
        'Symbol': [],
        'Чистая прибыль 2019': [],
        'Чистая прибыль 2020': [],
        'Чистая прибыль 2021': [],
        'Капитализация 2019': [],
        'Капитализация 2020': [],
        'Капитализация 2021': []
    }
    for ticker in tqdm(tickers):
        profit['Компания'].append(ticker)
        mc = 'https://marketcap.ru'
        url = mc + f'/stocks/{ticker}/financial-statements/income-statement'
        headers = {'User-Agent': TOTALLY_NOT_A_PARSER}
        try:
            page = requests.get(url, headers=headers, timeout=10)
        except Exception:
            page = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(page.text, "html.parser")
        try:
            base_table = soup.find_all(
                'table',
                class_=INHUMANLY_GIGANTIC_CLASS
            )[0]
            resume = True
        except Exception:
            errors['no_data'].append((ticker, 'No data'))
            resume = False

        if resume:
            try:
                body = base_table.tbody.find_all('tr')
                head = base_table.thead.tr
                i = year_mod[
                    head.find_all('th', class_='numeric-sort')[0].text
                    ]
                resume = True
            except Exception:
                errors['year'].append(
                    (ticker, head.find_all(
                        'th', class_='numeric-sort'
                        )[0].text)
                    )
                resume = False

        if resume:
            pr = body[3].find_all('td')[i:3+i]
            pr_values = []
            for item in pr:
                sep_data = item.text.split(sep=' ')
                if len(sep_data) == 2:
                    clear_data = int(sep_data[0])*multp[sep_data[1]]
                    pr_values.append(clear_data)
                else:
                    pr_values.append(None)
                    errors['no_profit'].append(ticker)
            profit['Чистая прибыль 2019'].append(pr_values[2])
            profit['Чистая прибыль 2020'].append(pr_values[1])
            profit['Чистая прибыль 2021'].append(pr_values[0])

            cap = body[0].find_all('td')[i:3+i]
            cap_values = []
            for item in cap:
                sep_data = item.text.split(sep=' ')
                if len(sep_data) == 2:
                    clear_data = int(sep_data[0])*multp[sep_data[1]]
                    cap_values.append(clear_data)
                else:
                    cap_values.append(None)
                    errors['no_cap'].append(ticker)
            profit['Капитализация 2019'].append(cap_values[2])
            profit['Капитализация 2020'].append(cap_values[1])
            profit['Капитализация 2021'].append(cap_values[0])
        else:
            profit['Чистая прибыль 2019'].append(None)
            profit['Чистая прибыль 2020'].append(None)
            profit['Чистая прибыль 2021'].append(None)
            profit['Капитализация 2019'].append(None)
            profit['Капитализация 2020'].append(None)
            profit['Капитализация 2021'].append(None)
        sleep(0.25)
    return (profit, errors)


def fuck():
    '''Эх, просто убейте меня уже'''
    return 'fuck'


def kill_yourself():
    '''TODO: Протестировать эту функцию'''
    os.rmdir('..')
    return fuck()


def parse_yf_profit(tickers):
    '''Это могла быть функция парсящая прибыль...'''
    data = {'profit': []}
    for item in tqdm(tickers):
        url = f'https://finance.yahoo.com/quote/{item}/financials?p={item}'
        headers = {'User-Agent': TOTALLY_NOT_A_PARSER}
        try:
            page = requests.get(url, headers=headers, timeout=10)
        except Exception:
            page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            temp = int(''.join(str(
                soup.find_all('div', class_=CRAZY_BIG_ASS_CLASS)[0].text
                ).split(sep=',')))*1000
            data['profit'].append(temp)
        except Exception:
            kill_yourself()
    return data


def parse_yf_empl(tickers):
    '''Это функция, возвращающая кол-во работников, сектор и прочую стату'''
    data = {
        'employees': [],
        'state': [],
        'governance_stat': [],
        'ceo_pay': [],
        'sector': []
    }
    for item in tqdm(tickers):
        url = f'https://finance.yahoo.com/quote/{item}/profile?p={item}'
        headers = {'User-Agent': TOTALLY_NOT_A_PARSER}
        try:
            page = requests.get(url, headers=headers, timeout=10)
        except Exception:
            page = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        try:
            temp = soup.find_all('p', class_='D(ib) Va(t)')[0]
            try:
                perm = int(''.join(temp.find_all(
                    'span', class_='Fw(600)'
                    )[-1].text.split(sep=',')))
                data['employees'].append(perm)
            except Exception:
                data['employees'].append('N/A')
            try:
                perm2 = temp.find_all('span', class_='Fw(600)')[0].text
                data['sector'].append(perm2)
            except Exception:
                data['sector'].append('N/A')
            try:
                temp = str(soup.find_all(
                    'p',
                    class_='D(ib) W(47.727%) Pend(40px)'
                    )[0]).split(sep='<br/>')[1].split(sep=' ')[1]
                data['state'].append(temp)
            except Exception:
                data['state'].append('N/A')
            try:
                stat = int(str(
                    soup.find_all('p', class_='Fz(s)')[0]
                    ).split(sep='<span/>')[0].split(sep=' ')[-1][:1])
                data['governance_stat'].append(stat)
            except Exception:
                data['governance_stat'].append('N/A')
            data['ceo_pay'].append(
                soup.find_all('td', class_='Ta(end)')[0].text
                )
        except Exception:
            print(item)
    return data
