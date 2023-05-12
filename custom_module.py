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


def parse_yf_esg(start=0, stop=-1):
    '''Функция возвращающая словарь из esg рисков
    после парсинга значений с сайта Yahoo Finance'''
    esg_scores = {
        'Environment Risk Score': [],
        'Social Risk Score': [],
        'Governance Risk Score': []
    }
    tickers = get_tickers()[start:stop]
    for item in tickers:
        url = 'https://finance.yahoo.com/quote/' + item + '/sustainability?p=' + item
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
