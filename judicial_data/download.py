import pandas as pd
from time import sleep
from os import path
from urllib.request import urlretrieve

# First date for which data is available.
MIN_DATE = pd.Timestamp('1981-01-01')

# Seconds to pause to be a good server user.
PAUSE = 3

# URL formats. We try them in order.
PDF_URL = 'https://www.uscourts.gov/judges-judgeships/judicial-vacancies/archive-judicial-vacancies/{}/vacancies/pdf'
HTML_URL = 'https://www.uscourts.gov/judges-judgeships/judicial-vacancies/archive-judicial-vacancies/{}/vacancies/html'
HTML_URL2 = 'https://www.uscourts.gov/judges-judgeships/judicial-vacancies/archive-judicial-vacancies/{}/vacancies'

def download_data(begin=MIN_DATE, end=None):
    if end is None:
        end = pd.Timestamp.now()

    for d in pd.date_range(begin, end, freq='MS'):
        ym = d.strftime('%Y/%m')
        filename = d.strftime('raw/%Y_%m')
        if path.exists(filename + '.pdf') or path.exists(filename + '.html'):
            continue
        print(filename)
        sleep(3)
        try:
            urlretrieve(PDF_URL.format(ym), filename+'.pdf')
            continue
        except:
            pass
        try:
            urlretrieve(HTML_URL.format(ym), filename+'.html')
            continue
        except:
            pass
        try:
            urlretrieve(HTML_URL2.format(ym), filename+'.html')
            continue
        except:
            pass
