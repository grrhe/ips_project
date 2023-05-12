import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_tickers():
    df = pd.read_csv("tickers_screener.csv")
    return df['Symbol']